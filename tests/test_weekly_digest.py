import subprocess
from pathlib import Path

from app.server.weekly_digest import generate_weekly_digest


def _git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=str(repo), text=True).strip()


def test_generate_weekly_digest_produces_summary_and_recap(tmp_path):
    repo = tmp_path / "digest-repo"
    repo.mkdir()

    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "Local User")
    _git(repo, "config", "user.email", "local@example.com")

    (repo / "README.md").write_text("project outline\n", encoding="utf-8")
    (repo / "app.py").write_text("value = 1\n", encoding="utf-8")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_app.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "init: project foundation")

    _git(repo, "checkout", "-b", "feature/first")
    (repo / "app.py").write_text("value = 2\nprint(value)\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "feat: add print statement")

    _git(repo, "checkout", "main")
    _git(repo, "merge", "feature/first", "--no-ff", "-m", "Merge feature/first")

    _git(repo, "checkout", "-b", "feature/second")
    (repo / "app.py").write_text("value = 2\nprint(value)\nprint('done')\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "feat: add done message")

    result = generate_weekly_digest(str(repo), "main")

    assert result["repo_name"]
    assert isinstance(result["recent_commits"], list)
    assert len(result["recent_commits"]) > 0
    assert result["release_score"] is not None
    assert isinstance(result["summary"], str)
    assert "commit" in result["summary"].lower() or "work" in result["summary"].lower()
    assert result["blockers"] is not None
