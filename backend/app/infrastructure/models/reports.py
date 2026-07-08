from sqlalchemy import Column, String, JSON, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid

class Report(Base):
    __tablename__ = "reports"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    report_type = Column(String, nullable=False) # INCIDENT_SUMMARY, ANALYST_PERFORMANCE
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
