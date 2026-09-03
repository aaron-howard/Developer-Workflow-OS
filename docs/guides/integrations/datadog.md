# Datadog Integration Guide

Ingest monitor alerts, metric anomaly notifications, and incident webhooks from Datadog into the **Developer Workflow OS**.

---

## 1. Overview & Capabilities

- **Observability Ingestion**: Ingest Datadog alert states (`ALERT`, `WARNING`, `OK`).
- **Release Risk Scoring**: Automatically reduces release readiness score when active Datadog monitors trigger in production.

---

## 2. Setup in Datadog

1. **Enable Webhook Integration**:
   - In Datadog -> **Integrations** -> search for **Webhooks**.
   - Click **New Webhook**.

2. **Configure Webhook**:
   - **Name**: `Developer-Workflow-OS-Webhook`
   - **URL**: `http://<your-host>:5000/api/v1/ingest/observability/datadog`
   - **Payload**:
     ```json
     {
       "event_type": "$EVENT_TYPE",
       "alert_title": "$EVENT_TITLE",
       "alert_status": "$ALERT_STATUS",
       "hostname": "$HOSTNAME",
       "link": "$LINK"
     }
     ```
   - Click **Save**.

3. **Attach to Monitors**:
   - Add `@webhook-Developer-Workflow-OS-Webhook` to monitor notification bodies.

---

## 3. Setup in Developer Workflow OS

Set credentials in [`.env`](file:///d:/repos/agentic-os/.env):

```bash
DATADOG_API_KEY="your_datadog_api_key"
```

---

## 4. Verification

Test the integration by triggering a monitor test notification in Datadog.
