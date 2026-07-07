from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.api.dependencies import get_db
from app.application.services.ioc import IOCService
from app.infrastructure.repositories.iocs import SQLAlchemyIOCRepository
from app.infrastructure.schemas.iocs import IOCCreate, IOCUpdate, IOCResponse

router = APIRouter(prefix="/iocs", tags=["IOCs"])

def get_ioc_service(db: Session = Depends(get_db)) -> IOCService:
    repo = SQLAlchemyIOCRepository(db)
    return IOCService(repo)

@router.post("/", response_model=IOCResponse, status_code=status.HTTP_201_CREATED)
async def create_ioc(
    ioc_in: IOCCreate,
    ioc_service: IOCService = Depends(get_ioc_service)
):
    return await ioc_service.create_ioc(ioc_in)

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
    ioc_service: IOCService = Depends(get_ioc_service)
):
    ioc = await ioc_service.update_ioc(ioc_id, ioc_update)
    if not ioc:
        raise HTTPException(status_code=404, detail="IOC not found")
    return ioc

@router.get("/", response_model=List[IOCResponse])
async def list_iocs(
    ioc_service: IOCService = Depends(get_ioc_service)
):
    return await ioc_service.list_iocs()
