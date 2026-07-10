from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text, JSON, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class DetectionRule(Base):
    __tablename__ = "detection_rules"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(50))  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    confidence_score: Mapped[int] = mapped_column(Integer, default=50)  # 1-100
    mitre_attack_mapping: Mapped[Optional[dict]] = mapped_column(JSON)  # list of technique/tactic IDs
    query_logic: Mapped[str] = mapped_column(Text)  # Rule query (e.g. SPL/KQL/SQL logic)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    versions: Mapped[List["RuleVersion"]] = relationship("RuleVersion", back_populates="rule", cascade="all, delete-orphan")
    alerts: Mapped[List["Alert"]] = relationship("Alert", back_populates="rule")

class RuleVersion(Base):
    __tablename__ = "rule_versions"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    detection_rule_id: Mapped[UUID] = mapped_column(ForeignKey("detection_rules.id", ondelete="CASCADE"))
    version_number: Mapped[int] = mapped_column(Integer)
    query_logic: Mapped[str] = mapped_column(Text)
    changelog: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    
    # Relationships
    rule: Mapped[DetectionRule] = relationship("DetectionRule", back_populates="versions")

# Association Table for Many-to-Many between Alerts and Incidents
incident_alerts = Table(
    "incident_alerts",
    Base.metadata,
    Column("incident_id", ForeignKey("incidents.id", ondelete="CASCADE"), primary_key=True),
    Column("alert_id", ForeignKey("alerts.id", ondelete="CASCADE"), primary_key=True),
)

from app.infrastructure.models.mixins import SoftDeleteMixin

class Alert(Base, SoftDeleteMixin):
    __tablename__ = "alerts"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255), index=True)
    severity: Mapped[str] = mapped_column(String(50), index=True)  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    confidence_score: Mapped[int] = mapped_column(Integer, default=50)  # 1-100
    status: Mapped[str] = mapped_column(String(50), default="NEW", index=True)  # NEW, INVESTIGATING, TRUE_POSITIVE, FALSE_POSITIVE, CLOSED
    mitre_attack_mapping: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Log details
    source_ip: Mapped[Optional[str]] = mapped_column(String(45), index=True)
    destination_ip: Mapped[Optional[str]] = mapped_column(String(45), index=True)
    hostname: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    raw_event: Mapped[dict] = mapped_column(JSON)  # Store original JSON log event
    
    # Target Asset association
    asset_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("assets.id", ondelete="SET NULL"))
    
    # Rule and Assignment
    detection_rule_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("detection_rules.id", ondelete="SET NULL"))
    assigned_user_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    
    recommended_response: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    rule: Mapped[Optional[DetectionRule]] = relationship("DetectionRule", back_populates="alerts")
    assigned_user: Mapped[Optional["User"]] = relationship(
        "User", back_populates="assigned_alerts", foreign_keys=[assigned_user_id]
    )
    asset: Mapped[Optional["Asset"]] = relationship("app.infrastructure.models.system.Asset", back_populates="alerts")
    incidents: Mapped[List["Incident"]] = relationship(
        "Incident", secondary=incident_alerts, back_populates="alerts"
    )
    evidence: Mapped[List["Evidence"]] = relationship("Evidence", back_populates="alert")
