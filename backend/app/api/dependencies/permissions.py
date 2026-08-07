from fastapi import Depends, HTTPException, status
from app.api.dependencies.auth import get_current_user
from app.infrastructure.models.iam import User
from sqlalchemy.orm import Session
from app.api.dependencies import get_db

def check_permission(required_permission: str):
    def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        # Fetch user with roles and permissions
        user = db.query(User).filter(User.id == current_user.id).first()
        
        # Check if user has permission through role
        has_permission = False
        if user and user.role:
            for permission in user.role.permissions:
                if permission.name == required_permission:
                    has_permission = True
                    break
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action"
            )
        return user
        
    return dependency
