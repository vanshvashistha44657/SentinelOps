from typing import Optional
from app.domain.repositories.iam import UserRepository
from app.domain.repositories.auth import RefreshTokenRepository
from app.infrastructure.models.iam import User
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, validate_password_complexity, verify_token
from app.infrastructure.schemas.iam import UserCreate, UserResponse

class AuthService:
    def __init__(self, user_repo: UserRepository, refresh_token_repo: RefreshTokenRepository):
        self.user_repo = user_repo
        self.refresh_token_repo = refresh_token_repo

    async def register_user(self, user_in: UserCreate) -> UserResponse:
        validate_password_complexity(user_in.password)
        hashed_pw = hash_password(user_in.password)
        user_data = {
            "email": user_in.email,
            "full_name": user_in.full_name,
            "hashed_password": hashed_pw,
            "role_id": "00000000-0000-0000-0000-000000000000" # Placeholder
        }
        user = self.user_repo.create(user_data)
        return UserResponse.model_validate(user)

    async def authenticate(self, email: str, password: str) -> Optional[dict]:
        user = self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        
        # Store refresh token
        from datetime import datetime, timedelta
        self.refresh_token_repo.create({
            "user_id": user.id,
            "token": refresh_token,
            "expires_at": datetime.utcnow() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        })

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    async def refresh_token(self, token: str) -> Optional[dict]:
        payload = verify_token(token)
        if not payload or payload.get("type") != "refresh":
            return None
        
        token_record = self.refresh_token_repo.get_by_hash(token)
        if not token_record:
            # Possible reuse or invalid token
            # In a real scenario, should revoke all tokens for user here
            return None
            
        # Revoke old token
        self.refresh_token_repo.revoke(token_record.id)
        
        # Issue new pair
        user_id = UUID(payload["sub"])
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)
        
        # Store new refresh token
        from datetime import datetime, timedelta
        self.refresh_token_repo.create({
            "user_id": user_id,
            "token": refresh_token,
            "expires_at": datetime.utcnow() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        })
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
