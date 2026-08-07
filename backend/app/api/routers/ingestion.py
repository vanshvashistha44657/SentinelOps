from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.api.dependencies import get_db
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.rbac import RBAC
from app.infrastructure.models.iam import User
from app.application.services.ingestion import IngestionService
from app.application.services.detection import DetectionService
from app.application.services.audit import AuditService
from app.infrastructure.repositories.logs import SQLAlchemyLogRepository
from app.infrastructure.repositories.rules import SQLAlchemyDetectionRuleRepository
from app.infrastructure.repositories.audit import SQLAlchemyAuditRepository
from app.infrastructure.models.logs import FailedLog
from app.infrastructure.schemas.logs import LogResponse, FailedLogResponse

router = APIRouter(prefix="/ingestion", tags=["Log Ingestion"])

def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    repo = SQLAlchemyAuditRepository(db)
    return AuditService(repo)

def get_ingestion_service(db: Session = Depends(get_db), audit: AuditService = Depends(get_audit_service)) -> IngestionService:
    log_repo = SQLAlchemyLogRepository(db)
    rule_repo = SQLAlchemyDetectionRuleRepository(db)
    detection_service = DetectionService(db, rule_repo)
    return IngestionService(db, log_repo, detection_service)

@router.post("/events", status_code=status.HTTP_201_CREATED)
def ingest_event(
    event: dict,
    ingestion_service: IngestionService = Depends(get_ingestion_service)
):
    # Public endpoint for ingestion (API key authentication usually)
    return ingestion_service.ingest_event(event, "REST_API")

@router.get("/status", dependencies=[Depends(RBAC("ingestion:view"))])
def get_status(ingestion_service: IngestionService = Depends(get_ingestion_service)):
    return ingestion_service.get_status()

@router.get("/statistics", dependencies=[Depends(RBAC("ingestion:view"))])
def get_statistics(ingestion_service: IngestionService = Depends(get_ingestion_service)):
    return ingestion_service.get_statistics()

@router.get("/failed", response_model=List[FailedLogResponse], dependencies=[Depends(RBAC("ingestion:view"))])
def get_failed(db: Session = Depends(get_db)):
    failed = db.query(FailedLog).all()
    return [FailedLogResponse.model_validate(f) for f in failed]

@router.delete("/failed/{failed_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(RBAC("ingestion:delete"))])
def delete_failed(
    failed_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    audit: AuditService = Depends(get_audit_service),
    db: Session = Depends(get_db)
):
    failed = db.query(FailedLog).filter(FailedLog.id == failed_id).first()
    if not failed:
        raise HTTPException(status_code=404, detail="Failed event not found")
    db.delete(failed)
    db.commit()
    audit.log_action(current_user.id, request.client.host, "ingestion", "FAILED_LOG_DELETE", {"id": str(failed_id)}, None)
    return None
