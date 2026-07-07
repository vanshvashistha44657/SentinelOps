from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.domain.repositories.threat_intel import ThreatIntelligenceRepository
from app.infrastructure.models.threat_intel import ThreatIntelligence

class SQLAlchemyThreatIntelligenceRepository(ThreatIntelligenceRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: UUID) -> Optional[ThreatIntelligence]:
        return self.db.query(ThreatIntelligence).filter(ThreatIntelligence.id == id).first()

    def create(self, intel_in: dict) -> ThreatIntelligence:
        intel = ThreatIntelligence(**intel_in)
        self.db.add(intel)
        self.db.commit()
        self.db.refresh(intel)
        return intel

    def update(self, intel_id: UUID, intel_update: dict) -> Optional[ThreatIntelligence]:
        intel = self.get_by_id(intel_id)
        if intel:
            for key, value in intel_update.items():
                setattr(intel, key, value)
            self.db.commit()
            self.db.refresh(intel)
        return intel

    def list(self) -> List[ThreatIntelligence]:
        return self.db.query(ThreatIntelligence).all()
