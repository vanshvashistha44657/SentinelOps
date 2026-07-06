from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from app.infrastructure.models.alerts import Alert

class AlertRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[Alert]:
        pass

    @abstractmethod
    async def create(self, alert_in: dict) -> Alert:
        pass

    @abstractmethod
    async def update(self, alert_id: UUID, alert_update: dict) -> Optional[Alert]:
        pass
