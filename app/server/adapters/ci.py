from typing import Any, Dict, Optional
from .base import IntegrationProvider, AgenticEvent

class CIProvider(IntegrationProvider):
    pass

class VercelAdapter(CIProvider):
    def parse_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> Optional[AgenticEvent]:
        # Handle Vercel webhook parsing
        event_type = payload.get("type", "unknown")
        return AgenticEvent(
            type=f"ci.{event_type}",
            source="vercel",
            payload=payload
        )
