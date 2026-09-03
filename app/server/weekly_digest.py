"""Weekly project digest generation module."""

from __future__ import annotations

from typing import Any

from app.server.adapters.git import GitInspector
from app.server.release_readiness import ReleaseReadinessAnalyzer


def generate_weekly_digest(
    repo_path: str,
    base_branch: str = "main",
    limit: int = 10,
    git_adapter: GitInspector | None = None,
) -> dict[str, Any]:
    """Generate a weekly digest including recent commits, branch counts, and release readiness."""
    analyzer = ReleaseReadinessAnalyzer(repo_path, git_adapter=git_adapter)
    return analyzer.generate_weekly_digest(base_branch=base_branch, limit=limit)

