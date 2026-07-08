from fastapi import APIRouter, Depends, status, Request, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.api.dependencies import get_db
from app.api.dependencies.auth import get_current_user
from app.infrastructure.models.iam import User
from app.application.services.assets import AssetService
from app.application.services.audit import AuditService
from app.infrastructure.repositories.assets import SQLAlchemyAssetRepository
from app.infrastructure.repositories.audit import SQLAlchemyAuditRepository
from app.infrastructure.schemas.assets import AssetCreate, AssetResponse
from typing import List
from app.core.exceptions import EntityNotFoundException

router = APIRouter(prefix="/assets", tags=["Assets"])

def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    repo = SQLAlchemyAuditRepository(db)
    return AuditService(repo)

def get_asset_service(db: Session = Depends(get_db), audit: AuditService = Depends(get_audit_service)) -> AssetService:
    repo = SQLAlchemyAssetRepository(db)
    return AssetService(repo, audit)

@router.post("/", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(
    asset_in: AssetCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    asset_service: AssetService = Depends(get_asset_service)
):
    return await asset_service.create_asset(asset_in, current_user.id, request.client.host)

@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: UUID,
    asset_service: AssetService = Depends(get_asset_service)
):
    asset = await asset_service.get_asset(asset_id)
    if not asset:
        raise EntityNotFoundException("Asset", str(asset_id))
    return asset

@router.get("/", response_model=List[AssetResponse])
async def list_assets(
    asset_service: AssetService = Depends(get_asset_service)
):
    return await asset_service.list_assets()
