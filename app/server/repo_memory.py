from __future__ import annotations

import os
from pathlib import Path
from typing import Any


def _safe_rel_path(base_path: Path, path: Path) -> str:
    try:
        return str(path.relative_to(base_path))
    except ValueError:
        return str(path)


def index_repo(repo_path: str) -> dict[str, Any]:
    base = Path(repo_path)
    areas: list[dict[str, Any]] = []
    key_files: list[str] = []

    for child in sorted(base.iterdir(), key=lambda p: p.name.lower()):
        if child.name.startswith('.'):
            continue
        if child.is_dir():
            areas.append({
                "name": child.name,
                "path": _safe_rel_path(base, child),
                "tags": [child.name],
            })
            continue
        if child.is_file():
            key_files.append(_safe_rel_path(base, child))

    if not key_files:
        for file in sorted(base.rglob('*')):
            if file.is_file() and not file.name.startswith('.'):
                key_files.append(_safe_rel_path(base, file))

    return {
        "repo_name": base.name,
        "repo_path": str(base),
        "areas": areas,
        "key_files": key_files[:20],
    }


def build_feature_context(repo_path: str, feature: str) -> dict[str, Any]:
    base = Path(repo_path)
    feature_name = feature.strip().lower()
    if not feature_name:
        raise ValueError("feature query parameter is required")

    candidate_files = [
        path for path in sorted(base.rglob('*'))
        if path.is_file() and not path.name.startswith('.')
    ]

    related_files: list[str] = []
    likely_implementation_surface: list[str] = []
    tests: list[str] = []
    docs: list[str] = []

    for file in candidate_files:
        rel_path = _safe_rel_path(base, file)
        name_lower = file.name.lower()
        text = file.read_text(encoding='utf-8', errors='ignore').lower()

        if feature_name in name_lower or feature_name in text:
            related_files.append(rel_path)

        if feature_name in name_lower or feature_name in text:
            if any(part in str(file).lower() for part in ["/tests/", "\\tests\\", "test_"]):
                tests.append(rel_path)
            elif any(part in str(file).lower() for part in ["/docs/", "\\docs\\", ".md", "readme"]):
                docs.append(rel_path)
            else:
                likely_implementation_surface.append(rel_path)

    if not related_files:
        related_files = [
            _safe_rel_path(base, path)
            for path in candidate_files[:10]
        ]

    if not likely_implementation_surface:
        likely_implementation_surface = related_files[:5]

    if not tests:
        tests = [
            _safe_rel_path(base, path)
            for path in candidate_files
            if "test" in path.name.lower() or "/tests/" in str(path).lower() or "\\tests\\" in str(path).lower()
        ][:5]

    if not docs:
        docs = [
            _safe_rel_path(base, path)
            for path in candidate_files
            if path.suffix.lower() in {".md", ".rst", ".txt"}
        ][:5]

    risk_notes = [
        f"The feature touches {feature_name} across {len(likely_implementation_surface)} likely implementation file(s).",
        "Validate the edge cases and error paths before release.",
        "Confirm any user-facing docs or release notes match the shipped behavior.",
    ]

    checklist = [
        f"Review the {feature_name} flow in the likely implementation surface",
        f"Validate tests and edge cases for {feature_name}",
        f"Check docs and release notes for {feature_name}",
        "Confirm the change is covered by smoke or integration validation",
    ]

    return {
        "feature": feature,
        "repo_path": str(base),
        "related_files": related_files[:10],
        "likely_implementation_surface": likely_implementation_surface[:10],
        "tests": tests[:10],
        "docs": docs[:10],
        "risk_notes": risk_notes,
        "checklist": checklist,
    }
