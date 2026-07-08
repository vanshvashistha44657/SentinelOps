from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class IncidentBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    severity: str = Field(..., pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    summary: Optional[str] = Field(None, max_length=2000)

class IncidentCreate(IncidentBase):
    pass

class IncidentUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(NEW|OPEN|IN_PROGRESS|RESOLVED|CLOSED)$")
    assigned_user_id: Optional[UUID] = None
    summary: Optional[str] = Field(None, max_length=2000)

class IncidentResponse(IncidentBase):
    id: UUID
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
