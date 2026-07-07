from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from app.infrastructure.models.alerts import Alert

class AlertRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: UUID) -> Optional[Alert]:
        pass

    @abstractmethod
    def get_unassigned_alerts(self) -> List[Alert]:
        pass

    @abstractmethod
    def create(self, alert_in: dict) -> Alert:
        pass

    @abstractmethod
    def update(self, alert_id: UUID, alert_update: dict) -> Optional[Alert]:
        pass

    @abstractmethod
    def link_alert_to_incident(self, alert_id: UUID, incident_id: UUID) -> None:
        pass
