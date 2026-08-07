from fastapi import APIRouter, Depends, status, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from app.api.dependencies import get_db
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.rbac import RBAC
from app.infrastructure.models.iam import User
from app.application.services.alert import AlertService
from app.application.services.audit import AuditService
from app.infrastructure.repositories.audit import SQLAlchemyAuditRepository
from app.infrastructure.schemas.alerts import AlertCreate, AlertResponse, AlertUpdate, PaginatedAlertResponse, AlertFilterParams, AlertSeverity, AlertStatus

router = APIRouter(prefix="/alerts", tags=["Alerts"])

def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    repo = SQLAlchemyAuditRepository(db)
    return AuditService(repo)

def get_alert_service(db: Session = Depends(get_db)) -> AlertService:
    return AlertService(db)

@router.get("/", response_model=PaginatedAlertResponse, dependencies=[Depends(RBAC("alerts:view"))])
def list_alerts(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    severity: Optional[AlertSeverity] = None,
    status: Optional[AlertStatus] = None,
    source_ip: Optional[str] = None,
    alert_service: AlertService = Depends(get_alert_service)
):
    filters = AlertFilterParams(severity=severity, status=status, source_ip=source_ip)
    return alert_service.list_alerts(page=page, size=size, filters=filters)

@router.post("/ingest", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def ingest_alert(
    alert_in: AlertCreate,
    alert_service: AlertService = Depends(get_alert_service)
):
    # Ingestion might be automated (system-to-system), handle auth/RBAC differently if needed
    return alert_service.ingest_alert(alert_in)

@router.patch("/{alert_id}", response_model=AlertResponse, dependencies=[Depends(RBAC("alerts:edit"))])
def update_alert(
    alert_id: UUID,
    alert_update: AlertUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    alert_service: AlertService = Depends(get_alert_service),
    audit: AuditService = Depends(get_audit_service)
):
    alert = alert_service.update_alert(alert_id, alert_update)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    audit.log_action(current_user.id, request.client.host, "alerts", "ALERT_UPDATE", {"id": str(alert_id)}, alert_update.model_dump())
    return alert

@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(RBAC("alerts:delete"))])
def delete_alert(
    alert_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    alert_service: AlertService = Depends(get_alert_service),
    audit: AuditService = Depends(get_audit_service)
):
    if not alert_service.delete_alert(alert_id):
        raise HTTPException(status_code=404, detail="Alert not found")
    audit.log_action(current_user.id, request.client.host, "alerts", "ALERT_DELETE", {"id": str(alert_id)}, None)
    return None
