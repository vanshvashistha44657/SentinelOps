from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.domain.repositories.iocs import IOCRepository
from app.infrastructure.models.threat_intel import IOCRecord

class SQLAlchemyIOCRepository(IOCRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: UUID) -> Optional[IOCRecord]:
        return self.db.query(IOCRecord).filter(IOCRecord.id == id).first()

    def get_by_value(self, value: str) -> Optional[IOCRecord]:
        return self.db.query(IOCRecord).filter(IOCRecord.value == value).first()

    def create(self, ioc_in: dict) -> IOCRecord:
        ioc = IOCRecord(**ioc_in)
        self.db.add(ioc)
        self.db.commit()
        self.db.refresh(ioc)
        return ioc

    def update(self, ioc_id: UUID, ioc_update: dict) -> Optional[IOCRecord]:
        ioc = self.get_by_id(ioc_id)
        if ioc:
            for key, value in ioc_update.items():
                setattr(ioc, key, value)
            self.db.commit()
            self.db.refresh(ioc)
        return ioc

    def list(self) -> List[IOCRecord]:
        return self.db.query(IOCRecord).all()
