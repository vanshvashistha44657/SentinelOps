from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
from uuid import UUID
from app.infrastructure.models.incidents import Case
from app.infrastructure.schemas.cases import CaseFilterParams

class CaseRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: UUID) -> Optional[Case]:
        pass

    @abstractmethod
    def list(self) -> List[Case]:
        pass

    @abstractmethod
    def list_paginated(
        self, 
        page: int, 
        size: int, 
        filters: Optional[CaseFilterParams] = None
    ) -> Tuple[List[Case], int]:
        pass

    @abstractmethod
    def create(self, case_in: dict) -> Case:
        pass

    @abstractmethod
    def update(self, case_id: UUID, case_update: dict) -> Optional[Case]:
        pass
