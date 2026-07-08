from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class AssetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    ip_address: Optional[str] = None
    os: Optional[str] = None
    owner_id: Optional[UUID] = None

class AssetCreate(AssetBase):
    pass

class AssetUpdate(AssetBase):
    pass

class AssetResponse(AssetBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
