from pydantic import BaseModel, Field
from typing import Optional, Dict
from uuid import UUID
from datetime import datetime

class LogCreate(BaseModel):
    source_connector: str
    event_type: str = "unknown"
    severity: str = "INFO"
    timestamp: Optional[datetime] = None
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    hostname: Optional[str] = None
    username: Optional[str] = None
    process_name: Optional[str] = None
    file_hash: Optional[str] = None
    domain: Optional[str] = None
    url: Optional[str] = None
    raw_content: str
    parsed_content: Optional[Dict] = None

class LogResponse(BaseModel):
    id: UUID
    ingested_at: datetime
    
    class Config:
        from_attributes = True

class FailedLogResponse(BaseModel):
    id: UUID
    source_connector: str
    raw_content: str
    error_reason: str
    retry_count: int
    failed_at: datetime
    
    class Config:
        from_attributes = True
