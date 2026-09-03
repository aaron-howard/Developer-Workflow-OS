"""
Tests for Canonical SDLC Event Ingestion Engine
"""
import hmac
import hashlib
import json
import pytest
from app.server.api import create_app
from app.server.events.schema import (
    SDLCEvent,
    SDLCCategory,
    SDLCEventType,
    SDLCRiskLevel,
    SDLCHealthImpact,
    SDLCActor
)
from app.server.events.security import verify_hmac_signature
from app.server.events.registry import get_event_registry


def test_sdlc_event_serialization():
    event = SDLCEvent(
        source="github",
        category=SDLCCategory.CODE,
        event_type=SDLCEventType.PR_MERGED,
        repository="aaron-howard/Developer-Workflow-OS",
        branch="feature/issue-12",
        actor=SDLCActor(name="aaron", email="aaron@example.com"),
        health_impact=SDLCHealthImpact(score_delta=10.0, risk_level=SDLCRiskLevel.LOW, message="PR merged successfully")
    )
    
    data = event.to_dict()
    assert data["source"] == "github"
    assert data["category"] == "code"
    assert data["eventType"] == "pr_merged"
    assert data["repository"] == "aaron-howard/Developer-Workflow-OS"
    assert data["actor"]["name"] == "aaron"
    assert data["healthImpact"]["scoreDelta"] == 10.0

    deserialized = SDLCEvent.from_dict(data)
    assert deserialized.source == event.source
    assert deserialized.category == event.category
    assert deserialized.event_type == event.event_type
    assert deserialized.health_impact.score_delta == 10.0


def test_verify_hmac_signature():
    secret = "my_super_secret_webhook_key"
    payload = b'{"event": "push", "repository": "test-repo"}'
    
    expected_hash = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    
    # Matching signature with sha256= prefix
    assert verify_hmac_signature(payload, secret, f"sha256={expected_hash}") is True
    # Matching raw hex signature
    assert verify_hmac_signature(payload, secret, expected_hash) is True
    # Invalid signature
    assert verify_hmac_signature(payload, secret, "sha256=invalid_hash_value") is False
    # Missing signature header
    assert verify_hmac_signature(payload, secret, None) is False
    # Empty secret should bypass
    assert verify_hmac_signature(payload, "", None) is True


def test_event_registry():
    registry = get_event_registry()
    
    # Generic fallback
    generic_event = registry.ingest(
        raw_payload={"repository": "demo-repo", "branch": "main", "eventType": "build_passed"},
        category="build",
        provider="custom_ci"
    )
    assert generic_event.source == "custom_ci"
    assert generic_event.category == SDLCCategory.BUILD
    assert generic_event.event_type == SDLCEventType.BUILD_PASSED
    assert generic_event.repository == "demo-repo"

    # GitHub provider normalizer
    github_event = registry.ingest(
        raw_payload={
            "action": "merged",
            "pull_request": {"number": 12, "merged": True, "head": {"ref": "feature-branch"}},
            "repository": {"full_name": "org/repo"},
            "sender": {"login": "octocat"}
        },
        category="code",
        provider="github"
    )
    assert github_event.source == "github"
    assert github_event.category == SDLCCategory.CODE
    assert github_event.event_type == SDLCEventType.PR_MERGED
    assert github_event.repository == "org/repo"
    assert github_event.actor.name == "octocat"


def test_universal_ingest_api(tmp_path):
    app = create_app(repo_path=str(tmp_path), memory_path=str(tmp_path / ".memory"))
    app.config["TESTING"] = True
    client = app.test_client()

    payload = {
        "repository": "my-org/my-app",
        "branch": "main",
        "eventType": "deploy_success",
        "actor": "release-bot"
    }

    response = client.post(
        "/api/v1/ingest/deploy/kubernetes",
        data=json.dumps(payload),
        content_type="application/json"
    )
    
    assert response.status_code == 200
    res_data = response.get_json()
    assert res_data["status"] == "success"
    assert res_data["event"]["source"] == "kubernetes"
    assert res_data["event"]["category"] == "deploy"
    assert res_data["event"]["eventType"] == "deploy_success"
