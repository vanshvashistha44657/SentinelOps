from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str


class RoleSummary(BaseModel):
    id: UUID
    name: str

    model_config = {"from_attributes": True}

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: UUID
    is_active: bool
    role_id: UUID
    created_at: datetime
    approval_status: Optional[str] = None
    email_verified: Optional[bool] = None
    last_seen_at: Optional[datetime] = None
    role: Optional[RoleSummary] = None

    class Config:
        from_attributes = True
