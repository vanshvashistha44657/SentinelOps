from typing import Optional, List
from uuid import UUID
from app.domain.repositories.cases import CaseRepository
from app.infrastructure.schemas.cases import CaseCreate, CaseUpdate, CaseResponse, CaseFilterParams, PaginatedCaseResponse
from app.infrastructure.models.incidents import Case
from app.application.services.audit import AuditService

class CaseService:
    def __init__(self, case_repo: CaseRepository, audit_service: AuditService):
        self.case_repo = case_repo
        self.audit_service = audit_service

    async def list_cases(
        self, 
        page: int = 1, 
        size: int = 20, 
        filters: Optional[CaseFilterParams] = None
    ) -> PaginatedCaseResponse:
        cases, total = self.case_repo.list_paginated(page, size, filters)
        return PaginatedCaseResponse(
            items=[CaseResponse.model_validate(c) for c in cases],
            total=total,
            page=page,
            size=size
        )

    async def get_case(self, case_id: UUID) -> Optional[CaseResponse]:
        case = self.case_repo.get_by_id(case_id)
        if not case:
            return None
        return CaseResponse.model_validate(case)

    async def create_case(self, case_in: CaseCreate, user_id: UUID, ip_address: str) -> CaseResponse:
        case = self.case_repo.create(case_in.model_dump())
        self.audit_service.log_action(user_id, ip_address, "cases", "CASE_CREATE", None, {"case_id": str(case.id)})
        return CaseResponse.model_validate(case)

    async def update_case(self, case_id: UUID, case_update: CaseUpdate, user_id: UUID, ip_address: str) -> Optional[CaseResponse]:
        old_case = self.case_repo.get_by_id(case_id)
        if not old_case:
            return None
        case = self.case_repo.update(case_id, case_update.model_dump(exclude_unset=True))
        if not case:
            return None
        self.audit_service.log_action(user_id, ip_address, "cases", "CASE_UPDATE", {"status": old_case.status}, {"status": case.status})
        return CaseResponse.model_validate(case)
