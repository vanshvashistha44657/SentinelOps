from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.application.services.auth import AuthService
from app.application.services.audit import AuditService
from app.infrastructure.repositories.iam import SQLAlchemyUserRepository, SQLAlchemyRoleRepository
from app.infrastructure.repositories.auth import SQLAlchemyRefreshTokenRepository
from app.infrastructure.repositories.audit import SQLAlchemyAuditRepository
from app.infrastructure.schemas.iam import UserCreate, UserResponse
from app.infrastructure.schemas.auth import TokenResponse, LoginRequest

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    user_repo = SQLAlchemyUserRepository(db)
    role_repo = SQLAlchemyRoleRepository(db)
    refresh_token_repo = SQLAlchemyRefreshTokenRepository(db)
    audit_repo = SQLAlchemyAuditRepository(db)
    audit_service = AuditService(audit_repo)
    return AuthService(user_repo, role_repo, refresh_token_repo, audit_service)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    user_in: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.register_user(user_in, request.client.host)

@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    token = await auth_service.authenticate(login_data.email, login_data.password, request.client.host)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return token

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
