from sqlalchemy import insert
from app.infrastructure.repositories.base import BaseRepository
from app.infrastructure.models.alerts import Alert, incident_alerts
from uuid import UUID
from typing import List

class SQLAlchemyAlertRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, Alert)

    def get_unassigned_alerts(self) -> List[Alert]:
        return self.db.query(Alert).filter(Alert.assigned_user_id == None).all()

    def link_alert_to_incident(self, alert_id: UUID, incident_id: UUID) -> None:
        stmt = insert(incident_alerts).values(alert_id=alert_id, incident_id=incident_id)
        self.db.execute(stmt)
        self.db.commit()
