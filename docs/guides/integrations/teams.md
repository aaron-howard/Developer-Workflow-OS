# Microsoft Teams Integration Guide

Send automated engineering digests and release status reports to Microsoft Teams channels with **Developer Workflow OS**.

---

## 1. Overview & Capabilities

- **Adaptive Card Delivery**: Delivers formatted Adaptive Cards to Microsoft Teams channels.
- **Inbound Event Ingestion**: Ingests incoming webhooks from Power Automate or Teams Workflow apps.

---

## 2. Setup in Microsoft Teams

1. **Create Incoming Webhook Connector**:
   - Go to your Teams Channel -> click `...` -> **Workflows** or **Connectors**.
   - Search for **Incoming Webhook** -> click **Add**.
   - Provide a name (e.g. `Developer Workflow OS Bot`).
   - Copy the generated Webhook URL (`https://outlook.office.com/webhook/...`).

---

## 3. Setup in Developer Workflow OS

Set credentials in [`.env`](file:///d:/repos/agentic-os/.env):

```bash
TEAMS_WEBHOOK_URL="https://outlook.office.com/webhook/..."
```

---

## 4. Verification

Trigger a test notification to Microsoft Teams via the routine scheduler endpoint.
