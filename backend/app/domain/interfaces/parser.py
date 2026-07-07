from abc import ABC, abstractmethod
from typing import Dict, Any

class LogParser(ABC):
    @abstractmethod
    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parses raw log content into structured dictionary."""
        pass
