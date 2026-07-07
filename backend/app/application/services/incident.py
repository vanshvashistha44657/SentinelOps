from typing import Optional
from uuid import UUID
from app.domain.repositories.incidents import IncidentRepository
from app.infrastructure.schemas.incidents import IncidentCreate, IncidentUpdate, IncidentResponse
from app.infrastructure.models.incidents import Incident
from app.application.services.audit import AuditService

class IncidentService:
    def __init__(self, incident_repo: IncidentRepository, audit_service: AuditService):
        self.incident_repo = incident_repo
        self.audit_service = audit_service

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
        incident = self.incident_repo.update(incident_id, incident_update.model_dump(exclude_unset=True))
        if not incident:
            return None
        self.audit_service.log_action(user_id, ip_address, "incidents", "INCIDENT_UPDATE", {"status": old_incident.status}, {"status": incident.status})
        return IncidentResponse.model_validate(incident)
