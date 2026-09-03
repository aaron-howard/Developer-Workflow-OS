"""Draft release note generation module."""

from __future__ import annotations

from typing import Any

from app.server.adapters.git import GitInspector
from app.server.release_readiness import ReleaseReadinessAnalyzer


def generate_release_notes(
    repo_path: str,
    base_branch: str = "main",
    git_adapter: GitInspector | None = None,
) -> dict[str, Any]:
    """Draft a concise release note summary from the diff against the base branch."""
    analyzer = ReleaseReadinessAnalyzer(repo_path, git_adapter=git_adapter)
    return analyzer.generate_release_notes(base_branch=base_branch)

