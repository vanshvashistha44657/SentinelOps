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

def run_migrations_offline() -> None:
    context.configure(
        url=get_db_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = create_engine(get_db_url(), poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

from sqlalchemy import create_engine

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
