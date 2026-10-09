from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from app.core.config import settings
from app.core.database import Base
from app.infrastructure.models import *  # Import all models for autogenerate

config = context.config

# Use DB_OVERRIDE if provided, otherwise default to DATABASE_URL
def get_db_url():
    return settings.DB_OVERRIDE or settings.DATABASE_URL

target_metadata = Base.metadata

LEGACY_TABLES = {"threat_feeds", "threat_intelligence", "ioc_records"}
LEGACY_COLUMNS = {"source", "log_type"}
LEGACY_INDEXES = {"ix_raw_logs_source", "ix_raw_logs_log_type"}


def include_object(object_, name, type_, reflected, compare_to):
    """Keep historical compatibility tables/columns under migration control.

    Older releases created these structures but the current application no
    longer maps them. They remain preserved in existing databases rather than
    being treated as accidental objects to remove during autogeneration.
    """
    if type_ == "table" and name in LEGACY_TABLES:
        return False
    if reflected and type_ == "column" and name in LEGACY_COLUMNS:
        return False
    if reflected and type_ == "index" and name in LEGACY_INDEXES:
        return False
    if reflected and type_ == "index" and getattr(object_, "table", None) is not None and object_.table.name in LEGACY_TABLES:
        return False
    if type_ == "foreign_key_constraint" and any(getattr(column, "name", None) == "approved_by" for column in getattr(object_, "columns", [])):
        return False
    return True

def run_migrations_offline() -> None:
    context.configure(
            url=get_db_url(),
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
            include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = create_engine(get_db_url(), poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata, include_object=include_object
        )

        with context.begin_transaction():
            context.run_migrations()

from sqlalchemy import create_engine

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
