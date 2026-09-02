from typing import Any, Dict, Optional
from ..adapters.github import GitHubAdapter
from ..adapters.ci import VercelAdapter
from ..adapters.observability import SentryAdapter
from ..events.bus import EventBus

class WebhookRouter:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.adapters = {
            "github": GitHubAdapter(),
            "vercel": VercelAdapter(),
            "sentry": SentryAdapter()
        }

    def route_payload(self, source: str, payload: Dict[str, Any], headers: Dict[str, str]) -> bool:
        """Route incoming payload to correct adapter and publish the normalized event."""
        adapter = self.adapters.get(source)
        if not adapter:
            return False
            
        event = adapter.parse_webhook(payload, headers)
        if event:
            self.event_bus.publish(event)
            return True
        return False
