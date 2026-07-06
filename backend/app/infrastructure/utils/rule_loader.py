import yaml
from typing import Dict, List, Any
from pathlib import Path

class RuleLoader:
    """Utility to load Detection Rules from YAML files."""
    
    @staticmethod
    def load_rules_from_file(file_path: Path) -> List[Dict[str, Any]]:
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
            return data.get("rules", [])
