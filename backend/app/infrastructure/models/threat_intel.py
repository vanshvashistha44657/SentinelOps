from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class IOCRecord(Base):
    __tablename__ = "threat_indicators"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    type: Mapped[str] = mapped_column(String(50), index=True) 
    value: Mapped[str] = mapped_column(String(512), unique=True, index=True)
    risk_score: Mapped[int] = mapped_column(Integer, default=50) # Renamed from confidence
    severity: Mapped[str] = mapped_column(String(50), index=True) 
    source: Mapped[str] = mapped_column(String(100), index=True) 
    description: Mapped[Optional[str]] = mapped_column(Text)
    tags: Mapped[Optional[dict]] = mapped_column(JSON)
    tlp: Mapped[str] = mapped_column(String(20), default="WHITE") 
    first_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    matches: Mapped[List["IOCMatch"]] = relationship("IOCMatch", back_populates="indicator", cascade="all, delete-orphan")

ThreatIndicator = IOCRecord

class IOCMatch(Base):
    __tablename__ = "ioc_matches"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    indicator_id: Mapped[UUID] = mapped_column(ForeignKey("threat_indicators.id", ondelete="CASCADE"), index=True)
    raw_log_id: Mapped[UUID] = mapped_column(ForeignKey("raw_logs.id", ondelete="CASCADE"), index=True)
    alert_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("alerts.id", ondelete="CASCADE"), index=True)
    matched_field: Mapped[str] = mapped_column(String(100)) # e.g. "source_ip", "hostname"
    matched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    indicator: Mapped["IOCRecord"] = relationship("IOCRecord", back_populates="matches")
    raw_log: Mapped["RawLog"] = relationship("RawLog")
    alert: Mapped[Optional["Alert"]] = relationship("Alert")
