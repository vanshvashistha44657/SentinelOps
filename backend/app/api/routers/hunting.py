from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.api.dependencies import get_db
from app.api.dependencies.auth import get_current_user
from app.application.services.hunting import ThreatHuntingService
from app.infrastructure.repositories.hunting import SQLAlchemyThreatHuntingRepository
from app.infrastructure.schemas.hunting import ThreatHuntingQueryCreate, ThreatHuntingQueryResponse
from app.infrastructure.models.iam import User

router = APIRouter(prefix="/hunting", tags=["Threat Hunting"])

def get_hunting_service(db: Session = Depends(get_db)) -> ThreatHuntingService:
    repo = SQLAlchemyThreatHuntingRepository(db)
    return ThreatHuntingService(repo)

@router.post("/queries", response_model=ThreatHuntingQueryResponse, status_code=status.HTTP_201_CREATED)
async def create_query(
    query_in: ThreatHuntingQueryCreate,
    current_user: User = Depends(get_current_user),
    hunting_service: ThreatHuntingService = Depends(get_hunting_service)
):
    return await hunting_service.create_query(query_in, current_user.id)

@router.get("/queries/{query_id}", response_model=ThreatHuntingQueryResponse)
async def get_query(
    query_id: UUID,
    hunting_service: ThreatHuntingService = Depends(get_hunting_service)
):
    query = await hunting_service.get_query(query_id)
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    return query

@router.get("/queries", response_model=List[ThreatHuntingQueryResponse])
async def list_queries(
    hunting_service: ThreatHuntingService = Depends(get_hunting_service)
):
    return await hunting_service.list_queries()
