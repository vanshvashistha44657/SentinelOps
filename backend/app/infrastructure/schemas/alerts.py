from pydantic import BaseModel, Field
from typing import Optional, Dict
from uuid import UUID
from datetime import datetime

class AlertBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    severity: str = Field(..., pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    confidence_score: int = Field(..., ge=1, le=100)
    source_ip: Optional[str] = Field(None, max_length=45)
    destination_ip: Optional[str] = Field(None, max_length=45)
    hostname: Optional[str] = Field(None, max_length=255)
    username: Optional[str] = Field(None, max_length=255)

class AlertCreate(AlertBase):
    raw_event: Dict
    detection_rule_id: Optional[UUID] = None

class AlertUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(NEW|OPEN|IN_PROGRESS|RESOLVED|CLOSED)$")
    assigned_user_id: Optional[UUID] = None
    recommended_response: Optional[str] = Field(None, max_length=2000)

class AlertResponse(AlertBase):
    id: UUID
    status: str
    mitre_attack_mapping: Optional[Dict] = None
    created_at: datetime

    class Config:
        from_attributes = True
