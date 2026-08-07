from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import String, DateTime, ForeignKey, Text, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class ThreatHuntingQuery(Base):
    __tablename__ = "threat_hunting_queries"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    query: Mapped[str] = mapped_column(Text)
    creator_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator: Mapped["User"] = relationship("User")

class ThreatHuntingHistory(Base):
    __tablename__ = "threat_hunting_history"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    query: Mapped[str] = mapped_column(Text)
    executed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    result_count: Mapped[int] = mapped_column(Integer, default=0)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    
    # Relationships
    user: Mapped["User"] = relationship("User")
