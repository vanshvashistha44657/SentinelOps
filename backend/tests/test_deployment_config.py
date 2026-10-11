import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import Settings
from app.main import app


def test_managed_postgres_url_and_render_hostname():
    settings = Settings(_env_file=None, SECRET_KEY="test", DATABASE_URL="postgres://user:password@db.example.invalid/sentinelops", RENDER=True, RENDER_EXTERNAL_HOSTNAME="sentinelops-api.onrender.com")
    assert settings.DATABASE_URL.startswith("postgresql+psycopg2://")
    assert "sentinelops-api.onrender.com" in settings.trusted_hosts


def test_render_rejects_sqlite():
    with pytest.raises(ValidationError, match="managed PostgreSQL"):
        Settings(_env_file=None, SECRET_KEY="test", DATABASE_URL="sqlite:///test.db", RENDER=True)


def test_unhealthy_database_returns_unhealthy_http_status(monkeypatch):
    class UnavailableEngine:
        def connect(self):
            raise RuntimeError("database unreachable")
    monkeypatch.setattr("app.main.engine", UnavailableEngine())
    with TestClient(app, base_url="http://localhost") as client:
        response = client.get("/health")
        assert response.status_code == 503
        assert response.json() == {"status": "degraded", "database": "unavailable"}
