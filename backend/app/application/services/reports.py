from typing import Optional, List
from uuid import UUID
from app.domain.repositories.reports import ReportRepository
from app.infrastructure.schemas.reports import ReportCreate, ReportResponse
from app.infrastructure.models.system import Report
from app.application.services.audit import AuditService

class ReportService:
    def __init__(self, report_repo: ReportRepository, audit_service: AuditService):
        self.report_repo = report_repo
        self.audit_service = audit_service

    async def get_report(self, report_id: UUID) -> Optional[ReportResponse]:
        report = self.report_repo.get_by_id(report_id)
        if not report:
            return None
        return ReportResponse.model_validate(report)

    async def create_report(self, report_in: ReportCreate, user_id: UUID, ip_address: str) -> ReportResponse:
        data = report_in.model_dump()
        data["generated_by_id"] = user_id
        report = self.report_repo.create(data)
        self.audit_service.log_action(user_id, ip_address, "reports", "REPORT_CREATE", None, {"report_id": str(report.id)})
        return ReportResponse.model_validate(report)

    async def list_reports(self) -> List[ReportResponse]:
        reports = self.report_repo.list()
        return [ReportResponse.model_validate(r) for r in reports]
