from __future__ import annotations

from typing import Any

from app.server.repo_memory import RepoMemory


def generate_implementation_checklist(repo_path: str, feature: str) -> dict[str, Any]:
    """Build a practical implementation checklist for a feature based on repo context."""
    return RepoMemory(repo_path).generate_checklist(feature)

