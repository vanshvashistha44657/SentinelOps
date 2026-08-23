from typing import Optional, List
from uuid import UUID
from datetime import datetime
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
        user = User(**user_in)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, id: UUID, user_in: dict) -> Optional[User]:
        user = self.get_by_id(id)
        if user:
            for key, value in user_in.items():
                setattr(user, key, value)
            self.db.commit()
            self.db.refresh(user)
        return user

    def update_last_seen(self, id: UUID) -> None:
        user = self.get_by_id(id)
        if user:
            user.last_seen_at = datetime.utcnow()
            self.db.commit()

class SQLAlchemyRoleRepository(RoleRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_name(self, name: str) -> Optional[Role]:
        return self.db.query(Role).filter(Role.name == name).first()
