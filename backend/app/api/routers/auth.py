from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.application.services.auth import AuthService
from app.infrastructure.repositories.iam import SQLAlchemyUserRepository
from app.infrastructure.repositories.auth import SQLAlchemyRefreshTokenRepository
from app.infrastructure.schemas.iam import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    user_repo = SQLAlchemyUserRepository(db)
    refresh_repo = SQLAlchemyRefreshTokenRepository(db)
    return AuthService(user_repo, refresh_repo)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.register_user(user_in)

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    tokens = await auth_service.authenticate(form_data.username, form_data.password)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    return tokens

@router.post("/refresh")
async def refresh(
    token: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    tokens = await auth_service.refresh_token(token)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    return tokens

@router.post("/logout")
async def logout(
    token: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    # Logic to revoke token from DB - need to expose revoke in AuthService
    return {"message": "Logged out"}
