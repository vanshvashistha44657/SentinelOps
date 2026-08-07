from typing import Optional, Dict
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.core.config import settings
from app.domain.enums.user import ApprovalStatus
from app.domain.repositories.iam import UserRepository, RoleRepository
from app.domain.repositories.auth import RefreshTokenRepository
from app.infrastructure.repositories.auth import SQLAlchemyEmailVerificationTokenRepository
from app.application.services.audit import AuditService
from app.infrastructure.models.iam import User
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, validate_password_complexity, verify_token, create_verification_token
from app.infrastructure.schemas.iam import UserCreate, UserResponse, UserUpdate

class AuthService:
    def __init__(self, user_repo: UserRepository, role_repo: RoleRepository, refresh_token_repo: RefreshTokenRepository, verification_token_repo: SQLAlchemyEmailVerificationTokenRepository, audit_service: AuditService):
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.refresh_token_repo = refresh_token_repo
        self.verification_token_repo = verification_token_repo
        self.audit_service = audit_service

    async def register_user(self, user_in: UserCreate, ip_address: str, device: str) -> dict:
        validate_password_complexity(user_in.password)
        hashed_pw = hash_password(user_in.password)

        role = self.role_repo.get_by_name("SOC Analyst")
        if not role:
            raise ValueError("Default role 'SOC Analyst' not found")

        user_data = {
            "email": user_in.email,
            "full_name": user_in.full_name,
            "hashed_password": hashed_pw,
            "role_id": role.id,
            "registration_ip": ip_address,
            "registration_device": device,
            "approval_status": ApprovalStatus.PENDING,
            "email_verified": False
        }

        user = self.user_repo.create(user_data)
        
        # Generate verification token
        token = create_verification_token()
        expires_at = datetime.utcnow() + timedelta(hours=24)
        self.verification_token_repo.create(user.id, token, expires_at)

        self.audit_service.log_action(user.id, ip_address, "auth", "USER_REGISTER", None, {"email": user.email})
        return {"user": UserResponse.model_validate(user), "verification_token": token}

    async def verify_email_with_token(self, token: str, ip_address: str) -> bool:
        verification_token = self.verification_token_repo.get_by_hash(token)
        if not verification_token or verification_token.expires_at < datetime.utcnow():
            return False
        
        self.user_repo.update(verification_token.user_id, {"email_verified": True, "email_verified_at": datetime.utcnow()})
        self.verification_token_repo.mark_as_used(verification_token.id)
        self.audit_service.log_action(verification_token.user_id, ip_address, "auth", "EMAIL_VERIFIED_WITH_TOKEN")
        return True

    async def authenticate(self, email: str, password: str, ip_address: str, device: str) -> Optional[dict]:
        user = self.user_repo.get_by_email(email)
        
        if not user or not verify_password(password, user.hashed_password):
            self.audit_service.log_action(None, ip_address, "auth", "USER_LOGIN_FAILED", None, {"email": email, "reason": "invalid_credentials"})
            return None
        
        # Check approval status and email verification
        if not user.email_verified:
            self.audit_service.log_action(user.id, ip_address, "auth", "USER_LOGIN_FAILED", None, {"reason": "email_not_verified"})
            raise HTTPException(status_code=403, detail="Email not verified")
            
        if user.approval_status == ApprovalStatus.PENDING:
            self.audit_service.log_action(user.id, ip_address, "auth", "USER_LOGIN_FAILED", None, {"reason": "pending_approval"})
            raise HTTPException(status_code=403, detail="Account pending approval")
            
        if user.approval_status == ApprovalStatus.REJECTED:
            self.audit_service.log_action(user.id, ip_address, "auth", "USER_LOGIN_FAILED", None, {"reason": "rejected", "rejected_reason": user.rejected_reason})
            raise HTTPException(status_code=403, detail=f"Account rejected: {user.rejected_reason}")
            
        if user.approval_status == ApprovalStatus.SUSPENDED:
            self.audit_service.log_action(user.id, ip_address, "auth", "USER_LOGIN_FAILED", None, {"reason": "suspended"})
            raise HTTPException(status_code=403, detail="Account suspended")

        # Update last login info
        self.user_repo.update(user.id, {"last_login_ip": ip_address, "last_login_device": device})
        
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        
        # Store refresh token
        self.refresh_token_repo.create({
            "user_id": user.id,
            "token": refresh_token,
            "expires_at": datetime.utcnow() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        })

        self.audit_service.log_action(user.id, ip_address, "auth", "USER_LOGIN_SUCCESS")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    async def approve_user(self, admin_id: UUID, user_id: UUID, ip_address: str) -> bool:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False
        
        self.user_repo.update(user_id, {
            "approval_status": ApprovalStatus.APPROVED,
            "approved_by": admin_id,
            "approved_at": datetime.utcnow()
        })
        self.audit_service.log_action(admin_id, ip_address, "auth", "USER_APPROVED", user_id, {"target_user_id": str(user_id)})
        return True

    async def reject_user(self, admin_id: UUID, user_id: UUID, reason: str, ip_address: str) -> bool:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False
        
        self.user_repo.update(user_id, {
            "approval_status": ApprovalStatus.REJECTED,
            "rejected_reason": reason
        })
        self.audit_service.log_action(admin_id, ip_address, "auth", "USER_REJECTED", user_id, {"target_user_id": str(user_id), "reason": reason})
        return True
    
    async def refresh_token(self, token: str, ip_address: str) -> Optional[dict]:
        payload = verify_token(token)
        if not payload or payload.get("type") != "refresh":
            return None
        
        token_record = self.refresh_token_repo.get_by_hash(token)
        if not token_record:
            return None
            
        # Revoke old token
        self.revoked_id = token_record.id
        self.refresh_token_repo.revoke(self.revoked_id)
        
        # Issue new pair
        user_id = UUID(payload["sub"])
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)
        
        # Store new refresh token
        self.refresh_token_repo.create({
            "user_id": user_id,
            "token": refresh_token,
            "expires_at": datetime.utcnow() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        })
        
        self.audit_service.log_action(user_id, ip_address, "auth", "TOKEN_REFRESH")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    async def get_user_profile(self, user_id: UUID) -> Optional[UserResponse]:
        user = self.user_repo.get_by_id(user_id)
        return UserResponse.model_validate(user) if user else None

    async def update_user_profile(self, user_id: UUID, update: UserUpdate, ip_address: str) -> Optional[UserResponse]:
        user = self.user_repo.update(user_id, update.model_dump(exclude_unset=True))
        if user:
            self.audit_service.log_action(user_id, ip_address, "auth", "PROFILE_UPDATE", None, update.model_dump())
            return UserResponse.model_validate(user)
        return None

    async def change_password(self, user_id: UUID, old_password: str, new_password: str, ip_address: str) -> bool:
        user = self.user_repo.get_by_id(user_id)
        if not user or not verify_password(old_password, user.hashed_password):
            return False
        
        hashed_password = hash_password(new_password)
        self.user_repo.update(user_id, {"hashed_password": hashed_password})
        self.audit_service.log_action(user_id, ip_address, "auth", "PASSWORD_CHANGE", None, None)
        return True

