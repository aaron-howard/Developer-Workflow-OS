from __future__ import annotations

from typing import Any

from app.server.implementation_checklist import generate_implementation_checklist
from app.server.issue_mapping import map_issue_to_code
from app.server.release_notes import generate_release_notes
from app.server.release_readiness import assess_release_readiness


def get_release_status(repo_path: str, base_branch: str = "main") -> dict[str, Any]:
    """Fetch combined release readiness and notes for the dashboard."""
    readiness = assess_release_readiness(repo_path, base_branch)
    notes = generate_release_notes(repo_path, base_branch)

    return {
        "readiness": readiness,
        "notes": notes,
    }


def get_action_items(repo_path: str, context: str) -> dict[str, Any]:
    """Fetch implementation checklist and issue mapping for a given context."""
    checklist = generate_implementation_checklist(repo_path, context)
    issue_map = map_issue_to_code(repo_path, f"Fix {context}")

    return {
        "context": context,
        "checklists": checklist["checklist"],
        "related_files": checklist["related_files"],
        "impact_map": issue_map["impact_map"],
        "related_issues": issue_map["related_files"],
        "suggested_checklist": issue_map["suggested_checklist"],
    }
