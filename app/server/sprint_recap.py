from __future__ import annotations

from typing import Any

from app.server.command_centre import CommandCentre


def generate_sprint_recap(repo_path: str, memory_path: str) -> dict[str, Any]:
    """Generate comprehensive sprint recap via CommandCentre."""
    centre = CommandCentre(repo_path=repo_path, memory_path=memory_path)
    return centre.generate_sprint_recap()


def validate_feature_parity(repo_path: str, memory_path: str) -> dict[str, Any]:
    """Validate that planned features match implemented features via CommandCentre."""
    centre = CommandCentre(repo_path=repo_path, memory_path=memory_path)
    return centre.validate_feature_parity()


def generate_project_snapshot(repo_path: str, memory_path: str) -> dict[str, Any]:
    """Generate consolidated snapshot of project state via CommandCentre."""
    centre = CommandCentre(repo_path=repo_path, memory_path=memory_path)
    return centre.generate_project_snapshot()

