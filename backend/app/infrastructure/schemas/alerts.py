from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from uuid import UUID
from datetime import datetime
from enum import Enum

class AlertSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AlertStatus(str, Enum):
    NEW = "NEW"
    INVESTIGATING = "INVESTIGATING"
    TRUE_POSITIVE = "TRUE_POSITIVE"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    CLOSED = "CLOSED"

class AlertBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    severity: AlertSeverity
    confidence_score: int = Field(..., ge=1, le=100)
    source_ip: Optional[str] = Field(None, max_length=45)
    destination_ip: Optional[str] = Field(None, max_length=45)
    hostname: Optional[str] = Field(None, max_length=255)
    username: Optional[str] = Field(None, max_length=255)

class AlertCreate(AlertBase):
    raw_event: Dict
    detection_rule_id: Optional[UUID] = None

class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None
    assigned_user_id: Optional[UUID] = None
    recommended_response: Optional[str] = Field(None, max_length=2000)
    reason: Optional[str] = Field(None, max_length=1000)

class AlertResponse(AlertBase):
    id: UUID
    status: AlertStatus
    mitre_attack_mapping: Optional[Dict] = None
    raw_event: Dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AlertFilterParams(BaseModel):
    severity: Optional[AlertSeverity] = None
    status: Optional[AlertStatus] = None
    source_ip: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class PaginatedAlertResponse(BaseModel):
    items: List[AlertResponse]
    total: int
    page: int
    size: int


class AlertStatusHistoryResponse(BaseModel):
    id: UUID
    alert_id: UUID
    changed_by_id: Optional[UUID] = None
    previous_status: str
    new_status: str
    reason: Optional[str] = None
    changed_at: datetime

    model_config = {"from_attributes": True}
