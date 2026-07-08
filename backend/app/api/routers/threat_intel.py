from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.orm import Session
from uuid import UUID
from app.api.dependencies import get_db
from app.api.dependencies.auth import get_current_user
from app.infrastructure.models.iam import User
from app.application.services.threat_intel import ThreatIntelligenceService
from app.application.services.audit import AuditService
from app.infrastructure.repositories.threat_intel import SQLAlchemyThreatIntelligenceRepository
from app.infrastructure.repositories.audit import SQLAlchemyAuditRepository
from app.infrastructure.schemas.threat_intel import ThreatIntelligenceCreate, ThreatIntelligenceUpdate, ThreatIntelligenceResponse
from typing import List

router = APIRouter(prefix="/threat-intel", tags=["Threat Intel"])

def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    repo = SQLAlchemyAuditRepository(db)
    return AuditService(repo)

def get_threat_intel_service(db: Session = Depends(get_db), audit: AuditService = Depends(get_audit_service)) -> ThreatIntelligenceService:
    repo = SQLAlchemyThreatIntelligenceRepository(db)
    return ThreatIntelligenceService(repo, audit)

@router.post("/", response_model=ThreatIntelligenceResponse, status_code=status.HTTP_201_CREATED)
async def create_threat_intel(
    intel_in: ThreatIntelligenceCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    intel_service: ThreatIntelligenceService = Depends(get_threat_intel_service)
):
    return await intel_service.create_threat_intel(intel_in, current_user.id, request.client.host)

@router.get("/{intel_id}", response_model=ThreatIntelligenceResponse)
async def get_threat_intel(
    intel_id: UUID,
    intel_service: ThreatIntelligenceService = Depends(get_threat_intel_service)
):
    intel = await intel_service.get_threat_intel(intel_id)
    if not intel:
        raise HTTPException(status_code=404, detail="Threat Intelligence not found")
    return intel

@router.patch("/{intel_id}", response_model=ThreatIntelligenceResponse)
async def update_threat_intel(
    intel_id: UUID,
    intel_update: ThreatIntelligenceUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    intel_service: ThreatIntelligenceService = Depends(get_threat_intel_service)
):
    intel = await intel_service.update_threat_intel(intel_id, intel_update, current_user.id, request.client.host)
    if not intel:
        raise HTTPException(status_code=404, detail="Threat Intelligence not found")
    return intel

@router.get("/", response_model=List[ThreatIntelligenceResponse])
async def list_threat_intel(
    intel_service: ThreatIntelligenceService = Depends(get_threat_intel_service)
):
    return await intel_service.list_threat_intel()

