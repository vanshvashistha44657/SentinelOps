from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum

class IncidentSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class IncidentStatus(str, Enum):
    OPEN = "OPEN"
    UNDER_INVESTIGATION = "UNDER_INVESTIGATION"
    CONTAINED = "CONTAINED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class IncidentBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    severity: IncidentSeverity
    summary: Optional[str] = Field(None, max_length=2000)

class IncidentCreate(IncidentBase):
    pass

class IncidentUpdate(BaseModel):
    status: Optional[IncidentStatus] = None
    assigned_user_id: Optional[UUID] = None
    summary: Optional[str] = Field(None, max_length=2000)

class IncidentResponse(IncidentBase):
    id: UUID
    status: IncidentStatus
    created_at: datetime

    class Config:
        from_attributes = True

class IncidentFilterParams(BaseModel):
    severity: Optional[IncidentSeverity] = None
    status: Optional[IncidentStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class PaginatedIncidentResponse(BaseModel):
    items: List[IncidentResponse]
    total: int
    page: int
    size: int
