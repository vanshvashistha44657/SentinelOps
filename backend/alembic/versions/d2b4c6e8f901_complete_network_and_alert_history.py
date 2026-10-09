"""Complete network telemetry and canonical alert history tables.

This migration is additive so installations already at the previous network
head can receive the new fields without replacing network observations.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "d2b4c6e8f901"
down_revision = "cff8339db910"
branch_labels = None
depends_on = None


def _tables():
    return set(inspect(op.get_bind()).get_table_names())


def _columns(table):
    return {column["name"] for column in inspect(op.get_bind()).get_columns(table)}


def _add(table, column):
    if table in _tables() and column.name not in _columns(table):
        op.add_column(table, column)


def _create(name, *columns):
    if name not in _tables():
        op.create_table(name, *columns)


def _index(name, table, column, unique=False):
    if table in _tables():
        existing = {item["name"] for item in inspect(op.get_bind()).get_indexes(table)}
        if name not in existing:
            op.create_index(name, table, [column], unique=unique)


def _ensure_foreign_key(table, column, referred_table, referred_column, name):
    if op.get_bind().dialect.name == "sqlite" or table not in _tables():
        return
    keys = inspect(op.get_bind()).get_foreign_keys(table)
    if not any(column in key.get("constrained_columns", []) and referred_table in (key.get("referred_table"),) for key in keys):
        op.create_foreign_key(name, table, referred_table, [column], [referred_column], ondelete="SET NULL")


def upgrade() -> None:
    _add("network_devices", sa.Column("last_observation_source", sa.String(100), nullable=True))
    for column in [
        sa.Column("sensor_key_hash", sa.String(64), nullable=True),
        sa.Column("sensor_key_prefix", sa.String(12), nullable=True),
        sa.Column("platform", sa.String(50), nullable=True),
        sa.Column("version", sa.String(50), nullable=True),
        sa.Column("capabilities", sa.JSON(), nullable=True),
        sa.Column("owner_id", sa.Uuid(), nullable=True),
        sa.Column("last_telemetry_at", sa.DateTime(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
    ]:
        _add("network_sensors", column)
    _add("network_events", sa.Column("sensor_id", sa.Uuid(), nullable=True))
    _ensure_foreign_key("users", "approved_by", "users", "id", "fk_users_approved_by_users")
    _ensure_foreign_key("network_sensors", "owner_id", "users", "id", "fk_network_sensors_owner_users")
    _ensure_foreign_key("network_events", "sensor_id", "network_sensors", "id", "fk_network_events_sensor_sensors")

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
        "network_interfaces",
        sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("sensor_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False), sa.Column("identifier", sa.String(255)),
        sa.Column("interface_type", sa.String(50), nullable=False), sa.Column("operational_state", sa.String(50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False), sa.Column("mac_address", sa.String(17)),
        sa.Column("ipv4_addresses", sa.JSON()), sa.Column("ipv6_addresses", sa.JSON()), sa.Column("subnet_cidr", sa.String(64)),
        sa.Column("gateway", sa.String(45)), sa.Column("dns_servers", sa.JSON()), sa.Column("dhcp_enabled", sa.Boolean()),
        sa.Column("dhcp_lease_expires_at", sa.DateTime()), sa.Column("route_metric", sa.Integer()), sa.Column("ssid", sa.String(255)),
        sa.Column("bssid", sa.String(17)), sa.Column("wifi_band", sa.String(30)), sa.Column("channel", sa.Integer()),
        sa.Column("frequency_mhz", sa.Integer()), sa.Column("signal_strength", sa.Float()), sa.Column("link_quality", sa.Float()),
        sa.Column("security_protocol", sa.String(100)), sa.Column("observed_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["sensor_id"], ["network_sensors.id"], ondelete="CASCADE"),
    )
    _create(
        "network_snapshots",
        sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("sensor_id", sa.Uuid(), nullable=False),
        sa.Column("active_interface_id", sa.Uuid()), sa.Column("captured_at", sa.DateTime(), nullable=False),
        sa.Column("connection_status", sa.String(50), nullable=False), sa.Column("connection_type", sa.String(50)),
        sa.Column("ssid", sa.String(255)), sa.Column("bssid", sa.String(17)), sa.Column("local_ipv4", sa.JSON()), sa.Column("local_ipv6", sa.JSON()),
        sa.Column("subnet_cidr", sa.String(64)), sa.Column("gateway", sa.String(45)), sa.Column("dns_servers", sa.JSON()),
        sa.Column("dhcp_enabled", sa.Boolean()), sa.Column("dhcp_lease_expires_at", sa.DateTime()), sa.Column("wifi_band", sa.String(30)),
        sa.Column("channel", sa.Integer()), sa.Column("frequency_mhz", sa.Integer()), sa.Column("signal_strength", sa.Float()),
        sa.Column("link_quality", sa.Float()), sa.Column("security_protocol", sa.String(100)), sa.Column("connection_started_at", sa.DateTime()),
        sa.Column("raw_metadata", sa.JSON()), sa.ForeignKeyConstraint(["sensor_id"], ["network_sensors.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["active_interface_id"], ["network_interfaces.id"], ondelete="SET NULL"),
    )
    _create(
        "network_device_observations",
        sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("device_id", sa.Uuid(), nullable=False), sa.Column("sensor_id", sa.Uuid(), nullable=False),
        sa.Column("observed_at", sa.DateTime(), nullable=False), sa.Column("ip_address", sa.String(45)), sa.Column("mac_address", sa.String(17)),
        sa.Column("hostname", sa.String(255)), sa.Column("vendor", sa.String(255)), sa.Column("discovery_method", sa.String(100), nullable=False),
        sa.Column("evidence_level", sa.String(30), nullable=False), sa.Column("interface_name", sa.String(255)), sa.Column("network_cidr", sa.String(64)),
        sa.Column("status", sa.String(30), nullable=False), sa.Column("metadata_json", sa.JSON()),
        sa.ForeignKeyConstraint(["device_id"], ["network_devices.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["sensor_id"], ["network_sensors.id"], ondelete="CASCADE"),
    )
    _create(
        "network_health_measurements",
        sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("sensor_id", sa.Uuid(), nullable=False), sa.Column("snapshot_id", sa.Uuid()),
        sa.Column("measured_at", sa.DateTime(), nullable=False), sa.Column("check_type", sa.String(50), nullable=False), sa.Column("target", sa.String(255)),
        sa.Column("status", sa.String(30), nullable=False), sa.Column("latency_ms", sa.Float()), sa.Column("packet_loss_pct", sa.Float()), sa.Column("detail", sa.JSON()),
        sa.ForeignKeyConstraint(["sensor_id"], ["network_sensors.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["snapshot_id"], ["network_snapshots.id"], ondelete="SET NULL"),
    )
    _create(
        "threat_hunting_history",
        sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("query", sa.Text(), nullable=False), sa.Column("executed_at", sa.DateTime(), nullable=False),
        sa.Column("result_count", sa.Integer(), nullable=False), sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )

    for name, table, column, unique in [
        ("ix_alert_status_history_alert_id", "alert_status_history", "alert_id", False),
        ("ix_alert_status_history_changed_at", "alert_status_history", "changed_at", False),
        ("ix_network_devices_mac_address", "network_devices", "mac_address", False),
        ("ix_network_devices_hostname", "network_devices", "hostname", False),
        ("ix_network_devices_ip_address", "network_devices", "ip_address", False),
        ("ix_network_devices_status", "network_devices", "status", False),
        ("ix_network_devices_first_seen", "network_devices", "first_seen", False),
        ("ix_network_devices_last_seen", "network_devices", "last_seen", False),
        ("ix_network_events_device_id", "network_events", "device_id", False),
        ("ix_network_events_sensor_id", "network_events", "sensor_id", False),
        ("ix_network_events_event_type", "network_events", "event_type", False),
        ("ix_network_events_timestamp", "network_events", "timestamp", False),
        ("ix_network_sensors_status", "network_sensors", "status", False),
        ("ix_network_sensors_sensor_key_hash", "network_sensors", "sensor_key_hash", True),
        ("ix_network_sensors_sensor_key_prefix", "network_sensors", "sensor_key_prefix", False),
        ("ix_network_sensors_last_telemetry_at", "network_sensors", "last_telemetry_at", False),
        ("ix_network_interfaces_sensor_id", "network_interfaces", "sensor_id", False),
        ("ix_network_interfaces_name", "network_interfaces", "name", False),
        ("ix_network_interfaces_is_active", "network_interfaces", "is_active", False),
        ("ix_network_interfaces_observed_at", "network_interfaces", "observed_at", False),
        ("ix_network_snapshots_sensor_id", "network_snapshots", "sensor_id", False),
        ("ix_network_snapshots_captured_at", "network_snapshots", "captured_at", False),
        ("ix_network_device_observations_device_id", "network_device_observations", "device_id", False),
        ("ix_network_device_observations_sensor_id", "network_device_observations", "sensor_id", False),
        ("ix_network_device_observations_observed_at", "network_device_observations", "observed_at", False),
        ("ix_network_device_observations_ip_address", "network_device_observations", "ip_address", False),
        ("ix_network_device_observations_mac_address", "network_device_observations", "mac_address", False),
        ("ix_network_health_measurements_sensor_id", "network_health_measurements", "sensor_id", False),
        ("ix_network_health_measurements_measured_at", "network_health_measurements", "measured_at", False),
        ("ix_network_health_measurements_check_type", "network_health_measurements", "check_type", False),
        ("ix_network_health_measurements_status", "network_health_measurements", "status", False),
        ("ix_threat_hunting_history_executed_at", "threat_hunting_history", "executed_at", False),
    ]:
        _index(name, table, column, unique)


def downgrade() -> None:
    pass
