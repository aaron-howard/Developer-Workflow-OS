"""GitHub integration adapter for parsing webhook events."""

from typing import Any, Dict, Optional
from .base import IntegrationProvider, AgenticEvent


class GitProvider(IntegrationProvider):
    """Abstract base class for Git provider integrations."""
    pass


class GitHubAdapter(GitProvider):
    """Adapter for processing incoming GitHub webhook payloads and headers."""

    def parse_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> Optional[AgenticEvent]:
        """
        Parse incoming GitHub webhook payload and headers into an AgenticEvent.
        
        Header lookup is case-insensitive (handles 'X-GitHub-Event', 'x-github-event', etc.).
        """
        # Case-insensitive header lookup
        normalized_headers = {k.lower(): v for k, v in headers.items()}
        event_type = normalized_headers.get("x-github-event", "unknown")
        
        if event_type == "pull_request":
            return AgenticEvent(
                type="git.pull_request",
                source="github",
                payload=payload
            )
        elif event_type == "push":
            return AgenticEvent(
                type="git.push",
                source="github",
                payload=payload
            )
            
        return AgenticEvent(
            type=f"git.{event_type}",
            source="github",
            payload=payload
        )
