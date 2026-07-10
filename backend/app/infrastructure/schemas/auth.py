from pydantic import BaseModel
from typing import Optional

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    email: str
    password: str
