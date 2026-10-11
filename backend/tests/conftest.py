"""Keep test imports isolated from the developer's configured database."""

import os
from pathlib import Path

import pytest
from alembic.config import Config

# The application engine is never used by tests; fixtures override DB sessions.
os.environ["DATABASE_URL"] = "sqlite:///unused-test-engine.db"
os.environ["DB_OVERRIDE"] = os.environ["DATABASE_URL"]
os.environ["SECRET_KEY"] = "isolated-test-signing-key-not-for-deployment"


@pytest.fixture
def migration_config():
    root = Path(__file__).resolve().parents[1]
    config = Config(str(root / "alembic.ini"))
    config.set_main_option("script_location", str(root / "alembic"))
    return config
