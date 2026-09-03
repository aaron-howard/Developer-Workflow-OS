"""Repo memory module for workspace indexing, feature context, work item mapping, and checklist generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _safe_rel_path(base_path: Path, path: Path) -> str:
    try:
        return str(path.relative_to(base_path)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _extract_keywords(text: str) -> list[str]:
    """Extract significant keywords from issue/work item text."""
    text_lower = text.lower()
    words = text_lower.replace("-", " ").replace("_", " ").replace(".", " ").split()
    keywords = [
        w for w in words
        if len(w) > 2 and w not in {
            "the", "are", "and", "that", "this", "with", "from", "into", "users",
            "cannot", "not", "can", "be", "is", "on", "or", "at", "to", "in",
            "a", "an", "of"
        }
    ]
    return list(set(keywords))


class RepoMemory:
    """
    Deep module responsible for workspace indexing, feature context retrieval,
    issue-to-code mapping, and implementation checklist generation.
    """

    def __init__(self, repo_path: str) -> None:
        """Initialize RepoMemory with repository path and build internal candidate file list."""
        self.repo_path = str(repo_path)
        self.base = Path(repo_path)
        self._candidate_files: list[Path] | None = None

    def _get_candidate_files(self) -> list[Path]:
        """Lazy-loaded candidate files list avoiding redundant rglob calls."""
        if self._candidate_files is None:
            if not self.base.exists():
                self._candidate_files = []
            else:
                self._candidate_files = [
                    path for path in sorted(self.base.rglob('*'))
                    if path.is_file() and not path.name.startswith('.')
                ]
        return self._candidate_files

    def index(self) -> dict[str, Any]:
        """Index repository structure and key files."""
        areas: list[dict[str, Any]] = []
        key_files: list[str] = []

        if self.base.exists():
            for child in sorted(self.base.iterdir(), key=lambda p: p.name.lower()):
                if child.name.startswith('.'):
                    continue
                if child.is_dir():
                    areas.append({
                        "name": child.name,
                        "path": _safe_rel_path(self.base, child),
                        "tags": [child.name],
                    })
                    continue
                if child.is_file():
                    key_files.append(_safe_rel_path(self.base, child))

        if not key_files:
            for file in self._get_candidate_files():
                key_files.append(_safe_rel_path(self.base, file))

        return {
            "repo_name": self.base.name,
            "repo_path": self.repo_path,
            "areas": areas,
            "key_files": key_files[:20],
        }

    def build_feature_context(self, feature: str) -> dict[str, Any]:
        """Build feature context and map related implementation, test, and doc surfaces."""
        feature_name = feature.strip().lower()
        if not feature_name:
            raise ValueError("feature query parameter is required")

        candidate_files = self._get_candidate_files()
        related_files: list[str] = []
        likely_implementation_surface: list[str] = []
        tests: list[str] = []
        docs: list[str] = []

        for file in candidate_files:
            rel_path = _safe_rel_path(self.base, file)
            name_lower = file.name.lower()
            try:
                text = file.read_text(encoding='utf-8', errors='ignore').lower()
            except (OSError, RuntimeError):
                text = ""

            if feature_name in name_lower or feature_name in text:
                related_files.append(rel_path)

                if any(part in str(file).lower() for part in ["/tests/", "\\tests\\", "test_"]):
                    tests.append(rel_path)
                elif any(part in str(file).lower() for part in ["/docs/", "\\docs\\", ".md", "readme"]):
                    docs.append(rel_path)
                else:
                    likely_implementation_surface.append(rel_path)

        if not related_files:
            related_files = [
                _safe_rel_path(self.base, path)
                for path in candidate_files[:10]
            ]

        if not likely_implementation_surface:
            likely_implementation_surface = related_files[:5]

        if not tests:
            tests = [
                _safe_rel_path(self.base, path)
                for path in candidate_files
                if "test" in path.name.lower() or "/tests/" in str(path).lower() or "\\tests\\" in str(path).lower()
            ][:5]

        if not docs:
            docs = [
                _safe_rel_path(self.base, path)
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
            "repo_path": self.repo_path,
            "related_files": related_files[:10],
            "likely_implementation_surface": likely_implementation_surface[:10],
            "tests": tests[:10],
            "docs": docs[:10],
            "risk_notes": risk_notes,
            "checklist": checklist,
        }

    def generate_checklist(self, feature: str) -> dict[str, Any]:
        """Build a practical implementation checklist for a feature based on repo context."""
        feature_name = feature.strip().lower()
        if not feature_name:
            raise ValueError("feature query parameter is required")

        candidate_files = self._get_candidate_files()
        related = []
        tests = []
        docs = []
        implementation_targets: list[str] = []

        for path in candidate_files:
            rel = _safe_rel_path(self.base, path)
            try:
                text = path.read_text(encoding="utf-8", errors="ignore").lower()
            except (OSError, RuntimeError):
                text = ""
            lower_name = path.name.lower()

            if feature_name in lower_name or feature_name in text:
                related.append(rel)
                if "test" in lower_name or "/tests/" in rel.lower():
                    tests.append(rel)
                elif rel.lower().endswith((".md", ".rst", ".txt")) or "/docs/" in rel.lower():
                    docs.append(rel)

        for path in candidate_files:
            rel = _safe_rel_path(self.base, path)
            lower_rel = rel.lower()
            if lower_rel.endswith((".py", ".js", ".ts")) and ("/app/" in lower_rel or lower_rel.startswith("app/")):
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
            "repo_path": self.repo_path,
            "checklist": checklist,
            "related_files": related[:10],
            "tests": tests[:5],
            "docs": docs[:5],
        }

    def map_issue(self, issue_summary: str) -> dict[str, Any]:
        """Map an issue description to the likely code files that need to be modified."""
        keywords = _extract_keywords(issue_summary)
        candidate_files = self._get_candidate_files()
        impact_map: dict[str, list[str]] = {"implementation": [], "tests": [], "docs": []}
        scored_files: list[tuple[str, float]] = []

        for file_path in candidate_files:
            rel_path = _safe_rel_path(self.base, file_path)
            file_name_lower = file_path.name.lower()
            file_words = file_name_lower.replace("_", " ").replace("-", " ").replace(".", " ").split()

            try:
                file_text = file_path.read_text(encoding="utf-8", errors="ignore").lower()
            except (OSError, RuntimeError):
                file_text = ""

            score = 0.0
            for keyword in keywords:
                if keyword in file_name_lower:
                    score += 3.0
                elif keyword in file_text:
                    score += 1.0
                elif any(keyword.rstrip('s') == word or keyword == word.rstrip('s') for word in file_words):
                    score += 2.5
                elif any(keyword in word for word in file_words):
                    score += 2.0

            if score == 0 and any(part in rel_path.lower() for part in ["/app/", "app/"]):
                score = 0.5

            if score > 0:
                scored_files.append((rel_path, score))

        scored_files.sort(key=lambda x: x[1], reverse=True)
        related_files = [path for path, _ in scored_files[:15]]

        for rel_path in related_files:
            if any(part in rel_path.lower() for part in ["test", "/tests/", "\\tests\\"]):
                impact_map["tests"].append(rel_path)
            elif any(part in rel_path.lower() for part in [".md", ".rst", "/docs/", "\\docs\\", "readme"]):
                impact_map["docs"].append(rel_path)
            else:
                impact_map["implementation"].append(rel_path)

        if not impact_map["implementation"]:
            impact_map["implementation"] = [f for f in related_files if f not in impact_map["tests"] + impact_map["docs"]][:5]

        if not impact_map["tests"]:
            impact_map["tests"] = [
                _safe_rel_path(self.base, p)
                for p in candidate_files
                if any(part in p.name.lower() for part in ["test", "_test"])
            ][:3]

        if not impact_map["docs"]:
            impact_map["docs"] = [
                _safe_rel_path(self.base, p)
                for p in candidate_files
                if p.suffix.lower() in {".md", ".rst"}
            ][:3]

        suggested_checklist = [
            f"Identify which files in the implementation layer will be modified to address: {issue_summary}",
            "Update the relevant test files to cover the new behavior or bug fix.",
            "Validate all existing tests continue to pass.",
            "Review and update documentation if user-facing behavior changes.",
            "Create a release note entry for this issue resolution.",
        ]

        return {
            "issue_summary": issue_summary,
            "repo_path": self.repo_path,
            "keywords": keywords[:10],
            "related_files": related_files,
            "impact_map": impact_map,
            "suggested_checklist": suggested_checklist,
        }


def index_repo(repo_path: str) -> dict[str, Any]:
    """Free function delegating to RepoMemory."""
    return RepoMemory(repo_path).index()


def build_feature_context(repo_path: str, feature: str) -> dict[str, Any]:
    """Free function delegating to RepoMemory."""
    return RepoMemory(repo_path).build_feature_context(feature)

