from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.domain.repositories.incidents import IncidentRepository
from app.infrastructure.models.incidents import Incident

class SQLAlchemyIncidentRepository(IncidentRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: UUID) -> Optional[Incident]:
        return self.db.query(Incident).filter(Incident.id == id).first()

    def list(self) -> List[Incident]:
        return self.db.query(Incident).all()

    def create(self, incident_in: dict) -> Incident:
        incident = Incident(**incident_in)
        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)
        return incident

    def update(self, incident_id: UUID, incident_update: dict) -> Optional[Incident]:
        incident = self.get_by_id(incident_id)
        if incident:
            for key, value in incident_update.items():
                setattr(incident, key, value)
            self.db.commit()
            self.db.refresh(incident)
        return incident
