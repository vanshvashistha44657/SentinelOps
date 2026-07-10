import uuid
from datetime import datetime
from app.infrastructure.models.iam import User, Role, Permission
from app.infrastructure.models.alerts import Alert, DetectionRule
from app.infrastructure.models.incidents import Incident, Case
from app.infrastructure.models.threat_intel import IOCRecord, ThreatFeed
from app.infrastructure.models.system import Asset, AuditTrail

def test_user_creation():
    user_id = uuid.uuid4()
    role_id = uuid.uuid4()
    user = User(
        id=user_id,
        email="analyst@sentinelsops.internal",
        hashed_password="argon2id$hashed",
        full_name="L1 SOC Analyst",
        role_id=role_id,
        is_active=True
    )
    assert user.id == user_id
    assert user.email == "analyst@sentinelsops.internal"
    assert user.hashed_password == "argon2id$hashed"
    assert user.full_name == "L1 SOC Analyst"
    assert user.role_id == role_id
    assert user.is_active is True

def test_alert_creation():
    alert_id = uuid.uuid4()
    alert = Alert(
        id=alert_id,
        title="Brute Force Attempt detected on Domain Controller",
        severity="HIGH",
        confidence_score=85,
        status="NEW",
        source_ip="192.168.1.100",
        destination_ip="10.0.0.1",
        hostname="DC-01",
        raw_event={"event_id": 4625, "reason": "Unknown user name or bad password"}
    )
    assert alert.id == alert_id
    assert alert.title == "Brute Force Attempt detected on Domain Controller"
    assert alert.severity == "HIGH"
    assert alert.confidence_score == 85
    assert alert.status == "NEW"
    assert alert.source_ip == "192.168.1.100"
    assert alert.destination_ip == "10.0.0.1"
    assert alert.hostname == "DC-01"
    assert alert.raw_event["event_id"] == 4625

def test_incident_creation():
    incident_id = uuid.uuid4()
    incident = Incident(
        id=incident_id,
        title="Brute Force - Administrative Escalation",
        severity="HIGH",
        status="OPEN",
        summary="Multiple failed authentication attempts on DC-01 followed by successful login."
    )
    assert incident.id == incident_id
    assert incident.title == "Brute Force - Administrative Escalation"
    assert incident.severity == "HIGH"
    assert incident.status == "OPEN"
    assert incident.summary == "Multiple failed authentication attempts on DC-01 followed by successful login."

def test_ioc_creation():
    ioc_id = uuid.uuid4()
    ioc = IOCRecord(
        id=ioc_id,
        value="185.220.101.5",
        type="IPV4",
        risk_score=95,
        description="Active Tor exit node observed in password spraying campaign."
    )
    assert ioc.id == ioc_id
    assert ioc.value == "185.220.101.5"
    assert ioc.type == "IPV4"
    assert ioc.risk_score == 95
    assert ioc.description == "Active Tor exit node observed in password spraying campaign."
