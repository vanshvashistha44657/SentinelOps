from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import StreamingResponse
import io
from openpyxl import Workbook
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from sqlalchemy.orm import Session
from uuid import UUID
from app.api.dependencies import get_db
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.rbac import RBAC
from app.infrastructure.models.iam import User
from app.application.services.reports import ReportService
from app.application.services.audit import AuditService
from app.infrastructure.repositories.reports import SQLAlchemyReportRepository
from app.infrastructure.repositories.audit import SQLAlchemyAuditRepository
from app.infrastructure.schemas.reports import ReportCreate, ReportResponse
from typing import List
from app.core.exceptions import EntityNotFoundException

router = APIRouter(prefix="/reports", tags=["Reports"], dependencies=[Depends(RBAC("reports:view"))])

def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    repo = SQLAlchemyAuditRepository(db)
    return AuditService(repo)

def get_report_service(db: Session = Depends(get_db), audit: AuditService = Depends(get_audit_service)) -> ReportService:
    repo = SQLAlchemyReportRepository(db)
    return ReportService(repo, audit)

@router.get("/export/excel")
async def export_excel(
    request: Request,
    current_user: User = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service),
    audit: AuditService = Depends(get_audit_service),
):
    reports = await report_service.list_reports()
    wb = Workbook()
    ws = wb.active
    ws.append(["ID", "Title", "Created At"])
    for report in reports:
        values = [str(report.id), report.title, str(report.created_at)]
        ws.append([_safe_spreadsheet_value(value) for value in values])
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    audit.log_action(current_user.id, request.client.host, "reports", "REPORT_EXPORT_EXCEL")
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=sentinelops-report.xlsx"}
    )

@router.get("/export/pdf")
async def export_pdf(
    request: Request,
    current_user: User = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service),
    audit: AuditService = Depends(get_audit_service),
):
    reports = await report_service.list_reports()
    output = io.BytesIO()
    c = canvas.Canvas(output, pagesize=letter)
    c.drawString(100, 750, "SentinelOps Report")
    y = 700
    for report in reports:
        c.drawString(100, y, f"{report.title} - {report.created_at}")
        y -= 20
    c.save()
    output.seek(0)
    
    audit.log_action(current_user.id, request.client.host, "reports", "REPORT_EXPORT_PDF")
    return StreamingResponse(
        output,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=sentinelops-report.pdf"}
    )

@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RBAC("reports:create"))])
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
    current_user: User = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service)
):
    return await report_service.list_reports()


def _safe_spreadsheet_value(value):
    text = str(value)
    return "'" + text if text[:1] in {"=", "+", "-", "@"} else value
