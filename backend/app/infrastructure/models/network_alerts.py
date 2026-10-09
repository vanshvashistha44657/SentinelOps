from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class SecurityAlert(Base):
    __tablename__ = "security_alerts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    alert_type: Mapped[str] = mapped_column(String(50), index=True)
    severity: Mapped[str] = mapped_column(String(20), index=True) # CRITICAL, HIGH, MEDIUM, LOW, INFO
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(100)) # e.g. "NetworkSensor"

    # Optional associations
    device_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("network_devices.id", ondelete="SET NULL"), nullable=True)
    sensor_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("network_sensors.id", ondelete="SET NULL"), nullable=True)

    source_ip: Mapped[Optional[str]] = mapped_column(String(45), index=True)
    source_mac: Mapped[Optional[str]] = mapped_column(String(17), index=True)

    # Status lifecycle: OPEN, ACKNOWLEDGED, RESOLVED, FALSE_POSITIVE
    status: Mapped[str] = mapped_column(String(20), default="OPEN", index=True)
    occurrence_count: Mapped[int] = mapped_column(Integer, default=1)

    first_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    alert_metadata: Mapped[Optional[dict]] = mapped_column(JSON)

    # Relationships
    device: Mapped[Optional["NetworkDevice"]] = relationship("NetworkDevice")
    sensor: Mapped[Optional["NetworkSensor"]] = relationship("NetworkSensor")
