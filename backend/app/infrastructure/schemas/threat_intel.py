from pydantic import BaseModel, Field
from typing import Optional, Dict
from uuid import UUID
from datetime import datetime

class ThreatIntelligenceBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    source: str = Field(..., min_length=3, max_length=100)
    external_id: Optional[str] = Field(None, max_length=100)
    content: Optional[Dict] = None

class ThreatIntelligenceCreate(ThreatIntelligenceBase):
    pass

class ThreatIntelligenceUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    content: Optional[Dict] = None
    is_active: Optional[bool] = None

class ThreatIntelligenceResponse(ThreatIntelligenceBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
