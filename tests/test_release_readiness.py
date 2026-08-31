import subprocess
from pathlib import Path

from app.server.release_readiness import assess_release_readiness


def _git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=str(repo), text=True).strip()


def test_assess_release_readiness_scores_repo_and_lists_blockers(tmp_path):
    repo = tmp_path / "release-repo"
    repo.mkdir()

    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "Local User")
    _git(repo, "config", "user.email", "local@example.com")

    (repo / "README.md").write_text("release plan\n", encoding="utf-8")
    (repo / "app.py").write_text("value = 1\n", encoding="utf-8")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_app.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "initial")

    (repo / "app.py").write_text("value = 2\n", encoding="utf-8")
    (repo / "notes.md").write_text("release note draft\n", encoding="utf-8")

    result = assess_release_readiness(str(repo), "main")

    assert result["score"] >= 0
    assert 0 <= result["score"] <= 100
    assert result["status"] in {"ready", "watch", "blocked"}
    assert isinstance(result["blockers"], list)
    assert result["summary"]
    assert "release" in result["summary"].lower()
