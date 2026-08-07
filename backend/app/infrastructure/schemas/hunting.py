from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class ThreatHuntingQueryBase(BaseModel):
    name: str
    description: Optional[str] = None
    query: str

class ThreatHuntingQueryCreate(ThreatHuntingQueryBase):
    pass

class ThreatHuntingQueryResponse(ThreatHuntingQueryBase):
    id: UUID
    creator_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ThreatHuntingHistoryResponse(BaseModel):
    id: UUID
    query: str
    executed_at: datetime
    result_count: int
    user_id: UUID

    class Config:
        from_attributes = True
