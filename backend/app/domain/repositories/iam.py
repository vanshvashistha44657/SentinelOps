from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from app.infrastructure.models.iam import User

class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    async def create(self, user_in: dict) -> User:
        pass
