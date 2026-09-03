from __future__ import annotations

from typing import Any

from app.server.repo_memory import RepoMemory


def map_issue_to_code(repo_path: str, issue_summary: str) -> dict[str, Any]:
    """Map an issue description to the likely code files that need to be modified."""
    return RepoMemory(repo_path).map_issue(issue_summary)

