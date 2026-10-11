"""Validate an existing legacy security-alert table before adopting its revision.

Only needed when the database is exactly at 1a0db3d3e168 and security_alerts
already exists (for example after an earlier create_all bootstrap).
"""

from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.script import ScriptDirectory
import sqlalchemy as sa


def adopt(connection, config):
    if MigrationContext.configure(connection).get_current_heads() != ("1a0db3d3e168",):
        raise RuntimeError("Adoption requires the database to be exactly at 1a0db3d3e168.")
    actual = sa.inspect(connection)
    if not actual.has_table("security_alerts"):
        raise RuntimeError("security_alerts does not exist; use alembic upgrade head.")

    # Build the exact published revision in a disposable database to validate
    # columns, primary key, foreign keys, and indexes before changing the stamp.
    reference = sa.create_engine("sqlite://")
    try:
        with reference.begin() as expected_connection:
            with Operations.context(MigrationContext.configure(expected_connection)):
                ScriptDirectory.from_config(config).get_revision("cff8339db910").module.upgrade()
            expected = sa.inspect(expected_connection)
            actual_columns = {item["name"]: item for item in actual.get_columns("security_alerts")}
            for column in expected.get_columns("security_alerts"):
                existing = actual_columns.get(column["name"])
                if existing is None or existing["nullable"] != column["nullable"]:
                    raise RuntimeError(f"Incompatible security_alerts column: {column['name']}")
                # SQLite reflects UUID as CHAR(32), PostgreSQL as UUID.
                if column["name"] in {"id", "device_id", "sensor_id"}:
                    compatible = isinstance(existing["type"], sa.Uuid) or isinstance(existing["type"], sa.CHAR) and existing["type"].length == 32
                else:
                    compatible = existing["type"]._type_affinity is column["type"]._type_affinity
                    expected_length = getattr(column["type"], "length", None)
                    if expected_length is not None:
                        compatible = compatible and getattr(existing["type"], "length", None) == expected_length
                if not compatible:
                    raise RuntimeError(f"Incompatible security_alerts type: {column['name']}")
            if actual.get_pk_constraint("security_alerts")["constrained_columns"] != ["id"]:
                raise RuntimeError("Incompatible security_alerts primary key")
            for method, fields in [
                ("get_indexes", ("name", "column_names", "unique")),
                ("get_foreign_keys", ("constrained_columns", "referred_table", "referred_columns", "options")),
            ]:
                observed = getattr(actual, method)("security_alerts")
                for item in getattr(expected, method)("security_alerts"):
                    if not any(all(candidate.get(field) == item.get(field) for field in fields) for candidate in observed):
                        raise RuntimeError(f"Missing/incompatible security_alerts {method}: {item.get('name')}")
    finally:
        reference.dispose()
    config.attributes["connection"] = connection
    command.stamp(config, "cff8339db910")


def main():
    from app.core.config import settings

    root = Path(__file__).resolve().parent
    config = Config(str(root / "alembic.ini"))
    config.set_main_option("script_location", str(root / "alembic"))
    engine = sa.create_engine(settings.DB_OVERRIDE or settings.DATABASE_URL)
    try:
        with engine.begin() as connection:
            adopt(connection, config)
        print("Validated existing security_alerts and adopted cff8339db910. Run alembic upgrade head next.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
