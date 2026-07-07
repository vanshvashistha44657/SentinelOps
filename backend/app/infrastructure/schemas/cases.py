from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class CaseBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "MEDIUM"
    incident_id: Optional[UUID] = None

class CaseCreate(CaseBase):
    pass

class CaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assigned_user_id: Optional[UUID] = None

class CaseResponse(CaseBase):
    id: UUID
    status: str
    assigned_user_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
