from fastapi import APIRouter, Depends, status, Request, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List
from app.api.dependencies import get_db
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.rbac import RBAC
from app.infrastructure.models.iam import User
from app.application.services.case import CaseService
from app.application.services.case_items import CaseItemService
from app.application.services.audit import AuditService
from app.infrastructure.repositories.cases import SQLAlchemyCaseRepository
from app.infrastructure.repositories.audit import SQLAlchemyAuditRepository
from app.infrastructure.schemas.cases import CaseCreate, CaseUpdate, CaseResponse, PaginatedCaseResponse, CaseFilterParams, CasePriority, CaseStatus
from app.infrastructure.schemas.case_items import NoteCreate, NoteResponse, EvidenceCreate, EvidenceResponse
from app.core.exceptions import EntityNotFoundException

router = APIRouter(prefix="/cases", tags=["Cases"])

def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    repo = SQLAlchemyAuditRepository(db)
    return AuditService(repo)

def get_case_service(db: Session = Depends(get_db), audit: AuditService = Depends(get_audit_service)) -> CaseService:
    repo = SQLAlchemyCaseRepository(db)
    return CaseService(repo, audit)

def get_case_item_service(db: Session = Depends(get_db)) -> CaseItemService:
    return CaseItemService(db)

@router.get("/", response_model=PaginatedCaseResponse, dependencies=[Depends(RBAC("cases:view"))])
async def list_cases(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    priority: Optional[CasePriority] = None,
    status: Optional[CaseStatus] = None,
    case_service: CaseService = Depends(get_case_service)
):
    filters = CaseFilterParams(priority=priority, status=status)
    return await case_service.list_cases(page=page, size=size, filters=filters)

@router.post("/", response_model=CaseResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RBAC("cases:create"))])
async def create_case(
    case_in: CaseCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    case_service: CaseService = Depends(get_case_service),
    audit: AuditService = Depends(get_audit_service)
):
    case = await case_service.create_case(case_in, current_user.id, request.client.host)
    audit.log_action(current_user.id, request.client.host, "cases", "CASE_CREATE", None, {"id": str(case.id)})
    return case

@router.get("/{case_id}", response_model=CaseResponse, dependencies=[Depends(RBAC("cases:view"))])
async def get_case(
    case_id: UUID,
    case_service: CaseService = Depends(get_case_service)
):
    case = await case_service.get_case(case_id)
    if not case:
        raise EntityNotFoundException("Case", str(case_id))
    return case

@router.patch("/{case_id}", response_model=CaseResponse, dependencies=[Depends(RBAC("cases:edit"))])
async def update_case(
    case_id: UUID,
    case_update: CaseUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    case_service: CaseService = Depends(get_case_service),
    audit: AuditService = Depends(get_audit_service)
):
    case = await case_service.update_case(case_id, case_update, current_user.id, request.client.host)
    if not case:
        raise EntityNotFoundException("Case", str(case_id))
    audit.log_action(current_user.id, request.client.host, "cases", "CASE_UPDATE", {"id": str(case_id)}, case_update.model_dump())
    return case
