from sqlalchemy.orm import Session
from app.domain.repositories.logs import LogRepository
from app.infrastructure.models.logs import RawLog

class SQLAlchemyLogRepository(LogRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, log_in: dict) -> RawLog:
        log = RawLog(**log_in)
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
