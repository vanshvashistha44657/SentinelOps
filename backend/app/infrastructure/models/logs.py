from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import String, DateTime, JSON, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class RawLog(Base):
    __tablename__ = "raw_logs"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    source_connector: Mapped[str] = mapped_column(String(100), index=True)
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    severity: Mapped[str] = mapped_column(String(50), index=True)
    
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    source_ip: Mapped[str] = mapped_column(String(45), index=True, nullable=True)
    destination_ip: Mapped[str] = mapped_column(String(45), index=True, nullable=True)
    hostname: Mapped[str] = mapped_column(String(255), index=True, nullable=True)
    username: Mapped[str] = mapped_column(String(255), index=True, nullable=True)
    process_name: Mapped[str] = mapped_column(String(255), index=True, nullable=True)
    file_hash: Mapped[str] = mapped_column(String(255), index=True, nullable=True)
    domain: Mapped[str] = mapped_column(String(255), index=True, nullable=True)
    url: Mapped[str] = mapped_column(Text, nullable=True)

    raw_content: Mapped[str] = mapped_column(Text)
    parsed_content: Mapped[dict] = mapped_column(JSON, nullable=True)
    ingested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

class FailedLog(Base):
    __tablename__ = "failed_logs"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    source_connector: Mapped[str] = mapped_column(String(100), index=True)
    raw_content: Mapped[str] = mapped_column(Text)
    error_reason: Mapped[str] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
