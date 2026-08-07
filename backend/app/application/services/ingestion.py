from typing import Any, Dict, List
from app.domain.repositories.logs import LogRepository
from app.infrastructure.models.logs import RawLog, FailedLog
from app.infrastructure.models.threat_intel import ThreatIndicator, IOCMatch
from app.infrastructure.models.alerts import Alert
from app.application.services.detection import DetectionService
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import func

class IngestionService:
    def __init__(self, db: Session, log_repo: LogRepository, detection_service: DetectionService):
        self.db = db
        self.log_repo = log_repo
        self.detection_service = detection_service

    def validate_event(self, event_data: dict) -> bool:
        # Simple validation: required fields
        if "raw_content" not in event_data and "event_type" not in event_data:
            return False
        return True

    def ingest_event(self, event_data: dict, source: str) -> Any:
        try:
            if not self.validate_event(event_data):
                raise ValueError("Invalid event format")

            # Normalize event
            normalized_data = {
                "source_connector": source,
                "event_type": event_data.get("event_type", "unknown"),
                "severity": event_data.get("severity", "INFO"),
                "timestamp": event_data.get("timestamp", datetime.utcnow()),
                "source_ip": event_data.get("source_ip"),
                "destination_ip": event_data.get("destination_ip"),
                "hostname": event_data.get("hostname"),
                "username": event_data.get("username"),
                "process_name": event_data.get("process_name"),
                "file_hash": event_data.get("file_hash"),
                "domain": event_data.get("domain"),
                "url": event_data.get("url"),
                "raw_content": str(event_data),
                "parsed_content": event_data
            }
            
            # Save log
            log = RawLog(**normalized_data)
            self.db.add(log)
            self.db.commit()
            self.db.refresh(log)
            
            # Trigger detection
            self.detection_service.run_detection(event_data)

            # IOC Matching
            self.match_iocs(log)
            
            return log
        except Exception as e:
            failed_log = FailedLog(
                source_connector=source,
                raw_content=str(event_data),
                error_reason=str(e)
            )
            self.db.add(failed_log)
            self.db.commit()
            return None

    def match_iocs(self, log: RawLog):
        # Fields to check against indicators
        fields_to_check = {
            "source_ip": log.source_ip,
            "destination_ip": log.destination_ip,
            "hostname": log.hostname,
            "username": log.username,
            "process_name": log.process_name,
            "file_hash": log.file_hash,
            "domain": log.domain,
            "url": log.url
        }
        
        indicators = self.db.query(ThreatIndicator).filter(ThreatIndicator.enabled == True).all()
        for indicator in indicators:
            for field, value in fields_to_check.items():
                if value and indicator.value == value:
                    # Create match
                    match = IOCMatch(
                        indicator_id=indicator.id,
                        raw_log_id=log.id,
                        matched_field=field
                    )
                    self.db.add(match)
                    
                    # Generate Alert
                    alert = Alert(
                        title=f"IOC Match: {indicator.type} - {indicator.value}",
                        severity=indicator.severity,
                        confidence_score=indicator.confidence,
                        raw_event=log.parsed_content
                    )
                    self.db.add(alert)
                    self.db.commit()
                    break

    def get_status(self) -> Dict[str, Any]:
        return {
            "status": "Running",
            "queue_size": 0,
            "failed_events": self.db.query(FailedLog).count(),
            "events_processed": self.db.query(RawLog).count(),
            "events_per_minute": 0
        }

    def get_statistics(self) -> Dict[str, Any]:
        return {
            "events_today": self.db.query(RawLog).filter(RawLog.ingested_at >= datetime.utcnow() - timedelta(days=1)).count(),
            "events_by_connector": [{"connector": r[0], "count": r[1]} for r in self.db.query(RawLog.source_connector, func.count(RawLog.id)).group_by(RawLog.source_connector).all()],
        }
