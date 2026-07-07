from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.api.dependencies import get_db
from app.application.services.incident import IncidentService
from app.infrastructure.repositories.incidents import SQLAlchemyIncidentRepository
from app.infrastructure.schemas.incidents import IncidentCreate, IncidentUpdate, IncidentResponse

router = APIRouter(prefix="/incidents", tags=["Incidents"])

def get_incident_service(db: Session = Depends(get_db)) -> IncidentService:
    repo = SQLAlchemyIncidentRepository(db)
    return IncidentService(repo)

@router.post("/", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    incident_in: IncidentCreate,
    incident_service: IncidentService = Depends(get_incident_service)
):
    return await incident_service.create_incident(incident_in)

@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: UUID,
    incident_service: IncidentService = Depends(get_incident_service)
):
    incident = await incident_service.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: UUID,
    incident_update: IncidentUpdate,
    incident_service: IncidentService = Depends(get_incident_service)
):
    incident = await incident_service.update_incident(incident_id, incident_update)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident
