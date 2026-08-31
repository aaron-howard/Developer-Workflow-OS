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
    feature_name = feature.lower()
    related_files: list[str] = []
    checklist: list[str] = []

    for file in sorted(base.rglob('*')):
        if not file.is_file() or file.name.startswith('.'):
            continue
        text = file.read_text(encoding='utf-8', errors='ignore').lower()
        if feature_name in text:
            related_files.append(_safe_rel_path(base, file))

    if not related_files:
        for file in sorted(base.rglob('*')):
            if not file.is_file() or file.name.startswith('.'):
                continue
            if feature_name in file.name.lower():
                related_files.append(_safe_rel_path(base, file))

    if not related_files:
        related_files = [
            _safe_rel_path(base, path)
            for path in sorted(base.rglob('*'))
            if path.is_file() and not path.name.startswith('.')
        ][:10]

    checklist = [
        f"Review the {feature_name} flow in the selected files",
        f"Validate tests and edge cases for {feature_name}",
        f"Confirm documentation and release notes for {feature_name}",
    ]

    return {
        "feature": feature,
        "repo_path": str(base),
        "related_files": related_files[:10],
        "checklist": checklist,
    }
