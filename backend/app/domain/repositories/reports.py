from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.infrastructure.models.system import Report

class ReportRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: UUID) -> Optional[Report]:
        pass

    @abstractmethod
    def create(self, report_in: dict) -> Report:
        pass

    @abstractmethod
    def list(self) -> List[Report]:
        pass
