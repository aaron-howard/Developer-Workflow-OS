"""
Tests for Cloud Monitoring & Observability Adapters (Datadog, Sentry, PagerDuty, New Relic)
"""
import json
import pytest
from app.server.api import create_app
from app.server.events.schema import SDLCEventType, SDLCCategory, SDLCRiskLevel
from app.server.events.registry import get_event_registry


def test_datadog_monitor_normalizer():
    registry = get_event_registry()
    
    # Monitor error alert
    error_payload = {
        "alert_type": "error",
        "title": "High Memory Utilization on API Gateway",
        "hostname": "gateway-pod-01"
    }
    error_event = registry.ingest(error_payload, category="observability", provider="datadog")
    assert error_event.source == "datadog"
    assert error_event.category == SDLCCategory.OBSERVABILITY
    assert error_event.event_type == SDLCEventType.INCIDENT_CREATED
    assert error_event.health_impact.score_delta == -15.0
    assert error_event.health_impact.risk_level == SDLCRiskLevel.CRITICAL

    # Monitor recovery
    ok_payload = {
        "alert_type": "success",
        "title": "High Memory Utilization on API Gateway",
        "hostname": "gateway-pod-01"
    }
    ok_event = registry.ingest(ok_payload, category="observability", provider="datadog")
    assert ok_event.event_type == SDLCEventType.INCIDENT_RESOLVED
    assert ok_event.health_impact.score_delta == 10.0


def test_sentry_exception_normalizer():
    registry = get_event_registry()
    
    # Exception issue created
    created_payload = {
        "action": "created",
        "issue": {
            "title": "NullPointerException in UserService.getUser()",
            "culprit": "app.services.user"
        }
    }
    created_event = registry.ingest(created_payload, category="observability", provider="sentry")
    assert created_event.source == "sentry"
    assert created_event.event_type == SDLCEventType.INCIDENT_CREATED
    assert created_event.repository == "app.services.user"
    assert created_event.health_impact.score_delta == -12.0
    assert created_event.health_impact.risk_level == SDLCRiskLevel.HIGH

    # Exception issue resolved
    resolved_payload = {
        "action": "resolved",
        "issue": {
            "title": "NullPointerException in UserService.getUser()",
            "culprit": "app.services.user"
        }
    }
    resolved_event = registry.ingest(resolved_payload, category="observability", provider="sentry")
    assert resolved_event.event_type == SDLCEventType.INCIDENT_RESOLVED
    assert resolved_event.health_impact.score_delta == 8.0


def test_pagerduty_incident_normalizer():
    registry = get_event_registry()
    
    # Triggered incident
    triggered_payload = {
        "event_type": "incident.triggered",
        "incident": {
            "title": "Database connection pool exhausted",
            "service": {"summary": "db-cluster"}
        }
    }
    trig_event = registry.ingest(triggered_payload, category="observability", provider="pagerduty")
    assert trig_event.source == "pagerduty"
    assert trig_event.event_type == SDLCEventType.INCIDENT_CREATED
    assert trig_event.health_impact.score_delta == -20.0
    assert trig_event.health_impact.risk_level == SDLCRiskLevel.CRITICAL

    # Resolved incident
    resolved_payload = {
        "event_type": "incident.resolved",
        "incident": {
            "title": "Database connection pool exhausted",
            "service": {"summary": "db-cluster"}
        }
    }
    res_event = registry.ingest(resolved_payload, category="observability", provider="pagerduty")
    assert res_event.event_type == SDLCEventType.INCIDENT_RESOLVED
    assert res_event.health_impact.score_delta == 10.0


def test_newrelic_alert_normalizer():
    registry = get_event_registry()
    
    # Open APM alert
    open_payload = {
        "current_state": "open",
        "condition_name": "Response Time > 2000ms",
        "targets": [{"name": "checkout-service"}]
    }
    open_event = registry.ingest(open_payload, category="observability", provider="newrelic")
    assert open_event.source == "newrelic"
    assert open_event.event_type == SDLCEventType.INCIDENT_CREATED
    assert open_event.repository == "checkout-service"
    assert open_event.health_impact.score_delta == -10.0

    # Closed alert
    close_payload = {
        "current_state": "closed",
        "condition_name": "Response Time > 2000ms",
        "targets": [{"name": "checkout-service"}]
    }
    close_event = registry.ingest(close_payload, category="observability", provider="newrelic")
    assert close_event.event_type == SDLCEventType.INCIDENT_RESOLVED
    assert close_event.health_impact.score_delta == 8.0


def test_observability_ingest_endpoints(tmp_path):
    app = create_app(repo_path=str(tmp_path), memory_path=str(tmp_path / ".memory"))
    app.config["TESTING"] = True
    client = app.test_client()

    # Datadog ingestion
    res = client.post(
        "/api/v1/ingest/observability/datadog",
        data=json.dumps({"alert_type": "error", "title": "500 Error Spike"}),
        content_type="application/json"
    )
    assert res.status_code == 200
    assert res.get_json()["event"]["source"] == "datadog"

    # PagerDuty ingestion
    res = client.post(
        "/api/v1/ingest/observability/pagerduty",
        data=json.dumps({"event_type": "incident.triggered", "incident": {"title": "Outage"}}),
        content_type="application/json"
    )
    assert res.status_code == 200
    assert res.get_json()["event"]["eventType"] == "incident_created"
