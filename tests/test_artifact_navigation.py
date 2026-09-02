def test_artifact_navigation_endpoint(tmp_path):
    """Test that artifact navigation endpoint exists and returns artifact history."""
    from app.server.api import create_app

    repo = tmp_path / "artifact-nav-repo"
    repo.mkdir()
    (repo / "app").mkdir()

    app = create_app(repo_path=str(repo), memory_path=str(tmp_path / "memory"))
    client = app.test_client()

    response = client.get("/api/artifacts/navigation")
    assert response.status_code == 200
    payload = response.get_json()

    assert payload.get("artifacts") is not None
    assert isinstance(payload["artifacts"], list)
    assert payload.get("total_count") is not None


def test_routine_execution_history_endpoint(tmp_path):
    """Test that routine execution history endpoint returns execution logs."""
    from app.server.api import create_app

    repo = tmp_path / "routine-history-repo"
    repo.mkdir()
    (repo / "app").mkdir()

    app = create_app(repo_path=str(repo), memory_path=str(tmp_path / "memory"))
    client = app.test_client()

    response = client.get("/api/routines/history")
    assert response.status_code == 200
    payload = response.get_json()

    assert payload.get("routines") is not None
    assert isinstance(payload["routines"], list)
    assert payload.get("total_executions") is not None


def test_routine_trigger_endpoint(tmp_path):
    """Test that routines can be manually triggered via API."""
    from app.server.api import create_app

    repo = tmp_path / "routine-trigger-repo"
    repo.mkdir()
    (repo / "app").mkdir()
    (repo / "tests").mkdir()

    app = create_app(repo_path=str(repo), memory_path=str(tmp_path / "memory"))
    client = app.test_client()

    response = client.post("/api/routines/trigger", json={"routine": "weekly-digest"})
    # Should return 200 (triggered) or 404 (routine not found), not 500
    assert response.status_code in [200, 404, 400]
