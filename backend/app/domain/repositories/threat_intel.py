from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from app.infrastructure.models.threat_intel import ThreatIntelligence

class ThreatIntelligenceRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: UUID) -> Optional[ThreatIntelligence]:
        pass

    @abstractmethod
    def create(self, intel_in: dict) -> ThreatIntelligence:
        pass

    @abstractmethod
    def update(self, intel_id: UUID, intel_update: dict) -> Optional[ThreatIntelligence]:
        pass

    @abstractmethod
    def list(self) -> List[ThreatIntelligence]:
        pass
