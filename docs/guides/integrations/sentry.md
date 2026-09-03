# Sentry Error Tracking Integration Guide

Ingest real-time application exceptions, issue regressions, and error spike alerts from Sentry into the **Developer Workflow OS**.

---

## 1. Overview & Capabilities

- **Exception Event Ingestion**: Ingest `issue.created` and `issue.resolved` webhooks.
- **Root Cause Context**: Links stack traces to workspace source code files.

---

## 2. Setup in Sentry

1. **Create Internal Integration**:
   - Go to Sentry -> **Settings** -> **Developer Settings** -> **New Internal Integration**.
   - **Name**: `Developer Workflow OS`
   - **Webhook URL**: `http://<your-host>:5000/api/v1/ingest/observability/sentry`
   - **Permissions**: Set `Issue & Event` to `Read`.
   - **Webhooks**: Check `issue`.
   - Click **Save Changes**.

2. **Copy Secret Key**:
   - Copy the Client Secret value (`sentry_secret`).

---

## 3. Setup in Developer Workflow OS

Set credentials in [`.env`](file:///d:/repos/agentic-os/.env):

```bash
WEBHOOK_HMAC_SECRET="sentry_secret"
SENTRY_AUTH_TOKEN="sntrys_your_sentry_token"
```

---

## 4. Verification

Send a test exception payload or trigger an alert rule in Sentry.
