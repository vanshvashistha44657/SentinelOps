from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from app.infrastructure.models.iam import User, Role

class UserRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: UUID) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def list(self) -> List[User]:
        pass

    @abstractmethod
    def create(self, user_in: dict) -> User:
        pass

    @abstractmethod
    def update(self, id: UUID, user_in: dict) -> Optional[User]:
        pass

    @abstractmethod
    def update_last_seen(self, id: UUID) -> None:
        pass

class RoleRepository(ABC):
    @abstractmethod
    def get_by_name(self, name: str) -> Optional[Role]:
        pass
