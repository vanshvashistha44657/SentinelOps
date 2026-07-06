from typing import List, Optional
from uuid import UUID
from app.domain.repositories.rules import DetectionRuleRepository
from app.infrastructure.schemas.rules import DetectionRuleCreate, DetectionRuleResponse
from app.infrastructure.models.alerts import DetectionRule

class DetectionService:
    def __init__(self, rule_repo: DetectionRuleRepository):
        self.rule_repo = rule_repo

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
