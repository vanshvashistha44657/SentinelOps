"""Opt-in PostgreSQL checks restricted to a disposable loopback test instance."""
import os
from datetime import datetime
from uuid import uuid4

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.migration import MigrationContext
from fastapi.testclient import TestClient
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from app.api.dependencies import get_db
from app.core.security import hash_password
from app.infrastructure.models.alerts import Alert
from app.infrastructure.models.iam import Permission, Role, User
from app.infrastructure.models.logs import RawLog
from app.main import app


@pytest.fixture
def pg_connection(migration_config):
    value = os.getenv("SENTINELOPS_TEST_POSTGRES_URL")
    if not value:
        pytest.skip("Set SENTINELOPS_TEST_POSTGRES_URL to the disposable PostgreSQL test instance")
    url = make_url(value)
    if url.get_backend_name() != "postgresql" or url.host not in {"127.0.0.1", "localhost"} or url.database != "sentinelops_verify":
        pytest.fail("PostgreSQL verification is restricted to a loopback sentinelops_verify database")
    engine = sa.create_engine(url)
    with engine.connect() as connection:
        if sa.inspect(connection).get_table_names():
            pytest.fail("Verification requires an empty disposable database; existing tables will not be touched")
        connection.rollback()
        transaction = connection.begin()
        migration_config.attributes["connection"] = connection
        try:
            yield connection
        finally:
            transaction.rollback()
    engine.dispose()


@pytest.mark.parametrize("start", ["base", "c0f80578b423", "1a0db3d3e168", "cff8339db910", "d2b4c6e8f901"])
def test_postgres_migrations_and_preserved_data(pg_connection, migration_config, start):
    command.upgrade(migration_config, start)
    log_id = uuid4()
    if start != "base":
        pg_connection.execute(sa.text("INSERT INTO raw_logs (id, source, log_type, raw_content, ingested_at) VALUES (:id, 'legacy', 'syslog', 'retain evidence', :now)"), {"id": log_id, "now": datetime(2026, 1, 1)})
    command.upgrade(migration_config, "head")
    assert MigrationContext.configure(pg_connection).get_current_heads() == ("e7b91c4a2d60",)
    with Session(pg_connection) as db:
        db.add(RawLog(source_connector="verified-agent", event_type="test", raw_content="test record"))
        db.commit()
    if start != "base":
        row = pg_connection.execute(sa.text("SELECT raw_content, source_connector FROM raw_logs WHERE id=:id"), {"id": log_id}).one()
        assert tuple(row) == ("retain evidence", "legacy")
    command.upgrade(migration_config, "head")


def test_postgres_login_and_database_backed_routes(pg_connection, migration_config, monkeypatch):
    command.upgrade(migration_config, "head")
    sessions = sessionmaker(bind=pg_connection, autoflush=False)
    password = "Isolated-Verification-Only-42!"
    with sessions() as db:
        role = Role(name="Verification Administrator", permissions=[Permission(name=name) for name in ["dashboard:view", "alerts:view", "alerts:edit", "reports:view", "network:view", "admin:write"]])
        db.add(role)
        db.flush()
        db.add(User(email="verification@example.com", full_name="Disposable verification account", hashed_password=hash_password(password), role_id=role.id, is_active=True, email_verified=True, approval_status="APPROVED"))
        db.commit()

    def get_test_db():
        with sessions() as db:
            yield db

    app.dependency_overrides[get_db] = get_test_db
    try:
        with TestClient(app, base_url="http://localhost") as client:
            login = client.post("/api/v1/auth/login", json={"email": "verification@example.com", "password": password})
            assert login.status_code == 200, login.status_code
            client.headers["Authorization"] = f"Bearer {login.json()['access_token']}"
            for path in ["auth/profile", "dashboard/overview", "dashboard/metrics", "dashboard/charts", "dashboard/top", "alerts/", "reports/", "network/overview", "network/devices", "network/interfaces", "network/health"]:
                result = client.get(f"/api/v1/{path}")
                assert result.status_code == 200, (path, result.status_code)
            enrollment = client.post("/api/v1/network/sensor/register", json={"name": "Disposable test sensor"})
            assert enrollment.status_code == 201
            sensor_id = enrollment.json()["sensor"]["id"]
            assert client.post(f"/api/v1/network/admin/sensor/activate/{sensor_id}").status_code == 200
            submitted = client.post("/api/v1/network/sensor/data", headers={"X-Sensor-Id": sensor_id, "X-Sensor-Key": enrollment.json()["sensor_key"]}, json={"devices": [{"ip_address": "192.168.2.3"}]})
            assert submitted.status_code == 200
            alert_id = client.get("/api/v1/alerts/").json()["items"][0]["id"]
            assert client.patch(f"/api/v1/alerts/{alert_id}", json={"status": "INVESTIGATING"}).status_code == 200
            assert client.get(f"/api/v1/alerts/{alert_id}/history").json()[0]["new_status"] == "INVESTIGATING"
            assert client.get("/api/v1/reports/export/pdf").status_code == 200
            assert client.get("/api/v1/reports/export/excel").status_code == 200
    finally:
        app.dependency_overrides.clear()
