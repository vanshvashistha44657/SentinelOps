from abc import ABC, abstractmethod
from app.infrastructure.models.logs import RawLog

class LogRepository(ABC):
    @abstractmethod
    def create(self, log_in: dict) -> RawLog:
        pass
