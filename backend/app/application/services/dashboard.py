from datetime import datetime, timedelta
from typing import Any, Dict

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.infrastructure.models.alerts import Alert
from app.infrastructure.models.incidents import Case, Incident
from app.infrastructure.models.network import NetworkDevice, NetworkHealthMeasurement
from app.infrastructure.models.network_sensor import NetworkSensor


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_overview(self) -> Dict[str, Any]:
        return {
            "total_alerts": self.db.query(Alert).count(),
            "open_alerts": self.db.query(Alert).filter(Alert.status.in_(["NEW", "INVESTIGATING"])).count(),
            "critical_alerts": self.db.query(Alert).filter(Alert.severity == "CRITICAL", Alert.status != "CLOSED").count(),
            "total_incidents": self.db.query(Incident).count(),
            "open_incidents": self.db.query(Incident).filter(Incident.status != "CLOSED").count(),
            "active_cases": self.db.query(Case).filter(Case.status != "CLOSED").count(),
            "closed_cases": self.db.query(Case).filter(Case.status == "CLOSED").count(),
            "high_priority_cases": self.db.query(Case).filter(Case.priority.in_(["HIGH", "CRITICAL"]), Case.status != "CLOSED").count(),
            "known_devices": self.db.query(NetworkDevice).count(),
            "online_sensors": self.db.query(NetworkSensor).filter(NetworkSensor.status == "ACTIVE").count(),
        }

    def get_metrics(self) -> Dict[str, Any]:
        since = datetime.utcnow() - timedelta(days=1)
        created_alerts = self.db.query(Alert).filter(Alert.created_at >= since).count()
        resolved_alerts = self.db.query(Alert).filter(Alert.updated_at >= since, Alert.status.in_(["CLOSED", "TRUE_POSITIVE", "FALSE_POSITIVE"])).count()
        return {
            "cases_closed_today": self.db.query(Case).filter(Case.status == "CLOSED", Case.updated_at >= since).count(),
            "alerts_today": created_alerts,
            "alerts_resolved_today": resolved_alerts,
            "mttd": None,
            "mttr": None,
            "metrics_note": "Time-based metrics are unavailable until lifecycle timestamps are recorded for the relevant records.",
        }

    def get_charts(self) -> Dict[str, Any]:
        now = datetime.utcnow()
        buckets = []
        for offset in range(6, -1, -1):
            start = (now - timedelta(days=offset)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
            buckets.append({
                "name": start.strftime("%a"),
                "alerts": self.db.query(Alert).filter(Alert.created_at >= start, Alert.created_at < end).count(),
                "incidents": self.db.query(Incident).filter(Incident.created_at >= start, Incident.created_at < end).count(),
            })
        severities = [
            {"name": severity, "value": self.db.query(Alert).filter(Alert.severity == severity).count()}
            for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
        ]
        return {"alerts_over_time": buckets, "incidents_over_time": buckets, "severity_distribution": severities}

    def get_top(self) -> Dict[str, Any]:
        top_ips = self.db.query(Alert.source_ip, func.count(Alert.id)).filter(Alert.source_ip.isnot(None)).group_by(Alert.source_ip).order_by(func.count(Alert.id).desc()).limit(10).all()
        top_types = self.db.query(Alert.title, func.count(Alert.id)).group_by(Alert.title).order_by(func.count(Alert.id).desc()).limit(10).all()
        return {
            "top_source_ips": [{"value": value, "count": count} for value, count in top_ips],
            "top_alert_types": [{"value": value, "count": count} for value, count in top_types],
        }
