from typing import Optional, List
from uuid import UUID
from app.domain.repositories.hunting import ThreatHuntingRepository
from app.infrastructure.schemas.hunting import ThreatHuntingQueryCreate, ThreatHuntingQueryResponse
from app.infrastructure.models.hunting import ThreatHuntingQuery

class ThreatHuntingService:
    def __init__(self, hunting_repo: ThreatHuntingRepository):
        self.hunting_repo = hunting_repo

    async def get_query(self, query_id: UUID) -> Optional[ThreatHuntingQueryResponse]:
        query = self.hunting_repo.get_by_id(query_id)
        if not query:
            return None
        return ThreatHuntingQueryResponse.model_validate(query)

    async def create_query(self, query_in: ThreatHuntingQueryCreate, creator_id: UUID) -> ThreatHuntingQueryResponse:
        data = query_in.model_dump()
        data["creator_id"] = creator_id
        query = self.hunting_repo.create(data)
        return ThreatHuntingQueryResponse.model_validate(query)

    async def list_queries(self) -> List[ThreatHuntingQueryResponse]:
        queries = self.hunting_repo.list()
        return [ThreatHuntingQueryResponse.model_validate(q) for q in queries]
