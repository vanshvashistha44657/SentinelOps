from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.api.dependencies.rbac import RBAC
from app.application.services.simulator import AttackSimulatorService
from app.application.services.ingestion import IngestionService
from app.application.services.detection import DetectionService
from app.infrastructure.repositories.logs import SQLAlchemyLogRepository
from app.infrastructure.repositories.rules import SQLAlchemyDetectionRuleRepository

router = APIRouter(prefix="/simulator", tags=["Attack Simulator"])

def get_simulator_service(db: Session = Depends(get_db)) -> AttackSimulatorService:
    log_repo = SQLAlchemyLogRepository(db)
    rule_repo = SQLAlchemyDetectionRuleRepository(db)
    detection_service = DetectionService(db, rule_repo)
    ingestion_service = IngestionService(db, log_repo, detection_service)
    return AttackSimulatorService(ingestion_service)

@router.post("/attack/{attack_type}", dependencies=[Depends(RBAC("admin:write"))])
def run_attack(
    attack_type: str,
    simulator_service: AttackSimulatorService = Depends(get_simulator_service)
):
    if not simulator_service.run_attack(attack_type):
        raise HTTPException(status_code=400, detail="Attack type not supported")
    return {"status": "Attack simulation completed"}
