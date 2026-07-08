from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class CaseBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    priority: str = Field("MEDIUM", pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    incident_id: Optional[UUID] = None

class CaseCreate(CaseBase):
    pass

class CaseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[str] = Field(None, pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    status: Optional[str] = Field(None, pattern="^(NEW|OPEN|IN_PROGRESS|RESOLVED|CLOSED)$")
    assigned_user_id: Optional[UUID] = None

class CaseResponse(CaseBase):
    id: UUID
    status: str
    assigned_user_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
