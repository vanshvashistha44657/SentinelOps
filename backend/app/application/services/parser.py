import json
from typing import Dict, Any
from app.domain.interfaces.parser import LogParser

class DefaultLogParser(LogParser):
    def parse(self, raw_content: str) -> Dict[str, Any]:
        try:
            return json.loads(raw_content)
        except json.JSONDecodeError:
            # Fallback to raw string if not JSON
            return {"raw": raw_content}
