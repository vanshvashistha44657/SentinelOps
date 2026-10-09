from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DeviceStatus(str, PyEnum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    UNKNOWN = "UNKNOWN"


class NetworkDevice(Base):
    __tablename__ = "network_devices"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    mac_address: Mapped[Optional[str]] = mapped_column(String(17), index=True, nullable=True)
    hostname: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), index=True)
    vendor: Mapped[Optional[str]] = mapped_column(String(255))
    device_type: Mapped[Optional[str]] = mapped_column(String(100))
    operating_system: Mapped[Optional[str]] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), default=DeviceStatus.UNKNOWN, index=True)
    first_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    gateway: Mapped[Optional[str]] = mapped_column(String(45))
    interface: Mapped[Optional[str]] = mapped_column(String(100))
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    services: Mapped[Optional[dict]] = mapped_column(JSON)
    last_observation_source: Mapped[Optional[str]] = mapped_column(String(100))

    events: Mapped[List["NetworkEvent"]] = relationship(
        "NetworkEvent", back_populates="device", cascade="all, delete-orphan"
    )
    observations: Mapped[List["NetworkDeviceObservation"]] = relationship(
        "NetworkDeviceObservation", back_populates="device", cascade="all, delete-orphan"
    )


class NetworkEvent(Base):
    __tablename__ = "network_events"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    device_id: Mapped[UUID] = mapped_column(ForeignKey("network_devices.id", ondelete="CASCADE"), index=True)
    sensor_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("network_sensors.id", ondelete="SET NULL"), index=True)
    event_type: Mapped[str] = mapped_column(String(50), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    event_metadata: Mapped[Optional[dict]] = mapped_column(JSON)

    device: Mapped["NetworkDevice"] = relationship("NetworkDevice", back_populates="events")
    sensor: Mapped[Optional["NetworkSensor"]] = relationship("NetworkSensor")


class NetworkInterface(Base):
    __tablename__ = "network_interfaces"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    sensor_id: Mapped[UUID] = mapped_column(ForeignKey("network_sensors.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    identifier: Mapped[Optional[str]] = mapped_column(String(255))
    interface_type: Mapped[str] = mapped_column(String(50), default="UNKNOWN")
    operational_state: Mapped[str] = mapped_column(String(50), default="UNKNOWN")
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    mac_address: Mapped[Optional[str]] = mapped_column(String(17))
    ipv4_addresses: Mapped[Optional[list]] = mapped_column(JSON)
    ipv6_addresses: Mapped[Optional[list]] = mapped_column(JSON)
    subnet_cidr: Mapped[Optional[str]] = mapped_column(String(64))
    gateway: Mapped[Optional[str]] = mapped_column(String(45))
    dns_servers: Mapped[Optional[list]] = mapped_column(JSON)
    dhcp_enabled: Mapped[Optional[bool]] = mapped_column(Boolean)
    dhcp_lease_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    route_metric: Mapped[Optional[int]] = mapped_column(Integer)
    ssid: Mapped[Optional[str]] = mapped_column(String(255))
    bssid: Mapped[Optional[str]] = mapped_column(String(17))
    wifi_band: Mapped[Optional[str]] = mapped_column(String(30))
    channel: Mapped[Optional[int]] = mapped_column(Integer)
    frequency_mhz: Mapped[Optional[int]] = mapped_column(Integer)
    signal_strength: Mapped[Optional[float]] = mapped_column(Float)
    link_quality: Mapped[Optional[float]] = mapped_column(Float)
    security_protocol: Mapped[Optional[str]] = mapped_column(String(100))
    observed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    sensor: Mapped["NetworkSensor"] = relationship("NetworkSensor", back_populates="interfaces")


class NetworkSnapshot(Base):
    __tablename__ = "network_snapshots"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    sensor_id: Mapped[UUID] = mapped_column(ForeignKey("network_sensors.id", ondelete="CASCADE"), index=True)
    active_interface_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("network_interfaces.id", ondelete="SET NULL"))
    captured_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    connection_status: Mapped[str] = mapped_column(String(50), default="UNKNOWN")
    connection_type: Mapped[Optional[str]] = mapped_column(String(50))
    ssid: Mapped[Optional[str]] = mapped_column(String(255))
    bssid: Mapped[Optional[str]] = mapped_column(String(17))
    local_ipv4: Mapped[Optional[list]] = mapped_column(JSON)
    local_ipv6: Mapped[Optional[list]] = mapped_column(JSON)
    subnet_cidr: Mapped[Optional[str]] = mapped_column(String(64))
    gateway: Mapped[Optional[str]] = mapped_column(String(45))
    dns_servers: Mapped[Optional[list]] = mapped_column(JSON)
    dhcp_enabled: Mapped[Optional[bool]] = mapped_column(Boolean)
    dhcp_lease_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    wifi_band: Mapped[Optional[str]] = mapped_column(String(30))
    channel: Mapped[Optional[int]] = mapped_column(Integer)
    frequency_mhz: Mapped[Optional[int]] = mapped_column(Integer)
    signal_strength: Mapped[Optional[float]] = mapped_column(Float)
    link_quality: Mapped[Optional[float]] = mapped_column(Float)
    security_protocol: Mapped[Optional[str]] = mapped_column(String(100))
    connection_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    raw_metadata: Mapped[Optional[dict]] = mapped_column(JSON)

    sensor: Mapped["NetworkSensor"] = relationship("NetworkSensor", back_populates="snapshots")


class NetworkDeviceObservation(Base):
    __tablename__ = "network_device_observations"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    device_id: Mapped[UUID] = mapped_column(ForeignKey("network_devices.id", ondelete="CASCADE"), index=True)
    sensor_id: Mapped[UUID] = mapped_column(ForeignKey("network_sensors.id", ondelete="CASCADE"), index=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), index=True)
    mac_address: Mapped[Optional[str]] = mapped_column(String(17), index=True)
    hostname: Mapped[Optional[str]] = mapped_column(String(255))
    vendor: Mapped[Optional[str]] = mapped_column(String(255))
    discovery_method: Mapped[str] = mapped_column(String(100))
    evidence_level: Mapped[str] = mapped_column(String(30), default="LIMITED")
    interface_name: Mapped[Optional[str]] = mapped_column(String(255))
    network_cidr: Mapped[Optional[str]] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(30), default="ONLINE")
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON)

    device: Mapped["NetworkDevice"] = relationship("NetworkDevice", back_populates="observations")
    sensor: Mapped["NetworkSensor"] = relationship("NetworkSensor")


class NetworkHealthMeasurement(Base):
    __tablename__ = "network_health_measurements"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    sensor_id: Mapped[UUID] = mapped_column(ForeignKey("network_sensors.id", ondelete="CASCADE"), index=True)
    snapshot_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("network_snapshots.id", ondelete="SET NULL"))
    measured_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    check_type: Mapped[str] = mapped_column(String(50), index=True)
    target: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(30), index=True)
    latency_ms: Mapped[Optional[float]] = mapped_column(Float)
    packet_loss_pct: Mapped[Optional[float]] = mapped_column(Float)
    detail: Mapped[Optional[dict]] = mapped_column(JSON)

    sensor: Mapped["NetworkSensor"] = relationship("NetworkSensor")
