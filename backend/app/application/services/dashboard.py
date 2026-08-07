from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, select
from datetime import datetime, timedelta
from app.infrastructure.models.alerts import Alert
from app.infrastructure.models.incidents import Incident, Case

class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_overview(self) -> Dict[str, Any]:
        # Perform all counts in a single efficient SQL query
        counts = self.db.query(
            func.count(Alert.id).filter(Alert.status == "NEW").label("open_alerts"),
            func.count(Alert.id).filter(Alert.severity == "CRITICAL").label("critical_alerts"),
            func.count(Alert.id).label("total_alerts"),
            func.count(Incident.id).filter(Incident.status != "CLOSED").label("open_incidents"),
            func.count(Incident.id).label("total_incidents"),
            func.count(Case.id).filter(Case.status != "CLOSED").label("active_cases"),
            func.count(Case.id).filter(Case.status == "CLOSED").label("closed_cases"),
            func.count(Case.id).filter(Case.priority == "HIGH").label("high_priority_cases"),
        ).select_from(Alert, Incident, Case).one()
        
        return {
            "total_alerts": counts.total_alerts,
            "open_alerts": counts.open_alerts,
            "critical_alerts": counts.critical_alerts,
            "total_incidents": counts.total_incidents,
            "open_incidents": counts.open_incidents,
            "active_cases": counts.active_cases,
            "closed_cases": counts.closed_cases,
            "high_priority_cases": counts.high_priority_cases,
        }

    def get_metrics(self) -> Dict[str, Any]:
        # Use more efficient filtering for today's statistics
        today = datetime.utcnow() - timedelta(days=1)
        cases_closed_today = self.db.query(func.count(Case.id)).filter(Case.status == "CLOSED", Case.updated_at >= today).scalar()
        alerts_today = self.db.query(func.count(Alert.id)).filter(Alert.created_at >= today).scalar()
        
        return {
            "mttd": 15,
            "mttr": 45,
            "avg_resolution_time": 120,
            "avg_investigation_time": 60,
            "cases_closed_today": cases_closed_today,
            "alerts_today": alerts_today,
        }

    def get_charts(self) -> Dict[str, Any]:
        # Placeholder chart data
        return {
            "alerts_over_time": [{"name": "00:00", "value": 10}, {"name": "04:00", "value": 20}],
            "incidents_over_time": [{"name": "00:00", "value": 2}, {"name": "04:00", "value": 5}],
            "cases_over_time": [{"name": "00:00", "value": 1}, {"name": "04:00", "value": 3}],
            "severity_distribution": [{"name": "CRITICAL", "value": 5}, {"name": "HIGH", "value": 15}],
        }

    def get_top(self) -> Dict[str, Any]:
        # Placeholder top data
        return {
            "top_source_ips": [{"value": "192.168.1.1", "count": 50}],
            "top_alert_types": [{"value": "Brute Force", "count": 100}],
        }
