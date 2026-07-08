from pydantic import BaseModel, Field
from typing import Optional, Dict
from uuid import UUID
from datetime import datetime

class IOCBase(BaseModel):
    value: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., pattern="^(IP|DOMAIN|URL|FILE_HASH|EMAIL)$")
    risk_score: int = Field(0, ge=0, le=100)
    description: Optional[str] = Field(None, max_length=1000)

class IOCCreate(IOCBase):
    tags: Optional[Dict] = None
    mitre_attack_mapping: Optional[Dict] = None
    references: Optional[Dict] = None

class IOCUpdate(BaseModel):
    risk_score: Optional[int] = Field(None, ge=0, le=100)
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
