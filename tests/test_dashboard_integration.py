def test_dashboard_release_status_widget(tmp_path):
    """Test that the dashboard can fetch release status and notes in a single call."""
    from app.server.api import create_app

    repo = tmp_path / "dashboard-release-repo"
    repo.mkdir()
    (repo / "app").mkdir()
    (repo / "tests").mkdir()
    (repo / "docs").mkdir()

    (repo / "app" / "core.py").write_text("def process():\n    pass\n", encoding="utf-8")
    (repo / "tests" / "test_core.py").write_text("def test_process():\n    pass\n", encoding="utf-8")
    (repo / "docs" / "api.md").write_text("API Docs\n", encoding="utf-8")

    app = create_app(repo_path=str(repo), memory_path=str(tmp_path / "memory"))
    client = app.test_client()

    response = client.get("/api/dashboard/release-status")
    assert response.status_code == 200
    payload = response.get_json()

    # Should provide both readiness and notes in one call
    assert payload.get("readiness")
    assert payload["readiness"].get("score") is not None
    assert payload["readiness"].get("status") is not None
    assert payload["readiness"].get("blockers") is not None

    assert payload.get("notes")
    assert payload["notes"].get("summary") is not None
    assert payload["notes"].get("changed_files") is not None


def test_dashboard_action_items_endpoint(tmp_path):
    """Test that dashboard can fetch actionable items (issues + checklists)."""
    from app.server.api import create_app

    repo = tmp_path / "dashboard-actions-repo"
    repo.mkdir()
    (repo / "app").mkdir()
    (repo / "tests").mkdir()
    (repo / "docs").mkdir()

    (repo / "app" / "auth.py").write_text("def authenticate():\n    pass\n", encoding="utf-8")
    (repo / "tests" / "test_auth.py").write_text("def test_auth():\n    pass\n", encoding="utf-8")

    app = create_app(repo_path=str(repo), memory_path=str(tmp_path / "memory"))
    client = app.test_client()

    # Query for auth-related action items
    response = client.get("/api/dashboard/action-items?context=auth")
    assert response.status_code == 200
    payload = response.get_json()

    assert payload.get("context") == "auth"
    assert payload.get("checklists")  # Implementation checklist for auth
    assert payload.get("related_issues")  # Issue mapping for auth
