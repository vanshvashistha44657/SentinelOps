from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.orm import Session
from uuid import UUID
from app.api.dependencies import get_db
from app.api.dependencies.auth import get_current_user
from app.infrastructure.models.iam import User
from app.application.services.case import CaseService
from app.application.services.audit import AuditService
from app.infrastructure.repositories.cases import SQLAlchemyCaseRepository
from app.infrastructure.repositories.audit import SQLAlchemyAuditRepository
from app.infrastructure.schemas.cases import CaseCreate, CaseUpdate, CaseResponse

router = APIRouter(prefix="/cases", tags=["Cases"])

def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    repo = SQLAlchemyAuditRepository(db)
    return AuditService(repo)

def get_case_service(db: Session = Depends(get_db), audit: AuditService = Depends(get_audit_service)) -> CaseService:
    repo = SQLAlchemyCaseRepository(db)
    return CaseService(repo, audit)

@router.post("/", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    case_in: CaseCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    case_service: CaseService = Depends(get_case_service)
):
    return await case_service.create_case(case_in, current_user.id, request.client.host)

@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: UUID,
    case_service: CaseService = Depends(get_case_service)
):
    case = await case_service.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.patch("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: UUID,
    case_update: CaseUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    case_service: CaseService = Depends(get_case_service)
):
    case = await case_service.update_case(case_id, case_update, current_user.id, request.client.host)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case
