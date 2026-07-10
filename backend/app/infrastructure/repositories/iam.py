from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.domain.repositories.iam import UserRepository, RoleRepository
from app.infrastructure.models.iam import User, Role

class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: UUID) -> Optional[User]:
        return self.db.query(User).filter(User.id == id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def list(self) -> List[User]:
        return self.db.query(User).all()

    def create(self, user_in: dict) -> User:
        print(f"DEBUG: [SQLAlchemyUserRepository] INPUT DATA: {user_in}")
        user = User(**user_in)
        print(f"DEBUG: [SQLAlchemyUserRepository] MODEL ROLE_ID BEFORE ADD: {user.role_id}")
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        print(f"DEBUG: [SQLAlchemyUserRepository] MODEL ROLE_ID AFTER REFRESH: {user.role_id}")
        return user

class SQLAlchemyRoleRepository(RoleRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_name(self, name: str) -> Optional[Role]:
        return self.db.query(Role).filter(Role.name == name).first()
