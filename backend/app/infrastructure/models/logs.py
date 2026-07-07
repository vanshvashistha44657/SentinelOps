from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import String, DateTime, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class RawLog(Base):
    __tablename__ = "raw_logs"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    source: Mapped[str] = mapped_column(String(255), index=True)  # e.g., "win_event_log", "nginx"
    log_type: Mapped[str] = mapped_column(String(100), index=True) # e.g., "syslog", "json"
    raw_content: Mapped[str] = mapped_column(Text)
    parsed_content: Mapped[dict] = mapped_column(JSON, nullable=True) # JSONB content
    ingested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
