from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.application.services.auth import AuthService
from app.application.services.audit import AuditService
from app.infrastructure.repositories.iam import SQLAlchemyUserRepository
from app.infrastructure.repositories.auth import SQLAlchemyRefreshTokenRepository
from app.infrastructure.repositories.audit import SQLAlchemyAuditRepository
from app.infrastructure.schemas.iam import UserCreate, UserResponse, TokenResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    user_repo = SQLAlchemyUserRepository(db)
    refresh_token_repo = SQLAlchemyRefreshTokenRepository(db)
    audit_repo = SQLAlchemyAuditRepository(db)
    audit_service = AuditService(audit_repo)
    return AuthService(user_repo, refresh_token_repo, audit_service)

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
    email: str, # Should be using Form or body model
    password: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    token = await auth_service.authenticate(email, password, request.client.host)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return token
