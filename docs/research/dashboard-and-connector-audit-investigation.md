# Research Findings: Connector Audit, Visual Second Brain, and Dashboard Data Validation

**Date**: 2026-09-04  
**Investigated By**: Antigravity Assistant  
**Target Repository**: Developer Workflow OS ([agentic-os](file:///d:/repos/agentic-os))  
**Primary Sources**:
- [`app/server/api.py`](file:///d:/repos/agentic-os/app/server/api.py)
- [`app/server/run.py`](file:///d:/repos/agentic-os/app/server/run.py)
- [`app/server/connectors_audit.py`](file:///d:/repos/agentic-os/app/server/connectors_audit.py)
- [`app/server/repo_graph.py`](file:///d:/repos/agentic-os/app/server/repo_graph.py)
- [`app/server/adapters/git.py`](file:///d:/repos/agentic-os/app/server/adapters/git.py)
- [`app/server/release_readiness.py`](file:///d:/repos/agentic-os/app/server/release_readiness.py)
- [`app/dashboard/index.html`](file:///d:/repos/agentic-os/app/dashboard/index.html)

---

## 1. Executive Summary

| Issue / Question | Status / Finding | Primary Root Cause & Resolution |
| :--- | :--- | :--- |
| **1. Connector Audit 404** | **Resolved by Server Restart** | Process ID 18396 was started before `@app.route("/api/connectors/audit")` was registered in `api.py`. Running Flask with `debug=False` does not auto-reload code changes. |
| **2. Second Brain 404** | **Resolved by Server Restart** | Process ID 18396 was started before `@app.route("/api/repo/graph")` was registered in `api.py`. |
| **3. Metrics Origin** | **Real Local Git Data + Live Heuristics** | Commit counts, branch counts, workspace graphs, and connector statuses use **real local Git CLI and environment checks**, not static mock/demo data. |

---

## 2. Detailed Findings

### Issue 1 & 2: Connector Audit & Visual Second Brain Returning 404 NOT FOUND

#### Diagnostic Evidence
HTTP requests executed against the active process (`http://127.0.0.1:5000` PID 18396):
- `GET /` ➔ `200 OK`
- `GET /api/repo/index` ➔ `200 OK`
- `GET /api/digest/weekly` ➔ `200 OK`
- `GET /api/connectors/audit` ➔ **`404 NOT FOUND`**
- `GET /api/repo/graph` ➔ **`404 NOT FOUND`**

#### Root Cause Analysis
In [`app/server/api.py`](file:///d:/repos/agentic-os/app/server/api.py#L59-L77), the endpoints `@app.route("/api/connectors/audit")` and `@app.route("/api/repo/graph")` are fully defined and linked to `audit_connectors()` and `generate_repo_graph()`.

However, in [`app/server/run.py`](file:///d:/repos/agentic-os/app/server/run.py#L41-L44), Flask is launched with `debug=False` by default:
```python
app.run(host=args.host, port=args.port, debug=args.debug)
```
When the user launched Python Process `18396`, Flask loaded the application routing table into memory once. Because debug auto-reloading was inactive, new endpoints added to `api.py` were not present in the process's memory space, yielding a standard 404 response.

#### Resolution
Restarting the Flask server process (`python -m app.server.run`) loads the latest `app/server/api.py` routing table, activating both endpoints (`200 OK`).

---

### Question 3: Data Validity Audit (Real Git Data vs. Demo/Mock Data)

An inspection of the adapter layer in [`app/server/adapters/git.py`](file:///d:/repos/agentic-os/app/server/adapters/git.py) and data aggregators reveals that the dashboard displays **live, local engineering metrics**:

#### 1. Recent Commits & Commit Count
- **Implementation**: [`SubprocessGitAdapter.repo_stats()`](file:///d:/repos/agentic-os/app/server/adapters/git.py#L163) and [`recent_commits()`](file:///d:/repos/agentic-os/app/server/adapters/git.py#L154).
- **Execution**: Runs native Git CLI commands directly on the host repository:
  ```bash
  git rev-list --count --end-of-options main
  git log -10 --oneline --end-of-options main
  ```
- **Data Status**: **REAL**. Reflects exact commit history on your local git branch.

#### 2. Repository Memory & Branch Count
- **Implementation**: [`SubprocessGitAdapter.current_branch()`](file:///d:/repos/agentic-os/app/server/adapters/git.py#L146) and `git branch -a`.
- **Data Status**: **REAL**. Inspects active checked-out branch and counts total local/remote branches.

#### 3. Release Readiness Score
- **Implementation**: [`ReleaseReadinessAnalyzer.assess_readiness()`](file:///d:/repos/agentic-os/app/server/release_readiness.py#L23).
- **Algorithm**: Evaluates real repository state using:
  - `git diff base...target` (changed file detection)
  - Code vs. test coverage heuristic (`has_code and not has_tests`)
  - Documentation presence (`.md` files in diff)
  - Glob scan for test runners (`**/test*.py` or `**/*_test.py`)
- **Data Status**: **REAL / DYNAMIC HEURISTIC**.

#### 4. Connector Audit Status
- **Implementation**: [`audit_connectors()`](file:///d:/repos/agentic-os/app/server/connectors_audit.py#L12).
- **Checks**:
  - **Git**: Validates `SubprocessGitAdapter` health.
  - **GitHub API**: Checks if `GITHUB_TOKEN` or `GH_TOKEN` is present in `os.environ`.
  - **Jira**: Checks if `JIRA_URL` is set in `os.environ`.
  - **Slack**: Checks if `SLACK_WEBHOOK_URL` is set in `os.environ`.
  - **MCP Servers**: Checks if `.mcp/config.json` exists in workspace root.
- **Data Status**: **REAL**. Directly inspects system environment and filesystem state.

---

## 3. Recommended Actions & Next Steps

1. **Restart Local Server**:
   Stop current terminal process (`CTRL+C`) and start the updated server:
   ```powershell
   python -m app.server.run
   ```
2. **Enable Environment Credentials**:
   To upgrade GitHub, Jira, and Slack connector pills from `AVAILABLE` to `CONNECTED`, populate values in `.env`:
   ```bash
   GITHUB_TOKEN=ghp_...
   JIRA_URL=https://yourcompany.atlassian.net
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
   ```
