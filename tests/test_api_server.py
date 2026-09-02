import json
import subprocess
from pathlib import Path

import pytest


def test_dashboard_root_serves_the_ui():
    """The app should serve the dashboard HTML at the root URL."""
    from app.server.api import create_app

    app = create_app(repo_path=".", memory_path=".memory")
    client = app.test_client()

    response = client.get("/")
    assert response.status_code == 200
    assert b"Developer Workflow OS" in response.data


def test_dashboard_root_includes_recent_artifacts_widget():
    """The dashboard should expose the recent-artifacts command-centre widget."""
    from app.server.api import create_app

    app = create_app(repo_path=".", memory_path=".memory")
    client = app.test_client()

    response = client.get("/")
    assert response.status_code == 200
    assert b"Recent artifacts" in response.data
    assert b"/api/artifacts?limit=5" in response.data


def test_api_server_exposes_repo_memory_endpoint(tmp_path):
    """Test that the API server can return repo memory data."""
    from app.server.api import create_app

    repo = tmp_path / "api-test-repo"
    repo.mkdir()

    subprocess.run(
        ["git", "init", "-b", "main"],
        cwd=str(repo),
        capture_output=True,
        text=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )

    (repo / "README.md").write_text("test project\n")
    (repo / "app.py").write_text("print('hello')\n")

    subprocess.run(
        ["git", "add", "."],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )

    app = create_app(repo_path=str(repo))
    client = app.test_client()

    response = client.get("/api/repo/index")
    assert response.status_code == 200

    data = response.get_json()
    assert data is not None
    assert "repo_name" in data
    assert "areas" in data
    assert "key_files" in data


def test_api_server_exposes_feature_context_with_risk_and_docs(tmp_path):
    """Feature drill-down should surface likely implementation files, tests, docs, and risks."""
    from app.server.api import create_app

    repo = tmp_path / "feature-drilldown-repo"
    repo.mkdir()

    subprocess.run(["git", "init", "-b", "main"], cwd=str(repo), capture_output=True, text=True, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(repo), capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(repo), capture_output=True, check=True)

    (repo / "README.md").write_text("Login flow documentation\n")
    (repo / "auth").mkdir()
    (repo / "auth" / "login.py").write_text("def login():\n    return 'ok'\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_login.py").write_text("def test_login():\n    assert True\n")
    (repo / "docs").mkdir()
    (repo / "docs" / "login.md").write_text("Login docs\n")
    subprocess.run(["git", "add", "."], cwd=str(repo), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=str(repo), capture_output=True, check=True)

    app = create_app(repo_path=str(repo))
    client = app.test_client()

    response = client.get("/api/repo/feature?feature=login")
    assert response.status_code == 200

    data = response.get_json()
    assert data is not None
    assert "feature" in data
    assert "related_files" in data
    assert "likely_implementation_surface" in data
    assert "tests" in data
    assert "docs" in data
    assert "risk_notes" in data
    assert "checklist" in data
    assert any("login" in item.lower() for item in data["related_files"])
    assert any("test_login" in item for item in data["tests"])
    assert any("login" in item.lower() for item in data["docs"])


def test_api_server_exposes_branch_summary_endpoint(tmp_path):
    """Test that the API server can return branch summary data."""
    from app.server.api import create_app

    repo = tmp_path / "branch-api-repo"
    repo.mkdir()

    subprocess.run(
        ["git", "init", "-b", "main"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )

    (repo / "README.md").write_text("test\n")
    subprocess.run(
        ["git", "add", "."],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )

    subprocess.run(
        ["git", "checkout", "-b", "feature/test"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    (repo / "app.py").write_text("print('hello')\n")
    subprocess.run(
        ["git", "add", "."],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "add app"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )

    app = create_app(repo_path=str(repo))
    client = app.test_client()

    response = client.get("/api/branch/summary?base=main&target=feature/test")
    assert response.status_code == 200

    data = response.get_json()
    assert data is not None
    assert "changed_files" in data
    assert "summary" in data
    assert "risk_areas" in data


def test_api_server_exposes_release_readiness_endpoint(tmp_path):
    """Test that the API server can return release readiness data."""
    from app.server.api import create_app

    repo = tmp_path / "release-api-repo"
    repo.mkdir()

    subprocess.run(
        ["git", "init", "-b", "main"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )

    (repo / "README.md").write_text("test\n")
    subprocess.run(
        ["git", "add", "."],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )

    app = create_app(repo_path=str(repo))
    client = app.test_client()

    response = client.get("/api/release/readiness")
    assert response.status_code == 200

    data = response.get_json()
    assert data is not None
    assert "score" in data
    assert "status" in data
    assert "blockers" in data
    assert "summary" in data


def test_api_server_exposes_weekly_digest_endpoint(tmp_path):
    """Test that the API server can return weekly digest data."""
    from app.server.api import create_app

    repo = tmp_path / "digest-api-repo"
    repo.mkdir()

    subprocess.run(
        ["git", "init", "-b", "main"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )

    (repo / "README.md").write_text("test\n")
    subprocess.run(
        ["git", "add", "."],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )

    app = create_app(repo_path=str(repo))
    client = app.test_client()

    response = client.get("/api/digest/weekly")
    assert response.status_code == 200

    data = response.get_json()
    assert data is not None
    assert "repo_name" in data
    assert "release_score" in data
    assert "summary" in data


def test_api_server_stores_and_retrieves_artifacts(tmp_path):
    """Test that the API server can store and retrieve artifacts."""
    from app.server.api import create_app

    repo = tmp_path / "artifact-api-repo"
    repo.mkdir()

    subprocess.run(
        ["git", "init", "-b", "main"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )

    (repo / "README.md").write_text("test\n")
    subprocess.run(
        ["git", "add", "."],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )

    memory_dir = tmp_path / "memory"
    app = create_app(repo_path=str(repo), memory_path=str(memory_dir))
    client = app.test_client()

    # Store an artifact
    response = client.post(
        "/api/artifacts",
        json={
            "name": "test_digest",
            "type": "weekly_digest",
            "content": {"summary": "test", "commits": 5},
            "tags": ["test"],
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    artifact_id = data["id"]

    # Retrieve the artifact
    response = client.get(f"/api/artifacts/{artifact_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "test_digest"
    assert data["content"]["summary"] == "test"

    # List artifacts
    response = client.get("/api/artifacts?type=weekly_digest")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["artifacts"]) > 0


def test_api_server_retrieves_latest_artifact(tmp_path):
    """Test that the API server can retrieve the latest artifact of a type."""
    from app.server.api import create_app

    repo = tmp_path / "latest-api-repo"
    repo.mkdir()

    subprocess.run(
        ["git", "init", "-b", "main"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )

    (repo / "README.md").write_text("test\n")
    subprocess.run(
        ["git", "add", "."],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )

    memory_dir = tmp_path / "memory"
    app = create_app(repo_path=str(repo), memory_path=str(memory_dir))
    client = app.test_client()

    # Store multiple artifacts
    client.post(
        "/api/artifacts",
        json={
            "name": "old",
            "type": "weekly_digest",
            "content": {"version": 1},
        },
    )
    client.post(
        "/api/artifacts",
        json={
            "name": "new",
            "type": "weekly_digest",
            "content": {"version": 2},
        },
    )

    # Get the latest
    response = client.get("/api/artifacts/latest?type=weekly_digest")
    assert response.status_code == 200
    data = response.get_json()
    assert data["content"]["version"] == 2


def test_api_server_masks_internal_exceptions_and_stack_traces(monkeypatch):
    """Verify that unexpected exceptions return sanitized messages without leaking stack traces."""
    from app.server.api import create_app

    app = create_app(repo_path=".")
    client = app.test_client()

    def mock_broken_index(_):
        raise RuntimeError("SecretDBConnectionFailed: at /internal/secrets/db.key line 42")

    monkeypatch.setattr("app.server.api.index_repo", mock_broken_index)

    response = client.get("/api/repo/index")
    assert response.status_code == 500
    data = response.get_json()
    assert data == {"error": "An internal error occurred."}
    assert "SecretDBConnectionFailed" not in response.get_data(as_text=True)
    assert "/internal/secrets" not in response.get_data(as_text=True)

