from app.server.issue_mapping import map_issue_to_code


def test_map_issue_to_code_finds_related_files(tmp_path):
    """Test that issue mapping finds files related to an issue description."""
    repo = tmp_path / "project"
    (repo / "app" / "models").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "docs").mkdir()

    (repo / "app" / "models" / "user.py").write_text("class User:\n    def authenticate():\n        pass\n", encoding="utf-8")
    (repo / "app" / "auth_service.py").write_text("def verify_credentials():\n    pass\n", encoding="utf-8")
    (repo / "tests" / "test_user.py").write_text("def test_user_auth():\n    pass\n", encoding="utf-8")
    (repo / "docs" / "auth.md").write_text("Authentication flow\n", encoding="utf-8")

    result = map_issue_to_code(str(repo), "Users cannot authenticate with expired tokens")

    assert result["issue_summary"] == "Users cannot authenticate with expired tokens"
    assert result["related_files"]
    assert result["impact_map"]
    assert result["suggested_checklist"]
    assert any("user" in f.lower() or "auth" in f.lower() for f in result["related_files"])


def test_issue_mapping_api_endpoint(tmp_path):
    """Test that the issue mapping API endpoint is exposed."""
    from app.server.api import create_app

    repo = tmp_path / "issue-api-repo"
    repo.mkdir()
    (repo / "app").mkdir()
    (repo / "app" / "payment.py").write_text("def process_payment():\n    pass\n", encoding="utf-8")
    (repo / "app" / "database.py").write_text("class Database:\n    pass\n", encoding="utf-8")
    (repo / "tests").mkdir()
    (repo / "docs").mkdir()

    app = create_app(repo_path=str(repo), memory_path=str(tmp_path / "memory"))
    client = app.test_client()

    response = client.get("/api/issue/map?issue=Payments%20are%20failing%20on%20stripe%20integration")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["issue_summary"]
    assert payload["related_files"]
    assert payload["impact_map"]
