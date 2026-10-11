from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.application.services.network import NetworkService, hash_sensor_key
from app.infrastructure.models.alerts import Alert
from app.infrastructure.models.network import NetworkDevice, NetworkDeviceObservation, NetworkEvent
from app.infrastructure.schemas.network import SensorDataSubmission, SensorStatus
from app.application.services.alert import AlertService
from app.infrastructure.schemas.alerts import AlertUpdate, AlertStatus


def test_sensor_enrollment_uses_hashed_key_and_persists_telemetry():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, autoflush=False)()
    try:
        service = NetworkService(session)
        sensor, key = service.enroll_sensor("test-sensor", "Windows", "test", {"arp_discovery": True})
        assert sensor.sensor_key is None
        assert sensor.sensor_key_hash == hash_sensor_key(key)
        service.activate_sensor(sensor.id)

        result = service.process_submission(sensor, SensorDataSubmission.model_validate({
            "submitted_at": datetime.utcnow().isoformat(),
            "interfaces": [{"name": "Wi-Fi", "interface_type": "Wi-Fi", "is_active": True, "ipv4_addresses": ["192.168.1.10"]}],
            "snapshot": {"connection_status": "CONNECTED", "connection_type": "Wi-Fi", "gateway": "192.168.1.1", "local_ipv4": ["192.168.1.10"]},
            "devices": [{"ip_address": "192.168.1.20", "mac_address": "AA-BB-CC-DD-EE-FF", "discovery_method": "arp_neighbor_table"}],
        }))

        assert result["devices_processed"] == 1
        assert session.query(NetworkDevice).count() == 1
        assert session.query(NetworkDeviceObservation).count() == 1
        assert session.query(Alert).count() == 1
        # A repeated observation updates the existing device and does not
        # create a second device record.
        service.process_submission(sensor, SensorDataSubmission.model_validate({
            "devices": [{"ip_address": "192.168.1.20", "mac_address": "aa:bb:cc:dd:ee:ff", "discovery_method": "arp_neighbor_table"}],
        }))
        assert session.query(NetworkDevice).count() == 1
        assert session.query(NetworkDeviceObservation).count() == 2
        assert session.query(Alert).count() == 1
        assert session.query(NetworkEvent).count() == 1
        assert sensor.last_telemetry_at is not None
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def service():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine, autoflush=False)() as db:
        yield NetworkService(db)
    engine.dispose()


def enroll(service, name):
    sensor, key = service.enroll_sensor(name, "Windows", "test", {})
    service.activate_sensor(sensor.id)
    return sensor, key


def submit(service, sensor, **payload):
    return service.process_submission(sensor, SensorDataSubmission.model_validate(payload))


def test_private_addresses_do_not_merge_between_sensors(service):
    first, _ = enroll(service, "first-lan")
    second, _ = enroll(service, "second-lan")
    device = {"ip_address": "192.168.1.2", "mac_address": "aa:bb:cc:dd:ee:ff"}
    for sensor in [first, second]:
        assert submit(service, sensor, devices=[device])["alerts_created"] == 1
    assert service.db.query(NetworkDevice).count() == 2
    assert service.db.query(Alert).count() == 2


def test_mac_identity_takes_priority_over_recycled_ip(service):
    sensor, _ = enroll(service, "lan")
    submit(service, sensor, devices=[
        {"ip_address": "192.168.1.2", "mac_address": "aa:bb:cc:dd:ee:01"},
        {"ip_address": "192.168.1.3", "mac_address": "aa:bb:cc:dd:ee:02"},
    ])
    submit(service, sensor, devices=[{"ip_address": "192.168.1.3", "mac_address": "aa:bb:cc:dd:ee:01"}])
    assert service.db.query(NetworkDevice).count() == 2
    assert service.db.query(NetworkDevice).filter_by(mac_address="aa:bb:cc:dd:ee:02").count() == 1
    event = service.db.query(NetworkEvent).filter_by(event_type="IP_CHANGED").one()
    assert event.device.mac_address == "aa:bb:cc:dd:ee:01"


def test_stale_sensors_recover_but_revoked_sensors_cannot(service):
    sensors = [enroll(service, name) for name in ["stale-one", "stale-two"]]
    for sensor, _ in sensors:
        sensor.last_seen = datetime.utcnow() - timedelta(minutes=10)
    service.db.commit()
    assert service.mark_stale_sensors() == 2
    assert service.db.query(Alert).filter_by(title="Network sensor telemetry stale").count() == 2
    sensor, key = sensors[0]
    assert service.authenticate_sensor(str(sensor.id), key) is sensor
    submit(service, sensor, submitted_at="2099-01-01T00:00:00Z")
    assert sensor.status == SensorStatus.ACTIVE
    assert sensor.last_telemetry_at < datetime.utcnow() + timedelta(seconds=1)
    service.revoke_sensor(sensor.id)
    assert service.authenticate_sensor(str(sensor.id), key) is None


def test_health_alert_requires_consecutive_failures_for_same_target(service):
    sensor, _ = enroll(service, "diagnostics")
    for status in ["FAIL", "FAIL", "PASS", "FAIL", "FAIL"]:
        result = submit(service, sensor, health=[{"check_type": "CONNECTIVITY", "target": "192.168.1.1", "status": status}])
        assert result["alerts_created"] == 0
    assert submit(service, sensor, health=[{"check_type": "CONNECTIVITY", "target": "192.168.1.2", "status": "FAIL"}])["alerts_created"] == 0
    assert submit(service, sensor, health=[{"check_type": "CONNECTIVITY", "target": "192.168.1.1", "status": "FAIL"}])["alerts_created"] == 1
    assert submit(service, sensor, health=[{"check_type": "CONNECTIVITY", "target": "192.168.1.1", "status": "FAIL"}])["alerts_created"] == 0


def test_alert_history_stores_canonical_status_values(service):
    sensor, _ = enroll(service, "history")
    submit(service, sensor, devices=[{"ip_address": "192.168.1.2"}])
    alert = service.db.query(Alert).one()
    alerts = AlertService(service.db)
    alerts.update_alert(alert.id, AlertUpdate(status=AlertStatus.INVESTIGATING, reason="Reviewing evidence"))
    alerts.update_alert(alert.id, AlertUpdate(status=AlertStatus.INVESTIGATING))
    history = alerts.list_status_history(alert.id)
    assert len(history) == 1
    assert history[0].previous_status == "NEW"
    assert history[0].new_status == "INVESTIGATING"
    assert history[0].reason == "Reviewing evidence"
