from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_db
from app.core.database import Base
from app.core.security import create_access_token, hash_password
from app.domain.enums.user import ApprovalStatus
from app.infrastructure.models.iam import Permission, Role, User
from app.main import app


@pytest.fixture
def api_client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    admin_write = Permission(name="admin:write")
    network_view = Permission(name="network:view")
    role = Role(name="Test Administrator", permissions=[admin_write, network_view])
    session.add(role)
    session.flush()
    user = User(
        email=f"admin-{uuid4()}@test.local",
        hashed_password=hash_password("StrongPassword123!"),
        full_name="Test Administrator",
        role_id=role.id,
        is_active=True,
        email_verified=True,
        approval_status=ApprovalStatus.APPROVED,
    )
    session.add(user)
    session.commit()
    token = create_access_token(user.id)

    def override_get_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app, headers={"host": "localhost", "Authorization": f"Bearer {token}"})
    try:
        yield client
    finally:
        app.dependency_overrides.clear()
        session.close()
        engine.dispose()


def test_sensor_enrollment_activation_and_submission(api_client):
    assert api_client.get("/api/v1/network/overview").status_code == 200
    enrollment = api_client.post(
        "/api/v1/network/sensor/register",
        json={"name": "api-test-sensor", "platform": "Windows", "capabilities": {"arp_discovery": True}},
    )
    assert enrollment.status_code == 201
    payload = enrollment.json()
    sensor_id = payload["sensor"]["id"]
    sensor_key = payload["sensor_key"]
    assert api_client.post(f"/api/v1/network/admin/sensor/activate/{sensor_id}").status_code == 200

    telemetry = api_client.post(
        "/api/v1/network/sensor/data",
        headers={"X-Sensor-Id": sensor_id, "X-Sensor-Key": sensor_key},
        json={"devices": [{"ip_address": "192.168.10.20", "mac_address": "aa:bb:cc:dd:ee:ff"}]},
    )
    assert telemetry.status_code == 200
    assert telemetry.json()["devices_processed"] == 1


def test_sensor_submission_rejects_invalid_key(api_client):
    response = api_client.post(
        "/api/v1/network/sensor/data",
        headers={"X-Sensor-Id": str(uuid4()), "X-Sensor-Key": "invalid"},
        json={"devices": []},
    )
    assert response.status_code == 401
