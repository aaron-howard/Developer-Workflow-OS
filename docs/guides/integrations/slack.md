# Slack Integration Guide

Send automated nightly digests, release readiness alerts, and sprint summaries to Slack channels, and ingest Slack command webhooks into **Developer Workflow OS**.

---

## 1. Overview & Capabilities

- **Outbound Notifications**: Dispatches formatted Block Kit summary messages to Slack channels.
- **Inbound Event Ingestion**: Ingests interactive slash commands or channel event webhooks.

---

## 2. Setup in Slack

1. **Create Slack Incoming Webhook**:
   - Visit [api.slack.com/apps](https://api.slack.com/apps) -> **Create New App** -> **From scratch**.
   - Select your Workspace.
   - Go to **Incoming Webhooks** -> Toggle **On** -> Click **Add New Webhook to Workspace**.
   - Select target channel (e.g. `#engineering-updates`) -> Click **Allow**.
   - Copy the Webhook URL (`https://hooks.slack.com/services/T.../B.../...`).

2. **Inbound Webhooks** (Optional):
   - Go to **Event Subscriptions** -> Toggle **On**.
   - Set **Request URL**: `http://<your-host>:5000/api/v1/ingest/chat/slack`

---

## 3. Setup in Developer Workflow OS

Set credentials in [`.env`](file:///d:/repos/agentic-os/.env):

```bash
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/T.../B.../..."
```

---

## 4. Verification

Test sending a Slack notification via Python CLI:
```bash
python skills/weekly_sprint_summary.py
```
Or test via HTTP POST trigger in routine scheduler.
