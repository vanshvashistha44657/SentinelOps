from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.api.dependencies import get_db
from app.application.services.detection import DetectionService
from app.infrastructure.repositories.rules import SQLAlchemyDetectionRuleRepository
from app.infrastructure.schemas.rules import DetectionRuleCreate, DetectionRuleResponse

router = APIRouter(prefix="/detection/rules", tags=["Detection Rules"])

def get_detection_service(db: Session = Depends(get_db)) -> DetectionService:
    rule_repo = SQLAlchemyDetectionRuleRepository(db)
    return DetectionService(rule_repo)

@router.post("/", response_model=DetectionRuleResponse, status_code=status.HTTP_201_CREATED)
def create_rule(
    rule_in: DetectionRuleCreate,
    detection_service: DetectionService = Depends(get_detection_service)
):
    return detection_service.create_rule(rule_in)

@router.get("/", response_model=List[DetectionRuleResponse])
def list_rules(detection_service: DetectionService = Depends(get_detection_service)):
    return detection_service.get_all_rules()

@router.get("/{rule_id}", response_model=DetectionRuleResponse)
def get_rule(
    rule_id: UUID,
    detection_service: DetectionService = Depends(get_detection_service)
):
    rule = detection_service.get_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule
