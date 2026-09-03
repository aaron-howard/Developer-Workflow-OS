# Getting Started with Developer Workflow OS

Welcome to the **Developer Workflow OS**, a local engineering command centre built on the **ARMS Framework** (**Applications**, **Routines**, **Memory**, **Skills**).

This guide walks you through setting up, running, using, and troubleshooting the application.

---

## 1. Overview & Core Features

Developer Workflow OS turns repository metadata, branch state, release readiness, and developer artifacts into an actionable visual operating surface:

- **Visual Command Centre**: Single local web dashboard (`http://localhost:5000/`) for tracking release readiness, recent commits, repository memory, and active connectors.
- **Visual Second Brain (Memory Level 3)**: Interactive D3.js node graph displaying workspace files, directory containment, router files, and reference linkages with live search and path copy.
- **Headless Skill Option Pickers (Skills Level 3)**: Trigger engineering skills directly from software buttons with selectable Model (`Sonnet 3.7`, `Opus 3.7`, `Flash 3.6`) and Effort levels (`Low`, `Medium`, `High`).
- **Interactive Artifact Store**: One-click modal viewer for recent summaries, sprint recaps, and implementation checklists.
- **Connector Audit (Applications Level 1)**: Integrated diagnostic status for Git, GitHub, Jira, and Slack integrations.

---

## 2. Prerequisites

- **Python**: Version `3.9` or higher (Python `3.14` supported).
- **Git**: Installed and available on your system `PATH`.
- **Operating System**: Windows, macOS, or Linux.

---

## 3. Installation & Environment Setup

1. **Clone or Navigate to the Repository**:
   ```bash
   cd d:\repos\agentic-os
   ```

2. **Set Up Python Virtual Environment** (Recommended):
   ```bash
   # Windows PowerShell
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Integration Environment Variables**:
   Copy [`.env.example`](file:///d:/repos/agentic-os/.env.example) to `.env` in the repository root directory and set your credentials to unlock external adapters and webhook verification:
   ```bash
   cp .env.example .env
   ```
   Or set environment variables directly in your shell or `.env` file:
   ```bash
   # Webhook HMAC Security Secret
   $env:WEBHOOK_HMAC_SECRET="your_shared_hmac_secret_key"

   # Cloudflare Workers & D1 Integration
   $env:CLOUDFLARE_API_TOKEN="your_cloudflare_api_token"
   $env:CLOUDFLARE_ACCOUNT_ID="your_cloudflare_account_id"
   $env:CLOUDFLARE_D1_DATABASE_ID="your_d1_database_id"

   # GitHub PR & API Integration
   $env:GITHUB_TOKEN="ghp_your_github_token"

   # Jira Ticket Mapping
   $env:JIRA_URL="https://yourcompany.atlassian.net"
   $env:JIRA_API_TOKEN="your_jira_token"

   # Observability & Chat Integrations
   $env:DATADOG_API_KEY="your_datadog_api_key"
   $env:SENTRY_AUTH_TOKEN="your_sentry_token"
   $env:SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
   ```

---

## 4. Starting the Application

Launch the local Flask application server:

```bash
python -m app.server.run
```

Output:
```text
 * Serving Flask app 'app.server.api'
 * Debug mode: off
 * Running on http://127.0.0.1:5000
```

Open **`http://localhost:5000/`** in any web browser to view the **Visual Command Centre**.

### Stopping the Server

- **Interactive Terminal**: Press **`Ctrl + C`** in the terminal window where the server is running.
- **PowerShell (Windows)**: Stop the process bound to port `5000`:
  ```powershell
  Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
  ```
---

## 5. Tool Integration Setup Pages (App-by-App Instructions)

Detailed setup guides for each supported tool integration, covering step-by-step instructions for **both** the third-party application (webhooks, API keys, events) and **Developer Workflow OS** (`.env` config, endpoints, signature verification):

### Source Code Management (SCM)
- **[GitHub Integration Guide](file:///d:/repos/agentic-os/docs/guides/integrations/github.md)**: Webhooks, Personal Access Tokens, `X-Hub-Signature-256`, and Actions.
- **[GitLab Integration Guide](file:///d:/repos/agentic-os/docs/guides/integrations/gitlab.md)**: Webhooks, Private Access Tokens, `X-Gitlab-Token`, and Merge Requests.

### Issue Tracking
- **[Jira Software Integration Guide](file:///d:/repos/agentic-os/docs/guides/integrations/jira.md)**: Cloud API tokens, issue webhooks, and issue-to-code mapping.
- **[Linear Integration Guide](file:///d:/repos/agentic-os/docs/guides/integrations/linear.md)**: Personal API keys, issue state webhooks, and cycle tracking.

### CI/CD Pipelines & Serverless Edge
- **[Jenkins Integration Guide](file:///d:/repos/agentic-os/docs/guides/integrations/jenkins.md)**: Pipeline Notification plugin, `Jenkinsfile` post steps, and API tokens.
- **[GitHub Actions Integration Guide](file:///d:/repos/agentic-os/docs/guides/integrations/github-actions.md)**: Workflow run webhooks, job status step notifications, and build error context.
- **[Cloudflare Workers & D1 Guide](file:///d:/repos/agentic-os/docs/guides/integrations/cloudflare.md)**: Wrangler CLI setup, Workers edge dispatcher, Workflows, and D1 SQL database initialization.

### Observability & Incident Management
- **[Datadog Integration Guide](file:///d:/repos/agentic-os/docs/guides/integrations/datadog.md)**: Webhooks integration, monitor alert channels, and release readiness risk scoring.
- **[Sentry Error Tracking Guide](file:///d:/repos/agentic-os/docs/guides/integrations/sentry.md)**: Internal Integration webhooks, issue exception triggers, and stack trace correlation.
- **[PagerDuty Integration Guide](file:///d:/repos/agentic-os/docs/guides/integrations/pagerduty.md)**: V3 Webhook subscriptions, User API tokens, and release blocker alerts.
- **[New Relic Integration Guide](file:///d:/repos/agentic-os/docs/guides/integrations/newrelic.md)**: Applied Intelligence Webhook destinations and APM performance monitoring.

### Chat & Collaboration
- **[Slack Integration Guide](file:///d:/repos/agentic-os/docs/guides/integrations/slack.md)**: Incoming Webhooks, Block Kit sprint summaries, and automated nightly digests.
- **[Microsoft Teams Integration Guide](file:///d:/repos/agentic-os/docs/guides/integrations/teams.md)**: Workflows / Incoming Webhook connectors and Adaptive Cards.
- **[Zoom Webhooks Guide](file:///d:/repos/agentic-os/docs/guides/integrations/zoom.md)**: Marketplace Webhook-Only App, meeting ended events, and cloud recording logs.

---


---

## 5. Using the Visual Command Centre

### Topbar Metric & Status Cards
- **Release Readiness**: Real-time readiness score %, release status (`READY`, `WATCH`, `BLOCK`), and active blocker count.
- **Recent Commits**: Total commit count on the main branch.
- **Repository Memory**: Active workspace root directory and total branch count.
- **Connectors (L1)**: Operational status of Git, GitHub, Jira, Slack, and MCP server mesh.

### Quick Actions (Headless Skills)
Clicking any Quick Action button opens the **Skill Option Picker**:
1. Select target **Model**: `Claude 3.7 Sonnet`, `Claude 3.7 Opus`, or `Gemini 3.6 Flash`.
2. Select **Effort Level**: `Low`, `Medium`, or `High`.
3. Provide optional context keywords (e.g., `auth`, `payments`, `main`).
4. Click **Execute Skill ⚡** to run the workflow and view results in a formatted modal. Every execution is logged to `.memory/runs.log`.

### Visual Second Brain (Memory Level 3)
1. Click **Second Brain 🧠** under Quick Actions.
2. The modal displays a zoomable visual node graph of all repository files and directories.
3. **Filter**: Click category badges (`Code`, `Docs`, `Skills`) to filter nodes.
4. **Search**: Type in the search box to highlight matching files in real time.
5. **Inspect**: Click any node to inspect file details and click **Copy Path** to copy relative paths to clipboard.

### Recent Artifacts
- The **Recent artifacts (Click to View)** section lists the latest generated summaries, recaps, and checklists.
- Click any item to view its formatted Markdown/JSON contents directly inside the detail viewer modal.

---

## 6. Command Line Utility Skills

You can also run standalone Python skills from the command line:

- **Branch Summary**:
  ```bash
  python skills/summarize_branch_changes.py --base main --target feature-branch
  ```
- **Find Feature Files**:
  ```bash
  python skills/find_feature_files.py --feature auth
  ```
- **Generate Implementation Checklist**:
  ```bash
  python skills/generate_implementation_checklist.py --feature payments
  ```
- **Draft Release Notes**:
  ```bash
  python skills/draft_release_notes.py --base main
  ```
- **Weekly Sprint Summary**:
  ```bash
  python skills/weekly_sprint_summary.py
  ```

---

## 7. Running Automated Tests

To run the complete automated test suite (86 unit and integration tests across 14 test suites):

```bash
python -m pytest
```

Expected Output:
```text
============================= 86 passed in 23.4s =============================
```

---

## 8. Troubleshooting & FAQs

### Q1: `ModuleNotFoundError: No module named 'app'`
**Cause**: Running python scripts directly without adding the repository root to `PYTHONPATH`.  
**Solution**: Always invoke server commands and tests using the module `-m` flag:
```bash
python -m app.server.run
python -m pytest
```

### Q2: Port 5000 is already in use
**Cause**: Another application or local service is running on port 5000.  
**Solution**: Set the `PORT` environment variable before running:
```bash
# Windows PowerShell
$env:PORT="5001"; python -m app.server.run

# macOS / Linux
PORT=5001 python3 -m app.server.run
```

### Q3: Git statistics or branch commits show `0` or `—`
**Cause**: The application path is not inside a git repository or git CLI is unavailable.  
**Solution**: Ensure `git` is installed (`git --version`) and you ran `git init` or pointed `REPO_PATH` to a valid git repo.

### Q4: Dashboard metrics do not update
**Cause**: Server is offline or browser cached data.  
**Solution**: Check terminal logs for server errors. The dashboard automatically polls `/api/digest/weekly` every 30 seconds, or you can force refresh with `F5` / `Ctrl+R`.

### Q5: How do I view skill execution logs?
**Solution**: Check `.memory/runs.log` in the workspace root. It records timestamped single-line entries for every skill triggered via the UI options modal:
```text
[2026-09-03T15:32:00Z] action='weekly_digest' model='claude-sonnet-3.7' effort='medium' status='ok'
```

---

## 9. Further Reading & Architectural References

- [`CLAUDE.md`](file:///d:/repos/agentic-os/CLAUDE.md): Master agent configuration & routing table.
- [`CONTEXT.md`](file:///d:/repos/agentic-os/CONTEXT.md): Domain terms, boundaries, and invariants.
- [`TECHNICAL_ARCHITECTURE.md`](file:///d:/repos/agentic-os/TECHNICAL_ARCHITECTURE.md): Deep module design and architecture specs.
- [`docs/guides/sdlc-integration-how-to-guide.md`](file:///d:/repos/agentic-os/docs/guides/sdlc-integration-how-to-guide.md): Comprehensive SDLC Tool & Cloudflare integration manual.
- [`docs/research/arms-design-verification.md`](file:///d:/repos/agentic-os/docs/research/arms-design-verification.md): Full ARMS framework compliance audit report.
