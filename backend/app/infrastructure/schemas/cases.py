from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum

class CasePriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class CaseStatus(str, Enum):
    NEW = "NEW"
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class CaseBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    priority: CasePriority = CasePriority.MEDIUM
    incident_id: Optional[UUID] = None

class CaseCreate(CaseBase):
    pass

class CaseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[CasePriority] = None
    status: Optional[CaseStatus] = None
    assigned_user_id: Optional[UUID] = None

class CaseResponse(CaseBase):
    id: UUID
    status: CaseStatus
    assigned_user_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CaseFilterParams(BaseModel):
    priority: Optional[CasePriority] = None
    status: Optional[CaseStatus] = None
    assigned_user_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class PaginatedCaseResponse(BaseModel):
    items: List[CaseResponse]
    total: int
    page: int
    size: int
