# Developer Integration How-To Guide - SDLC Monitoring Hub

This guide provides end-to-end instructions for configuring third-party SDLC tools to send webhooks and telemetry signals into the **Developer Workflow OS** Central Monitoring Hub.

---

## Ingestion Architecture & Security

### Universal Ingestion Endpoint
All incoming tool telemetry and webhooks are ingested via the universal REST endpoint:
```http
POST /api/v1/ingest/<category>/<provider>
```

### Supported Categories & Providers

| Category | Supported Providers | Payload Endpoint URL |
| :--- | :--- | :--- |
| **`code`** | `github`, `gitlab`, `azure_devops` | `/api/v1/ingest/code/<provider>` |
| **`ticket`** | `jira`, `linear`, `msteams` | `/api/v1/ingest/ticket/<provider>` |
| **`build`** | `jenkins`, `circleci`, `gradle` | `/api/v1/ingest/build/<provider>` |
| **`testing`** | `playwright`, `junit` | `/api/v1/ingest/testing/<provider>` |
| **`observability`** | `datadog`, `sentry`, `pagerduty`, `newrelic` | `/api/v1/ingest/observability/<provider>` |
| **`security_quality`** | `sonarqube`, `snyk` | `/api/v1/ingest/security_quality/<provider>` |

### Security & HMAC Validation
Webhooks can be authenticated using HMAC-SHA256 signature verification. Set your shared secret in `WEBHOOK_SECRET`.
Pass signature in header:
- `X-SDLC-Signature: sha256=<hmac-hash>` or `X-Hub-Signature-256: sha256=<hmac-hash>`

---

## Provider Setup & Configuration

### 1. SCM & Issue Tracking

#### GitHub
1. Go to **Repository Settings** -> **Webhooks** -> **Add Webhook**.
2. Set **Payload URL**: `https://<your-hub-domain>/api/v1/ingest/code/github`
3. Content Type: `application/json`
4. Events: Select **Pushes** and **Pull Requests**.

#### GitLab
1. Go to **Settings** -> **Webhooks**.
2. Set **URL**: `https://<your-hub-domain>/api/v1/ingest/code/gitlab`
3. Trigger: Check **Push events** and **Merge request events**.

#### Jira Cloud
1. Go to **Jira Settings** -> **System** -> **Webhooks**.
2. Set **URL**: `https://<your-hub-domain>/api/v1/ingest/ticket/jira`
3. Events: Check **Issue created** and **Issue updated**.
4. *Blocker Detection*: Assigning status `"Blocker"` or label `"release-blocker"` automatically flags `SDLCEventType.ISSUE_BLOCKED` and penalizes score delta (`-15.0`).

---

### 2. CI/CD & Build Systems

#### Jenkins
1. Install **Notification Plugin** or **Generic Webhook Trigger Plugin**.
2. Configure Post-build action to POST JSON to:
   `https://<your-hub-domain>/api/v1/ingest/build/jenkins`
3. Sample Payload:
   ```json
   {
     "name": "payment-service-ci",
     "number": 104,
     "status": "FAILURE"
   }
   ```

#### Playwright / JUnit Test Runner
1. In your E2E test reporter (e.g. `playwright.config.ts`), add a custom HTTP reporter posting test execution summaries:
2. POST to: `https://<your-hub-domain>/api/v1/ingest/testing/playwright`
3. Sample Payload:
   ```json
   {
     "suite": "e2e-checkout-suite",
     "passed": 48,
     "failed": 2,
     "skipped": 0
   }
   ```

---

### 3. Cloud Observability & Monitoring

#### Datadog
1. Go to **Integrations** -> **Webhooks**.
2. Add Webhook named `sdlc-hub` with URL: `https://<your-hub-domain>/api/v1/ingest/observability/datadog`
3. Monitor Payload:
   ```json
   {
     "alert_type": "$EVENT_TYPE",
     "title": "$EVENT_TITLE",
     "hostname": "$HOSTNAME"
   }
   ```

#### PagerDuty
1. Go to **Services** -> **Integrations** -> **Add Webhook Subscription**.
2. Set URL: `https://<your-hub-domain>/api/v1/ingest/observability/pagerduty`
3. Events: `incident.triggered`, `incident.resolved`.

---

## Verification & Testing

Verify your integration setup using `curl`:
```bash
curl -X POST "http://localhost:5000/api/v1/ingest/observability/datadog" \
  -H "Content-Type: application/json" \
  -d '{"alert_type": "error", "title": "API Gateway 5xx Spike"}'
```
Expected response:
```json
{
  "status": "success",
  "event": {
    "source": "datadog",
    "category": "observability",
    "eventType": "incident_created",
    "healthImpact": {
      "riskLevel": "CRITICAL",
      "scoreDelta": -15.0
    }
  }
}
```
