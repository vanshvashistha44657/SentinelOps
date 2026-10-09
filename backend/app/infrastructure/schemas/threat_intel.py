from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from uuid import UUID
from datetime import datetime

class ThreatIndicatorBase(BaseModel):
    type: str = Field(..., min_length=2, max_length=50)
    value: str = Field(..., min_length=1, max_length=512)
    risk_score: int = Field(50, ge=0, le=100)
    severity: str = Field("MEDIUM", pattern="^(CRITICAL|HIGH|MEDIUM|LOW|INFO)$")
    source: str = Field("manual", min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    tags: Optional[Dict] = None
    tlp: str = "WHITE"
    expires_at: Optional[datetime] = None
    enabled: bool = True

class ThreatIndicatorCreate(ThreatIndicatorBase):
    pass

class ThreatIndicatorUpdate(BaseModel):
    risk_score: Optional[int] = Field(None, ge=0, le=100)
    severity: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[Dict] = None
    tlp: Optional[str] = None
    expires_at: Optional[datetime] = None
    enabled: Optional[bool] = None

class ThreatIndicatorResponse(ThreatIndicatorBase):
    id: UUID
    first_seen: datetime
    last_seen: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class IOCMatchResponse(BaseModel):
    id: UUID
    indicator_id: UUID
    raw_log_id: UUID
    alert_id: Optional[UUID] = None
    matched_field: str
    matched_at: datetime

    class Config:
        from_attributes = True
