from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Asset(Base):
    __tablename__ = "assets"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    type: Mapped[str] = mapped_column(String(100))  # SERVER, WORKSTATION, DOMAIN_CONTROLLER, FIREWALL, ROUTER, CLOUD_VM
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), index=True)
    mac_address: Mapped[Optional[str]] = mapped_column(String(17))
    os: Mapped[Optional[str]] = mapped_column(String(100))
    criticality: Mapped[str] = mapped_column(String(50), default="MEDIUM")  # CRITICAL, HIGH, MEDIUM, LOW
    owner_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    alerts: Mapped[List["Alert"]] = relationship("Alert", back_populates="asset")
    owner: Mapped[Optional["User"]] = relationship("User")

class Notification(Base):
    __tablename__ = "notifications"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(String(50), default="INFO")  # INFO, WARNING, ALERT, SUCCESS
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(String(100), index=True)  # e.g., USER_LOGIN, ALERT_CLOSE, RULE_CREATE
    details: Mapped[Optional[dict]] = mapped_column(JSON)  # rich metadata about the mutation
    ip_address: Mapped[str] = mapped_column(String(45))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User")

class Report(Base):
    __tablename__ = "reports"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(100))  # DAILY_SOC, WEEKLY_SOC, EXECUTIVE, DETECTION_COVERAGE, INCIDENT_SUMMARY
    format: Mapped[str] = mapped_column(String(20))  # PDF, CSV
    file_path: Mapped[str] = mapped_column(String(512))  # path on S3 or local directory
    generated_by_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    generated_by: Mapped[Optional["User"]] = relationship("User")

class Playbook(Base):
    __tablename__ = "playbooks"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    trigger_type: Mapped[str] = mapped_column(String(50))  # AUTOMATIC, MANUAL
    steps: Mapped[dict] = mapped_column(JSON)  # Conditional play steps configuration
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SystemSetting(Base):
    __tablename__ = "system_settings"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    value: Mapped[dict] = mapped_column(JSON)  # flexible JSON value structure
    description: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    
    # Relationships
    updated_by: Mapped[Optional["User"]] = relationship("User")
