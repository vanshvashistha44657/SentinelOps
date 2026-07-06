from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.application.services.alert import AlertService
from app.infrastructure.schemas.alerts import AlertCreate, AlertResponse

router = APIRouter(prefix="/alerts", tags=["Alerts"])

def get_alert_service(db: Session = Depends(get_db)) -> AlertService:
    return AlertService(db)

@router.post("/ingest", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def ingest_alert(
    alert_in: AlertCreate,
    alert_service: AlertService = Depends(get_alert_service)
):
    return alert_service.ingest_alert(alert_in)
