from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from app.infrastructure.models.incidents import Incident

class IncidentRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[Incident]:
        pass

    @abstractmethod
    async def create(self, incident_in: dict) -> Incident:
        pass

    @abstractmethod
    async def update(self, incident_id: UUID, incident_update: dict) -> Optional[Incident]:
        pass
