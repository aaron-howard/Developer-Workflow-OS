# GitHub Actions Integration Guide

Ingest real-time workflow run events, test matrix results, and deployment pipeline signals from GitHub Actions into the **Developer Workflow OS**.

---

## 1. Overview & Capabilities

- **Workflow Run Monitoring**: Ingest `workflow_run` and `workflow_job` webhooks.
- **Automated Failure Analysis**: Captures build errors and test failures to enrich release notes and branch summaries.

---

## 2. Setup in GitHub Actions

1. **Configure Webhook**:
   - In GitHub repository **Settings** -> **Webhooks**.
   - URL: `http://<your-host>:5000/api/v1/ingest/cicd/github_actions`
   - Select event: `Workflow runs`, `Workflow jobs`.

2. **Custom Step Post Notification** (Alternative):
   Add a curl step to `.github/workflows/ci.yml`:
   ```yaml
   - name: Notify Developer Workflow OS
     if: always()
     run: |
       curl -X POST "http://<your-host>:5000/api/v1/ingest/cicd/github_actions" \
         -H "Content-Type: application/json" \
         -d '{"workflow": "${{ github.workflow }}", "status": "${{ job.status }}", "commit": "${{ github.sha }}"}'
   ```

---

## 3. Setup in Developer Workflow OS

Set environment variable in [`.env`](file:///d:/repos/agentic-os/.env):

```bash
GITHUB_ACTIONS_TOKEN="ghp_your_github_actions_token"
```

---

## 4. Verification

Run a GitHub Actions workflow and confirm event receipt in `.memory/runs.log`.
