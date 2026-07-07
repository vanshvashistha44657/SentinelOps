from typing import Optional
from app.domain.repositories.rules import DetectionRuleRepository
from app.infrastructure.models.alerts import Alert
from app.infrastructure.schemas.alerts import AlertCreate, AlertResponse
from app.application.services.audit import AuditService
from sqlalchemy.orm import Session
from app.infrastructure.models.alerts import Alert as AlertModel

class AlertService:
    def __init__(self, db: Session, audit_service: AuditService):
        self.db = db
        self.audit_service = audit_service

    def ingest_alert(self, alert_in: AlertCreate, ip_address: str) -> AlertResponse:
        """
        Ingests a raw alert, applies severity/confidence scoring logic,
        and saves it to the database.
        """
        alert_model = AlertModel(**alert_in.model_dump())
        self.db.add(alert_model)
        self.db.commit()
        self.db.refresh(alert_model)
        
        self.audit_service.log_action(None, ip_address, "alerts", "ALERT_INGEST", None, {"alert_id": str(alert_model.id)})
        return AlertResponse.model_validate(alert_model)
