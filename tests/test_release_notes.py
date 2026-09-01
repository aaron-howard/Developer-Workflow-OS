import subprocess
from pathlib import Path

from app.server.release_notes import generate_release_notes


def _git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=str(repo), text=True).strip()


def test_generate_release_notes_drafts_summary_from_recent_changes(tmp_path):
    repo = tmp_path / "release-notes-repo"
    repo.mkdir()

    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "Local User")
    _git(repo, "config", "user.email", "local@example.com")

    (repo / "README.md").write_text("release repo\n", encoding="utf-8")
    (repo / "app.py").write_text("value = 1\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "initial")

    _git(repo, "checkout", "-b", "feature/release")
    (repo / "app.py").write_text("value = 2\nprint(value)\n", encoding="utf-8")
    (repo / "notes.md").write_text("release note draft\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "ship feature")

    result = generate_release_notes(str(repo), "main")

    assert result["repo_name"] == "release-notes-repo"
    assert "summary" in result
    assert "highlights" in result
    assert any("app.py" in item for item in result["highlights"])
    assert "release" in result["summary"].lower()


def test_release_notes_api_exposes_draft_endpoint(tmp_path):
    from app.server.api import create_app

    repo = tmp_path / "release-notes-api-repo"
    repo.mkdir()

    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "Local User")
    _git(repo, "config", "user.email", "local@example.com")

    (repo / "README.md").write_text("demo\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "initial")

    _git(repo, "checkout", "-b", "feature/release")
    (repo / "service.py").write_text("print('hello')\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "add service")

    app = create_app(repo_path=str(repo), memory_path=str(tmp_path / "memory"))
    client = app.test_client()

    response = client.get("/api/release/notes")
    assert response.status_code == 200
    payload = response.get_json()
    assert "summary" in payload
    assert "highlights" in payload
