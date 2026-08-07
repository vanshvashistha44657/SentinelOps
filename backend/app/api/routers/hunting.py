from fastapi import APIRouter, Depends, status, HTTPException, Request, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.api.dependencies import get_db
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.rbac import RBAC
from app.infrastructure.models.iam import User
from app.application.services.hunting import ThreatHuntingService
from app.application.services.audit import AuditService
from app.infrastructure.repositories.hunting import SQLAlchemyThreatHuntingRepository
from app.infrastructure.repositories.audit import SQLAlchemyAuditRepository
from app.infrastructure.schemas.hunting import ThreatHuntingQueryCreate, ThreatHuntingQueryResponse, ThreatHuntingHistoryResponse

router = APIRouter(prefix="/hunting", tags=["Threat Hunting"])

def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    repo = SQLAlchemyAuditRepository(db)
    return AuditService(repo)

def get_hunting_service(db: Session = Depends(get_db), audit: AuditService = Depends(get_audit_service)) -> ThreatHuntingService:
    repo = SQLAlchemyThreatHuntingRepository(db)
    return ThreatHuntingService(db, repo, audit)

@router.get("/search", dependencies=[Depends(RBAC("hunting:search"))])
async def search_events(
    request: Request,
    query: str,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    hunting_service: ThreatHuntingService = Depends(get_hunting_service)
):
    return await hunting_service.search(query, page, size, current_user.id, request.client.host)

@router.get("/history", response_model=List[ThreatHuntingHistoryResponse], dependencies=[Depends(RBAC("hunting:search"))])
async def get_history(
    current_user: User = Depends(get_current_user),
    hunting_service: ThreatHuntingService = Depends(get_hunting_service)
):
    return await hunting_service.get_history(current_user.id)

@router.post("/", response_model=ThreatHuntingQueryResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RBAC("hunting:save"))])
async def create_query(
    query_in: ThreatHuntingQueryCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    hunting_service: ThreatHuntingService = Depends(get_hunting_service)
):
    return await hunting_service.create_query(query_in, current_user.id, current_user.id, request.client.host)

@router.get("/saved", response_model=List[ThreatHuntingQueryResponse], dependencies=[Depends(RBAC("hunting:search"))])
async def list_queries(
    hunting_service: ThreatHuntingService = Depends(get_hunting_service)
):
    return await hunting_service.list_queries()

@router.delete("/saved/{query_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(RBAC("hunting:save"))])
async def delete_query(
    query_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    hunting_service: ThreatHuntingService = Depends(get_hunting_service)
):
    if not await hunting_service.delete_query(query_id, current_user.id, request.client.host):
        raise HTTPException(status_code=404, detail="Query not found")
    return None
