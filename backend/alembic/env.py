from sqlalchemy import create_engine, inspect, pool, text
from alembic import context
from alembic.script import ScriptDirectory
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

def migrate_connection(connection):
    context.configure(
        connection=connection, target_metadata=target_metadata, include_object=include_object
    )
    # The historical audit migration drops its predecessor table. Refuse an
    # upgrade that would erase records rather than rewriting a published revision.
    heads = context.get_context().get_current_heads()
    scripts = ScriptDirectory.from_config(config)
    applied = {item.revision for item in scripts.iterate_revisions(heads, "base")}
    if "6a8b7c9d0e1f" not in applied and "audit_logs" in inspect(connection).get_table_names():
        if connection.execute(text("SELECT 1 FROM audit_logs LIMIT 1")).first():
            raise RuntimeError("Legacy audit_logs contains data. Preserve/migrate that history before upgrading past 6a8b7c9d0e1f; see MIGRATIONS.md.")
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # Test and maintenance callers can supply an isolated connection. Never
    # fall back to the configured database when one was explicitly supplied.
    connection = config.attributes.get("connection")
    if connection is not None:
        migrate_connection(connection)
        return
    connectable = create_engine(get_db_url(), poolclass=pool.NullPool)
    try:
        with connectable.begin() as connection:
            migrate_connection(connection)
    finally:
        connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
