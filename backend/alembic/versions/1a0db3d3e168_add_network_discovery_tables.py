"""Add network intelligence persistence tables without replacing core data."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "1a0db3d3e168"
down_revision = "c0f80578b423"
branch_labels = None
depends_on = None


def _has(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def _create(name: str, *columns):
    if not _has(name):
        op.create_table(name, *columns)


def upgrade() -> None:
    _create(
        "network_devices",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("mac_address", sa.String(17), nullable=True),
        sa.Column("hostname", sa.String(255), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("vendor", sa.String(255), nullable=True),
        sa.Column("device_type", sa.String(100), nullable=True),
        sa.Column("operating_system", sa.String(100), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="UNKNOWN"),
        sa.Column("first_seen", sa.DateTime(), nullable=False),
        sa.Column("last_seen", sa.DateTime(), nullable=False),
        sa.Column("gateway", sa.String(45), nullable=True),
        sa.Column("interface", sa.String(100), nullable=True),
        sa.Column("risk_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("services", sa.JSON(), nullable=True),
        sa.Column("last_observation_source", sa.String(100), nullable=True),
    )
    _create(
        "alert_status_history",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("alert_id", sa.Uuid(), nullable=False),
        sa.Column("changed_by_id", sa.Uuid(), nullable=True),
        sa.Column("previous_status", sa.String(50), nullable=False),
        sa.Column("new_status", sa.String(50), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("changed_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["alert_id"], ["alerts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["changed_by_id"], ["users.id"], ondelete="SET NULL"),
    )
    _create(
        "network_sensors",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("sensor_key", sa.String(255), nullable=True),
        sa.Column("sensor_key_hash", sa.String(64), nullable=True),
        sa.Column("sensor_key_prefix", sa.String(12), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("platform", sa.String(50), nullable=True),
        sa.Column("version", sa.String(50), nullable=True),
        sa.Column("capabilities", sa.JSON(), nullable=True),
        sa.Column("owner_id", sa.Uuid(), nullable=True),
        sa.Column("last_seen", sa.DateTime(), nullable=False),
        sa.Column("last_telemetry_at", sa.DateTime(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("sensor_key"),
        sa.UniqueConstraint("sensor_key_hash"),
    )
    _create(
        "network_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("device_id", sa.Uuid(), nullable=False),
        sa.Column("sensor_id", sa.Uuid(), nullable=True),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("event_metadata", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["device_id"], ["network_devices.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sensor_id"], ["network_sensors.id"], ondelete="SET NULL"),
    )
    _create(
        "network_interfaces",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("sensor_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("identifier", sa.String(255), nullable=True),
        sa.Column("interface_type", sa.String(50), nullable=False, server_default="UNKNOWN"),
        sa.Column("operational_state", sa.String(50), nullable=False, server_default="UNKNOWN"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("mac_address", sa.String(17), nullable=True),
        sa.Column("ipv4_addresses", sa.JSON(), nullable=True),
        sa.Column("ipv6_addresses", sa.JSON(), nullable=True),
        sa.Column("subnet_cidr", sa.String(64), nullable=True),
        sa.Column("gateway", sa.String(45), nullable=True),
        sa.Column("dns_servers", sa.JSON(), nullable=True),
        sa.Column("dhcp_enabled", sa.Boolean(), nullable=True),
        sa.Column("dhcp_lease_expires_at", sa.DateTime(), nullable=True),
        sa.Column("route_metric", sa.Integer(), nullable=True),
        sa.Column("ssid", sa.String(255), nullable=True),
        sa.Column("bssid", sa.String(17), nullable=True),
        sa.Column("wifi_band", sa.String(30), nullable=True),
        sa.Column("channel", sa.Integer(), nullable=True),
        sa.Column("frequency_mhz", sa.Integer(), nullable=True),
        sa.Column("signal_strength", sa.Float(), nullable=True),
        sa.Column("link_quality", sa.Float(), nullable=True),
        sa.Column("security_protocol", sa.String(100), nullable=True),
        sa.Column("observed_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["sensor_id"], ["network_sensors.id"], ondelete="CASCADE"),
    )
    _create(
        "network_snapshots",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("sensor_id", sa.Uuid(), nullable=False),
        sa.Column("active_interface_id", sa.Uuid(), nullable=True),
        sa.Column("captured_at", sa.DateTime(), nullable=False),
        sa.Column("connection_status", sa.String(50), nullable=False, server_default="UNKNOWN"),
        sa.Column("connection_type", sa.String(50), nullable=True),
        sa.Column("ssid", sa.String(255), nullable=True),
        sa.Column("bssid", sa.String(17), nullable=True),
        sa.Column("local_ipv4", sa.JSON(), nullable=True),
        sa.Column("local_ipv6", sa.JSON(), nullable=True),
        sa.Column("subnet_cidr", sa.String(64), nullable=True),
        sa.Column("gateway", sa.String(45), nullable=True),
        sa.Column("dns_servers", sa.JSON(), nullable=True),
        sa.Column("dhcp_enabled", sa.Boolean(), nullable=True),
        sa.Column("dhcp_lease_expires_at", sa.DateTime(), nullable=True),
        sa.Column("wifi_band", sa.String(30), nullable=True),
        sa.Column("channel", sa.Integer(), nullable=True),
        sa.Column("frequency_mhz", sa.Integer(), nullable=True),
        sa.Column("signal_strength", sa.Float(), nullable=True),
        sa.Column("link_quality", sa.Float(), nullable=True),
        sa.Column("security_protocol", sa.String(100), nullable=True),
        sa.Column("connection_started_at", sa.DateTime(), nullable=True),
        sa.Column("raw_metadata", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["sensor_id"], ["network_sensors.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["active_interface_id"], ["network_interfaces.id"], ondelete="SET NULL"),
    )
    _create(
        "network_device_observations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("device_id", sa.Uuid(), nullable=False),
        sa.Column("sensor_id", sa.Uuid(), nullable=False),
        sa.Column("observed_at", sa.DateTime(), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("mac_address", sa.String(17), nullable=True),
        sa.Column("hostname", sa.String(255), nullable=True),
        sa.Column("vendor", sa.String(255), nullable=True),
        sa.Column("discovery_method", sa.String(100), nullable=False),
        sa.Column("evidence_level", sa.String(30), nullable=False, server_default="LIMITED"),
        sa.Column("interface_name", sa.String(255), nullable=True),
        sa.Column("network_cidr", sa.String(64), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="ONLINE"),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["device_id"], ["network_devices.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sensor_id"], ["network_sensors.id"], ondelete="CASCADE"),
    )
    _create(
        "network_health_measurements",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("sensor_id", sa.Uuid(), nullable=False),
        sa.Column("snapshot_id", sa.Uuid(), nullable=True),
        sa.Column("measured_at", sa.DateTime(), nullable=False),
        sa.Column("check_type", sa.String(50), nullable=False),
        sa.Column("target", sa.String(255), nullable=True),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("latency_ms", sa.Float(), nullable=True),
        sa.Column("packet_loss_pct", sa.Float(), nullable=True),
        sa.Column("detail", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["sensor_id"], ["network_sensors.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["snapshot_id"], ["network_snapshots.id"], ondelete="SET NULL"),
    )
    _create(
        "threat_hunting_history",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("executed_at", sa.DateTime(), nullable=False),
        sa.Column("result_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    # Network history is operational evidence. It must be removed only through
    # an explicit, separately approved data-retention operation.
    pass
