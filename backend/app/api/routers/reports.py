from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from uuid import UUID
from app.api.dependencies import get_db
from app.api.dependencies.auth import get_current_user
from app.infrastructure.models.iam import User
from app.application.services.reports import ReportService
from app.application.services.audit import AuditService
from app.infrastructure.repositories.reports import SQLAlchemyReportRepository
from app.infrastructure.repositories.audit import SQLAlchemyAuditRepository
from app.infrastructure.schemas.reports import ReportCreate, ReportResponse
from typing import List
from app.core.exceptions import EntityNotFoundException

router = APIRouter(prefix="/reports", tags=["Reports"])

def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    repo = SQLAlchemyAuditRepository(db)
    return AuditService(repo)

def get_report_service(db: Session = Depends(get_db), audit: AuditService = Depends(get_audit_service)) -> ReportService:
    repo = SQLAlchemyReportRepository(db)
    return ReportService(repo, audit)

@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    report_in: ReportCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service)
):
    return await report_service.create_report(report_in, current_user.id, request.client.host)

@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: UUID,
    report_service: ReportService = Depends(get_report_service)
):
    report = await report_service.get_report(report_id)
    if not report:
        raise EntityNotFoundException("Report", str(report_id))
    return report

@router.get("/", response_model=List[ReportResponse])
async def list_reports(
    report_service: ReportService = Depends(get_report_service)
):
    return await report_service.list_reports()
