from fastapi import Depends, HTTPException, status
from app.api.dependencies.auth import get_current_user
from app.infrastructure.models.iam import User

class RBAC:
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    def __call__(self, current_user: User = Depends(get_current_user)):
        # Check if user role has the required permission
        user_permissions = [p.name for p in current_user.role.permissions]
        if self.required_permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return current_user
