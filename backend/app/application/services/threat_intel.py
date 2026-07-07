from typing import Optional, List
from uuid import UUID
from app.domain.repositories.threat_intel import ThreatIntelligenceRepository
from app.infrastructure.schemas.threat_intel import ThreatIntelligenceCreate, ThreatIntelligenceUpdate, ThreatIntelligenceResponse
from app.infrastructure.models.threat_intel import ThreatIntelligence

class ThreatIntelligenceService:
    def __init__(self, intel_repo: ThreatIntelligenceRepository):
        self.intel_repo = intel_repo

    async def get_threat_intel(self, intel_id: UUID) -> Optional[ThreatIntelligenceResponse]:
        intel = self.intel_repo.get_by_id(intel_id)
        if not intel:
            return None
        return ThreatIntelligenceResponse.model_validate(intel)

    async def create_threat_intel(self, intel_in: ThreatIntelligenceCreate) -> ThreatIntelligenceResponse:
        intel = self.intel_repo.create(intel_in.model_dump())
        return ThreatIntelligenceResponse.model_validate(intel)

    async def update_threat_intel(self, intel_id: UUID, intel_update: ThreatIntelligenceUpdate) -> Optional[ThreatIntelligenceResponse]:
        intel = self.intel_repo.update(intel_id, intel_update.model_dump(exclude_unset=True))
        if not intel:
            return None
        return ThreatIntelligenceResponse.model_validate(intel)

    async def list_threat_intel(self) -> List[ThreatIntelligenceResponse]:
        intel_list = self.intel_repo.list()
        return [ThreatIntelligenceResponse.model_validate(intel) for intel in intel_list]
