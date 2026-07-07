from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from app.domain.repositories.audit import AuditRepository
from app.infrastructure.models.system import AuditTrail

class SQLAlchemyAuditRepository(AuditRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, audit_in: dict) -> AuditTrail:
        audit = AuditTrail(**audit_in)
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(audit)
        return audit

    def list_by_resource(self, resource: str) -> List[AuditTrail]:
        return self.db.query(AuditTrail).filter(AuditTrail.resource == resource).all()

    def list_by_user(self, user_id: UUID) -> List[AuditTrail]:
        return self.db.query(AuditTrail).filter(AuditTrail.user_id == user_id).all()
