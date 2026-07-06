from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from app.infrastructure.models.auth import RefreshToken

class RefreshTokenRepository(ABC):
    @abstractmethod
    def get_by_hash(self, token_hash: str) -> Optional[RefreshToken]:
        pass

    @abstractmethod
    def create(self, token_in: dict) -> RefreshToken:
        pass

    @abstractmethod
    def revoke(self, token_id: UUID) -> None:
        pass
