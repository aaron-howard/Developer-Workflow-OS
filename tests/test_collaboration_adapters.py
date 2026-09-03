"""
Tests for Chat & Collaboration Event Adapters (MS Teams, Zoom, Slack)
"""
import json
import pytest
from app.server.api import create_app
from app.server.events.schema import SDLCEventType, SDLCCategory, SDLCRiskLevel
from app.server.events.registry import get_event_registry


def test_msteams_normalizer():
    registry = get_event_registry()
    
    payload = {
        "title": "Release v2.0 Deployed to Production",
        "summary": "Deployment Completed",
        "from": {"name": "DevOps Bot"}
    }
    
    event = registry.ingest(payload, category="ticket", provider="msteams")
    assert event.source == "msteams"
    assert event.category == SDLCCategory.TICKET
    assert event.event_type == SDLCEventType.ISSUE_UPDATED
    assert event.actor.name == "DevOps Bot"
    assert event.health_impact.score_delta == 1.0


def test_zoom_meeting_normalizer():
    registry = get_event_registry()
    
    # Meeting started
    start_payload = {
        "event": "meeting.started",
        "payload": {
            "object": {"topic": "P0 Outage Incident War-Room"}
        }
    }
    start_event = registry.ingest(start_payload, category="code", provider="zoom")
    assert start_event.source == "zoom"
    assert start_event.category == SDLCCategory.CODE
    assert start_event.event_type == SDLCEventType.GENERIC_SIGNAL
    assert start_event.repository == "P0 Outage Incident War-Room"
    assert start_event.health_impact.score_delta == 1.0

    # Meeting ended
    end_payload = {
        "event": "meeting.ended",
        "payload": {
            "object": {"topic": "P0 Outage Incident War-Room"}
        }
    }
    end_event = registry.ingest(end_payload, category="code", provider="zoom")
    assert end_event.event_type == SDLCEventType.GENERIC_SIGNAL
    assert end_event.health_impact.score_delta == 0.0


def test_collaboration_ingest_endpoints(tmp_path):
    app = create_app(repo_path=str(tmp_path), memory_path=str(tmp_path / ".memory"))
    app.config["TESTING"] = True
    client = app.test_client()

    # MS Teams ingestion
    res = client.post(
        "/api/v1/ingest/ticket/msteams",
        data=json.dumps({"title": "Critical Patch Sync"}),
        content_type="application/json"
    )
    assert res.status_code == 200
    assert res.get_json()["event"]["source"] == "msteams"

    # Zoom ingestion
    res = client.post(
        "/api/v1/ingest/code/zoom",
        data=json.dumps({"event": "meeting.started", "payload": {"object": {"topic": "Sprint Retro"}}}),
        content_type="application/json"
    )
    assert res.status_code == 200
    assert res.get_json()["event"]["source"] == "zoom"
