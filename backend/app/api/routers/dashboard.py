from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.application.services.dashboard import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    return DashboardService(db)

@router.get("/overview")
def get_overview(dashboard_service: DashboardService = Depends(get_dashboard_service)):
    return dashboard_service.get_overview()

@router.get("/metrics")
def get_metrics(dashboard_service: DashboardService = Depends(get_dashboard_service)):
    return dashboard_service.get_metrics()

@router.get("/charts")
def get_charts(dashboard_service: DashboardService = Depends(get_dashboard_service)):
    return dashboard_service.get_charts()

@router.get("/top")
def get_top(dashboard_service: DashboardService = Depends(get_dashboard_service)):
    return dashboard_service.get_top()
