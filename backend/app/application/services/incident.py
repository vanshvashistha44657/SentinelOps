from typing import Optional, List
from uuid import UUID
from app.domain.repositories.incidents import IncidentRepository
from app.infrastructure.schemas.incidents import IncidentCreate, IncidentUpdate, IncidentResponse, IncidentFilterParams, PaginatedIncidentResponse
from app.application.services.audit import AuditService
from sqlalchemy import desc

class IncidentService:
    def __init__(self, incident_repo: IncidentRepository, audit_service: AuditService):
        self.incident_repo = incident_repo
        self.audit_service = audit_service

    async def list_incidents(
        self, 
        page: int = 1, 
        size: int = 20, 
        filters: Optional[IncidentFilterParams] = None
    ) -> PaginatedIncidentResponse:
        # Assuming repository supports querying/filtering
        query = self.incident_repo.db.query(self.incident_repo.model)
        
        if filters:
            if filters.severity:
                query = query.filter(self.incident_repo.model.severity == filters.severity)
            if filters.status:
                query = query.filter(self.incident_repo.model.status == filters.status)
            if filters.start_date:
                query = query.filter(self.incident_repo.model.created_at >= filters.start_date)
            if filters.end_date:
                query = query.filter(self.incident_repo.model.created_at <= filters.end_date)
                
        total = query.count()
        incidents = query.order_by(desc(self.incident_repo.model.created_at)).offset((page - 1) * size).limit(size).all()
        
        return PaginatedIncidentResponse(
            items=[IncidentResponse.model_validate(i) for i in incidents],
            total=total,
            page=page,
            size=size
        )

    async def get_incident(self, incident_id: UUID) -> Optional[IncidentResponse]:
        incident = self.incident_repo.get_by_id(incident_id)
        if not incident:
            return None
        return IncidentResponse.model_validate(incident)

    async def create_incident(self, incident_in: IncidentCreate, user_id: UUID, ip_address: str) -> IncidentResponse:
        incident = self.incident_repo.create(incident_in.model_dump())
        self.audit_service.log_action(user_id, ip_address, "incidents", "INCIDENT_CREATE", None, {"incident_id": str(incident.id)})
        return IncidentResponse.model_validate(incident)

    async def update_incident(self, incident_id: UUID, incident_update: IncidentUpdate, user_id: UUID, ip_address: str) -> Optional[IncidentResponse]:
        old_incident = self.incident_repo.get_by_id(incident_id)
        if not old_incident:
            return None
        
        incident = self.incident_repo.update(incident_id, incident_update.model_dump(exclude_unset=True))
        self.audit_service.log_action(user_id, ip_address, "incidents", "INCIDENT_UPDATE", {"status": old_incident.status}, {"status": incident.status})
        return IncidentResponse.model_validate(incident)
