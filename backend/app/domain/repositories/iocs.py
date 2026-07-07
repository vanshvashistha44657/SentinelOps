from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from app.infrastructure.models.threat_intel import IOCRecord

class IOCRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: UUID) -> Optional[IOCRecord]:
        pass

    @abstractmethod
    def get_by_value(self, value: str) -> Optional[IOCRecord]:
        pass

    @abstractmethod
    def create(self, ioc_in: dict) -> IOCRecord:
        pass

    @abstractmethod
    def update(self, ioc_id: UUID, ioc_update: dict) -> Optional[IOCRecord]:
        pass

    @abstractmethod
    def list(self) -> List[IOCRecord]:
        pass
