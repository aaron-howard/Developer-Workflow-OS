from __future__ import annotations

import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Re-export webhook adapters for backward compatibility
from .github import GitProvider, GitHubAdapter


@dataclass(frozen=True)
class FileDiff:
    """Represents a changed file and its diff status."""
    path: str
    status: str = "modified"  # e.g., "modified", "added", "deleted", "untracked"


class GitInspector(ABC):
    """Abstract interface defining high-leverage repository inspection queries."""

    @abstractmethod
    def diff(self, base: str, target: str = "HEAD") -> list[FileDiff]:
        """Return structured list of changed files between base and target, with fallbacks."""
        pass

    @abstractmethod
    def current_branch(self) -> str:
        """Return the current checked-out branch name, defaulting to 'main'."""
        pass

    @abstractmethod
    def recent_commits(self, branch: str = "main", limit: int = 10) -> list[str]:
        """Return list of recent commit oneline summaries."""
        pass

    @abstractmethod
    def repo_stats(self, branch: str = "main") -> dict[str, int]:
        """Return summary repository stats such as commit count and branch count."""
        pass


class SubprocessGitAdapter(GitInspector):
    """Production git adapter that executes git CLI commands via subprocess."""

    def __init__(self, repo_path: str | Path):
        self.repo_path = str(repo_path)

    def _git(self, *args: str) -> str:
        return subprocess.check_output(
            ["git", *args],
            cwd=self.repo_path,
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()

    def diff(self, base: str, target: str = "HEAD") -> list[FileDiff]:
        diff_files: list[FileDiff] = []
        try:
            if target != "HEAD":
                try:
                    self._git("rev-parse", "--verify", target)
                except subprocess.CalledProcessError:
                    pass

            diff_range = f"{base}...{target}" if target != "HEAD" else f"{base}...HEAD"
            output = self._git("diff", "--name-status", diff_range)
            for line in output.splitlines():
                if not line.strip():
                    continue
                parts = line.split("\t")
                status_code = parts[0].strip().upper()
                file_path = parts[-1].strip() if len(parts) >= 2 else line.strip()

                status = "modified"
                if status_code.startswith("A"):
                    status = "added"
                elif status_code.startswith("D"):
                    status = "deleted"

                diff_files.append(FileDiff(path=file_path, status=status))

        except (subprocess.CalledProcessError, OSError):
            try:
                status_output = self._git("status", "--short")
                for line in status_output.splitlines():
                    if not line.strip():
                        continue
                    status_prefix = line[:2].strip()
                    file_path = line[3:].strip()
                    status = "untracked" if "??" in status_prefix else "modified"
                    diff_files.append(FileDiff(path=file_path, status=status))
            except (subprocess.CalledProcessError, OSError):
                return []

        # Deduplicate preserving order
        unique: list[FileDiff] = []
        seen: set[str] = set()
        for fd in diff_files:
            if fd.path and fd.path not in seen:
                unique.append(fd)
                seen.add(fd.path)
        return unique

    def current_branch(self) -> str:
        try:
            branch = self._git("branch", "--show-current")
            return branch if branch else "main"
        except (subprocess.CalledProcessError, OSError):
            return "main"

    def recent_commits(self, branch: str = "main", limit: int = 10) -> list[str]:
        try:
            output = self._git("log", f"-{limit}", "--oneline", branch)
            return [line.strip() for line in output.splitlines() if line.strip()]
        except (subprocess.CalledProcessError, OSError):
            return []

    def repo_stats(self, branch: str = "main") -> dict[str, int]:
        commit_count = 0
        branch_count = 1
        try:
            count_output = self._git("rev-list", "--count", branch)
            commit_count = int(count_output)
        except (subprocess.CalledProcessError, OSError, ValueError):
            commit_count = 0

        try:
            branch_output = self._git("branch", "-a")
            branch_count = len([b for b in branch_output.splitlines() if b.strip()]) or 1
        except (subprocess.CalledProcessError, OSError):
            branch_count = 1

        return {
            "commit_count": commit_count,
            "branch_count": branch_count,
        }


class FakeGitAdapter(GitInspector):
    """In-memory test fake adapter allowing tests to specify repository inspection state."""

    def __init__(
        self,
        diff_files: list[FileDiff] | None = None,
        branch: str = "main",
        commits: list[str] | None = None,
        stats: dict[str, int] | None = None,
    ):
        self._diff_files = diff_files or []
        self._branch = branch
        self._commits = commits or []
        self._stats = stats or {"commit_count": len(self._commits), "branch_count": 1}

    def diff(self, base: str, target: str = "HEAD") -> list[FileDiff]:
        return list(self._diff_files)

    def current_branch(self) -> str:
        return self._branch

    def recent_commits(self, branch: str = "main", limit: int = 10) -> list[str]:
        return self._commits[:limit]

    def repo_stats(self, branch: str = "main") -> dict[str, int]:
        return dict(self._stats)
