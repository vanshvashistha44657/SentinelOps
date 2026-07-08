from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.orm import Session
from uuid import UUID
from app.api.dependencies import get_db
from app.api.dependencies.auth import get_current_user
from app.infrastructure.models.iam import User
from app.application.services.ioc import IOCService
from app.application.services.audit import AuditService
from app.infrastructure.repositories.iocs import SQLAlchemyIOCRepository
from app.infrastructure.repositories.audit import SQLAlchemyAuditRepository
from app.infrastructure.schemas.iocs import IOCCreate, IOCUpdate, IOCResponse
from typing import List

router = APIRouter(prefix="/iocs", tags=["IOCs"])

def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    repo = SQLAlchemyAuditRepository(db)
    return AuditService(repo)

def get_ioc_service(db: Session = Depends(get_db), audit: AuditService = Depends(get_audit_service)) -> IOCService:
    repo = SQLAlchemyIOCRepository(db)
    return IOCService(repo, audit)

@router.post("/", response_model=IOCResponse, status_code=status.HTTP_201_CREATED)
async def create_ioc(
    ioc_in: IOCCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    ioc_service: IOCService = Depends(get_ioc_service)
):
    return await ioc_service.create_ioc(ioc_in, current_user.id, request.client.host)

@router.get("/{ioc_id}", response_model=IOCResponse)
async def get_ioc(
    ioc_id: UUID,
    ioc_service: IOCService = Depends(get_ioc_service)
):
    ioc = await ioc_service.get_ioc(ioc_id)
    if not ioc:
        raise HTTPException(status_code=404, detail="IOC not found")
    return ioc

@router.patch("/{ioc_id}", response_model=IOCResponse)
async def update_ioc(
    ioc_id: UUID,
    ioc_update: IOCUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    ioc_service: IOCService = Depends(get_ioc_service)
):
    ioc = await ioc_service.update_ioc(ioc_id, ioc_update, current_user.id, request.client.host)
    if not ioc:
        raise HTTPException(status_code=404, detail="IOC not found")
    return ioc

@router.get("/", response_model=List[IOCResponse])
async def list_iocs(
    ioc_service: IOCService = Depends(get_ioc_service)
):
    return await ioc_service.list_iocs()

