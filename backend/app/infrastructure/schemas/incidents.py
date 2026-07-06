from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class IncidentBase(BaseModel):
    title: str
    severity: str
    summary: Optional[str] = None

class IncidentCreate(IncidentBase):
    pass

class IncidentUpdate(BaseModel):
    status: Optional[str] = None
    assigned_user_id: Optional[UUID] = None
    summary: Optional[str] = None

class IncidentResponse(IncidentBase):
    id: UUID
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
