# PagerDuty Integration Guide

Ingest incident alerts, escalation events, and resolution notifications from PagerDuty into the **Developer Workflow OS**.

---

## 1. Overview & Capabilities

- **Incident Signal Ingestion**: Ingest `incident.triggered`, `incident.acknowledged`, and `incident.resolved`.
- **Release Readiness Blocker**: Automatically flags active Sev1/Sev2 incidents as blockers against upcoming releases.

---

## 2. Setup in PagerDuty

1. **Create Generic Webhooks (V3)**:
   - In PagerDuty -> **Services** -> **Service Directory** -> Select Service -> **Integrations** -> **Add Webhook**.
   - **Webhook URL**: `http://<your-host>:5000/api/v1/ingest/observability/pagerduty`
   - Copy the secret generated for HMAC signature validation.

2. **User API Token**:
   - Go to **Integrations** -> **API Access Keys** -> **Create New API Key**.

---

## 3. Setup in Developer Workflow OS

Set credentials in [`.env`](file:///d:/repos/agentic-os/.env):

```bash
WEBHOOK_HMAC_SECRET="your_pagerduty_secret"
PAGERDUTY_API_KEY="y_pduty_token"
```

---

## 4. Verification

Trigger a test incident on the configured PagerDuty service.
