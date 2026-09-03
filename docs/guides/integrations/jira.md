# Jira Software Integration Guide

Connect Jira Cloud or Data Center issues, sprint changes, and status updates to the **Developer Workflow OS**.

---

## 1. Overview & Capabilities

- **Issue Mapping**: Maps Jira issue keys (e.g. `PROJ-123`) to target code files in the workspace.
- **Webhook Ingestion**: Captures `jira:issue_created`, `jira:issue_updated`, and `sprint_started` events.

---

## 2. Setup in Jira

1. **System Webhook Setup**:
   - Go to Jira Settings (Gear icon) -> **System** -> **Webhooks**.
   - Click **Create a Webhook**.
   - **URL**: `http://<your-host>:5000/api/v1/ingest/issues/jira`
   - **Events**: Check `Issue -> created, updated`.

2. **Generate API Token**:
   - Visit [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens).
   - Click **Create API token**.

---

## 3. Setup in Developer Workflow OS

Add credentials to [`.env`](file:///d:/repos/agentic-os/.env):

```bash
JIRA_URL="https://yourcompany.atlassian.net"
JIRA_API_TOKEN="your_jira_api_token"
```

---

## 4. Verification

Test issue mapping via the CLI or API:
```bash
curl "http://localhost:5000/api/issue/map?issue=PROJ-123"
```
