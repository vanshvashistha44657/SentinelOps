import re
from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional
from jose import jwt
import secrets
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import HTTPException, status
from app.core.config import settings

def create_verification_token() -> str:
    """
    Generate a cryptographically secure token.
    """
    return secrets.token_urlsafe(32)


# Initialize password hasher with production-strength parameters
ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16
)

def validate_password_complexity(password: str) -> None:
    """
    Validates password complexity.
    """
    if len(password) < 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 12 characters long",
        )
    if not re.search(r"[A-Z]", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one uppercase letter",
        )
    if not re.search(r"[a-z]", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one lowercase letter",
        )
    if not re.search(r"\d", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one number",
        )
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one special character",
        )

def hash_password(password: str) -> str:
    """
    Hash a password using Argon2id.
    """
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against its Argon2id hash.
    """
    try:
        return ph.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False
...

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Generate an access JWT token.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Generate a refresh JWT token.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token.
    """
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return decoded_token if decoded_token["exp"] >= datetime.now(timezone.utc).timestamp() else None
    except jwt.JWTError:
        return None
