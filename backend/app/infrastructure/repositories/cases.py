from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.domain.repositories.cases import CaseRepository
from app.infrastructure.models.incidents import Case

class SQLAlchemyCaseRepository(CaseRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: UUID) -> Optional[Case]:
        return self.db.query(Case).filter(Case.id == id).first()

    def list(self) -> List[Case]:
        return self.db.query(Case).all()

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
