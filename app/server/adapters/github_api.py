"""GitHub REST API integration adapter implementing GitInspector."""

from __future__ import annotations

import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from app.server.adapters.git import FileDiff, GitInspector, RepoStats


def parse_github_repo_nwo(repo_path: str | Path = ".") -> str | None:
    """
    Parse repository name-with-owner (e.g. 'owner/repo') from environment or git remote.origin.url.
    """
    # 1. Direct environment variable override
    env_nwo = os.environ.get("GITHUB_REPOSITORY") or os.environ.get("GITHUB_REPO")
    if env_nwo and "/" in env_nwo:
        return env_nwo.strip()

    # 2. Extract from git remote origin URL if in git directory
    try:
        remote_url = subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"],
            cwd=str(repo_path),
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()

        # Handle SSH: git@github.com:owner/repo.git or git@github.com:owner/repo
        # Handle HTTPS: https://github.com/owner/repo.git or https://github.com/owner/repo
        match = re.search(r"github\.com[:/]([^/]+)/([^/\.]+)(?:\.git)?$", remote_url)
        if match:
            return f"{match.group(1)}/{match.group(2)}"
    except (subprocess.CalledProcessError, OSError):
        pass

    return None


class GitHubApiAdapter(GitInspector):
    """
    Production GitInspector adapter fetching repository data directly from GitHub REST API.
    """

    def __init__(
        self,
        repo_nwo: str,
        token: str | None = None,
        timeout: int = 5,
        repo_path: str = ".",
    ) -> None:
        """Initialize adapter with GitHub target repo (owner/repo) and optional PAT token."""
        self.repo_nwo = repo_nwo
        self.token = token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        self.timeout = timeout
        self.repo_path = repo_path
        self.api_base = "https://api.github.com"

    def _http_get(self, endpoint: str) -> tuple[Any, int]:
        """Make an authenticated HTTP GET request to GitHub REST API."""
        url = f"{self.api_base}{endpoint}"
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "DeveloperWorkflowOS/1.0")
        req.add_header("Accept", "application/vnd.github.v3+json")

        if self.token:
            # Support token prefix or raw token
            auth_val = self.token if self.token.startswith("Bearer ") or self.token.startswith("token ") else f"token {self.token}"
            req.add_header("Authorization", auth_val)

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                status_code = resp.getcode()
                body = resp.read().decode("utf-8")
                data = json.loads(body) if body else {}
                return data, status_code
        except urllib.error.HTTPError as e:
            return {"error": e.reason}, e.code
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            return {"error": str(e)}, 500

    def current_branch(self) -> str:
        """Fetch default branch from GitHub repository endpoint."""
        data, status = self._http_get(f"/repos/{self.repo_nwo}")
        if status == 200 and isinstance(data, dict):
            return data.get("default_branch", "main")
        return "main"

    def recent_commits(self, branch: str = "main", limit: int = 10) -> list[str]:
        """Fetch recent commit summaries on the specified branch from GitHub API."""
        endpoint = f"/repos/{self.repo_nwo}/commits?sha={branch}&per_page={int(limit)}"
        data, status = self._http_get(endpoint)
        if status != 200 or not isinstance(data, list):
            return []

        commits: list[str] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            sha = item.get("sha", "")[:7]
            commit_obj = item.get("commit", {})
            msg = commit_obj.get("message", "").splitlines()[0] if commit_obj.get("message") else "No message"
            if sha:
                commits.append(f"{sha} {msg}")

        return commits

    def repo_stats(self, branch: str = "main") -> RepoStats:
        """Fetch repository commit count and branch count from GitHub API."""
        # 1. Branch count
        branch_count = 1
        b_data, b_status = self._http_get(f"/repos/{self.repo_nwo}/branches?per_page=100")
        if b_status == 200 and isinstance(b_data, list):
            branch_count = len(b_data) or 1

        # 2. Commit count on specified branch
        commit_count = 0
        c_data, c_status = self._http_get(f"/repos/{self.repo_nwo}/commits?sha={branch}&per_page=100")
        if c_status == 200 and isinstance(c_data, list):
            commit_count = len(c_data)

        return RepoStats(
            commit_count=commit_count,
            branch_count=branch_count,
        )

    def diff(self, base: str, target: str = "HEAD") -> list[FileDiff]:
        """Fetch changed files between base and target using GitHub Compare API."""
        # If target is HEAD, try to resolve to default branch or current branch
        resolved_target = target
        if target == "HEAD":
            resolved_target = self.current_branch()

        endpoint = f"/repos/{self.repo_nwo}/compare/{base}...{resolved_target}"
        data, status = self._http_get(endpoint)
        if status != 200 or not isinstance(data, dict):
            return []

        files_list = data.get("files", [])
        diff_files: list[FileDiff] = []

        for item in files_list:
            if not isinstance(item, dict):
                continue
            path = item.get("filename", "")
            raw_status = item.get("status", "modified").lower()

            status = "modified"
            if raw_status in ("added", "created"):
                status = "added"
            elif raw_status in ("removed", "deleted"):
                status = "deleted"

            if path:
                diff_files.append(FileDiff(path=path, status=status))

        return diff_files
