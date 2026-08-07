from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from app.infrastructure.models.hunting import ThreatHuntingQuery

class ThreatHuntingRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: UUID) -> Optional[ThreatHuntingQuery]:
        pass

    @abstractmethod
    def create(self, query_in: dict) -> ThreatHuntingQuery:
        pass

    @abstractmethod
    def list(self) -> List[ThreatHuntingQuery]:
        pass

    @abstractmethod
    def delete(self, id: UUID) -> None:
        pass
