from fastapi import APIRouter, Depends, status, Request, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.api.dependencies import get_db
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.rbac import RBAC
from app.infrastructure.models.iam import User
from app.application.services.admin import AdminService
from app.application.services.audit import AuditService
from app.infrastructure.repositories.iam import SQLAlchemyUserRepository
from app.infrastructure.repositories.audit import SQLAlchemyAuditRepository
from app.infrastructure.schemas.iam import UserResponse, UserUpdate
from typing import List

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(RBAC("admin:write"))])

def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    repo = SQLAlchemyAuditRepository(db)
    return AuditService(repo)

def get_admin_service(db: Session = Depends(get_db), audit: AuditService = Depends(get_audit_service)) -> AdminService:
    repo = SQLAlchemyUserRepository(db)
    return AdminService(repo, audit)

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    admin_service: AdminService = Depends(get_admin_service)
):
    return await admin_service.list_users()

@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    admin_service: AdminService = Depends(get_admin_service)
):
    user = await admin_service.update_user(user_id, user_update, current_user.id, request.client.host)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
