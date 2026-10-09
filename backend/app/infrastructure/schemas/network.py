from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, IPvAnyAddress


class SensorStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    OFFLINE = "OFFLINE"
    REVOKED = "REVOKED"


class DeviceStatus(str, Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    UNKNOWN = "UNKNOWN"


class SensorRegistration(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    platform: Optional[str] = Field(None, max_length=50)
    version: Optional[str] = Field(None, max_length=50)
    capabilities: Dict[str, Any] = Field(default_factory=dict)


class DeviceDiscoverySchema(BaseModel):
    ip_address: IPvAnyAddress
    mac_address: Optional[str] = Field(None, max_length=17)
    hostname: Optional[str] = Field(None, max_length=255)
    vendor: Optional[str] = Field(None, max_length=255)
    device_type: Optional[str] = Field(None, max_length=100)
    operating_system: Optional[str] = Field(None, max_length=100)
    gateway: Optional[IPvAnyAddress] = None
    interface: Optional[str] = Field(None, max_length=255)
    discovery_method: str = Field("arp_neighbor_table", max_length=100)
    evidence_level: str = Field("LIMITED", max_length=30)
    network_cidr: Optional[str] = Field(None, max_length=64)
    observed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class InterfaceTelemetry(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    identifier: Optional[str] = Field(None, max_length=255)
    interface_type: str = Field("UNKNOWN", max_length=50)
    operational_state: str = Field("UNKNOWN", max_length=50)
    is_active: bool = False
    mac_address: Optional[str] = Field(None, max_length=17)
    ipv4_addresses: List[str] = Field(default_factory=list)
    ipv6_addresses: List[str] = Field(default_factory=list)
    subnet_cidr: Optional[str] = Field(None, max_length=64)
    gateway: Optional[str] = Field(None, max_length=45)
    dns_servers: List[str] = Field(default_factory=list)
    dhcp_enabled: Optional[bool] = None
    dhcp_lease_expires_at: Optional[datetime] = None
    route_metric: Optional[int] = Field(None, ge=0)
    ssid: Optional[str] = Field(None, max_length=255)
    bssid: Optional[str] = Field(None, max_length=17)
    wifi_band: Optional[str] = Field(None, max_length=30)
    channel: Optional[int] = Field(None, ge=0)
    frequency_mhz: Optional[int] = Field(None, ge=0)
    signal_strength: Optional[float] = Field(None, ge=-150, le=100)
    link_quality: Optional[float] = Field(None, ge=0, le=100)
    security_protocol: Optional[str] = Field(None, max_length=100)


class NetworkHealthTelemetry(BaseModel):
    check_type: str = Field(..., max_length=50)
    target: Optional[str] = Field(None, max_length=255)
    status: str = Field(..., max_length=30)
    latency_ms: Optional[float] = Field(None, ge=0)
    packet_loss_pct: Optional[float] = Field(None, ge=0, le=100)
    measured_at: Optional[datetime] = None
    detail: Dict[str, Any] = Field(default_factory=dict)


class NetworkSnapshotTelemetry(BaseModel):
    captured_at: Optional[datetime] = None
    connection_status: str = Field("UNKNOWN", max_length=50)
    connection_type: Optional[str] = Field(None, max_length=50)
    ssid: Optional[str] = Field(None, max_length=255)
    bssid: Optional[str] = Field(None, max_length=17)
    local_ipv4: List[str] = Field(default_factory=list)
    local_ipv6: List[str] = Field(default_factory=list)
    subnet_cidr: Optional[str] = Field(None, max_length=64)
    gateway: Optional[str] = Field(None, max_length=45)
    dns_servers: List[str] = Field(default_factory=list)
    dhcp_enabled: Optional[bool] = None
    dhcp_lease_expires_at: Optional[datetime] = None
    wifi_band: Optional[str] = None
    channel: Optional[int] = None
    frequency_mhz: Optional[int] = None
    signal_strength: Optional[float] = None
    link_quality: Optional[float] = None
    security_protocol: Optional[str] = None
    connection_started_at: Optional[datetime] = None
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)


class SensorDataSubmission(BaseModel):
    model_config = ConfigDict(extra="forbid")
    submitted_at: Optional[datetime] = None
    devices: List[DeviceDiscoverySchema] = Field(default_factory=list, max_length=1000)
    interfaces: List[InterfaceTelemetry] = Field(default_factory=list, max_length=100)
    snapshot: Optional[NetworkSnapshotTelemetry] = None
    health: List[NetworkHealthTelemetry] = Field(default_factory=list, max_length=100)


class SensorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    status: SensorStatus
    platform: Optional[str] = None
    version: Optional[str] = None
    capabilities: Optional[dict] = None
    last_seen: Optional[datetime] = None
    last_telemetry_at: Optional[datetime] = None
    created_at: datetime


class SensorEnrollmentResponse(BaseModel):
    sensor: SensorResponse
    sensor_key: str


class NetworkDeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    hostname: Optional[str] = None
    vendor: Optional[str] = None
    device_type: Optional[str] = None
    operating_system: Optional[str] = None
    status: DeviceStatus
    first_seen: datetime
    last_seen: datetime
    gateway: Optional[str] = None
    interface: Optional[str] = None
    last_observation_source: Optional[str] = None


class NetworkInterfaceResponse(InterfaceTelemetry):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    sensor_id: UUID
    observed_at: datetime


class NetworkSnapshotResponse(NetworkSnapshotTelemetry):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    sensor_id: UUID


class NetworkHealthResponse(NetworkHealthTelemetry):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    sensor_id: UUID
