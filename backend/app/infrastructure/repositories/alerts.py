from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import insert
from app.domain.repositories.alerts import AlertRepository
from app.infrastructure.models.alerts import Alert, incident_alerts

class SQLAlchemyAlertRepository(AlertRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: UUID) -> Optional[Alert]:
        return self.db.query(Alert).filter(Alert.id == id).first()

    def get_unassigned_alerts(self) -> List[Alert]:
        return self.db.query(Alert).filter(Alert.assigned_user_id == None).all()

    def create(self, alert_in: dict) -> Alert:
        alert = Alert(**alert_in)
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def update(self, alert_id: UUID, alert_update: dict) -> Optional[Alert]:
        alert = self.get_by_id(alert_id)
        if alert:
            for key, value in alert_update.items():
                setattr(alert, key, value)
            self.db.commit()
            self.db.refresh(alert)
        return alert

    def link_alert_to_incident(self, alert_id: UUID, incident_id: UUID) -> None:
        stmt = insert(incident_alerts).values(alert_id=alert_id, incident_id=incident_id)
        self.db.execute(stmt)
        self.db.commit()
