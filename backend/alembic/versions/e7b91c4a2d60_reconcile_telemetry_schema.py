"""Reconcile schemas produced by both published onboarding implementations.

Revision ID: e7b91c4a2d60
Revises: d2b4c6e8f901

Existing revision files are immutable. In particular, databases that applied
the original c607f5c28195 do not rerun the additive version published later.
This new revision repairs missing structures and preserves surviving records.
"""

from alembic import op
from alembic.script import ScriptDirectory
import sqlalchemy as sa

revision = "e7b91c4a2d60"
down_revision = "d2b4c6e8f901"
branch_labels = None
depends_on = None


def _has_table(name):
    return sa.inspect(op.get_bind()).has_table(name)


def _relax_columns(table, names):
    columns = {item["name"]: item for item in sa.inspect(op.get_bind()).get_columns(table)}
    required = [name for name in names if name in columns and not columns[name]["nullable"]]
    if not required:
        return
    # SQLite's batch ALTER copies the table. Foreign-key cascades must not run
    # during that copy. Refuse an unsafe connection instead of deleting children.
    if op.get_bind().dialect.name == "sqlite" and op.get_bind().exec_driver_sql("PRAGMA foreign_keys").scalar():
        raise RuntimeError("SQLite compatibility repair needs foreign_keys=OFF before the migration transaction; run foreign_key_check afterwards. See MIGRATIONS.md.")
    with op.batch_alter_table(table) as batch:
        for name in required:
            batch.alter_column(name, existing_type=columns[name]["type"], nullable=True)


def upgrade():
    scripts = ScriptDirectory.from_config(op.get_context().config)
    # Reuse frozen, additive schema definitions, never the changing ORM metadata.
    # c607's original implementation removed these tables even on successful runs.
    scripts.get_revision("c607f5c28195").module.upgrade()
    if not _has_table("threat_hunting_queries"):
        scripts.get_revision("bfa61a95331c").module.upgrade()
    scripts.get_revision("1a0db3d3e168").module.upgrade()
    if not _has_table("security_alerts"):
        scripts.get_revision("cff8339db910").module.upgrade()
    scripts.get_revision("d2b4c6e8f901").module.upgrade()

    # The current ORM no longer supplies these historical ingestion fields.
    # Retain their values, but allow new normalized logs to be inserted.
    _relax_columns("raw_logs", ["source", "log_type", "source_connector", "event_type", "severity", "timestamp"])
    _relax_columns("network_sensors", ["sensor_key"])
    columns = {item["name"] for item in sa.inspect(op.get_bind()).get_columns("raw_logs")}
    for old, new in [("source", "source_connector"), ("log_type", "event_type"), ("ingested_at", "timestamp")]:
        if old in columns and new in columns:
            op.execute(sa.text(f"UPDATE raw_logs SET {new} = {old} WHERE {new} IS NULL"))


def downgrade():
    raise RuntimeError("This data-preserving repair is forward-only. Use a forward migration or a verified backup.")
