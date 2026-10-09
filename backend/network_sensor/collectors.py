"""Platform collectors with bounded subprocess calls and graceful degradation."""

import ipaddress
import platform
import os
import re
import socket
import subprocess
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _run(command: List[str], timeout: float = 5) -> str:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
        return result.stdout if result.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


def _normalize_mac(value: str) -> Optional[str]:
    value = value.strip().replace("-", ":").lower()
    return value if re.fullmatch(r"[0-9a-f]{2}(:[0-9a-f]{2}){5}", value) else None


def discover_neighbors() -> List[Dict[str, Any]]:
    system = platform.system()
    output = _run(["arp", "-a"] if system == "Windows" else ["ip", "neigh"])
    devices: List[Dict[str, Any]] = []
    for line in output.splitlines():
        if system == "Windows":
            parts = line.split()
            if len(parts) < 3 or parts[2].lower() not in {"dynamic", "static"}:
                continue
            ip, mac = parts[0], _normalize_mac(parts[1])
            interface = None
        else:
            parts = line.split()
            if not parts or "lladdr" not in parts:
                continue
            ip = parts[0]
            mac = _normalize_mac(parts[parts.index("lladdr") + 1])
            interface = parts[parts.index("dev") + 1] if "dev" in parts else None
        try:
            address = ipaddress.ip_address(ip)
            if address.is_multicast or address.is_unspecified or address.is_loopback or address.is_reserved:
                continue
        except ValueError:
            continue
        devices.append({
            "ip_address": ip,
            "mac_address": mac,
            "interface": interface,
            "discovery_method": "arp_neighbor_table",
            "evidence_level": "LIMITED",
        })
    return devices


def _dns_check(server: Optional[str]) -> Dict[str, Any]:
    if not server:
        return {"check_type": "DNS", "status": "UNAVAILABLE", "detail": {"reason": "no DNS server reported"}}
    started = time.monotonic()
    try:
        socket.gethostbyname("example.com")
        return {"check_type": "DNS", "target": server, "status": "PASS", "latency_ms": round((time.monotonic() - started) * 1000, 2), "detail": {"method": "OS resolver"}}
    except OSError as exc:
        return {"check_type": "DNS", "target": server, "status": "FAIL", "detail": {"method": "OS resolver", "error": str(exc)}}


def _reachability_check(target: Optional[str], check_type: str) -> Dict[str, Any]:
    if not target:
        return {"check_type": check_type, "status": "UNAVAILABLE", "detail": {"reason": "target unavailable"}}
    command = ["ping", "-n", "1", "-w", "1000", target] if platform.system() == "Windows" else ["ping", "-c", "1", "-W", "1", target]
    started = time.monotonic()
    output = _run(command, timeout=3)
    passed = bool(output)
    return {
        "check_type": check_type,
        "target": target,
        "status": "PASS" if passed else "FAIL",
        "latency_ms": round((time.monotonic() - started) * 1000, 2) if passed else None,
        "packet_loss_pct": 0 if passed else 100,
        "detail": {"method": "bounded single ICMP echo", "limitation": "A ping result does not prove complete internet health."},
    }


def collect_network_state() -> Dict[str, Any]:
    # The standard library provides safe local addresses; platform-specific
    # commands enrich the record when available. Missing values remain absent.
    hostname = socket.gethostname()
    local_ip = None
    try:
        local_ip = socket.gethostbyname(hostname)
    except OSError:
        pass

    system = platform.system()
    interfaces: List[Dict[str, Any]] = []
    if local_ip:
        interfaces.append({
            "name": "default",
            "identifier": hostname,
            "interface_type": "UNKNOWN",
            "operational_state": "UP",
            "is_active": True,
            "ipv4_addresses": [local_ip],
        })

    # Windows exposes Wi-Fi fields through netsh. We intentionally do not use
    # commands that reveal saved credentials.
    wifi_output = _run(["netsh", "wlan", "show", "interfaces"]) if system == "Windows" else ""
    wifi: Dict[str, Any] = {}
    for line in wifi_output.splitlines():
        if ":" not in line:
            continue
        key, value = (part.strip() for part in line.split(":", 1))
        mapping = {"SSID": "ssid", "BSSID": "bssid", "Signal": "link_quality", "Channel": "channel", "Radio type": "wifi_band", "Authentication": "security_protocol", "State": "connection_status"}
        if key in mapping:
            wifi[mapping[key]] = float(value.rstrip("%")) if key == "Signal" and value.rstrip("%").replace(".", "", 1).isdigit() else int(value) if key == "Channel" and value.isdigit() else value
    if wifi and interfaces:
        interfaces[0].update({"interface_type": "Wi-Fi", **wifi})

    gateway = None
    route_output = _run(["route", "print", "-4"]) if system == "Windows" else _run(["ip", "route"])
    for line in route_output.splitlines():
        match = re.search(r"(?:0\.0\.0\.0\s+0\.0\.0\.0\s+|default via\s+)(\d+(?:\.\d+){3})", line)
        if match:
            gateway = match.group(1)
            break
    if interfaces:
        interfaces[0]["gateway"] = gateway

    dns_server = None
    ipconfig = _run(["ipconfig", "/all"]) if system == "Windows" else ""
    for line in ipconfig.splitlines():
        if "DNS Servers" in line:
            candidate = line.split(":", 1)[-1].strip()
            if candidate:
                dns_server = candidate
                break
    if interfaces and dns_server:
        interfaces[0]["dns_servers"] = [dns_server]

    snapshot = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "connection_status": wifi.get("connection_status", "CONNECTED" if local_ip else "DISCONNECTED"),
        "connection_type": interfaces[0].get("interface_type") if interfaces else None,
        "ssid": wifi.get("ssid"),
        "bssid": wifi.get("bssid"),
        "local_ipv4": [local_ip] if local_ip else [],
        "gateway": gateway,
        "dns_servers": [dns_server] if dns_server else [],
        "wifi_band": wifi.get("wifi_band"),
        "channel": wifi.get("channel"),
        "link_quality": wifi.get("link_quality"),
        "security_protocol": wifi.get("security_protocol"),
    }
    health = [_reachability_check(gateway, "GATEWAY")]
    health.append(_dns_check(dns_server))
    health.append(_reachability_check(os.getenv("NETWORK_CONNECTIVITY_TARGET", "1.1.1.1"), "CONNECTIVITY"))
    return {"interfaces": interfaces, "snapshot": snapshot, "health": health}
