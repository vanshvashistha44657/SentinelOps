from typing import List, Optional
from uuid import UUID
from app.domain.repositories.rules import DetectionRuleRepository
from app.infrastructure.schemas.rules import DetectionRuleCreate, DetectionRuleResponse
from app.infrastructure.models.alerts import DetectionRule, Alert
from sqlalchemy.orm import Session

class DetectionService:
    def __init__(self, db: Session, rule_repo: DetectionRuleRepository):
        self.db = db
        self.rule_repo = rule_repo

    def run_detection(self, event: dict):
        rules = self.rule_repo.get_all()
        for rule in rules:
            # Simple simulation of rule matching for now
            # In a real system, this would evaluate the query_logic against the event
            if rule.is_active and "severity" in event and event["severity"] == "CRITICAL":
                # Create alert
                alert = Alert(
                    title=f"Rule Match: {rule.name}",
                    severity="CRITICAL",
                    confidence_score=rule.confidence_score,
                    raw_event=event,
                    detection_rule_id=rule.id
                )
                self.db.add(alert)
                self.db.commit()

    def create_rule(self, rule_in: DetectionRuleCreate) -> DetectionRuleResponse:
        rule_data = rule_in.model_dump()
        rule = self.rule_repo.create(rule_data)
        return DetectionRuleResponse.model_validate(rule)

    def get_all_rules(self) -> List[DetectionRuleResponse]:
        rules = self.rule_repo.get_all()
        return [DetectionRuleResponse.model_validate(rule) for rule in rules]

    def get_rule(self, rule_id: UUID) -> Optional[DetectionRuleResponse]:
        rule = self.rule_repo.get_by_id(rule_id)
        if not rule:
            return None
        return DetectionRuleResponse.model_validate(rule)
