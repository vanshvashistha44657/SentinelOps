"""Persistence and detection orchestration for authorized network telemetry."""

import hashlib
import ipaddress
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.infrastructure.models.alerts import Alert
from app.infrastructure.models.network import (
    DeviceStatus,
    NetworkDevice,
    NetworkDeviceObservation,
    NetworkEvent,
    NetworkHealthMeasurement,
    NetworkInterface,
    NetworkSnapshot,
)
from app.infrastructure.models.network_sensor import NetworkSensor
from app.infrastructure.schemas.network import SensorDataSubmission, SensorStatus


def hash_sensor_key(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def is_endpoint_ip(value: Optional[str]) -> bool:
    if not value:
        return False
    try:
        address = ipaddress.ip_address(value)
    except ValueError:
        return False
    return not (address.is_multicast or address.is_unspecified or address.is_loopback or address.is_reserved)


def normalize_mac(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    normalized = value.strip().lower().replace("-", ":")
    return normalized if len(normalized) == 17 else normalized


def utc_naive(value: Optional[datetime]) -> Optional[datetime]:
    if value is None:
        return None
    if value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


class NetworkService:
    def __init__(self, db: Session):
        self.db = db

    def enroll_sensor(self, name: str, platform: Optional[str], version: Optional[str], capabilities: dict, owner_id: Optional[UUID] = None) -> tuple[NetworkSensor, str]:
        key = secrets.token_urlsafe(48)
        sensor = NetworkSensor(
            name=name,
            sensor_key_hash=hash_sensor_key(key),
            sensor_key_prefix=key[:10],
            platform=platform,
            version=version,
            capabilities=capabilities,
            owner_id=owner_id,
            status=SensorStatus.PENDING,
        )
        self.db.add(sensor)
        self.db.commit()
        self.db.refresh(sensor)
        return sensor, key

    def authenticate_sensor(self, sensor_id: str, presented_key: str) -> Optional[NetworkSensor]:
        try:
            sensor_uuid = UUID(sensor_id)
        except (ValueError, TypeError):
            return None
        sensor = self.db.query(NetworkSensor).filter(NetworkSensor.id == sensor_uuid).first()
        if not sensor or sensor.status != SensorStatus.ACTIVE or sensor.revoked_at:
            return None
        presented_hash = hash_sensor_key(presented_key)
        if sensor.sensor_key_hash:
            return sensor if secrets.compare_digest(sensor.sensor_key_hash, presented_hash) else None
        # Legacy local enrollments may have a plaintext key.  Do not create new
        # plaintext records, but permit one compatibility submission and migrate
        # the value to a hash during that request.
        if sensor.sensor_key and secrets.compare_digest(sensor.sensor_key, presented_key):
            sensor.sensor_key_hash = presented_hash
            sensor.sensor_key = None
            self.db.commit()
            return sensor
        return None

    def activate_sensor(self, sensor_id: UUID) -> Optional[NetworkSensor]:
        sensor = self.db.query(NetworkSensor).filter(NetworkSensor.id == sensor_id).first()
        if not sensor:
            return None
        sensor.status = SensorStatus.ACTIVE
        sensor.revoked_at = None
        self.db.commit()
        self.db.refresh(sensor)
        return sensor

    def revoke_sensor(self, sensor_id: UUID) -> bool:
        sensor = self.db.query(NetworkSensor).filter(NetworkSensor.id == sensor_id).first()
        if not sensor:
            return False
        sensor.status = SensorStatus.REVOKED
        sensor.revoked_at = datetime.utcnow()
        self.db.commit()
        return True

    def _upsert_interface(self, sensor: NetworkSensor, data: Any) -> NetworkInterface:
        interface = (
            self.db.query(NetworkInterface)
            .filter(NetworkInterface.sensor_id == sensor.id, NetworkInterface.name == data.name)
            .first()
        )
        values = data.model_dump()
        if not interface:
            interface = NetworkInterface(sensor_id=sensor.id, **values)
            self.db.add(interface)
        else:
            for key, value in values.items():
                setattr(interface, key, value)
            interface.observed_at = datetime.utcnow()
        self.db.flush()
        return interface

    def _find_device(self, sensor_id: UUID, ip_address: Optional[str], mac_address: Optional[str]) -> Optional[NetworkDevice]:
        clauses = []
        if mac_address:
            clauses.append(NetworkDevice.mac_address == mac_address.lower())
        if ip_address:
            clauses.extend([
                NetworkDevice.ip_address == ip_address,
                NetworkDevice.observations.any(NetworkDeviceObservation.ip_address == ip_address),
            ])
        return self.db.query(NetworkDevice).filter(or_(*clauses)).order_by(NetworkDevice.last_seen.desc()).first() if clauses else None

    def _create_network_alert(self, alert_type: str, title: str, description: str, severity: str, device: Optional[NetworkDevice], sensor: NetworkSensor, evidence: dict) -> None:
        source_ip = device.ip_address if device else evidence.get("ip_address")
        duplicate = (
            self.db.query(Alert)
            .filter(
                Alert.title == title,
                Alert.source_ip == source_ip,
                Alert.status.in_(["NEW", "INVESTIGATING"]),
            )
            .first()
        )
        if duplicate:
            return
        self.db.add(Alert(
            title=title,
            severity=severity,
            confidence_score=70 if evidence.get("evidence_level") == "LIMITED" else 85,
            status="NEW",
            source_ip=source_ip,
            hostname=device.hostname if device else evidence.get("hostname"),
            raw_event={
                "source": "NetworkSensor",
                "alert_type": alert_type,
                "sensor_id": str(sensor.id),
                "evidence": evidence,
                "limitations": "ARP and neighbor-table observations are not a complete network inventory.",
            },
            recommended_response="Validate the observation against authorized asset records and network topology before taking action.",
        ))

    def process_submission(self, sensor: NetworkSensor, submission: SensorDataSubmission) -> dict:
        now = datetime.utcnow()
        sensor.last_seen = now
        sensor.last_telemetry_at = utc_naive(submission.submitted_at) or now
        interface_map = {item.name: self._upsert_interface(sensor, item) for item in submission.interfaces}

        snapshot = None
        if submission.snapshot:
            previous_snapshot = self.db.query(NetworkSnapshot).filter(NetworkSnapshot.sensor_id == sensor.id).order_by(NetworkSnapshot.captured_at.desc()).first()
            values = submission.snapshot.model_dump()
            values["captured_at"] = utc_naive(values.get("captured_at")) or now
            values["connection_started_at"] = utc_naive(values.get("connection_started_at"))
            active_name = next((item.name for item in submission.interfaces if item.is_active), None)
            snapshot = NetworkSnapshot(
                sensor_id=sensor.id,
                active_interface_id=interface_map[active_name].id if active_name in interface_map else None,
                **values,
            )
            self.db.add(snapshot)
            self.db.flush()
            if previous_snapshot and previous_snapshot.gateway and values.get("gateway") and previous_snapshot.gateway != values.get("gateway"):
                self._create_network_alert(
                    "GATEWAY_CHANGED",
                    "Network gateway changed",
                    "The sensor observed a different default gateway.",
                    "MEDIUM",
                    None,
                    sensor,
                    {"previous_gateway": previous_snapshot.gateway, "gateway": values.get("gateway"), "evidence_level": "DIRECT_HOST_CONFIGURATION"},
                )
            if previous_snapshot and (previous_snapshot.dns_servers or values.get("dns_servers")) and previous_snapshot.dns_servers != values.get("dns_servers"):
                self._create_network_alert(
                    "DNS_CONFIGURATION_CHANGED",
                    "DNS configuration changed",
                    "The sensor observed a change in configured DNS servers.",
                    "LOW",
                    None,
                    sensor,
                    {"previous_dns_servers": previous_snapshot.dns_servers, "dns_servers": values.get("dns_servers"), "evidence_level": "DIRECT_HOST_CONFIGURATION"},
                )

        for health in submission.health:
            health_values = health.model_dump()
            health_values["measured_at"] = utc_naive(health_values.get("measured_at")) or now
            self.db.add(NetworkHealthMeasurement(sensor_id=sensor.id, snapshot_id=snapshot.id if snapshot else None, **health_values))
            if health.status.upper() == "FAIL":
                recent_failures = (
                    self.db.query(NetworkHealthMeasurement)
                    .filter(NetworkHealthMeasurement.sensor_id == sensor.id, NetworkHealthMeasurement.check_type == health.check_type, NetworkHealthMeasurement.status == "FAIL")
                    .order_by(NetworkHealthMeasurement.measured_at.desc())
                    .limit(3)
                    .count()
                )
                if recent_failures >= 3 and not self.db.query(Alert).filter(Alert.title == "Network connectivity degraded", Alert.status.in_(["NEW", "INVESTIGATING"])).first():
                    self.db.add(Alert(
                        title="Network connectivity degraded",
                        severity="MEDIUM",
                        confidence_score=75,
                        status="NEW",
                        raw_event={"source": "NetworkSensor", "sensor_id": str(sensor.id), "check_type": health.check_type, "target": health.target, "evidence": health.detail},
                        recommended_response="Review the bounded diagnostic target and compare gateway, DNS, and sensor-to-server measurements.",
                    ))

        created_devices = 0
        generated_alerts = 0
        for item in submission.devices:
            ip = str(item.ip_address)
            if not is_endpoint_ip(ip):
                continue
            mac = normalize_mac(item.mac_address)
            device = self._find_device(sensor.id, ip, mac)
            is_new = device is None
            previous_ip = device.ip_address if device else None
            previous_mac = device.mac_address if device else None
            if not device:
                device = NetworkDevice(
                    ip_address=ip,
                    mac_address=mac,
                    hostname=item.hostname,
                    vendor=item.vendor,
                    device_type=item.device_type,
                    operating_system=item.operating_system,
                    gateway=str(item.gateway) if item.gateway else None,
                    interface=item.interface,
                    status=DeviceStatus.ONLINE,
                    last_observation_source=item.discovery_method,
                )
                self.db.add(device)
                self.db.flush()
                created_devices += 1
            else:
                device.ip_address = ip
                device.mac_address = mac or device.mac_address
                device.hostname = item.hostname or device.hostname
                device.vendor = item.vendor or device.vendor
                device.gateway = str(item.gateway) if item.gateway else device.gateway
                device.interface = item.interface or device.interface
                device.status = DeviceStatus.ONLINE
                device.last_observation_source = item.discovery_method
                device.last_seen = now

            observed_at = utc_naive(item.observed_at) or now
            device.first_seen = device.first_seen or observed_at
            device.last_seen = observed_at
            evidence = {
                "ip_address": ip,
                "mac_address": mac,
                "hostname": item.hostname,
                "vendor": item.vendor,
                "discovery_method": item.discovery_method,
                "evidence_level": item.evidence_level,
                "network_cidr": item.network_cidr,
            }
            self.db.add(NetworkDeviceObservation(
                device_id=device.id,
                sensor_id=sensor.id,
                observed_at=observed_at,
                ip_address=ip,
                mac_address=mac,
                hostname=item.hostname,
                vendor=item.vendor,
                discovery_method=item.discovery_method,
                evidence_level=item.evidence_level,
                interface_name=item.interface,
                network_cidr=item.network_cidr,
                metadata_json=item.metadata,
            ))
            if is_new:
                self.db.add(NetworkEvent(device_id=device.id, sensor_id=sensor.id, event_type="NEW_DEVICE", timestamp=observed_at, event_metadata=evidence))
                self._create_network_alert("NEW_DEVICE", "New network device observed", f"An authorized sensor observed {ip}.", "MEDIUM", device, sensor, evidence)
                generated_alerts += 1
            elif previous_ip and previous_ip != ip:
                self.db.add(NetworkEvent(device_id=device.id, sensor_id=sensor.id, event_type="IP_CHANGED", timestamp=observed_at, event_metadata={**evidence, "previous_ip": previous_ip}))
                self._create_network_alert("IP_CHANGED", "Network device IP changed", f"A known device changed IP from {previous_ip} to {ip}.", "LOW", device, sensor, {**evidence, "previous_ip": previous_ip})
                generated_alerts += 1
            elif previous_mac and mac and previous_mac != mac:
                self.db.add(NetworkEvent(device_id=device.id, sensor_id=sensor.id, event_type="MAC_CHANGED", timestamp=observed_at, event_metadata={**evidence, "previous_mac": previous_mac}))
                self._create_network_alert("MAC_CHANGED", "Network device MAC changed", f"A known IP was observed with a different MAC address.", "MEDIUM", device, sensor, {**evidence, "previous_mac": previous_mac})
                generated_alerts += 1

        self.db.commit()
        return {"devices_processed": created_devices, "alerts_created": generated_alerts, "interfaces_processed": len(interface_map), "health_measurements": len(submission.health)}

    def mark_stale_sensors(self, stale_after_seconds: int = 180) -> int:
        cutoff = datetime.utcnow() - timedelta(seconds=stale_after_seconds)
        stale = self.db.query(NetworkSensor).filter(NetworkSensor.status == SensorStatus.ACTIVE, NetworkSensor.last_telemetry_at < cutoff).all()
        for sensor in stale:
            sensor.status = SensorStatus.OFFLINE
            if not self.db.query(Alert).filter(Alert.title == "Network sensor telemetry stale", Alert.status.in_(["NEW", "INVESTIGATING"])).first():
                self.db.add(Alert(
                    title="Network sensor telemetry stale",
                    severity="MEDIUM",
                    confidence_score=90,
                    status="NEW",
                    raw_event={"source": "NetworkSensor", "sensor_id": str(sensor.id), "last_telemetry_at": sensor.last_telemetry_at.isoformat() if sensor.last_telemetry_at else None},
                    recommended_response="Confirm the authorized host is running and can reach the SentinelOps API.",
                ))
        count = len(stale)
        self.db.commit()
        return count
