from __future__ import annotations

from pathlib import Path
from typing import Any


def _extract_keywords(text: str) -> list[str]:
    """Extract significant keywords from issue text."""
    text_lower = text.lower()
    # Split on common separators and filter noise
    words = text_lower.replace("-", " ").replace("_", " ").replace(".", " ").split()
    # Filter short words and common words
    keywords = [
        w for w in words
        if len(w) > 2 and w not in {
            "the", "are", "and", "that", "this", "with", "from", "into", "users",
            "cannot", "not", "can", "be", "is", "on", "or", "at", "to", "in",
            "a", "an", "of"
        }
    ]
    return list(set(keywords))  # Deduplicate


def map_issue_to_code(repo_path: str, issue_summary: str) -> dict[str, Any]:
    """Map an issue description to the likely code files that need to be modified."""
    repo = Path(repo_path)
    issue_lower = issue_summary.lower()
    keywords = _extract_keywords(issue_summary)

    impact_map: dict[str, list[str]] = {"implementation": [], "tests": [], "docs": []}

    candidate_files = [p for p in sorted(repo.rglob("*")) if p.is_file() and not p.name.startswith(".")]

    scored_files: list[tuple[str, float]] = []

    for file_path in candidate_files:
        rel_path = str(file_path.relative_to(repo)).replace("\\", "/")
        file_name_lower = file_path.name.lower()
        # Extract words from file name for matching
        file_words = file_name_lower.replace("_", " ").replace("-", " ").replace(".", " ").split()

        try:
            file_text = file_path.read_text(encoding="utf-8", errors="ignore").lower()
        except (OSError, RuntimeError):
            file_text = ""

        # Score files based on keyword matches
        score = 0.0

        for keyword in keywords:
            if keyword in file_name_lower:
                score += 3.0
            elif keyword in file_text:
                score += 1.0
            # Handle plurals like "payments" matching "payment"
            elif any(keyword.rstrip('s') == word or keyword == word.rstrip('s') for word in file_words):
                score += 2.5
            # Partial word match
            elif any(keyword in word for word in file_words):
                score += 2.0

        # If no exact keyword match, include files from app/src directories
        if score == 0 and any(part in rel_path.lower() for part in ["/app/", "\\app\\", "src/"]):
            score = 0.5

        if score > 0:
            scored_files.append((rel_path, score))

    # Sort by score descending
    scored_files.sort(key=lambda x: x[1], reverse=True)
    related_files = [path for path, _ in scored_files[:15]]

    # Categorize files by impact
    for rel_path in related_files:
        if any(part in rel_path.lower() for part in ["test", "/tests/", "\\tests\\"]):
            impact_map["tests"].append(rel_path)
        elif any(part in rel_path.lower() for part in [".md", ".rst", "/docs/", "\\docs\\", "readme"]):
            impact_map["docs"].append(rel_path)
        else:
            impact_map["implementation"].append(rel_path)

    # Ensure each category has files if they exist in the repo
    if not impact_map["implementation"]:
        impact_map["implementation"] = [f for f in related_files if f not in impact_map["tests"] + impact_map["docs"]][:5]

    if not impact_map["tests"]:
        impact_map["tests"] = [
            str(p.relative_to(repo)).replace("\\", "/")
            for p in candidate_files
            if any(part in p.name.lower() for part in ["test", "_test"])
        ][:3]

    if not impact_map["docs"]:
        impact_map["docs"] = [
            str(p.relative_to(repo)).replace("\\", "/")
            for p in candidate_files
            if p.suffix.lower() in {".md", ".rst"}
        ][:3]

    suggested_checklist = [
        f"Identify which files in the implementation layer will be modified to address: {issue_summary}",
        f"Update the relevant test files to cover the new behavior or bug fix.",
        "Validate all existing tests continue to pass.",
        "Review and update documentation if user-facing behavior changes.",
        "Create a release note entry for this issue resolution.",
    ]

    return {
        "issue_summary": issue_summary,
        "repo_path": str(repo),
        "keywords": keywords[:10],
        "related_files": related_files,
        "impact_map": impact_map,
        "suggested_checklist": suggested_checklist,
    }
