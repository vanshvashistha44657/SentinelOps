from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.domain.repositories.cases import CaseRepository
from app.infrastructure.models.incidents import Case
from app.infrastructure.schemas.cases import CaseFilterParams

class SQLAlchemyCaseRepository(CaseRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: UUID) -> Optional[Case]:
        return self.db.query(Case).filter(Case.id == id).first()

    def list(self) -> List[Case]:
        return self.db.query(Case).all()

    def list_paginated(
        self, 
        page: int, 
        size: int, 
        filters: Optional[CaseFilterParams] = None
    ) -> Tuple[List[Case], int]:
        query = self.db.query(Case)

        if filters:
            if filters.priority:
                query = query.filter(Case.priority == filters.priority)
            if filters.status:
                query = query.filter(Case.status == filters.status)
            if filters.assigned_user_id:
                query = query.filter(Case.assigned_user_id == filters.assigned_user_id)
            if filters.start_date:
                query = query.filter(Case.created_at >= filters.start_date)
            if filters.end_date:
                query = query.filter(Case.created_at <= filters.end_date)
        
        total = query.count()
        cases = query.order_by(desc(Case.created_at)).offset((page - 1) * size).limit(size).all()
        return cases, total

    def create(self, case_in: dict) -> Case:
        case = Case(**case_in)
        self.db.add(case)
        self.db.commit()
        self.db.refresh(case)
        return case

    def update(self, case_id: UUID, case_update: dict) -> Optional[Case]:
        case = self.get_by_id(case_id)
        if case:
            for key, value in case_update.items():
                setattr(case, key, value)
            self.db.commit()
            self.db.refresh(case)
        return case
