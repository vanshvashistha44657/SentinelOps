from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from app.infrastructure.models.incidents import Incident

class IncidentRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: UUID) -> Optional[Incident]:
        pass

    @abstractmethod
    def list(self) -> List[Incident]:
        pass

    @abstractmethod
    def create(self, incident_in: dict) -> Incident:
        pass

    @abstractmethod
    def update(self, incident_id: UUID, incident_update: dict) -> Optional[Incident]:
        pass
