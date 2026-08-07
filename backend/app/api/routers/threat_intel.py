from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.api.dependencies import get_db
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.rbac import RBAC
from app.infrastructure.models.iam import User
from app.application.services.threat_intel import ThreatIntelService
from app.application.services.audit import AuditService
from app.infrastructure.repositories.audit import SQLAlchemyAuditRepository
from app.infrastructure.schemas.threat_intel import ThreatIndicatorCreate, ThreatIndicatorUpdate, ThreatIndicatorResponse, IOCMatchResponse

router = APIRouter(prefix="/threat-intelligence", tags=["Threat Intelligence"])

def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    repo = SQLAlchemyAuditRepository(db)
    return AuditService(repo)

def get_threat_intel_service(db: Session = Depends(get_db), audit: AuditService = Depends(get_audit_service)) -> ThreatIntelService:
    return ThreatIntelService(db, audit)

@router.get("/iocs", response_model=List[ThreatIndicatorResponse], dependencies=[Depends(RBAC("threat_intel:view"))])
def list_iocs(threat_intel_service: ThreatIntelService = Depends(get_threat_intel_service)):
    return threat_intel_service.list_indicators()

@router.post("/iocs", response_model=ThreatIndicatorResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RBAC("threat_intel:create"))])
def create_ioc(
    ioc_in: ThreatIndicatorCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    threat_intel_service: ThreatIntelService = Depends(get_threat_intel_service)
):
    return threat_intel_service.create_indicator(ioc_in, current_user.id, request.client.host)

@router.patch("/iocs/{ioc_id}", response_model=ThreatIndicatorResponse, dependencies=[Depends(RBAC("threat_intel:edit"))])
def update_ioc(
    ioc_id: UUID,
    ioc_update: ThreatIndicatorUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    threat_intel_service: ThreatIntelService = Depends(get_threat_intel_service)
):
    ioc = threat_intel_service.update_indicator(ioc_id, ioc_update, current_user.id, request.client.host)
    if not ioc:
        raise HTTPException(status_code=404, detail="IOC not found")
    return ioc

@router.delete("/iocs/{ioc_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(RBAC("threat_intel:delete"))])
def delete_ioc(
    ioc_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    threat_intel_service: ThreatIntelService = Depends(get_threat_intel_service)
):
    if not threat_intel_service.delete_indicator(ioc_id, current_user.id, request.client.host):
        raise HTTPException(status_code=404, detail="IOC not found")
    return None

@router.get("/matches", response_model=List[IOCMatchResponse], dependencies=[Depends(RBAC("threat_intel:view"))])
def get_matches(threat_intel_service: ThreatIntelService = Depends(get_threat_intel_service)):
    return threat_intel_service.get_matches()
