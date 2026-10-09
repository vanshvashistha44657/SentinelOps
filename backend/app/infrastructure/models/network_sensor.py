from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.infrastructure.schemas.network import SensorStatus

class NetworkSensor(Base):
    __tablename__ = "network_sensors"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    # ``sensor_key`` is retained for a backwards-compatible migration path.
    # New enrollments use the hash fields and never persist the presented key.
    sensor_key: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    sensor_key_hash: Mapped[Optional[str]] = mapped_column(String(64), unique=True, index=True, nullable=True)
    sensor_key_prefix: Mapped[Optional[str]] = mapped_column(String(12), index=True, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default=SensorStatus.PENDING, index=True)
    platform: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    capabilities: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    owner_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_telemetry_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    interfaces: Mapped[list["NetworkInterface"]] = relationship(
        "NetworkInterface", back_populates="sensor", cascade="all, delete-orphan"
    )
    snapshots: Mapped[list["NetworkSnapshot"]] = relationship(
        "NetworkSnapshot", back_populates="sensor", cascade="all, delete-orphan"
    )
