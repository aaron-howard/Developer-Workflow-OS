# Linear Integration Guide

Integrate Linear issue tracking and cycle updates into the **Developer Workflow OS**.

---

## 1. Overview & Capabilities

- **Issue Correlation**: Connect Linear issue identifier keys (e.g. `ENG-404`) directly to commit diffs and feature maps.
- **Webhook Ingestion**: Listen to issue status shifts (`In Progress`, `Done`, `Canceled`).

---

## 2. Setup in Linear

1. **Create Webhook**:
   - Go to Linear -> **Workspace Settings** -> **API** -> **Webhooks** -> **New Webhook**.
   - **URL**: `http://<your-host>:5000/api/v1/ingest/issues/linear`
   - **Label**: `Developer Workflow OS Ingestion`
   - **Events**: Check `Issues`.
   - Copy the generated Webhook Secret.

2. **Generate API Key**:
   - Under **Personal API keys**, click **New API Key**.

---

## 3. Setup in Developer Workflow OS

Add credentials to [`.env`](file:///d:/repos/agentic-os/.env):

```bash
WEBHOOK_HMAC_SECRET="your_linear_webhook_secret"
LINEAR_API_KEY="lin_api_your_key_here"
```

---

## 4. Verification

Create or update an issue in Linear and verify log output in `.memory/runs.log`.
