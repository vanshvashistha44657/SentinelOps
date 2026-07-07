from pydantic import BaseModel
from typing import Optional, Dict
from uuid import UUID
from datetime import datetime

class IOCBase(BaseModel):
    value: str
    type: str
    risk_score: int = 0
    description: Optional[str] = None

class IOCCreate(IOCBase):
    tags: Optional[Dict] = None
    mitre_attack_mapping: Optional[Dict] = None
    references: Optional[Dict] = None

class IOCUpdate(BaseModel):
    risk_score: Optional[int] = None
    tags: Optional[Dict] = None
    mitre_attack_mapping: Optional[Dict] = None
    is_active: Optional[bool] = None

class IOCResponse(IOCBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
