from pydantic import BaseModel
from typing import Optional, Dict
from uuid import UUID
from datetime import datetime

class IOCRecordBase(BaseModel):
    value: str
    type: str
    risk_score: int

class IOCRecordCreate(IOCRecordBase):
    description: Optional[str] = None
    tags: Optional[Dict] = None

class IOCRecordResponse(IOCRecordBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
