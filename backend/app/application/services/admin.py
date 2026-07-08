from typing import List, Optional
from uuid import UUID
from app.infrastructure.repositories.iam import SQLAlchemyUserRepository
from app.infrastructure.schemas.iam import UserResponse, UserUpdate
from app.application.services.audit import AuditService

class AdminService:
    def __init__(self, user_repo: SQLAlchemyUserRepository, audit_service: AuditService):
        self.user_repo = user_repo
        self.audit_service = audit_service

    async def list_users(self) -> List[UserResponse]:
        users = self.user_repo.list()
        return [UserResponse.model_validate(u) for u in users]

    async def update_user(self, user_id: UUID, user_update: UserUpdate, admin_id: UUID, ip_address: str) -> Optional[UserResponse]:
        user = self.user_repo.update(user_id, user_update.model_dump(exclude_unset=True))
        if user:
            self.audit_service.log_action(admin_id, ip_address, "admin", "USER_UPDATE", {"id": str(user_id)}, user_update.model_dump())
        return UserResponse.model_validate(user) if user else None
