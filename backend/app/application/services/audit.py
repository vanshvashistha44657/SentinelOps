from typing import Optional, Dict
from uuid import UUID
from app.domain.repositories.audit import AuditRepository
from app.infrastructure.models.system import AuditTrail

class AuditService:
    def __init__(self, audit_repo: AuditRepository):
        self.audit_repo = audit_repo

    def log_action(
        self,
        user_id: Optional[UUID],
        ip_address: str,
        resource: str,
        action: str,
        prev_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None
    ) -> AuditTrail:
        audit_data = {
            "user_id": user_id,
            "ip_address": ip_address,
            "resource": resource,
            "action": action,
            "prev_values": prev_values,
            "new_values": new_values
        }
        return self.audit_repo.create(audit_data)
