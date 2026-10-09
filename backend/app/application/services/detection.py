"""Detection-rule management and event evaluation.

Network telemetry has its own service.  Keeping the generic detection service
here preserves the original ingestion and rule-management contracts while
allowing network detections to share the canonical ``alerts`` table.
"""

import json
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.repositories.rules import DetectionRuleRepository
from app.infrastructure.models.alerts import Alert
from app.infrastructure.schemas.rules import DetectionRuleCreate, DetectionRuleResponse


class DetectionService:
    def __init__(self, db: Session, rule_repo: DetectionRuleRepository):
        self.db = db
        self.rule_repo = rule_repo

    @staticmethod
    def _matches(rule_logic: str, event: Dict[str, Any]) -> bool:
        """Evaluate the deliberately small, auditable rule language.

        Rules may be JSON objects (exact field matches) or a conservative
        ``field=value AND field2=value`` expression.  Unknown syntax does not
        match; it never produces an alert by accident.
        """
        if not rule_logic:
            return False
        try:
            parsed = json.loads(rule_logic)
        except (TypeError, json.JSONDecodeError):
            parsed = None
        if isinstance(parsed, dict):
            return all(str(event.get(key)) == str(value) for key, value in parsed.items())

        clauses = [part.strip() for part in rule_logic.split(" AND ") if part.strip()]
        if not clauses:
            return False
        for clause in clauses:
            if "=" not in clause:
                return False
            key, value = (piece.strip() for piece in clause.split("=", 1))
            if str(event.get(key)) != value.strip("\"'"):
                return False
        return True

    def run_detection(self, event: dict) -> List[Alert]:
        created: List[Alert] = []
        for rule in self.rule_repo.get_all():
            if not rule.is_active or not self._matches(rule.query_logic, event):
                continue

            event_key = f"rule:{rule.id}:{event.get('event_id') or event.get('timestamp') or str(event)}"
            duplicate = next(
                (
                    alert
                    for alert in self.db.query(Alert).filter(Alert.detection_rule_id == rule.id).all()
                    if isinstance(alert.raw_event, dict) and alert.raw_event.get("_detection_key") == event_key
                ),
                None,
            )
            if duplicate:
                continue
            alert = Alert(
                title=f"Rule Match: {rule.name}",
                severity=rule.severity,
                confidence_score=rule.confidence_score,
                raw_event={**event, "_detection_key": event_key, "rule_version": str(rule.updated_at)},
                detection_rule_id=rule.id,
            )
            self.db.add(alert)
            created.append(alert)
        if created:
            self.db.commit()
            for alert in created:
                self.db.refresh(alert)
        return created

    def create_rule(self, rule_in: DetectionRuleCreate) -> DetectionRuleResponse:
        rule = self.rule_repo.create(rule_in.model_dump())
        return DetectionRuleResponse.model_validate(rule)

    def get_all_rules(self) -> List[DetectionRuleResponse]:
        return [DetectionRuleResponse.model_validate(rule) for rule in self.rule_repo.get_all()]

    def get_rule(self, rule_id: UUID) -> Optional[DetectionRuleResponse]:
        rule = self.rule_repo.get_by_id(rule_id)
        return DetectionRuleResponse.model_validate(rule) if rule else None
