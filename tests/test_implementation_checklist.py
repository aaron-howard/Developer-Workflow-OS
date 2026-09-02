from app.server.implementation_checklist import generate_implementation_checklist


def test_generate_implementation_checklist_builds_action_plan(tmp_path):
    repo = tmp_path / "project"
    (repo / "app" / "auth").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "docs").mkdir()

    (repo / "app" / "auth" / "login.py").write_text("def login():\n    return True\n", encoding="utf-8")
    (repo / "tests" / "test_login.py").write_text("def test_login():\n    assert True\n", encoding="utf-8")
    (repo / "docs" / "auth.md").write_text("Auth flow\n", encoding="utf-8")

    result = generate_implementation_checklist(str(repo), "auth")

    assert result["feature"] == "auth"
    assert result["checklist"]
    assert any("login" in item.lower() for item in result["checklist"])
    assert any("test" in item.lower() for item in result["checklist"])
    assert any("doc" in item.lower() or "release" in item.lower() for item in result["checklist"])


def test_feature_checklist_api_exposes_plan(tmp_path):
    from app.server.api import create_app

    repo = tmp_path / "checklist-api-repo"
    repo.mkdir()
    (repo / "app").mkdir()
    (repo / "tests").mkdir()
    (repo / "docs").mkdir()
    (repo / "app" / "auth.py").write_text("def auth():\n    return True\n", encoding="utf-8")
    (repo / "tests" / "test_auth.py").write_text("def test_auth():\n    assert True\n", encoding="utf-8")
    (repo / "docs" / "auth.md").write_text("Auth docs\n", encoding="utf-8")

    app = create_app(repo_path=str(repo), memory_path=str(tmp_path / "memory"))
    client = app.test_client()

    response = client.get("/api/feature/checklist?feature=auth")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["feature"] == "auth"
    assert payload["checklist"]
