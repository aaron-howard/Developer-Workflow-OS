"""Tests for connectors audit endpoint and module."""

from app.server.connectors_audit import audit_connectors


def test_audit_connectors(tmp_path):
    result = audit_connectors(repo_path=str(tmp_path), memory_path=str(tmp_path / ".memory"))
    assert "connected_count" in result
    assert "total_count" in result
    assert "connectors" in result
    assert "recommendations" in result
    assert isinstance(result["connectors"], list)
    assert len(result["connectors"]) >= 4

    connector_ids = [c["id"] for c in result["connectors"]]
    assert "git" in connector_ids
    assert "github" in connector_ids
    assert "jira" in connector_ids
    assert "slack" in connector_ids


def test_connectors_audit_endpoint(tmp_path):
    from app.server.api import create_app

    app = create_app(repo_path=str(tmp_path), memory_path=str(tmp_path / ".memory"))
    client = app.test_client()

    response = client.get("/api/connectors/audit")
    assert response.status_code == 200
    data = response.get_json()
    assert "connectors" in data
    assert data["total_count"] >= 4
