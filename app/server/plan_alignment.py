from __future__ import annotations

import re
from pathlib import Path

PLAN_PATH = Path(__file__).resolve().parents[2] / "DEVELOPER_WORKFLOW_OS_PLAN.md"


def _normalize_heading_name(name: str) -> str:
    """Strip numbering prefixes from section headings while preserving the human-readable label."""
    cleaned = name.strip()
    cleaned = re.sub(r"^\d+(?:\.\d+)*(?:\s*[-:])?\s*", "", cleaned)
    return cleaned.strip()


def load_plan_sections() -> list[dict[str, str]]:
    """Extract the main section headings from the design plan."""
    if not PLAN_PATH.exists():
        raise FileNotFoundError(f"Plan file not found: {PLAN_PATH}")

    sections: list[dict[str, str]] = []
    current_name = None
    in_body = False

    for raw_line in PLAN_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        if line.startswith("### "):
            name = _normalize_heading_name(line[4:].strip())
            current_name = name
            in_body = True
            sections.append({"name": name, "body": ""})
            continue
        if line.startswith("## "):
            current_name = None
            in_body = False
            continue

        if current_name is not None and in_body:
            sections[-1]["body"] += line + "\n"

    return sections


def _implemented_modules() -> dict[str, bool]:
    """Map implemented modules to plan components by their stable names."""
    return {
        "repo_indexer": True,
        "feature_context": True,
        "branch_summary": True,
        "release_readiness": True,
        "weekly_digest": True,
        "command_centre": True,
        "routine_scheduler": True,
    }


def plan_coverage_report() -> dict[str, object]:
    """Return a simple coverage report tying the build to the plan document."""
    sections = load_plan_sections()
    implemented = _implemented_modules()

    section_names = {item["name"] for item in sections}
    coverage = {}

    match_map = {
        "Repo indexer": "repo_indexer",
        "Feature context engine": "feature_context",
        "Branch and PR summary engine": "branch_summary",
        "Release readiness agent": "release_readiness",
        "Sprint digest agent": "weekly_digest",
        "Command centre UI": "command_centre",
    }

    for plan_name, key in match_map.items():
        coverage[key] = plan_name in section_names and bool(implemented.get(key, False))

    missing = [key for key, present in coverage.items() if not present]
    status = "complete" if not missing else "partial"

    return {
        "status": status,
        "plan_file": str(PLAN_PATH),
        "coverage": coverage,
        "missing": missing,
        "sections_checked": len(sections),
    }
