"""Branch difference and risk summary module."""

from __future__ import annotations

from typing import Any

from app.server.adapters.git import GitInspector
from app.server.release_readiness import ReleaseReadinessAnalyzer


def summarize_branch(
    repo_path: str,
    base_branch: str,
    target_branch: str,
    git_adapter: GitInspector | None = None,
) -> dict[str, Any]:
    """Summarize differences, changed files, and risk areas between base and target branches."""
    analyzer = ReleaseReadinessAnalyzer(repo_path, git_adapter=git_adapter)
    return analyzer.summarize_branch(base_branch, target_branch)

