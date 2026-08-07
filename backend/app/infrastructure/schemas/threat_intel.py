from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from uuid import UUID
from datetime import datetime

class ThreatIndicatorBase(BaseModel):
    type: str
    value: str
    confidence: int = 50
    severity: str
    source: str
    description: Optional[str] = None
    tags: Optional[Dict] = None
    tlp: str = "WHITE"
    expires_at: Optional[datetime] = None
    enabled: bool = True

class ThreatIndicatorCreate(ThreatIndicatorBase):
    pass

class ThreatIndicatorUpdate(BaseModel):
    confidence: Optional[int] = None
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
