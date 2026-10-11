"""Exercise real migration paths on disposable databases, never local .env DBs."""

from datetime import datetime
from uuid import uuid4

import pytest
import sqlalchemy as sa
from alembic import command, op
from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.script import ScriptDirectory
from sqlalchemy.orm import Session

from adopt_security_alerts import adopt
from app.application.services.network import NetworkService
from app.infrastructure.models.logs import RawLog
from app.infrastructure.schemas.network import SensorDataSubmission


@pytest.fixture
def connection(migration_config):
    engine = sa.create_engine("sqlite://")
    with engine.begin() as connection:
        migration_config.attributes["connection"] = connection
        yield connection
    engine.dispose()


@pytest.mark.parametrize("start", ["base", "c0f80578b423", "1a0db3d3e168", "cff8339db910", "d2b4c6e8f901"])
def test_upgrade_preserves_history_and_supports_writes(connection, migration_config, start):
    command.upgrade(migration_config, start)
    old_id = uuid4().hex
    if start != "base":
        connection.execute(sa.text("INSERT INTO raw_logs (id, source, log_type, raw_content, ingested_at) VALUES (:id, 'legacy-agent', 'syslog', 'keep this log', :now)"), {"id": old_id, "now": datetime(2026, 1, 1)})
    command.upgrade(migration_config, "head")
    assert MigrationContext.configure(connection).get_current_heads() == ("e7b91c4a2d60",)
    with Session(connection, autoflush=False) as db:
        db.add(RawLog(source_connector="new-agent", event_type="test", raw_content="new log"))
        db.commit()
        service = NetworkService(db)
        sensor, key = service.enroll_sensor("migration-test", "Windows", "test", {})
        service.activate_sensor(sensor.id)
        assert service.authenticate_sensor(str(sensor.id), key)
        service.process_submission(sensor, SensorDataSubmission.model_validate({
            "devices": [{"ip_address": "192.168.2.3", "mac_address": "aa:bb:cc:dd:ee:ff"}],
            "interfaces": [{"name": "Ethernet", "is_active": True}],
            "snapshot": {"connection_status": "CONNECTED"},
        }))
    if start != "base":
        old = connection.execute(sa.text("SELECT raw_content, source, source_connector FROM raw_logs WHERE id=:id"), {"id": old_id}).one()
        assert tuple(old) == ("keep this log", "legacy-agent", "legacy-agent")
    counts = {table: connection.execute(sa.text(f"SELECT count(*) FROM {table}")).scalar() for table in ["raw_logs", "network_devices", "alerts"]}
    command.upgrade(migration_config, "head")
    for table, count in counts.items():
        assert connection.execute(sa.text(f"SELECT count(*) FROM {table}")).scalar() == count
    assert not connection.exec_driver_sql("PRAGMA foreign_key_check").fetchall()


def test_repair_original_onboarding_missing_tables(connection, migration_config):
    command.upgrade(migration_config, "d2b4c6e8f901")
    # Reproduce the schema left by the original, already published c607 upgrade.
    for table in ["ioc_matches", "case_mitre_techniques", "case_incidents", "case_alerts", "email_verification_tokens", "threat_indicators", "mitre_techniques", "failed_logs", "threat_hunting_queries"]:
        connection.exec_driver_sql(f"DROP TABLE {table}")
    connection.exec_driver_sql("INSERT INTO raw_logs (id, source, log_type, raw_content, ingested_at) VALUES ('00000000000000000000000000000001', 'old', 'syslog', 'survivor', '2026-01-01')")
    command.upgrade(migration_config, "head")
    tables = set(sa.inspect(connection).get_table_names())
    assert {"failed_logs", "ioc_matches", "case_alerts", "email_verification_tokens", "threat_hunting_queries"} <= tables
    assert connection.exec_driver_sql("SELECT raw_content FROM raw_logs").scalar() == "survivor"


def test_existing_security_alert_table_can_be_validated_and_adopted(connection, migration_config):
    command.upgrade(migration_config, "1a0db3d3e168")
    with Operations.context(MigrationContext.configure(connection)):
        ScriptDirectory.from_config(migration_config).get_revision("cff8339db910").module.upgrade()
    connection.execute(sa.text("""INSERT INTO security_alerts
        (id, alert_type, severity, title, description, source, status, occurrence_count, first_seen, last_seen, created_at, updated_at)
        VALUES (:id, 'TEST', 'LOW', 'Retain me', 'Original evidence', 'legacy', 'NEW', 1, :now, :now, :now, :now)"""), {"id": uuid4().hex, "now": datetime(2026, 1, 1)})
    adopt(connection, migration_config)
    command.upgrade(migration_config, "head")
    assert connection.exec_driver_sql("SELECT title FROM security_alerts").scalar() == "Retain me"


def test_adoption_refuses_partial_table_without_advancing_version(connection, migration_config):
    command.upgrade(migration_config, "1a0db3d3e168")
    connection.exec_driver_sql("CREATE TABLE security_alerts (id CHAR(32) PRIMARY KEY)")
    with pytest.raises(RuntimeError, match="Incompatible"):
        adopt(connection, migration_config)
    assert MigrationContext.configure(connection).get_current_heads() == ("1a0db3d3e168",)


def test_legacy_audit_records_are_not_silently_dropped(connection, migration_config):
    command.upgrade(migration_config, "0e83e6c91c1c")
    connection.execute(sa.text("INSERT INTO audit_logs (id, action, ip_address, created_at) VALUES (:id, 'KEEP', '127.0.0.1', :now)"), {"id": uuid4().hex, "now": datetime(2026, 1, 1)})
    with pytest.raises(RuntimeError, match="audit_logs contains data"):
        command.upgrade(migration_config, "head")
    assert connection.exec_driver_sql("SELECT action FROM audit_logs").scalar() == "KEEP"


def test_legacy_sensor_key_constraint_is_repaired_without_losing_children(connection, migration_config):
    command.upgrade(migration_config, "d2b4c6e8f901")
    with Session(connection, autoflush=False) as db:
        service = NetworkService(db)
        sensor, key = service.enroll_sensor("legacy-sensor", "Windows", "test", {})
        sensor.sensor_key = key
        service.activate_sensor(sensor.id)
        service.process_submission(sensor, SensorDataSubmission.model_validate({"interfaces": [{"name": "Ethernet"}], "snapshot": {"connection_status": "CONNECTED"}}))
    with Operations.context(MigrationContext.configure(connection)):
        # Reproduce an earlier schema requiring plaintext sensor_key.
        with op.batch_alter_table("network_sensors") as batch:
            batch.alter_column("sensor_key", existing_type=sa.String(255), nullable=False)
    command.upgrade(migration_config, "head")
    assert connection.exec_driver_sql("SELECT count(*) FROM network_interfaces").scalar() == 1
    assert connection.exec_driver_sql("SELECT count(*) FROM network_snapshots").scalar() == 1
    with Session(connection) as db:
        service = NetworkService(db)
        new_sensor, _ = service.enroll_sensor("hash-only", "Linux", "test", {})
        assert new_sensor.sensor_key is None
    assert not connection.exec_driver_sql("PRAGMA foreign_key_check").fetchall()
