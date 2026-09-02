"""Unit tests for integration adapters and webhook routing."""

from app.server.adapters.base import AgenticEvent
from app.server.events.bus import EventBus
from app.server.webhooks.router import WebhookRouter


def test_github_pull_request_webhook():
    """Test processing GitHub pull request webhook with lowercase header."""
    event_bus = EventBus()
    events = []
    
    def on_event(event: AgenticEvent):
        events.append(event)
        
    event_bus.subscribe("git.pull_request", on_event)
    router = WebhookRouter(event_bus)
    
    # Mock incoming github webhook
    payload = {"action": "opened", "number": 123}
    headers = {"x-github-event": "pull_request"}
    
    # Process
    success = router.route_payload("github", payload, headers)
    
    assert success is True
    assert len(events) == 1
    assert events[0].type == "git.pull_request"
    assert events[0].source == "github"
    assert events[0].payload["number"] == 123


def test_github_webhook_wire_case_headers():
    """Test that GitHubAdapter case-insensitively parses X-GitHub-Event headers."""
    event_bus = EventBus()
    events = []

    def on_event(event: AgenticEvent):
        events.append(event)

    event_bus.subscribe("git.push", on_event)
    router = WebhookRouter(event_bus)

    payload = {"ref": "refs/heads/main"}
    headers = {"X-GitHub-Event": "push"}

    success = router.route_payload("github", payload, headers)

    assert success is True
    assert len(events) == 1
    assert events[0].type == "git.push"
    assert events[0].source == "github"


def test_vercel_webhook():
    """Test processing Vercel deployment webhook."""
    event_bus = EventBus()
    events = []
    
    def on_event(event: AgenticEvent):
        events.append(event)
        
    event_bus.subscribe("*", on_event)  # Subscribe to all
    router = WebhookRouter(event_bus)
    
    # Mock incoming vercel webhook
    payload = {"type": "deployment.succeeded", "projectId": "prj_123"}
    
    # Process
    success = router.route_payload("vercel", payload, {})
    
    assert success is True
    assert len(events) == 1
    assert events[0].type == "ci.deployment.succeeded"
    assert events[0].source == "vercel"
    assert events[0].payload["projectId"] == "prj_123"
