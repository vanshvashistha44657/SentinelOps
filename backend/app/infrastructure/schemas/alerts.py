from pydantic import BaseModel, Field
from typing import Optional, Dict
from uuid import UUID
from datetime import datetime

class AlertBase(BaseModel):
    title: str
    severity: str
    confidence_score: int = Field(..., ge=1, le=100)
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    hostname: Optional[str] = None
    username: Optional[str] = None

class AlertCreate(AlertBase):
    raw_event: Dict
    detection_rule_id: Optional[UUID] = None

class AlertUpdate(BaseModel):
    status: Optional[str] = None
    assigned_user_id: Optional[UUID] = None
    recommended_response: Optional[str] = None

class AlertResponse(AlertBase):
    id: UUID
    status: str
    mitre_attack_mapping: Optional[Dict] = None
    created_at: datetime

    class Config:
        from_attributes = True
