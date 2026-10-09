from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.application.services.network import NetworkService, hash_sensor_key
from app.infrastructure.models.alerts import Alert
from app.infrastructure.models.network import NetworkDevice, NetworkDeviceObservation, NetworkEvent
from app.infrastructure.schemas.network import SensorDataSubmission, SensorStatus


def test_sensor_enrollment_uses_hashed_key_and_persists_telemetry():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
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
