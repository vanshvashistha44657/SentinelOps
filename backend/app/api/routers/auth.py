from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.orm import Session
from uuid import UUID
from app.api.dependencies import get_db
from app.api.dependencies.auth import get_current_user
from app.application.services.auth import AuthService
from app.application.services.audit import AuditService
from app.infrastructure.repositories.iam import SQLAlchemyUserRepository, SQLAlchemyRoleRepository
from app.infrastructure.repositories.auth import SQLAlchemyRefreshTokenRepository, SQLAlchemyEmailVerificationTokenRepository
from app.infrastructure.repositories.audit import SQLAlchemyAuditRepository
from app.infrastructure.models.iam import User
from app.infrastructure.schemas.iam import UserCreate, UserResponse, UserUpdate
from app.infrastructure.schemas.auth import TokenResponse, LoginRequest

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    user_repo = SQLAlchemyUserRepository(db)
    role_repo = SQLAlchemyRoleRepository(db)
    refresh_token_repo = SQLAlchemyRefreshTokenRepository(db)
    verification_token_repo = SQLAlchemyEmailVerificationTokenRepository(db)
    audit_repo = SQLAlchemyAuditRepository(db)
    audit_service = AuditService(audit_repo)
    return AuthService(user_repo, role_repo, refresh_token_repo, verification_token_repo, audit_service)

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    user_in: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.register_user(user_in, request.client.host, request.headers.get("User-Agent", "unknown"))

@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    token = await auth_service.authenticate(login_data.email, login_data.password, request.client.host, request.headers.get("User-Agent", "unknown"))
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return token

@router.post("/heartbeat", status_code=status.HTTP_204_NO_CONTENT)
async def heartbeat(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    await auth_service.heartbeat(current_user.id)
    return None

@router.post("/verify-email", status_code=status.HTTP_204_NO_CONTENT)
async def verify_email(
    request: Request,
    token: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    if not await auth_service.verify_email_with_token(token, request.client.host):
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    return None

@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: Request,
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    token = await auth_service.refresh_token(refresh_token, request.client.host)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return token

from pydantic import BaseModel

class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str

@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.get_user_profile(current_user.id)

@router.patch("/profile", response_model=UserResponse)
async def update_profile(
    request: Request,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    user = await auth_service.update_user_profile(current_user.id, user_update, request.client.host)
    if not user:
        raise HTTPException(status_code=400, detail="Failed to update profile")
    return user

@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    request: Request,
    pw_request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    if not await auth_service.change_password(current_user.id, pw_request.old_password, pw_request.new_password, request.client.host):
        raise HTTPException(status_code=400, detail="Invalid password")
    return None
