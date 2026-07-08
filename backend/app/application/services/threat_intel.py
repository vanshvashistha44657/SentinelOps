from typing import Optional, List
from uuid import UUID
from app.domain.repositories.threat_intel import ThreatIntelligenceRepository
from app.infrastructure.schemas.threat_intel import ThreatIntelligenceCreate, ThreatIntelligenceUpdate, ThreatIntelligenceResponse
from app.infrastructure.models.threat_intel import ThreatIntelligence
from app.application.services.audit import AuditService

class ThreatIntelligenceService:
    def __init__(self, intel_repo: ThreatIntelligenceRepository, audit_service: AuditService):
        self.intel_repo = intel_repo
        self.audit_service = audit_service

    async def get_threat_intel(self, intel_id: UUID) -> Optional[ThreatIntelligenceResponse]:
        intel = self.intel_repo.get_by_id(intel_id)
        if not intel:
            return None
        return ThreatIntelligenceResponse.model_validate(intel)

    async def create_threat_intel(self, intel_in: ThreatIntelligenceCreate, user_id: UUID, ip_address: str) -> ThreatIntelligenceResponse:
        intel = self.intel_repo.create(intel_in.model_dump())
        self.audit_service.log_action(user_id, ip_address, "threat_intel", "THREAT_INTEL_CREATE", None, {"intel_id": str(intel.id)})
        return ThreatIntelligenceResponse.model_validate(intel)

    async def update_threat_intel(self, intel_id: UUID, intel_update: ThreatIntelligenceUpdate, user_id: UUID, ip_address: str) -> Optional[ThreatIntelligenceResponse]:
        old_intel = self.intel_repo.get_by_id(intel_id)
        if not old_intel:
            return None
        intel = self.intel_repo.update(intel_id, intel_update.model_dump(exclude_unset=True))
        if not intel:
            return None
        self.audit_service.log_action(user_id, ip_address, "threat_intel", "THREAT_INTEL_UPDATE", {"value": old_intel.value}, {"value": intel.value})
        return ThreatIntelligenceResponse.model_validate(intel)

    async def list_threat_intel(self) -> List[ThreatIntelligenceResponse]:
        intel_list = self.intel_repo.list()
        return [ThreatIntelligenceResponse.model_validate(intel) for intel in intel_list]
