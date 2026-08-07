from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

class EvidenceType(str, Enum):
    IP = "IP"
    FILE_HASH = "FILE_HASH"
    DOMAIN = "DOMAIN"
    PROCESS = "PROCESS"
    OTHER = "OTHER"

class EvidenceBase(BaseModel):
    name: str
    type: EvidenceType
    value: str
    description: Optional[str] = None

class EvidenceCreate(EvidenceBase):
    pass

class EvidenceResponse(EvidenceBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class NoteBase(BaseModel):
    content: str

class NoteCreate(NoteBase):
    pass

class NoteResponse(NoteBase):
    id: UUID
    author_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
