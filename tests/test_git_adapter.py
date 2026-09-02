"""Unit tests for GitInspector adapters and caller integrations."""

import subprocess
from pathlib import Path

from app.server.adapters.git import (
    FileDiff,
    FakeGitAdapter,
    SubprocessGitAdapter,
)
from app.server.branch_summary import summarize_branch
from app.server.release_notes import generate_release_notes
from app.server.release_readiness import assess_release_readiness
from app.server.weekly_digest import generate_weekly_digest


def _git(repo: Path, *args: str) -> str:
    """Helper to run git commands during test fixture setup."""
    return subprocess.check_output(["git", *args], cwd=str(repo), text=True).strip()


def test_fake_git_adapter_in_memory():
    """Test that FakeGitAdapter accurately returns configured in-memory state."""
    diffs = [
        FileDiff(path="app/server/api.py", status="modified"),
        FileDiff(path="docs/notes.md", status="added"),
    ]
    commits = ["abc1234 Initial commit", "def5678 Add feature"]
    stats = {"commit_count": 2, "branch_count": 1}

    fake = FakeGitAdapter(
        diff_files=diffs,
        branch="feature/test",
        commits=commits,
        stats=stats,
    )

    assert fake.current_branch() == "feature/test"
    assert fake.diff("main", "feature/test") == diffs
    assert fake.recent_commits("main", limit=1) == ["abc1234 Initial commit"]
    assert fake.repo_stats("main") == stats


def test_callers_with_fake_git_adapter(tmp_path):
    """Test that domain modules integrate seamlessly with FakeGitAdapter in memory."""
    repo = tmp_path / "mock-repo"
    repo.mkdir()
    (repo / "README.md").write_text("readme", encoding="utf-8")

    fake = FakeGitAdapter(
        diff_files=[
            FileDiff(path="logic.py", status="modified"),
            FileDiff(path="notes.md", status="added"),
        ],
        branch="feature/summary",
        commits=["1234567 feat: change logic"],
        stats={"commit_count": 1, "branch_count": 2},
    )

    # branch_summary
    branch_res = summarize_branch(str(repo), "main", "feature/summary", git_adapter=fake)
    assert branch_res["base_branch"] == "main"
    assert branch_res["target_branch"] == "feature/summary"
    assert "logic.py" in branch_res["changed_files"]
    assert any("Runtime behavior" in r for r in branch_res["risk_areas"])

    # release_notes
    notes_res = generate_release_notes(str(repo), "main", git_adapter=fake)
    assert "logic.py" in notes_res["changed_files"]
    assert any("logic.py" in h for h in notes_res["highlights"])

    # release_readiness
    readiness_res = assess_release_readiness(str(repo), "main", git_adapter=fake)
    assert readiness_res["branch"] == "feature/summary"
    assert "logic.py" in readiness_res["changed_files"]

    # weekly_digest
    digest_res = generate_weekly_digest(str(repo), "main", git_adapter=fake)
    assert digest_res["total_commits"] == 1
    assert digest_res["branch_count"] == 2
    assert "1234567 feat: change logic" in digest_res["recent_commits"]


def test_subprocess_git_adapter_with_real_repo(tmp_path):
    """Test that SubprocessGitAdapter operates correctly on a real Git repository."""
    repo = tmp_path / "real-repo"
    repo.mkdir()

    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "config", "user.email", "test@example.com")

    (repo / "README.md").write_text("initial\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "initial commit")

    _git(repo, "checkout", "-b", "feature/test")
    (repo / "app.py").write_text("print('hello')\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "add app.py")

    adapter = SubprocessGitAdapter(repo)

    assert adapter.current_branch() == "feature/test"

    diffs = adapter.diff("main", "feature/test")
    assert any(d.path == "app.py" for d in diffs)

    commits = adapter.recent_commits("feature/test", limit=5)
    assert len(commits) == 2
    assert any("add app.py" in c for c in commits)

    stats = adapter.repo_stats("feature/test")
    assert stats["commit_count"] == 2
    assert stats["branch_count"] >= 1


def test_subprocess_git_adapter_resilience_on_non_git_path(tmp_path):
    """Test that SubprocessGitAdapter gracefully handles non-git directories."""
    non_git_dir = tmp_path / "not-git"
    non_git_dir.mkdir()

    adapter = SubprocessGitAdapter(non_git_dir)

    assert adapter.current_branch() == "main"
    assert adapter.diff("main", "HEAD") == []
    assert adapter.recent_commits("main") == []
    stats = adapter.repo_stats("main")
    assert stats["commit_count"] == 0
    assert stats["branch_count"] == 1


def test_subprocess_git_adapter_prevents_option_injection(tmp_path):
    """Verify that option-prefixed revision strings cannot inject git diff flags."""
    repo = tmp_path / "inject-repo"
    repo.mkdir()

    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "config", "user.email", "test@example.com")

    (repo / "README.md").write_text("initial\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "initial commit")

    adapter = SubprocessGitAdapter(repo)

    injected_file = tmp_path / "injected_output.txt"
    malicious_ref = f"--output={injected_file}"

    # Attempting diff with malicious option as base
    diffs = adapter.diff(malicious_ref, "main")

    # Injected file must not be created
    assert not injected_file.exists()
    assert isinstance(diffs, list)
