from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


def _git(repo_path: str, *args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=repo_path,
        text=True,
        stderr=subprocess.STDOUT,
    ).strip()


def generate_release_notes(repo_path: str, base_branch: str = "main") -> dict[str, Any]:
    """Draft a concise release note summary from the diff against the base branch."""
    repo = Path(repo_path)
    changed_files: list[str] = []

    try:
        diff_output = _git(repo_path, "diff", "--name-status", f"{base_branch}...HEAD")
        for line in diff_output.splitlines():
            if not line.strip():
                continue
            parts = [part.strip() for part in line.split("\t") if part.strip()]
            changed_files.append(parts[-1] if parts else line.strip())
    except subprocess.CalledProcessError:
        try:
            status_output = _git(repo_path, "status", "--short")
            for line in status_output.splitlines():
                if not line.strip():
                    continue
                changed_files.append(line[3:].strip())
        except subprocess.CalledProcessError:
            changed_files = []

    unique_files = []
    seen: set[str] = set()
    for item in changed_files:
        if item and item not in seen:
            unique_files.append(item)
            seen.add(item)

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
