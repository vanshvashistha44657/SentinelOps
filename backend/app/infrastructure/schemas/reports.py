from pydantic import BaseModel, Field
from typing import Optional, Dict
from uuid import UUID
from datetime import datetime

class ReportCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    type: str = Field(..., pattern="^(DAILY_SOC|WEEKLY_SOC|EXECUTIVE|DETECTION_COVERAGE|INCIDENT_SUMMARY)$")
    format: str = Field(..., pattern="^(PDF|CSV)$")
    file_path: str = Field(..., max_length=512)

class ReportResponse(ReportCreate):
    id: UUID
    generated_by_id: Optional[UUID]
    created_at: datetime

    class Config:
        from_attributes = True
