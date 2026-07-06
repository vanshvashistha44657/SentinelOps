from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from uuid import UUID
from datetime import datetime

class DetectionRuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    confidence_score: int = Field(..., ge=1, le=100)
    mitre_attack_mapping: Optional[Dict] = None
    query_logic: str

class DetectionRuleCreate(DetectionRuleBase):
    pass

class DetectionRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    confidence_score: Optional[int] = Field(None, ge=1, le=100)
    mitre_attack_mapping: Optional[Dict] = None
    query_logic: Optional[str] = None
    is_active: Optional[bool] = None

class DetectionRuleResponse(DetectionRuleBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RuleVersionResponse(BaseModel):
    id: UUID
    detection_rule_id: UUID
    version_number: int
    query_logic: str
    changelog: Optional[str] = None
    created_at: datetime
    created_by_id: UUID

    class Config:
        from_attributes = True
