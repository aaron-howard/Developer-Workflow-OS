def test_sprint_recap_endpoint(tmp_path):
    """Test that sprint recap endpoint returns comprehensive project summary."""
    from app.server.api import create_app

    repo = tmp_path / "sprint-repo"
    repo.mkdir()
    (repo / "app").mkdir()

    app = create_app(repo_path=str(repo), memory_path=str(tmp_path / "memory"))
    client = app.test_client()

    response = client.get("/api/sprint/recap")
    assert response.status_code == 200
    payload = response.get_json()

    assert payload.get("summary") is not None
    assert payload.get("features_implemented") is not None
    assert isinstance(payload["features_implemented"], list)
    assert payload.get("tasks_completed") is not None


def test_feature_parity_validation(tmp_path):
    """Test that feature parity endpoint validates implementation completeness."""
    from app.server.api import create_app

    repo = tmp_path / "parity-repo"
    repo.mkdir()
    (repo / "app").mkdir()

    app = create_app(repo_path=str(repo), memory_path=str(tmp_path / "memory"))
    client = app.test_client()

    response = client.get("/api/features/parity")
    assert response.status_code == 200
    payload = response.get_json()

    assert payload.get("planned_features") is not None
    assert payload.get("implemented_features") is not None
    assert payload.get("parity_score") is not None
    assert isinstance(payload["parity_score"], (int, float))
    assert 0 <= payload["parity_score"] <= 100


def test_project_snapshot(tmp_path):
    """Test that project snapshot endpoint generates consolidated artifact view."""
    from app.server.api import create_app

    repo = tmp_path / "snapshot-repo"
    repo.mkdir()
    (repo / "app").mkdir()

    app = create_app(repo_path=str(repo), memory_path=str(tmp_path / "memory"))
    client = app.test_client()

    response = client.get("/api/project/snapshot")
    assert response.status_code == 200
    payload = response.get_json()

    assert payload.get("repo_name") is not None
    assert payload.get("analysis_artifacts") is not None
    assert isinstance(payload["analysis_artifacts"], list)
    assert payload.get("workflow_status") is not None
