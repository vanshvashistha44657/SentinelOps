from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from app.infrastructure.models.system import AuditTrail

class AuditRepository(ABC):
    @abstractmethod
    def create(self, audit_in: dict) -> AuditTrail:
        pass

    @abstractmethod
    def list_by_resource(self, resource: str) -> List[AuditTrail]:
        pass

    @abstractmethod
    def list_by_user(self, user_id: UUID) -> List[AuditTrail]:
        pass
