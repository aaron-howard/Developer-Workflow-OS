"""Webhook router for dispatching incoming payloads to integration adapters."""

from typing import Any, Dict, Optional
from ..adapters.github import GitHubAdapter
from ..adapters.ci import VercelAdapter
from ..adapters.observability import SentryAdapter
from app.server.events.registry import get_event_registry
from ..events.bus import EventBus


class WebhookRouter:
    """Router for dispatching incoming webhook payloads to appropriate integration adapters."""

    def __init__(self, event_bus: EventBus | None = None) -> None:
        """Initialize webhook router with event bus, integration adapters, and EventRegistry connection."""
        self.event_bus = event_bus or EventBus()
        self.adapters = {
            "github": GitHubAdapter(),
            "vercel": VercelAdapter(),
            "sentry": SentryAdapter()
        }
        self.registry = get_event_registry()

    def route_payload(self, source: str, payload: Dict[str, Any], headers: Dict[str, str]) -> bool:
        """Route incoming payload to correct adapter and publish the normalized event."""
        adapter = self.adapters.get(source)
        if adapter:
            event = adapter.parse_webhook(payload, headers)
            if event:
                self.event_bus.publish(event)
                return True

        try:
            sdlc_event = self.registry.ingest(payload, category="webhook", provider=source)
            if sdlc_event:
                self.event_bus.publish(sdlc_event)
                return True
        except Exception:
            return False

        return False


