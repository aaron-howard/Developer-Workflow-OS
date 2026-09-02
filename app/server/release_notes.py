"""Draft release note generation module."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.server.adapters.git import GitInspector, SubprocessGitAdapter


def generate_release_notes(
    repo_path: str,
    base_branch: str = "main",
    git_adapter: GitInspector | None = None,
) -> dict[str, Any]:
    """Draft a concise release note summary from the diff against the base branch."""
    repo = Path(repo_path)
    adapter = git_adapter or SubprocessGitAdapter(repo_path)

    diff_items = adapter.diff(base_branch, "HEAD")
    unique_files = [item.path for item in diff_items]

    if not unique_files:
        highlight_lines = ["No code or docs changes detected against the base branch."]
        summary = (
            f"Release notes for {repo.name}: no changes were detected relative to {base_branch}, "
            "so the draft is intentionally minimal."
        )
    else:
        highlight_lines = []
        for file_name in unique_files[:5]:
            if file_name.endswith(".py") or file_name.endswith(".js") or file_name.endswith(".ts"):
                highlight_lines.append(f"Updated {file_name} to improve runtime behavior and application flow.")
            elif file_name.endswith(".md"):
                highlight_lines.append(f"Refreshed documentation in {file_name} to match the shipped changes.")
            else:
                highlight_lines.append(f"Touched {file_name} as part of the current release.")

        summary = (
            f"Release notes for {repo.name}: the current change set introduces {len(unique_files)} file(s) "
            f"of work relative to {base_branch}. The most important changes are summarized below."
        )

    return {
        "repo_name": repo.name,
        "repo_path": str(repo),
        "base_branch": base_branch,
        "summary": summary,
        "highlights": highlight_lines,
        "changed_files": unique_files,
    }
