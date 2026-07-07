from typing import Optional
from uuid import UUID
from app.domain.repositories.cases import CaseRepository
from app.infrastructure.schemas.cases import CaseCreate, CaseUpdate, CaseResponse
from app.infrastructure.models.incidents import Case

class CaseService:
    def __init__(self, case_repo: CaseRepository):
        self.case_repo = case_repo

    async def get_case(self, case_id: UUID) -> Optional[CaseResponse]:
        case = self.case_repo.get_by_id(case_id)
        if not case:
            return None
        return CaseResponse.model_validate(case)

    async def create_case(self, case_in: CaseCreate) -> CaseResponse:
        case = self.case_repo.create(case_in.model_dump())
        return CaseResponse.model_validate(case)

    async def update_case(self, case_id: UUID, case_update: CaseUpdate) -> Optional[CaseResponse]:
        case = self.case_repo.update(case_id, case_update.model_dump(exclude_unset=True))
        if not case:
            return None
        return CaseResponse.model_validate(case)
