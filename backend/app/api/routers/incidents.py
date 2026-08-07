from fastapi import APIRouter, Depends, status, HTTPException, Request, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from app.api.dependencies import get_db
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.rbac import RBAC
from app.infrastructure.models.iam import User
from app.application.services.incident import IncidentService
from app.application.services.audit import AuditService
from app.infrastructure.repositories.incidents import SQLAlchemyIncidentRepository
from app.infrastructure.repositories.audit import SQLAlchemyAuditRepository
from app.infrastructure.schemas.incidents import IncidentCreate, IncidentUpdate, IncidentResponse, PaginatedIncidentResponse, IncidentFilterParams, IncidentSeverity, IncidentStatus

router = APIRouter(prefix="/incidents", tags=["Incidents"])

def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    repo = SQLAlchemyAuditRepository(db)
    return AuditService(repo)

def get_incident_service(db: Session = Depends(get_db), audit: AuditService = Depends(get_audit_service)) -> IncidentService:
    repo = SQLAlchemyIncidentRepository(db)
    return IncidentService(repo, audit)

@router.get("/", response_model=PaginatedIncidentResponse, dependencies=[Depends(RBAC("incidents:view"))])
async def list_incidents(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    severity: Optional[IncidentSeverity] = None,
    status: Optional[IncidentStatus] = None,
    incident_service: IncidentService = Depends(get_incident_service)
):
    filters = IncidentFilterParams(severity=severity, status=status)
    return await incident_service.list_incidents(page=page, size=size, filters=filters)

@router.post("/", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RBAC("incidents:create"))])
async def create_incident(
    incident_in: IncidentCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    incident_service: IncidentService = Depends(get_incident_service),
    audit: AuditService = Depends(get_audit_service)
):
    incident = await incident_service.create_incident(incident_in, current_user.id, request.client.host)
    audit.log_action(current_user.id, request.client.host, "incidents", "INCIDENT_CREATE", None, {"id": str(incident.id)})
    return incident

@router.get("/{incident_id}", response_model=IncidentResponse, dependencies=[Depends(RBAC("incidents:view"))])
async def get_incident(
    incident_id: UUID,
    incident_service: IncidentService = Depends(get_incident_service)
):
    incident = await incident_service.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.patch("/{incident_id}", response_model=IncidentResponse, dependencies=[Depends(RBAC("incidents:edit"))])
async def update_incident(
    incident_id: UUID,
    incident_update: IncidentUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    incident_service: IncidentService = Depends(get_incident_service),
    audit: AuditService = Depends(get_audit_service)
):
    incident = await incident_service.update_incident(incident_id, incident_update, current_user.id, request.client.host)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    audit.log_action(current_user.id, request.client.host, "incidents", "INCIDENT_UPDATE", {"id": str(incident_id)}, incident_update.model_dump())
    return incident
