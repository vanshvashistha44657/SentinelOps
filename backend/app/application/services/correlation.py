from collections import defaultdict
from datetime import datetime, timedelta
from typing import List
from app.domain.repositories.alerts import AlertRepository
from app.domain.repositories.incidents import IncidentRepository
from app.infrastructure.models.alerts import Alert

class CorrelationService:
    def __init__(self, alert_repo: AlertRepository, incident_repo: IncidentRepository):
        self.alert_repo = alert_repo
        self.incident_repo = incident_repo

    def correlate_alerts(self, time_window_minutes: int = 5, threshold: int = 3):
        """
        Correlates recent unassigned alerts and creates incidents based on hostname.
        """
        unassigned_alerts = self.alert_repo.get_unassigned_alerts()
        
        # Simple grouping by hostname
        grouped_alerts = defaultdict(list)
        for alert in unassigned_alerts:
            # Only consider alerts within the time window
            if alert.created_at >= datetime.utcnow() - timedelta(minutes=time_window_minutes):
                grouped_alerts[alert.hostname].append(alert)
        
        # Check threshold
        for hostname, alerts in grouped_alerts.items():
            if len(alerts) >= threshold:
                # Create Incident
                incident_data = {
                    "title": f"Multiple alerts on {hostname}",
                    "severity": "HIGH",
                    "status": "OPEN",
                    "summary": f"Automated incident: {len(alerts)} alerts grouped on {hostname} within {time_window_minutes} minutes."
                }
                incident = self.incident_repo.create(incident_data)
                
                # Link alerts to incident
                for alert in alerts:
                    self.alert_repo.link_alert_to_incident(alert.id, incident.id)

