"""
Tests for Cloudflare Workers, Workflows, and D1 Database Infrastructure Port
"""
import json
import pytest
from api.index import get_serverless_app, app
from app.server.db.d1_adapter import D1DatabaseAdapter
from app.server.events.schema import SDLCEvent, SDLCHealthImpact, SDLCRiskLevel, SDLCCategory, SDLCEventType, SDLCActor
from app.server.workflows.routines import NightlyDigestWorkflow, ReleaseReadinessWorkflow, Step


def test_serverless_entrypoint():
    serverless_app = get_serverless_app()
    assert serverless_app is not None
    client = serverless_app.test_client()
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "healthy"


def test_wrangler_jsonc_manifest(tmp_path):
    with open("wrangler.jsonc", "r", encoding="utf-8") as f:
        content = f.read()
    # Basic structural verification
    assert '"name": "developer-workflow-os"' in content
    assert '"main": "api/index.py"' in content
    assert '"database_name": "sdlc_monitoring_db"' in content
    assert '"class_name": "NightlyDigestWorkflow"' in content


def test_d1_database_adapter():
    adapter = D1DatabaseAdapter()
    event = SDLCEvent(
        source="github",
        category=SDLCCategory.CODE,
        event_type=SDLCEventType.PR_MERGED,
        repository="aaron-howard/Developer-Workflow-OS",
        branch="main",
        actor=SDLCActor(name="aaron-dev"),
        payload={"merged": True},
        health_impact=SDLCHealthImpact(
            score_delta=10.0,
            risk_level=SDLCRiskLevel.LOW,
            message="PR #42 merged into main"
        )
    )
    
    inserted = adapter.insert_event(event)
    assert inserted is True

    events = adapter.get_recent_events(limit=10)
    assert len(events) == 1
    assert events[0]["source"] == "github"
    assert events[0]["repository"] == "aaron-howard/Developer-Workflow-OS"
    assert events[0]["scoreDelta"] == 10.0


def test_nightly_digest_workflow():
    workflow = NightlyDigestWorkflow()
    step = Step("test-step")
    result = workflow.run({"repositories": ["repo-a", "repo-b"]}, step)
    
    assert result["status"] == "COMPLETED"
    assert result["telemetry"]["repo_count"] == 2
    assert result["health_report"]["score"] == 92.5
    assert "Overall SDLC Score 92.5%" in result["recap"]


def test_release_readiness_workflow():
    workflow = ReleaseReadinessWorkflow()
    step = Step("test-step")
    result = workflow.run({"target_branch": "release/v2.0"}, step)
    
    assert result["status"] == "COMPLETED"
    assert result["evaluation"]["is_release_ready"] is True
    assert result["evaluation"]["readiness_score"] == 98.0
