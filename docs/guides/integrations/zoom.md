# Zoom Webhooks Integration Guide

Ingest engineering sync meeting recordings, transcript events, and standup completion webhooks from Zoom into **Developer Workflow OS**.

---

## 1. Overview & Capabilities

- **Meeting Event Ingestion**: Ingest `meeting.ended` and `recording.completed` webhooks.
- **Automated Summary Logging**: Parse meeting metadata into sprint recaps and artifact logs.

---

## 2. Setup in Zoom

1. **Create Webhook-Only App**:
   - Go to Zoom App Marketplace ([marketplace.zoom.us](https://marketplace.zoom.us)) -> **Develop** -> **Build App**.
   - Choose **Webhook Only** app type.
   - **Event Notification Endpoint URL**: `http://<your-host>:5000/api/v1/ingest/chat/zoom`
   - **Event Subscriptions**: Add `Meeting -> End Meeting`, `Recording -> All Cloud Recordings Completed`.
   - Copy Secret Token (`zoom_secret_token`).

---

## 3. Setup in Developer Workflow OS

Set credentials in [`.env`](file:///d:/repos/agentic-os/.env):

```bash
ZOOM_WEBHOOK_SECRET="zoom_secret_token"
```

---

## 4. Verification

Complete a Zoom test meeting and verify webhook event processing in `.memory/runs.log`.
