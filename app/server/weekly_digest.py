"""Weekly project digest generation module."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.server.adapters.git import GitInspector, SubprocessGitAdapter
from app.server.release_readiness import assess_release_readiness


def generate_weekly_digest(
    repo_path: str,
    base_branch: str = "main",
    limit: int = 10,
    git_adapter: GitInspector | None = None,
) -> dict[str, Any]:
    """Generate a weekly digest including recent commits, branch counts, and release readiness."""
    repo = Path(repo_path)
    adapter = git_adapter or SubprocessGitAdapter(repo_path)

    commits = adapter.recent_commits(base_branch, limit=limit)
    stats = adapter.repo_stats(base_branch)
    total_commits = stats["commit_count"]
    branch_count = stats["branch_count"]

    readiness = assess_release_readiness(repo_path, base_branch, git_adapter=adapter)
    release_score = readiness.get("score", 0)
    blockers = readiness.get("blockers", [])

    commit_summary = f"Latest {len(commits)} commit(s):"
    if commits:
        commit_lines = [f"  • {commit}" for commit in commits[:5]]
        commit_summary += "\n" + "\n".join(commit_lines)
        if len(commits) > 5:
            commit_summary += f"\n  ... and {len(commits) - 5} more"

    blocker_text = ""
    if blockers:
        blocker_text = "\n\nBlockers:\n"
        blocker_text += "\n".join(f"  • {blocker}" for blocker in blockers)

    summary = (
        f"Weekly digest for {repo.name}:\n"
        f"• Total commits on {base_branch}: {total_commits}\n"
        f"• Branches: {branch_count}\n"
        f"• Release readiness: {release_score}/100 ({readiness.get('status', 'unknown')})\n"
        f"\n{commit_summary}"
        f"{blocker_text}"
    )

    return {
        "repo_name": repo.name,
        "repo_path": str(repo),
        "base_branch": base_branch,
        "recent_commits": commits,
        "total_commits": total_commits,
        "branch_count": branch_count,
        "release_score": release_score,
        "release_status": readiness.get("status", "unknown"),
        "blockers": blockers,
        "summary": summary,
    }
