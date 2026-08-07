from typing import Optional, List
from app.infrastructure.models.alerts import Alert as AlertModel
from app.infrastructure.schemas.alerts import AlertCreate, AlertUpdate, AlertResponse, AlertFilterParams, PaginatedAlertResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from uuid import UUID

class AlertService:
    def __init__(self, db: Session):
        self.db = db

    def list_alerts(
        self, 
        page: int = 1, 
        size: int = 20, 
        filters: Optional[AlertFilterParams] = None
    ) -> PaginatedAlertResponse:
        query = self.db.query(AlertModel)

        if filters:
            if filters.severity:
                query = query.filter(AlertModel.severity == filters.severity)
            if filters.status:
                query = query.filter(AlertModel.status == filters.status)
            if filters.source_ip:
                query = query.filter(AlertModel.source_ip == filters.source_ip)
            if filters.start_date:
                query = query.filter(AlertModel.created_at >= filters.start_date)
            if filters.end_date:
                query = query.filter(AlertModel.created_at <= filters.end_date)

        total = query.count()
        alerts = query.order_by(desc(AlertModel.created_at)).offset((page - 1) * size).limit(size).all()
        
        return PaginatedAlertResponse(
            items=[AlertResponse.model_validate(a) for a in alerts],
            total=total,
            page=page,
            size=size
        )

    def get_alert(self, alert_id: UUID) -> Optional[AlertModel]:
        return self.db.query(AlertModel).filter(AlertModel.id == alert_id).first()

    def update_alert(self, alert_id: UUID, alert_update: AlertUpdate) -> Optional[AlertResponse]:
        alert = self.get_alert(alert_id)
        if not alert:
            return None
        
        for key, value in alert_update.model_dump(exclude_unset=True).items():
            setattr(alert, key, value)
            
        self.db.commit()
        self.db.refresh(alert)
        return AlertResponse.model_validate(alert)

    def delete_alert(self, alert_id: UUID) -> bool:
        alert = self.get_alert(alert_id)
        if not alert:
            return False
        self.db.delete(alert)
        self.db.commit()
        return True

    def ingest_alert(self, alert_in: AlertCreate) -> AlertResponse:
        alert_model = AlertModel(**alert_in.model_dump())
        self.db.add(alert_model)
        self.db.commit()
        self.db.refresh(alert_model)
        return AlertResponse.model_validate(alert_model)
