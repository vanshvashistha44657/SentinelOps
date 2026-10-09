"""Add onboarding and normalized ingestion fields without dropping data.

The previous generated revision dropped multiple tables with CASCADE and
recreated them.  This replacement is intentionally additive and idempotent so
it can be applied to an existing installation containing records.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "c607f5c28195"
down_revision = "bfa61a95331c"
branch_labels = None
depends_on = None


def _inspector():
    return inspect(op.get_bind())


def _table(name: str) -> bool:
    return name in _inspector().get_table_names()


def _column(table: str, name: str) -> bool:
    return any(column["name"] == name for column in _inspector().get_columns(table))


def _add(table: str, column: sa.Column) -> None:
    if _table(table) and not _column(table, column.name):
        op.add_column(table, column)


def _create(table_name: str, *columns, indexes=()):
    if not _table(table_name):
        op.create_table(table_name, *columns)
    existing = {item["name"] for item in _inspector().get_indexes(table_name)} if _table(table_name) else set()
    for index_name, column_name, unique in indexes:
        if index_name not in existing:
            op.create_index(index_name, table_name, [column_name], unique=unique)


def _ensure_index(name: str, table: str, column: str, unique: bool = False) -> None:
    if _table(table):
        existing = {item["name"] for item in _inspector().get_indexes(table)}
        if name not in existing:
            op.create_index(name, table, [column], unique=unique)


def upgrade() -> None:
    # Existing log records are preserved. New columns are nullable during the
    # compatibility migration; the application validates all new submissions.
    log_columns = [
        sa.Column("source_connector", sa.String(100), nullable=True),
        sa.Column("event_type", sa.String(100), nullable=True),
        sa.Column("severity", sa.String(50), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.Column("source_ip", sa.String(45), nullable=True),
        sa.Column("destination_ip", sa.String(45), nullable=True),
        sa.Column("hostname", sa.String(255), nullable=True),
        sa.Column("username", sa.String(255), nullable=True),
        sa.Column("process_name", sa.String(255), nullable=True),
        sa.Column("file_hash", sa.String(255), nullable=True),
        sa.Column("domain", sa.String(255), nullable=True),
        sa.Column("url", sa.Text(), nullable=True),
    ]
    for column in log_columns:
        _add("raw_logs", column)
    for name, column in [
        ("ix_raw_logs_source_connector", "source_connector"),
        ("ix_raw_logs_event_type", "event_type"),
        ("ix_raw_logs_severity", "severity"),
        ("ix_raw_logs_timestamp", "timestamp"),
        ("ix_raw_logs_source_ip", "source_ip"),
        ("ix_raw_logs_destination_ip", "destination_ip"),
        ("ix_raw_logs_hostname", "hostname"),
        ("ix_raw_logs_username", "username"),
        ("ix_raw_logs_process_name", "process_name"),
        ("ix_raw_logs_file_hash", "file_hash"),
        ("ix_raw_logs_domain", "domain"),
    ]:
        _ensure_index(name, "raw_logs", column)

    user_columns = [
        sa.Column("email_verified", sa.Boolean(), nullable=True, server_default=sa.text("false")),
        sa.Column("email_verified_at", sa.DateTime(), nullable=True),
        sa.Column("approval_status", sa.String(50), nullable=True, server_default="PENDING"),
        sa.Column("approved_by", sa.Uuid(), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("rejected_reason", sa.String(255), nullable=True),
        sa.Column("registration_ip", sa.String(45), nullable=True),
        sa.Column("registration_device", sa.String(255), nullable=True),
        sa.Column("last_login_ip", sa.String(45), nullable=True),
        sa.Column("last_login_device", sa.String(255), nullable=True),
    ]
    for column in user_columns:
        _add("users", column)

    _create(
        "failed_logs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("source_connector", sa.String(100), nullable=False),
        sa.Column("raw_content", sa.Text(), nullable=False),
        sa.Column("error_reason", sa.Text(), nullable=False),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed_at", sa.DateTime(), nullable=False),
        indexes=(("ix_failed_logs_failed_at", "failed_at", False), ("ix_failed_logs_source_connector", "source_connector", False)),
    )
    _create(
        "mitre_techniques",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("mitre_id", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("tactic", sa.String(255), nullable=False),
        indexes=(("ix_mitre_techniques_mitre_id", "mitre_id", True),),
    )
    _create(
        "threat_indicators",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("value", sa.String(512), nullable=False),
        sa.Column("risk_score", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("severity", sa.String(50), nullable=False, server_default="MEDIUM"),
        sa.Column("source", sa.String(100), nullable=False, server_default="manual"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("tlp", sa.String(20), nullable=False, server_default="WHITE"),
        sa.Column("first_seen", sa.DateTime(), nullable=False),
        sa.Column("last_seen", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        indexes=(
            ("ix_threat_indicators_value", "value", True),
            ("ix_threat_indicators_type", "type", False),
            ("ix_threat_indicators_source", "source", False),
            ("ix_threat_indicators_severity", "severity", False),
            ("ix_threat_indicators_created_at", "created_at", False),
        ),
    )
    _create(
        "email_verification_tokens",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(255), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("is_used", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        indexes=(("ix_email_verification_tokens_token_hash", "token_hash", True),),
    )
    _create(
        "ioc_matches",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("indicator_id", sa.Uuid(), nullable=False),
        sa.Column("raw_log_id", sa.Uuid(), nullable=False),
        sa.Column("alert_id", sa.Uuid(), nullable=True),
        sa.Column("matched_field", sa.String(100), nullable=False),
        sa.Column("matched_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["indicator_id"], ["threat_indicators.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["raw_log_id"], ["raw_logs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["alert_id"], ["alerts.id"], ondelete="CASCADE"),
        indexes=(
            ("ix_ioc_matches_indicator_id", "indicator_id", False),
            ("ix_ioc_matches_raw_log_id", "raw_log_id", False),
            ("ix_ioc_matches_alert_id", "alert_id", False),
            ("ix_ioc_matches_matched_at", "matched_at", False),
        ),
    )
    _create(
        "case_alerts",
        sa.Column("case_id", sa.Uuid(), primary_key=True),
        sa.Column("alert_id", sa.Uuid(), primary_key=True),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["alert_id"], ["alerts.id"], ondelete="CASCADE"),
    )
    _create(
        "case_incidents",
        sa.Column("case_id", sa.Uuid(), primary_key=True),
        sa.Column("incident_id", sa.Uuid(), primary_key=True),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["incident_id"], ["incidents.id"], ondelete="CASCADE"),
    )
    _create(
        "case_mitre_techniques",
        sa.Column("case_id", sa.Uuid(), primary_key=True),
        sa.Column("mitre_technique_id", sa.Uuid(), primary_key=True),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["mitre_technique_id"], ["mitre_techniques.id"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    # Compatibility migrations are intentionally not destructive. A rollback
    # must use a database backup or a separately reviewed migration.
    pass
