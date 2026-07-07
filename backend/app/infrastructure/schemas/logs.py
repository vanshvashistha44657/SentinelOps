from pydantic import BaseModel
from typing import Optional, Dict
from uuid import UUID
from datetime import datetime

class LogBase(BaseModel):
    source: str
    log_type: str
    raw_content: str

class LogCreate(LogBase):
    pass

class LogResponse(LogBase):
    id: UUID
    parsed_content: Optional[Dict] = None
    ingested_at: datetime

    class Config:
        from_attributes = True
