from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from app.infrastructure.models.alerts import DetectionRule

class DetectionRuleRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: UUID) -> Optional[DetectionRule]:
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[DetectionRule]:
        pass

    @abstractmethod
    def create(self, rule_in: dict) -> DetectionRule:
        pass

    @abstractmethod
    def update(self, rule_id: UUID, rule_update: dict) -> Optional[DetectionRule]:
        pass
