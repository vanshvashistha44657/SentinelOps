from pydantic import BaseModel, Field
from typing import Optional, Dict
from uuid import UUID
from datetime import datetime

class IOCBase(BaseModel):
    value: str = Field(..., min_length=1, max_length=512)
    type: str = Field(..., pattern="^(IP|IPV4|IPV6|DOMAIN|URL|FILE_HASH|EMAIL)$")
    risk_score: int = Field(50, ge=0, le=100)
    severity: str = Field("MEDIUM", pattern="^(CRITICAL|HIGH|MEDIUM|LOW|INFO)$")
    source: str = Field("manual", min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    tags: Optional[Dict] = None
    tlp: str = "WHITE"
    expires_at: Optional[datetime] = None
    enabled: bool = True

class IOCCreate(IOCBase):
    tags: Optional[Dict] = None
    mitre_attack_mapping: Optional[Dict] = None
    references: Optional[Dict] = None

class IOCUpdate(BaseModel):
    risk_score: Optional[int] = Field(None, ge=0, le=100)
    severity: Optional[str] = Field(None, pattern="^(CRITICAL|HIGH|MEDIUM|LOW|INFO)$")
    source: Optional[str] = Field(None, max_length=100)
    tags: Optional[Dict] = None
    expires_at: Optional[datetime] = None
    enabled: Optional[bool] = None

class IOCResponse(IOCBase):
    id: UUID
    severity: str
    source: str
    enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
