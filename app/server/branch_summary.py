"""Branch difference and risk summary module."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.server.adapters.git import GitInspector, SubprocessGitAdapter


def summarize_branch(
    repo_path: str,
    base_branch: str,
    target_branch: str,
    git_adapter: GitInspector | None = None,
) -> dict[str, Any]:
    """Summarize differences, changed files, and risk areas between base and target branches."""
    repo = Path(repo_path)
    adapter = git_adapter or SubprocessGitAdapter(repo_path)

    diff_items = adapter.diff(base_branch, target_branch)
    changed_files = [item.path for item in diff_items]
    change_summary = []

    for item in diff_items:
        if item.is_code:
            change_summary.append(f"Code update in {item.path} likely affects runtime behavior")
        elif item.is_doc:
            change_summary.append(f"Documentation update in {item.path} may affect release notes or onboarding")
        else:
            change_summary.append(f"Updated {item.path}")

    risk_areas = []
    if any(item.is_code for item in diff_items):
        risk_areas.append("Runtime behavior risk in application logic")
    if any(item.is_doc for item in diff_items):
        risk_areas.append("Documentation drift risk")
    if not risk_areas:
        risk_areas.append("No major risk signals detected from the current diff")

    summary_lines = [
        f"Branch {target_branch} differs from {base_branch}.",
        "This change set includes:",
    ]
    summary_lines.extend(f"- {item}" for item in change_summary[:6])
    summary_lines.append("Review should focus on runtime impact, docs, and release impact.")

    return {
        "base_branch": base_branch,
        "target_branch": target_branch,
        "changed_files": changed_files,
        "summary": "\n".join(summary_lines),
        "risk_areas": risk_areas,
    }
