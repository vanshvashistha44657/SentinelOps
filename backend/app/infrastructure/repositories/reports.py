from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.domain.repositories.reports import ReportRepository
from app.infrastructure.models.system import Report

class SQLAlchemyReportRepository(ReportRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: UUID) -> Optional[Report]:
        return self.db.query(Report).filter(Report.id == id).first()

    def create(self, report_in: dict) -> Report:
        report = Report(**report_in)
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def list(self) -> List[Report]:
        return self.db.query(Report).all()
