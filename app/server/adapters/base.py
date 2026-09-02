from typing import Any, Dict, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime

@dataclass
class AgenticEvent:
    type: str
    source: str
    payload: Dict[str, Any]
    timestamp: datetime = datetime.now()

class IntegrationProvider(ABC):
    @abstractmethod
    def parse_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> Optional[AgenticEvent]:
        """Parse incoming webhook and return normalized AgenticEvent."""
        pass
