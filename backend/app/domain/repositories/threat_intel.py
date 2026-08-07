from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from app.infrastructure.models.threat_intel import IOCRecord, IOCMatch

class ThreatIntelligenceRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: UUID) -> Optional[IOCRecord]:
        pass

    @abstractmethod
    def create(self, intel_in: dict) -> IOCRecord:
        pass

    @abstractmethod
    def update(self, intel_id: UUID, intel_update: dict) -> Optional[IOCRecord]:
        pass

    @abstractmethod
    def list(self) -> List[IOCRecord]:
        pass
