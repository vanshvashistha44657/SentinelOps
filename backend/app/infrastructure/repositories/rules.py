from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.domain.repositories.rules import DetectionRuleRepository
from app.infrastructure.models.alerts import DetectionRule

class SQLAlchemyDetectionRuleRepository(DetectionRuleRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: UUID) -> Optional[DetectionRule]:
        return self.db.query(DetectionRule).filter(DetectionRule.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[DetectionRule]:
        return self.db.query(DetectionRule).offset(skip).limit(limit).all()

    def create(self, rule_in: dict) -> DetectionRule:
        rule = DetectionRule(**rule_in)
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def update(self, rule_id: UUID, rule_update: dict) -> Optional[DetectionRule]:
        rule = self.get_by_id(rule_id)
        if rule:
            for key, value in rule_update.items():
                setattr(rule, key, value)
            self.db.commit()
            self.db.refresh(rule)
        return rule
