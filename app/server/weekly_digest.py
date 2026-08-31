from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from app.server.release_readiness import assess_release_readiness


def _git(repo_path: str, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=repo_path, text=True, stderr=subprocess.STDOUT).strip()


def generate_weekly_digest(repo_path: str, base_branch: str = "main", limit: int = 10) -> dict[str, Any]:
    repo = Path(repo_path)

    try:
        recent_log = _git(repo_path, "log", f"-{limit}", "--oneline", base_branch)
        commits = [line.strip() for line in recent_log.splitlines() if line.strip()]
    except subprocess.CalledProcessError:
        commits = []

    try:
        total_commits = int(_git(repo_path, "rev-list", "--count", base_branch))
    except (subprocess.CalledProcessError, ValueError):
        total_commits = 0

    try:
        branch_count = len(_git(repo_path, "branch", "-a").splitlines())
    except subprocess.CalledProcessError:
        branch_count = 0

    readiness = assess_release_readiness(repo_path, base_branch)
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
