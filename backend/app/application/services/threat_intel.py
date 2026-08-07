from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.infrastructure.models.threat_intel import ThreatIndicator, IOCMatch
from app.infrastructure.schemas.threat_intel import ThreatIndicatorCreate, ThreatIndicatorUpdate, ThreatIndicatorResponse, IOCMatchResponse
from app.application.services.audit import AuditService

class ThreatIntelService:
    def __init__(self, db: Session, audit_service: AuditService):
        self.db = db
        self.audit_service = audit_service

    # IOC Management
    def create_indicator(self, indicator_in: ThreatIndicatorCreate, user_id: UUID, ip_address: str) -> ThreatIndicatorResponse:
        indicator = ThreatIndicator(**indicator_in.model_dump())
        self.db.add(indicator)
        self.db.commit()
        self.db.refresh(indicator)
        self.audit_service.log_action(user_id, ip_address, "threat_intel", "IOC_CREATE", None, {"indicator_id": str(indicator.id)})
        return ThreatIndicatorResponse.model_validate(indicator)

    def list_indicators(self) -> List[ThreatIndicatorResponse]:
        indicators = self.db.query(ThreatIndicator).all()
        return [ThreatIndicatorResponse.model_validate(i) for i in indicators]

    def update_indicator(self, indicator_id: UUID, update: ThreatIndicatorUpdate, user_id: UUID, ip_address: str) -> Optional[ThreatIndicatorResponse]:
        indicator = self.db.query(ThreatIndicator).filter(ThreatIndicator.id == indicator_id).first()
        if not indicator:
            return None
        
        for key, value in update.model_dump(exclude_unset=True).items():
            setattr(indicator, key, value)
            
        self.db.commit()
        self.db.refresh(indicator)
        self.audit_service.log_action(user_id, ip_address, "threat_intel", "IOC_UPDATE", {"indicator_id": str(indicator_id)}, update.model_dump())
        return ThreatIndicatorResponse.model_validate(indicator)

    def delete_indicator(self, indicator_id: UUID, user_id: UUID, ip_address: str) -> bool:
        indicator = self.db.query(ThreatIndicator).filter(ThreatIndicator.id == indicator_id).first()
        if not indicator:
            return False
        self.db.delete(indicator)
        self.db.commit()
        self.audit_service.log_action(user_id, ip_address, "threat_intel", "IOC_DELETE", {"indicator_id": str(indicator_id)}, None)
        return True

    # Matches
    def get_matches(self) -> List[IOCMatchResponse]:
        matches = self.db.query(IOCMatch).all()
        return [IOCMatchResponse.model_validate(m) for m in matches]
