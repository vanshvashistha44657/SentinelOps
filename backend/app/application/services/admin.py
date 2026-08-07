from typing import List, Optional, Dict, Any
from uuid import UUID
from app.infrastructure.repositories.iam import SQLAlchemyUserRepository
from app.infrastructure.schemas.iam import UserResponse, UserUpdate
from app.infrastructure.models.iam import User, Role, LoginHistory
from app.infrastructure.models.system import AuditTrail
from app.application.services.audit import AuditService
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from typing import List, Optional, Dict, Any
from uuid import UUID
from app.infrastructure.repositories.iam import SQLAlchemyUserRepository
from app.infrastructure.schemas.iam import UserResponse, UserUpdate
from app.infrastructure.models.iam import User, Role, LoginHistory
from app.infrastructure.models.system import AuditTrail
from app.domain.enums.user import ApprovalStatus
from app.application.services.audit import AuditService
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

class AdminService:
    def __init__(self, db: Session, user_repo: SQLAlchemyUserRepository, audit_service: AuditService):
        self.db = db
        self.user_repo = user_repo
        self.audit_service = audit_service

    async def approve_user(self, admin_id: UUID, user_id: UUID, ip_address: str) -> bool:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False
        
        self.user_repo.update(user_id, {
            "approval_status": ApprovalStatus.APPROVED,
            "approved_by": admin_id,
            "approved_at": datetime.utcnow()
        })
        self.audit_service.log_action(admin_id, ip_address, "admin", "USER_APPROVED", user_id, {"target_user_id": str(user_id)})
        return True

    async def reject_user(self, admin_id: UUID, user_id: UUID, reason: str, ip_address: str) -> bool:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False
        
        self.user_repo.update(user_id, {
            "approval_status": ApprovalStatus.REJECTED,
            "rejected_reason": reason
        })
        self.audit_service.log_action(admin_id, ip_address, "admin", "USER_REJECTED", user_id, {"target_user_id": str(user_id), "reason": reason})
        return True

    # ... (existing methods)

    async def get_dashboard_stats(self) -> Dict[str, Any]:
        return {
            "total_users": self.db.query(User).count(),
            "active_users": self.db.query(User).filter(User.is_active == True).count(),
            "disabled_users": self.db.query(User).filter(User.is_active == False).count(),
            "role_distribution": [{"role": r[0], "count": r[1]} for r in self.db.query(Role.name, func.count(User.id)).join(User).group_by(Role.name).all()],
            "audit_events_today": self.db.query(AuditTrail).filter(AuditTrail.timestamp >= datetime.utcnow() - timedelta(days=1)).count(),
        }

    async def list_users(self) -> List[UserResponse]:
        users = self.user_repo.list()
        return [UserResponse.model_validate(u) for u in users]

    async def update_user(self, user_id: UUID, user_update: UserUpdate, admin_id: UUID, ip_address: str) -> Optional[UserResponse]:
        user = self.user_repo.update(user_id, user_update.model_dump(exclude_unset=True))
        if user:
            self.audit_service.log_action(admin_id, ip_address, "admin", "USER_UPDATE", {"id": str(user_id)}, user_update.model_dump())
        return UserResponse.model_validate(user) if user else None
