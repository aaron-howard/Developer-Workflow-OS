from __future__ import annotations

from pathlib import Path
from typing import Any


def generate_implementation_checklist(repo_path: str, feature: str) -> dict[str, Any]:
    """Build a practical implementation checklist for a feature based on repo context."""
    repo = Path(repo_path)
    feature_name = feature.strip().lower()
    if not feature_name:
        raise ValueError("feature query parameter is required")

    related = []
    tests = []
    docs = []
    implementation_targets: list[str] = []

    for path in sorted(repo.rglob("*")):
        if not path.is_file() or path.name.startswith("."):
            continue

        rel = str(path.relative_to(repo)).replace("\\", "/")
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        lower_name = path.name.lower()

        if feature_name in lower_name or feature_name in text:
            related.append(rel)
            if "test" in lower_name or "/tests/" in rel.lower():
                tests.append(rel)
            elif rel.lower().endswith((".md", ".rst", ".txt")) or "/docs/" in rel.lower():
                docs.append(rel)

    for path in sorted(repo.rglob("*")):
        if not path.is_file() or path.name.startswith("."):
            continue
        rel = str(path.relative_to(repo)).replace("\\", "/")
        lower_rel = rel.lower()
        if lower_rel.endswith((".py", ".js", ".ts")) and ("/app/" in lower_rel or "app" == lower_rel.split("/")[0]):
            implementation_targets.append(path.name)
        if len(implementation_targets) >= 3:
            break

    if not implementation_targets and related:
        implementation_targets = [Path(item).name for item in related[:3]]

    if not implementation_targets:
        implementation_targets = ["the repo entry points"]

    checklist = [
        f"Inspect the implementation surface for {feature_name}, starting with the highest-signal files such as {', '.join(implementation_targets)}.",
        f"Review the relevant tests for {feature_name} and confirm coverage for success, failure, and edge-case behavior.",
        f"Validate any documentation or release-note updates related to {feature_name}.",
        "Check integration touchpoints and confirm the change is safe to ship in context.",
    ]

    if not related:
        checklist.insert(
            0,
            f"Start by locating the likely implementation surface for {feature_name} in the repo tree and map the key files before editing.",
        )

    if tests:
        checklist.insert(1, f"Prioritize the relevant test files for {feature_name}: {', '.join(tests[:3])}.")

    if docs:
        checklist.insert(-1, f"Update and review docs for {feature_name}: {', '.join(docs[:3])}.")

    return {
        "feature": feature,
        "repo_path": str(repo),
        "checklist": checklist,
        "related_files": related[:10],
        "tests": tests[:5],
        "docs": docs[:5],
    }
