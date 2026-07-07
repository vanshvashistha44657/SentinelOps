from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.api.dependencies import get_db
from app.application.services.threat_intel import ThreatIntelligenceService
from app.infrastructure.repositories.threat_intel import SQLAlchemyThreatIntelligenceRepository
from app.infrastructure.schemas.threat_intel import ThreatIntelligenceCreate, ThreatIntelligenceUpdate, ThreatIntelligenceResponse

router = APIRouter(prefix="/threat-intel", tags=["Threat Intelligence"])

def get_threat_intel_service(db: Session = Depends(get_db)) -> ThreatIntelligenceService:
    repo = SQLAlchemyThreatIntelligenceRepository(db)
    return ThreatIntelligenceService(repo)

@router.post("/", response_model=ThreatIntelligenceResponse, status_code=status.HTTP_201_CREATED)
async def create_threat_intel(
    intel_in: ThreatIntelligenceCreate,
    intel_service: ThreatIntelligenceService = Depends(get_threat_intel_service)
):
    return await intel_service.create_threat_intel(intel_in)

@router.get("/{intel_id}", response_model=ThreatIntelligenceResponse)
async def get_threat_intel(
    intel_id: UUID,
    intel_service: ThreatIntelligenceService = Depends(get_threat_intel_service)
):
    intel = await intel_service.get_threat_intel(intel_id)
    if not intel:
        raise HTTPException(status_code=404, detail="Threat intelligence record not found")
    return intel

@router.patch("/{intel_id}", response_model=ThreatIntelligenceResponse)
async def update_threat_intel(
    intel_id: UUID,
    intel_update: ThreatIntelligenceUpdate,
    intel_service: ThreatIntelligenceService = Depends(get_threat_intel_service)
):
    intel = await intel_service.update_threat_intel(intel_id, intel_update)
    if not intel:
        raise HTTPException(status_code=404, detail="Threat intelligence record not found")
    return intel

@router.get("/", response_model=List[ThreatIntelligenceResponse])
async def list_threat_intel(
    intel_service: ThreatIntelligenceService = Depends(get_threat_intel_service)
):
    return await intel_service.list_threat_intel()
