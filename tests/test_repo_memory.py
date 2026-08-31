from pathlib import Path

from app.server.repo_memory import build_feature_context, index_repo


def test_index_repo_builds_area_map(tmp_path):
    repo = tmp_path / "project"
    (repo / "app" / "dashboard").mkdir(parents=True)
    (repo / "services" / "api").mkdir(parents=True)
    (repo / "docs").mkdir(parents=True)

    (repo / "app" / "dashboard" / "index.html").write_text("dashboard", encoding="utf-8")
    (repo / "services" / "api" / "server.py").write_text("server", encoding="utf-8")
    (repo / "docs" / "README.md").write_text("docs", encoding="utf-8")

    result = index_repo(str(repo))

    assert result["repo_name"] == "project"
    assert any(area["name"] == "app" for area in result["areas"])
    assert any(area["name"] == "services" for area in result["areas"])
    assert any(area["name"] == "docs" for area in result["areas"])
    assert result["key_files"]


def test_build_feature_context_finds_related_files_and_checklist(tmp_path):
    repo = tmp_path / "project"
    (repo / "app" / "auth").mkdir(parents=True)
    (repo / "services" / "gateway").mkdir(parents=True)
    (repo / "docs").mkdir(parents=True)

    (repo / "app" / "auth" / "login.py").write_text("login and auth logic", encoding="utf-8")
    (repo / "services" / "gateway" / "auth_routes.py").write_text("route auth", encoding="utf-8")
    (repo / "docs" / "auth.md").write_text("auth flow", encoding="utf-8")

    result = build_feature_context(str(repo), "auth")

    assert result["feature"] == "auth"
    assert any("login.py" in path for path in result["related_files"])
    assert any("auth_routes.py" in path for path in result["related_files"])
    assert any("auth" in item.lower() for item in result["checklist"])
