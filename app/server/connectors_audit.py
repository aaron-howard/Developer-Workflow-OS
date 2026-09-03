"""Connectors and MCP servers audit module for Applications Level 1."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from app.server.adapters.git import SubprocessGitAdapter


def audit_connectors(repo_path: str = ".", memory_path: str = ".memory") -> dict[str, Any]:
    """
    Audit active application connectors and MCP servers.
    
    Returns a map of connected adapters, their operational status,
    and recommended connectors matching ARMS Applications Level 1.
    """
    connectors: list[dict[str, Any]] = []

    # 1. Git Local VCS Adapter
    git_adapter = SubprocessGitAdapter(repo_path)
    branch = git_adapter.current_branch()
    stats = git_adapter.repo_stats(branch)
    commit_count = stats["commit_count"] if isinstance(stats, dict) else stats.commit_count
    
    connectors.append({
        "id": "git",
        "name": "Git (Local VCS)",
        "type": "cli",
        "status": "connected",
        "details": f"Active branch: {branch}, Commits: {commit_count}",
        "tier": "built-in",
    })

    # 2. GitHub API Connector
    github_token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if github_token:
        github_status = "connected"
        github_details = "GitHub API token detected in environment"
    else:
        github_status = "available"
        github_details = "Token missing (set GITHUB_TOKEN for PR/issue sync)"

    connectors.append({
        "id": "github",
        "name": "GitHub Connector",
        "type": "api",
        "status": github_status,
        "details": github_details,
        "tier": "integration",
    })

    # 3. Jira / Linear Connector
    jira_url = os.environ.get("JIRA_URL") or os.environ.get("JIRA_BASE_URL")
    if jira_url:
        jira_status = "connected"
        jira_details = f"Connected to {jira_url}"
    else:
        jira_status = "available"
        jira_details = "Set JIRA_URL / JIRA_API_TOKEN for ticket mapping"

    connectors.append({
        "id": "jira",
        "name": "Jira / Issue Tracker",
        "type": "api",
        "status": jira_status,
        "details": jira_details,
        "tier": "integration",
    })

    # 4. Slack Notifier Webhook
    slack_webhook = os.environ.get("SLACK_WEBHOOK_URL")
    if slack_webhook:
        slack_status = "connected"
        slack_details = "Webhook URL configured for scheduled digests"
    else:
        slack_status = "available"
        slack_details = "Set SLACK_WEBHOOK_URL to enable Slack digest broadcasts"

    connectors.append({
        "id": "slack",
        "name": "Slack Notifications",
        "type": "webhook",
        "status": slack_status,
        "details": slack_details,
        "tier": "integration",
    })

    # 5. MCP Servers (Model Context Protocol)
    mcp_config_path = Path(repo_path) / ".mcp" / "config.json"
    mcp_status = "connected" if mcp_config_path.exists() else "available"
    connectors.append({
        "id": "mcp_servers",
        "name": "MCP Server Mesh",
        "type": "mcp",
        "status": mcp_status,
        "details": ".mcp configuration detected" if mcp_config_path.exists() else "No .mcp config; ready for MCP server search",
        "tier": "mcp",
    })

    recommendations = [
        {
            "name": "GitHub CLI / MCP Server",
            "unlocks": "Direct PR inspection, inline reviews, and release drafting",
            "setup": "gh auth login || npx -y @modelcontextprotocol/server-github",
        },
        {
            "name": "Slack Webhook Connector",
            "unlocks": "Automated delivery of nightly repo digests and release readiness alerts",
            "setup": "export SLACK_WEBHOOK_URL='https://hooks.slack.com/services/...'",
        },
        {
            "name": "PostgreSQL / SQLite Memory MCP",
            "unlocks": "Persistent state indexing across team members and multi-repo sessions",
            "setup": "npx -y @modelcontextprotocol/server-sqlite --db .memory/state.db",
        },
    ]

    connected_count = len([c for c in connectors if c["status"] == "connected"])
    
    return {
        "connected_count": connected_count,
        "total_count": len(connectors),
        "connectors": connectors,
        "recommendations": recommendations,
    }
