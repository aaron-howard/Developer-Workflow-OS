"""Unit tests for GitHub REST API adapter and factory selection."""

import os
from io import BytesIO
from unittest.mock import MagicMock, patch

from app.server.adapters.git import FileDiff, RepoStats, get_git_adapter
from app.server.adapters.github_api import GitHubApiAdapter, parse_github_repo_nwo


def test_parse_github_repo_nwo_from_env(monkeypatch):
    """Test parsing NWO from GITHUB_REPOSITORY environment variable."""
    monkeypatch.setenv("GITHUB_REPOSITORY", "aaron-howard/Developer-Workflow-OS")
    nwo = parse_github_repo_nwo(".")
    assert nwo == "aaron-howard/Developer-Workflow-OS"


def test_parse_github_repo_nwo_from_git_remote():
    """Test parsing NWO from local git remote origin URL."""
    with patch("subprocess.check_output") as mock_sub:
        mock_sub.return_value = "git@github.com:octocat/Hello-World.git\n"
        nwo = parse_github_repo_nwo(".")
        assert nwo == "octocat/Hello-World"

    with patch("subprocess.check_output") as mock_sub:
        mock_sub.return_value = "https://github.com/octocat/Spoon-Knife.git\n"
        nwo = parse_github_repo_nwo(".")
        assert nwo == "octocat/Spoon-Knife"


def make_mock_response(body_bytes: bytes, status_code: int = 200) -> MagicMock:
    """Helper to construct a mock HTTP response compatible with 'with urlopen() as resp'."""
    mock_resp = MagicMock()
    mock_resp.getcode.return_value = status_code
    mock_resp.read.return_value = body_bytes
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.__exit__.return_value = False
    return mock_resp


def test_github_api_adapter_current_branch():
    """Test fetching default branch via GitHubApiAdapter."""
    adapter = GitHubApiAdapter(repo_nwo="owner/repo", token="fake_token")
    mock_resp = make_mock_response(b'{"default_branch": "main"}')

    with patch("urllib.request.urlopen", return_value=mock_resp):
        assert adapter.current_branch() == "main"


def test_github_api_adapter_recent_commits():
    """Test fetching recent commits via GitHubApiAdapter."""
    adapter = GitHubApiAdapter(repo_nwo="owner/repo", token="fake_token")
    mock_resp = make_mock_response(b'''[
        {"sha": "abc123456789", "commit": {"message": "Initial commit"}},
        {"sha": "def987654321", "commit": {"message": "Add feature"}}
    ]''')

    with patch("urllib.request.urlopen", return_value=mock_resp):
        commits = adapter.recent_commits("main", limit=2)
        assert len(commits) == 2
        assert commits[0] == "abc1234 Initial commit"
        assert commits[1] == "def9876 Add feature"


def test_github_api_adapter_repo_stats():
    """Test fetching repository stats via GitHubApiAdapter."""
    adapter = GitHubApiAdapter(repo_nwo="owner/repo", token="fake_token")

    branches_resp = make_mock_response(b'[{"name": "main"}, {"name": "feature"}]')
    commits_resp = make_mock_response(b'[{"sha": "1"}, {"sha": "2"}, {"sha": "3"}]')

    with patch("urllib.request.urlopen", side_effect=[branches_resp, commits_resp]):
        stats = adapter.repo_stats("main")
        assert stats.branch_count == 2
        assert stats.commit_count == 3


def test_github_api_adapter_diff():
    """Test fetching diff via GitHubApiAdapter compare endpoint."""
    adapter = GitHubApiAdapter(repo_nwo="owner/repo", token="fake_token")
    mock_resp = make_mock_response(b'''{
        "files": [
            {"filename": "app/main.py", "status": "modified"},
            {"filename": "docs/readme.md", "status": "added"}
        ]
    }''')

    with patch("urllib.request.urlopen", return_value=mock_resp):
        diffs = adapter.diff("main", "feature")
        assert len(diffs) == 2
        assert diffs[0] == FileDiff(path="app/main.py", status="modified")
        assert diffs[1] == FileDiff(path="docs/readme.md", status="added")



def test_get_git_adapter_factory(monkeypatch):
    """Test factory selection for GitHubApiAdapter vs SubprocessGitAdapter."""
    monkeypatch.setenv("GITHUB_TOKEN", "fake_token")
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")

    adapter = get_git_adapter(".")
    assert isinstance(adapter, GitHubApiAdapter)
    assert adapter.repo_nwo == "owner/repo"
