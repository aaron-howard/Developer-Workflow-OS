import subprocess
from pathlib import Path

from app.server.branch_summary import summarize_branch


def _git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=str(repo), text=True).strip()


def test_summarize_branch_reports_changed_files_and_risk(tmp_path):
    repo = tmp_path / "branch-repo"
    repo.mkdir()

    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "Local User")
    _git(repo, "config", "user.email", "local@example.com")

    (repo / "README.md").write_text("hello\n", encoding="utf-8")
    (repo / "logic.py").write_text("value = 1\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "initial")

    _git(repo, "checkout", "-b", "feature/summary")
    (repo / "logic.py").write_text("value = 2\nprint(value)\n", encoding="utf-8")
    (repo / "notes.md").write_text("release note draft\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "change logic")

    result = summarize_branch(str(repo), "main", "feature/summary")

    assert result["base_branch"] == "main"
    assert result["target_branch"] == "feature/summary"
    assert any("logic.py" in path for path in result["changed_files"])
    assert any("risk" in item.lower() for item in result["risk_areas"])
    assert result["summary"]
