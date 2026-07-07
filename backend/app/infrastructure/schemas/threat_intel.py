from pydantic import BaseModel
from typing import Optional, Dict
from uuid import UUID
from datetime import datetime

class ThreatIntelligenceBase(BaseModel):
    title: str
    source: str
    external_id: Optional[str] = None
    content: Optional[Dict] = None

class ThreatIntelligenceCreate(ThreatIntelligenceBase):
    pass

class ThreatIntelligenceUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[Dict] = None
    is_active: Optional[bool] = None

class ThreatIntelligenceResponse(ThreatIntelligenceBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
