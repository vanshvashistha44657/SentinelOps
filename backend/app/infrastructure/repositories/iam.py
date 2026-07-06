from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.domain.repositories.iam import UserRepository
from app.infrastructure.models.iam import User

class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: UUID) -> Optional[User]:
        return self.db.query(User).filter(User.id == id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def create(self, user_in: dict) -> User:
        user = User(**user_in)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
