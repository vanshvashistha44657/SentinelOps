from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.infrastructure.models.assets import Asset

class AssetRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: UUID) -> Optional[Asset]:
        pass

    @abstractmethod
    def create(self, asset_in: dict) -> Asset:
        pass

    @abstractmethod
    def list(self) -> List[Asset]:
        pass
