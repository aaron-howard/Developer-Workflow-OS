"""Release readiness evaluation and git change analysis module."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.server.adapters.git import GitInspector, SubprocessGitAdapter


class ReleaseReadinessAnalyzer:
    """
    Deep module responsible for git change inspection, release readiness scoring,
    release note generation, branch summaries, and weekly digest aggregation.
    """

    def __init__(self, repo_path: str, git_adapter: GitInspector | None = None) -> None:
        """Initialize analyzer with repository path and optional git adapter."""
        self.repo_path = str(repo_path)
        self.repo = Path(repo_path)
        self.adapter = git_adapter or SubprocessGitAdapter(self.repo_path)

    def assess_readiness(self, base_branch: str = "main") -> dict[str, Any]:
        """Assess whether a repository is ready for release based on branch diff and blockers."""
        blockers: list[str] = []
        checks: list[str] = []

        if not self.repo.exists():
            return {
                "score": 0,
                "status": "blocked",
                "blockers": [f"Repository path does not exist: {self.repo_path}"],
                "summary": "Release readiness is blocked because the repository path is missing.",
                "checks": [],
            }

        branch = self.adapter.current_branch()

        if not (self.repo / ".git").exists() and not hasattr(self.adapter, "is_mock"):
            checks.append("Repository is not a git checkout; release readiness is based on workspace scan only")

        diff_items = self.adapter.diff(base_branch, branch)
        files = [item.path for item in diff_items]

        if not files:
            checks.append("No local branch diff detected against the base branch")
            blockers.append("No code changes currently queued for release")

        has_code = any(path.endswith((".py", ".js", ".ts", ".java", ".cs")) for path in files)
        has_tests = any("test" in path.lower() for path in files)
        has_docs = any(path.endswith(".md") for path in files)

        if has_code and not has_tests:
            blockers.append("Code changes are present without matching test updates")
        if not has_docs:
            checks.append("No documentation changes were detected in the current diff")
        if not has_code:
            checks.append("No runtime code changes were detected")

        test_candidates = list(self.repo.glob("**/test*.py")) + list(self.repo.glob("**/*_test.py"))
        if not test_candidates:
            blockers.append("No obvious automated tests are present in the repo")

        score = 100
        score -= len(blockers) * 25
        score -= max(0, len(checks) - 1) * 5
        score = max(0, min(100, score))

        if blockers:
            status = "blocked" if score < 40 else "watch"
        elif score >= 80:
            status = "ready"
        else:
            status = "watch"

        summary = (
            f"Release readiness for {self.repo.name} is {status} "
            f"with a score of {score}/100. "
            f"The current change set includes {len(files)} relevant file(s); "
            f"{len(blockers)} blocker(s) were detected and {len(checks)} review signal(s) were noted."
        )

        return {
            "repo": self.repo.name,
            "base_branch": base_branch,
            "branch": branch,
            "score": score,
            "status": status,
            "blockers": blockers,
            "summary": summary,
            "checks": checks,
            "changed_files": files,
        }

    def generate_release_notes(self, base_branch: str = "main") -> dict[str, Any]:
        """Draft a concise release note summary from the diff against the base branch."""
        diff_items = self.adapter.diff(base_branch, "HEAD")
        unique_files = [item.path for item in diff_items]

        if not unique_files:
            highlight_lines = ["No code or docs changes detected against the base branch."]
            summary = (
                f"Release notes for {self.repo.name}: no changes were detected relative to {base_branch}, "
                "so the draft is intentionally minimal."
            )
        else:
            highlight_lines = []
            for item in diff_items[:5]:
                if item.is_code:
                    highlight_lines.append(f"Updated {item.path} to improve runtime behavior and application flow.")
                elif item.is_doc:
                    highlight_lines.append(f"Refreshed documentation in {item.path} to match the shipped changes.")
                else:
                    highlight_lines.append(f"Touched {item.path} as part of the current release.")

            summary = (
                f"Release notes for {self.repo.name}: the current change set introduces {len(unique_files)} file(s) "
                f"of work relative to {base_branch}. The most important changes are summarized below."
            )

        return {
            "repo_name": self.repo.name,
            "repo_path": self.repo_path,
            "base_branch": base_branch,
            "summary": summary,
            "highlights": highlight_lines,
            "changed_files": unique_files,
        }

    def summarize_branch(self, base_branch: str, target_branch: str) -> dict[str, Any]:
        """Summarize differences, changed files, and risk areas between base and target branches."""
        diff_items = self.adapter.diff(base_branch, target_branch)
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

    def generate_weekly_digest(self, base_branch: str = "main", limit: int = 10) -> dict[str, Any]:
        """Generate a weekly digest including recent commits, branch counts, and release readiness."""
        commits = self.adapter.recent_commits(base_branch, limit=limit)
        stats = self.adapter.repo_stats(base_branch)
        total_commits = stats.commit_count if hasattr(stats, "commit_count") else stats.get("commit_count", 0)
        branch_count = stats.branch_count if hasattr(stats, "branch_count") else stats.get("branch_count", 1)

        readiness = self.assess_readiness(base_branch)
        release_score = readiness.get("score", 0)
        blockers = readiness.get("blockers", [])

        commit_summary = f"Latest {len(commits)} commit(s):"
        if commits:
            commit_lines = [f"  • {commit}" for commit in commits[:5]]
            commit_summary += "\n" + "\n".join(commit_lines)
            if len(commits) > 5:
                commit_summary += f"\n  ... and {len(commits) - 5} more"

        blocker_text = ""
        if blockers:
            blocker_text = "\n\nBlockers:\n"
            blocker_text += "\n".join(f"  • {blocker}" for blocker in blockers)

        summary = (
            f"Weekly digest for {self.repo.name}:\n"
            f"• Total commits on {base_branch}: {total_commits}\n"
            f"• Branches: {branch_count}\n"
            f"• Release readiness: {release_score}/100 ({readiness.get('status', 'unknown')})\n"
            f"\n{commit_summary}"
            f"{blocker_text}"
        )

        return {
            "repo_name": self.repo.name,
            "repo_path": self.repo_path,
            "base_branch": base_branch,
            "recent_commits": commits,
            "total_commits": total_commits,
            "branch_count": branch_count,
            "release_score": release_score,
            "release_status": readiness.get("status", "unknown"),
            "blockers": blockers,
            "summary": summary,
        }


def assess_release_readiness(
    repo_path: str,
    base_branch: str = "main",
    git_adapter: GitInspector | None = None,
) -> dict[str, Any]:
    """Free function delegating to ReleaseReadinessAnalyzer for backward compatibility."""
    analyzer = ReleaseReadinessAnalyzer(repo_path, git_adapter=git_adapter)
    return analyzer.assess_readiness(base_branch=base_branch)

