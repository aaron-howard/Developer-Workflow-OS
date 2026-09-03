# GitHub Integration Guide

Integrate GitHub repositories, Pull Request webhooks, and Actions workflows with the **Developer Workflow OS & SDLC Monitoring Hub**.

---

## 1. Overview & Capabilities

- **Normalized Event Ingestion**: Ingest `push`, `pull_request`, `issue_comment`, and `workflow_run` events.
- **HMAC Signature Verification**: Validates `X-Hub-Signature-256` header payloads using your shared `WEBHOOK_HMAC_SECRET`.
- **Command Centre Features**: Real-time git commit stats, active branch diff summaries, and release readiness analysis.

---

## 2. Setup in GitHub

1. **Navigate to Repository Settings**:
   - Go to your GitHub repository -> **Settings** -> **Webhooks** -> **Add webhook**.

2. **Configure Webhook Payload**:
   - **Payload URL**: `http://<your-host>:5000/api/v1/ingest/scm/github` (or your Cloudflare Worker URL `/api/v1/events/webhook`).
   - **Content type**: `application/json`
   - **Secret**: Enter your `WEBHOOK_HMAC_SECRET` key (e.g. `secret_key_12345`).
   - **SSL verification**: Enable SSL verification for HTTPS endpoints.

3. **Select Events**:
   - Choose *Let me select individual events*:
     - `Pushes`
     - `Pull requests`
     - `Issues`
     - `Workflow runs`
   - Click **Add webhook**.

4. **Generate Personal Access Token (PAT)** (Optional for API polling):
   - Go to **Developer Settings** -> **Personal Access Tokens** -> **Tokens (classic)**.
   - Select scopes: `repo`, `read:org`, `workflow`.
   - Copy the token value (`ghp_...`).

---

## 3. Setup in Developer Workflow OS

Add your token and secret to your local [`.env`](file:///d:/repos/agentic-os/.env) file:

```bash
# Webhook Signature Secret (matches secret in GitHub Webhook Settings)
WEBHOOK_HMAC_SECRET="secret_key_12345"

# GitHub Personal Access Token
GITHUB_TOKEN="ghp_your_github_token_here"
```

---

## 4. Verification & Testing

1. **Send Test Payload**:
   - In GitHub Webhook settings, click **Recent Deliveries** -> select the latest payload -> click **Redeliver**.

2. **Verify in Developer Workflow OS**:
   - Check application log or `.memory/runs.log`:
     ```text
     [INGEST] Category: scm, Provider: github, Event: push, Status: 200 OK
     ```
   - Query connectors audit endpoint:
     ```bash
     curl http://localhost:5000/api/connectors/audit
     ```
