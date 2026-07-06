from typing import Optional
from app.domain.repositories.rules import DetectionRuleRepository
from app.infrastructure.models.alerts import Alert
from app.infrastructure.schemas.alerts import AlertCreate, AlertResponse
from sqlalchemy.orm import Session
from app.infrastructure.models.alerts import Alert as AlertModel

class AlertService:
    def __init__(self, db: Session):
        self.db = db

    def ingest_alert(self, alert_in: AlertCreate) -> AlertResponse:
        """
        Ingests a raw alert, applies severity/confidence scoring logic,
        and saves it to the database.
        """
        # Logic for automated severity/confidence adjustment could be added here
        
        alert_model = AlertModel(**alert_in.model_dump())
        self.db.add(alert_model)
        self.db.commit()
        self.db.refresh(alert_model)
        
        return AlertResponse.model_validate(alert_model)
