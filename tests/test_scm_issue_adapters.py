"""
Tests for SCM and Issue Tracking Event Adapters (GitLab, Azure DevOps, Jira, Linear)
"""
import json
import pytest
from app.server.api import create_app
from app.server.events.schema import SDLCEventType, SDLCCategory, SDLCRiskLevel
from app.server.events.registry import get_event_registry


def test_gitlab_merge_request_normalizer():
    registry = get_event_registry()
    payload = {
        "object_kind": "merge_request",
        "project": {"path_with_namespace": "my-group/my-project"},
        "user": {"name": "GitLab Dev", "username": "gldev"},
        "object_attributes": {
            "id": 99,
            "iid": 42,
            "state": "merged",
            "action": "merge",
            "source_branch": "feature/awesome"
        }
    }
    
    event = registry.ingest(payload, category="code", provider="gitlab")
    assert event.source == "gitlab"
    assert event.category == SDLCCategory.CODE
    assert event.event_type == SDLCEventType.PR_MERGED
    assert event.repository == "my-group/my-project"
    assert event.branch == "feature/awesome"
    assert event.actor.name == "GitLab Dev"
    assert event.health_impact.score_delta == 10.0


def test_gitlab_push_normalizer():
    registry = get_event_registry()
    payload = {
        "object_kind": "push",
        "ref": "refs/heads/main",
        "project": {"path_with_namespace": "org/repo"},
        "user": {"name": "Pusher"},
        "commits": [{"id": "1"}, {"id": "2"}]
    }

    event = registry.ingest(payload, category="code", provider="gitlab")
    assert event.source == "gitlab"
    assert event.event_type == SDLCEventType.COMMIT_PUSHED
    assert event.branch == "main"
    assert event.health_impact.score_delta == 2.0


def test_azure_devops_pull_request_normalizer():
    registry = get_event_registry()
    payload = {
        "eventType": "git.pullrequest.updated",
        "resource": {
            "pullRequestId": 101,
            "status": "completed",
            "sourceRefName": "refs/heads/feature-azure",
            "repository": {"name": "azure-repo"},
            "createdBy": {"displayName": "Azure Engineer"}
        }
    }

    event = registry.ingest(payload, category="code", provider="azure_devops")
    assert event.source == "azure_devops"
    assert event.event_type == SDLCEventType.PR_MERGED
    assert event.repository == "azure-repo"
    assert event.branch == "feature-azure"
    assert event.actor.name == "Azure Engineer"


def test_jira_blocker_detection():
    registry = get_event_registry()
    
    # Blocker issue
    blocker_payload = {
        "webhookEvent": "jira:issue_updated",
        "issue": {
            "key": "PROJ-123",
            "fields": {
                "summary": "Database connectivity loss on staging",
                "status": {"name": "Blocker"},
                "priority": {"name": "Highest"},
                "labels": ["release-blocker"]
            }
        },
        "user": {"displayName": "QA Lead"}
    }

    event = registry.ingest(blocker_payload, category="ticket", provider="jira")
    assert event.source == "jira"
    assert event.category == SDLCCategory.TICKET
    assert event.event_type == SDLCEventType.ISSUE_BLOCKED
    assert event.health_impact.risk_level == SDLCRiskLevel.HIGH
    assert event.health_impact.score_delta == -15.0
    assert "Release Blocker" in event.health_impact.message

    # Regular update
    normal_payload = {
        "webhookEvent": "jira:issue_updated",
        "issue": {
            "key": "PROJ-124",
            "fields": {
                "summary": "Update readme formatting",
                "status": {"name": "In Progress"},
                "priority": {"name": "Medium"},
                "labels": []
            }
        }
    }
    normal_event = registry.ingest(normal_payload, category="ticket", provider="jira")
    assert normal_event.event_type == SDLCEventType.ISSUE_UPDATED
    assert normal_event.health_impact.score_delta == 1.0


def test_linear_normalizer():
    registry = get_event_registry()
    payload = {
        "type": "Issue",
        "action": "update",
        "data": {
            "identifier": "ENG-404",
            "title": "Auth token expiration flaw",
            "state": {"name": "Blocked"}
        }
    }

    event = registry.ingest(payload, category="ticket", provider="linear")
    assert event.source == "linear"
    assert event.category == SDLCCategory.TICKET
    assert event.event_type == SDLCEventType.ISSUE_BLOCKED
    assert event.health_impact.risk_level == SDLCRiskLevel.HIGH
    assert event.health_impact.score_delta == -10.0


def test_scm_issue_ingest_endpoints(tmp_path):
    app = create_app(repo_path=str(tmp_path), memory_path=str(tmp_path / ".memory"))
    app.config["TESTING"] = True
    client = app.test_client()

    # GitLab ingestion endpoint
    res = client.post(
        "/api/v1/ingest/code/gitlab",
        data=json.dumps({"object_kind": "merge_request", "object_attributes": {"state": "merged"}}),
        content_type="application/json"
    )
    assert res.status_code == 200
    assert res.get_json()["event"]["source"] == "gitlab"

    # Jira ingestion endpoint
    res = client.post(
        "/api/v1/ingest/ticket/jira",
        data=json.dumps({"issue": {"key": "PAY-888", "fields": {"status": {"name": "Blocker"}}}}),
        content_type="application/json"
    )
    assert res.status_code == 200
    assert res.get_json()["event"]["eventType"] == "issue_blocked"
