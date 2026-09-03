"""
Tests for CI/CD and Build System Event Adapters (Jenkins, CircleCI, Gradle, Playwright)
"""
import json
import pytest
from app.server.api import create_app
from app.server.events.schema import SDLCEventType, SDLCCategory, SDLCRiskLevel
from app.server.events.registry import get_event_registry


def test_jenkins_normalizer_success_and_failure():
    registry = get_event_registry()
    
    # Success build
    pass_payload = {
        "name": "deploy-production",
        "build_number": 42,
        "status": "SUCCESS"
    }
    pass_event = registry.ingest(pass_payload, category="build", provider="jenkins")
    assert pass_event.source == "jenkins"
    assert pass_event.category == SDLCCategory.BUILD
    assert pass_event.event_type == SDLCEventType.BUILD_PASSED
    assert pass_event.health_impact.score_delta == 5.0
    assert pass_event.health_impact.risk_level == SDLCRiskLevel.LOW

    # Failed build
    fail_payload = {
        "name": "deploy-production",
        "build_number": 43,
        "status": "FAILURE"
    }
    fail_event = registry.ingest(fail_payload, category="build", provider="jenkins")
    assert fail_event.event_type == SDLCEventType.BUILD_FAILED
    assert fail_event.health_impact.score_delta == -10.0
    assert fail_event.health_impact.risk_level == SDLCRiskLevel.HIGH


def test_circleci_workflow_normalizer():
    registry = get_event_registry()
    
    payload = {
        "type": "workflow-completed",
        "workflow": {"name": "build-and-test", "status": "failed"},
        "project": {"name": "web-client"}
    }
    
    event = registry.ingest(payload, category="build", provider="circleci")
    assert event.source == "circleci"
    assert event.category == SDLCCategory.BUILD
    assert event.event_type == SDLCEventType.BUILD_FAILED
    assert event.repository == "web-client"
    assert event.health_impact.score_delta == -10.0


def test_gradle_build_telemetry_normalizer():
    registry = get_event_registry()
    
    # Successful compilation
    pass_payload = {
        "projectName": "user-service",
        "taskNames": ["compileJava", "test"],
        "durationMs": 4200,
        "failure": False
    }
    pass_event = registry.ingest(pass_payload, category="build", provider="gradle")
    assert pass_event.source == "gradle"
    assert pass_event.category == SDLCCategory.BUILD
    assert pass_event.event_type == SDLCEventType.BUILD_PASSED
    assert pass_event.health_impact.score_delta == 3.0

    # Failed task compilation
    fail_payload = {
        "projectName": "user-service",
        "taskNames": ["compileJava"],
        "durationMs": 1200,
        "failure": True
    }
    fail_event = registry.ingest(fail_payload, category="build", provider="gradle")
    assert fail_event.event_type == SDLCEventType.BUILD_FAILED
    assert fail_event.health_impact.score_delta == -5.0


def test_playwright_test_report_normalizer():
    registry = get_event_registry()
    
    # Passed test suite
    pass_payload = {
        "suite": "checkout-flow",
        "passed": 48,
        "failed": 0,
        "skipped": 2
    }
    pass_event = registry.ingest(pass_payload, category="testing", provider="playwright")
    assert pass_event.source == "playwright"
    assert pass_event.category == SDLCCategory.TESTING
    assert pass_event.event_type == SDLCEventType.TESTS_PASSED
    assert pass_event.health_impact.score_delta == 5.0

    # Failed test suite
    fail_payload = {
        "suite": "checkout-flow",
        "passed": 45,
        "failed": 3,
        "skipped": 0
    }
    fail_event = registry.ingest(fail_payload, category="testing", provider="playwright")
    assert fail_event.event_type == SDLCEventType.TESTS_FAILED
    assert fail_event.health_impact.risk_level == SDLCRiskLevel.HIGH
    assert fail_event.health_impact.score_delta == -12.0


def test_cicd_ingest_endpoints(tmp_path):
    app = create_app(repo_path=str(tmp_path), memory_path=str(tmp_path / ".memory"))
    app.config["TESTING"] = True
    client = app.test_client()

    # Jenkins ingestion
    res = client.post(
        "/api/v1/ingest/build/jenkins",
        data=json.dumps({"name": "ci-pipeline", "number": 1, "status": "SUCCESS"}),
        content_type="application/json"
    )
    assert res.status_code == 200
    assert res.get_json()["event"]["source"] == "jenkins"

    # Playwright ingestion
    res = client.post(
        "/api/v1/ingest/testing/playwright",
        data=json.dumps({"suite": "e2e-smoke", "passed": 10, "failed": 0}),
        content_type="application/json"
    )
    assert res.status_code == 200
    assert res.get_json()["event"]["eventType"] == "tests_passed"
