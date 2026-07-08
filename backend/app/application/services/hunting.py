from typing import Optional, List
from uuid import UUID
from app.domain.repositories.hunting import ThreatHuntingRepository
from app.infrastructure.schemas.hunting import ThreatHuntingQueryCreate, ThreatHuntingQueryResponse
from app.infrastructure.models.hunting import ThreatHuntingQuery
from app.application.services.audit import AuditService

class ThreatHuntingService:
    def __init__(self, hunting_repo: ThreatHuntingRepository, audit_service: AuditService):
        self.hunting_repo = hunting_repo
        self.audit_service = audit_service

    async def get_query(self, query_id: UUID) -> Optional[ThreatHuntingQueryResponse]:
        query = self.hunting_repo.get_by_id(query_id)
        if not query:
            return None
        return ThreatHuntingQueryResponse.model_validate(query)

    async def create_query(self, query_in: ThreatHuntingQueryCreate, creator_id: UUID, user_id: UUID, ip_address: str) -> ThreatHuntingQueryResponse:
        data = query_in.model_dump()
        data["creator_id"] = creator_id
        query = self.hunting_repo.create(data)
        self.audit_service.log_action(user_id, ip_address, "threat_hunting", "HUNTING_QUERY_CREATE", None, {"query_id": str(query.id)})
        return ThreatHuntingQueryResponse.model_validate(query)

    async def list_queries(self) -> List[ThreatHuntingQueryResponse]:
        queries = self.hunting_repo.list()
        return [ThreatHuntingQueryResponse.model_validate(q) for q in queries]
