from typing import List, Dict, Any
from app.application.services.ingestion import IngestionService
from uuid import UUID

class AttackSimulatorService:
    def __init__(self, ingestion_service: IngestionService):
        self.ingestion_service = ingestion_service

    def _get_attack_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "brute_force": [
                {
                    "event_type": "login_failure",
                    "severity": "CRITICAL",
                    "username": "admin",
                    "hostname": "SERVER-01",
                    "source_ip": "10.0.0.50"
                }
            ],
            "powershell_execution": [
                {
                    "event_type": "process_creation",
                    "severity": "CRITICAL",
                    "process_name": "powershell.exe",
                    "hostname": "SERVER-01"
                }
            ]
        }

    def run_attack(self, attack_type: str) -> bool:
        templates = self._get_attack_templates()
        if attack_type not in templates:
            return False
        
        for event in templates[attack_type]:
            self.ingestion_service.ingest_event(event, "ATTACK_SIMULATOR")
            
        return True
