from typing import Optional, List, Any
from uuid import UUID
from app.domain.repositories.hunting import ThreatHuntingRepository
from app.infrastructure.schemas.hunting import ThreatHuntingQueryCreate, ThreatHuntingQueryResponse, ThreatHuntingHistoryResponse
from app.infrastructure.models.hunting import ThreatHuntingQuery, ThreatHuntingHistory
from app.application.services.audit import AuditService
from sqlalchemy.orm import Session
from datetime import datetime

class ThreatHuntingService:
    def __init__(self, db: Session, hunting_repo: ThreatHuntingRepository, audit_service: AuditService):
        self.db = db
        self.hunting_repo = hunting_repo
        self.audit_service = audit_service

from typing import Optional, List, Any, Dict
from uuid import UUID
from app.domain.repositories.hunting import ThreatHuntingRepository
from app.infrastructure.schemas.hunting import ThreatHuntingQueryCreate, ThreatHuntingQueryResponse, ThreatHuntingHistoryResponse
from app.infrastructure.models.hunting import ThreatHuntingQuery, ThreatHuntingHistory
from app.infrastructure.models.logs import RawLog
from app.application.services.audit import AuditService
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime

class ThreatHuntingService:
    def __init__(self, db: Session, hunting_repo: ThreatHuntingRepository, audit_service: AuditService):
        self.db = db
        self.hunting_repo = hunting_repo
        self.audit_service = audit_service

    # Search
    async def search(self, query_str: str, page: int, size: int, user_id: UUID, ip_address: str) -> Dict[str, Any]:
        # Parse basic query language: key=value AND key2=value2
        filters = []
        if query_str:
            parts = query_str.split(" AND ")
            for part in parts:
                if "=" in part:
                    key, value = part.split("=", 1)
                    # Filter against parsed_content JSON field in RawLog
                    filters.append(RawLog.parsed_content[key].as_string() == value)
        
        query = self.db.query(RawLog)
        if filters:
            query = query.filter(and_(*filters))
        
        total = query.count()
        results = query.order_by(RawLog.ingested_at.desc()).offset((page - 1) * size).limit(size).all()
        
        formatted_results = [
            {
                "id": str(r.id),
                "timestamp": r.ingested_at.isoformat(),
                "event": r.source,
                "raw": r.raw_content,
                "parsed": r.parsed_content
            } for r in results
        ]
        
        # Track history
        history = ThreatHuntingHistory(query=query_str, result_count=total, user_id=user_id)
        self.db.add(history)
        self.db.commit()
        
        self.audit_service.log_action(user_id, ip_address, "threat_hunting", "HUNTING_SEARCH", None, {"query": query_str})
        return {"items": formatted_results, "total": total, "page": page, "size": size}

    # Saved Searches
    async def get_query(self, query_id: UUID) -> Optional[ThreatHuntingQueryResponse]:
        query = self.hunting_repo.get_by_id(query_id)
        if not query:
            return None
        return ThreatHuntingQueryResponse.model_validate(query)

    async def create_query(self, query_in: ThreatHuntingQueryCreate, creator_id: UUID, user_id: UUID, ip_address: str) -> ThreatHuntingQueryResponse:
        data = query_in.model_dump()
        data["creator_id"] = creator_id
        query = self.hunting_repo.create(data)
        self.audit_service.log_action(user_id, ip_address, "threat_hunting", "HUNTING_QUERY_CREATE", None, {"query_id": str(query.id)})
        return ThreatHuntingQueryResponse.model_validate(query)

    async def list_queries(self) -> List[ThreatHuntingQueryResponse]:
        queries = self.hunting_repo.list()
        return [ThreatHuntingQueryResponse.model_validate(q) for q in queries]
        
    async def delete_query(self, query_id: UUID, user_id: UUID, ip_address: str) -> bool:
        self.hunting_repo.delete(query_id)
        self.audit_service.log_action(user_id, ip_address, "threat_hunting", "HUNTING_QUERY_DELETE", {"query_id": str(query_id)}, None)
        return True

    # History
    async def get_history(self, user_id: UUID) -> List[ThreatHuntingHistoryResponse]:
        history = self.db.query(ThreatHuntingHistory).filter(ThreatHuntingHistory.user_id == user_id).order_by(ThreatHuntingHistory.executed_at.desc()).limit(50).all()
        return [ThreatHuntingHistoryResponse.model_validate(h) for h in history]
