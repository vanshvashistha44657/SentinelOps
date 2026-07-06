from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.infrastructure.models.alerts import incident_alerts

from app.infrastructure.models.mixins import SoftDeleteMixin

class Incident(Base, SoftDeleteMixin):
    __tablename__ = "incidents"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255), index=True)
    severity: Mapped[str] = mapped_column(String(50), index=True)  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    status: Mapped[str] = mapped_column(String(50), default="OPEN", index=True)  # OPEN, UNDER_INVESTIGATION, CONTAINED, RESOLVED, CLOSED
    summary: Mapped[Optional[str]] = mapped_column(Text)
    assigned_user_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assigned_user: Mapped[Optional["User"]] = relationship(
        "User", back_populates="assigned_incidents", foreign_keys=[assigned_user_id]
    )
    alerts: Mapped[List["Alert"]] = relationship(
        "Alert", secondary=incident_alerts, back_populates="incidents"
    )
    cases: Mapped[List["Case"]] = relationship("Case", back_populates="incident", cascade="all, delete-orphan")
    notes: Mapped[List["AnalystNote"]] = relationship("AnalystNote", back_populates="incident", cascade="all, delete-orphan")
    evidence: Mapped[List["Evidence"]] = relationship("Evidence", back_populates="incident", cascade="all, delete-orphan")
    attachments: Mapped[List["Attachment"]] = relationship("Attachment", back_populates="incident", cascade="all, delete-orphan")

class Case(Base, SoftDeleteMixin):
    __tablename__ = "cases"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(50), default="MEDIUM")  # CRITICAL, HIGH, MEDIUM, LOW
    status: Mapped[str] = mapped_column(String(50), default="OPEN")  # OPEN, IN_PROGRESS, RESOLVED, CLOSED
    assigned_user_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    incident_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("incidents.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assigned_user: Mapped[Optional["User"]] = relationship(
        "User", back_populates="assigned_cases", foreign_keys=[assigned_user_id]
    )
    incident: Mapped[Optional[Incident]] = relationship("Incident", back_populates="cases")
    notes: Mapped[List["AnalystNote"]] = relationship("CaseNote", back_populates="case", cascade="all, delete-orphan")
    evidence: Mapped[List["Evidence"]] = relationship("Evidence", back_populates="case", cascade="all, delete-orphan")
    attachments: Mapped[List["Attachment"]] = relationship("Attachment", back_populates="case", cascade="all, delete-orphan")

class AnalystNote(Base):
    __tablename__ = "analyst_notes"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    incident_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("incidents.id", ondelete="CASCADE"))
    case_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"))
    author_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    incident: Mapped[Optional[Incident]] = relationship("Incident", back_populates="notes")
    case: Mapped[Optional[Case]] = relationship("Case", primaryjoin="AnalystNote.case_id == Case.id", back_populates="notes")
    author: Mapped["User"] = relationship("User")

class CaseNote(AnalystNote):
    # Standard base handles both, but we can map specifically or use polymorphism
    pass

class Evidence(Base):
    __tablename__ = "evidence"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    incident_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("incidents.id", ondelete="CASCADE"))
    case_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"))
    alert_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("alerts.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(100))  # IP, FILE_HASH, DOMAIN, PROCESS, OTHER
    value: Mapped[str] = mapped_column(String(512), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    added_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    incident: Mapped[Optional[Incident]] = relationship("Incident", back_populates="evidence")
    case: Mapped[Optional[Case]] = relationship("Case", back_populates="evidence")
    alert: Mapped[Optional["Alert"]] = relationship("Alert", back_populates="evidence")
    added_by: Mapped["User"] = relationship("User")

class Attachment(Base):
    __tablename__ = "attachments"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    incident_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("incidents.id", ondelete="CASCADE"))
    case_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"))
    file_name: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(512))  # S3 bucket url or local storage path
    file_size: Mapped[int] = mapped_column(Integer)
    mime_type: Mapped[str] = mapped_column(String(100))
    uploaded_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    incident: Mapped[Optional[Incident]] = relationship("Incident", back_populates="attachments")
    case: Mapped[Optional[Case]] = relationship("Case", back_populates="attachments")
    uploaded_by: Mapped["User"] = relationship("User")
