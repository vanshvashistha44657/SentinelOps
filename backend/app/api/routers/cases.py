from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.api.dependencies import get_db
from app.application.services.case import CaseService
from app.infrastructure.repositories.cases import SQLAlchemyCaseRepository
from app.infrastructure.schemas.cases import CaseCreate, CaseUpdate, CaseResponse

router = APIRouter(prefix="/cases", tags=["Cases"])

def get_case_service(db: Session = Depends(get_db)) -> CaseService:
    repo = SQLAlchemyCaseRepository(db)
    return CaseService(repo)

@router.post("/", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    case_in: CaseCreate,
    case_service: CaseService = Depends(get_case_service)
):
    return await case_service.create_case(case_in)

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
    case_service: CaseService = Depends(get_case_service)
):
    case = await case_service.update_case(case_id, case_update)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case
