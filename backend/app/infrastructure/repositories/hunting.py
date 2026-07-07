from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.domain.repositories.hunting import ThreatHuntingRepository
from app.infrastructure.models.hunting import ThreatHuntingQuery

class SQLAlchemyThreatHuntingRepository(ThreatHuntingRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: UUID) -> Optional[ThreatHuntingQuery]:
        return self.db.query(ThreatHuntingQuery).filter(ThreatHuntingQuery.id == id).first()

    def create(self, query_in: dict) -> ThreatHuntingQuery:
        query = ThreatHuntingQuery(**query_in)
        self.db.add(query)
        self.db.commit()
        self.db.refresh(query)
        return query

    def list(self) -> List[ThreatHuntingQuery]:
        return self.db.query(ThreatHuntingQuery).all()
