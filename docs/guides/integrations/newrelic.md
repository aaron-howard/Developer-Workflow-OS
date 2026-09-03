# New Relic Integration Guide

Ingest APM performance metrics, latency degradation alerts, and error rate spikes from New Relic into the **Developer Workflow OS**.

---

## 1. Overview & Capabilities

- **Performance Signal Ingestion**: Ingest APM anomaly events and alert incidents.
- **Branch Risk Assessment**: Correlate deployment timing with APM throughput and response time spikes.

---

## 2. Setup in New Relic

1. **Configure Webhook Destination**:
   - Go to New Relic -> **Alerts & AI** -> **Destinations** -> **Create destination** -> **Webhook**.
   - **Endpoint URL**: `http://<your-host>:5000/api/v1/ingest/observability/newrelic`
   - **Headers**: Add `X-SDLC-Signature: <your_secret>`

2. **Create Workflow Channel**:
   - Associate the destination with your alert workflows.

---

## 3. Setup in Developer Workflow OS

Set credentials in [`.env`](file:///d:/repos/agentic-os/.env):

```bash
NEWRELIC_API_KEY="NRAK-your_newrelic_key"
```

---

## 4. Verification

Send a test notification payload from New Relic Alert Destination UI.
