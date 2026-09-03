# GitLab Integration Guide

Integrate GitLab repositories, Merge Requests, and CI/CD pipelines with the **Developer Workflow OS & SDLC Monitoring Hub**.

---

## 1. Overview & Capabilities

- **Normalized Event Ingestion**: Ingest Push, Merge Request, Pipeline, and Issue webhooks from GitLab.com or self-hosted GitLab instances.
- **Header Token Authentication**: Validates `X-Gitlab-Token` header.
- **Command Centre Features**: Multi-provider SCM audit and unified branch summary analysis.

---

## 2. Setup in GitLab

1. **Navigate to Webhook Settings**:
   - Go to your GitLab Project -> **Settings** -> **Webhooks**.

2. **Configure Webhook**:
   - **URL**: `http://<your-host>:5000/api/v1/ingest/scm/gitlab`
   - **Secret token**: Enter your shared secret (`WEBHOOK_HMAC_SECRET`).
   - **Trigger Events**: Check *Push events*, *Tag push events*, *Merge request events*, *Pipeline events*.
   - Click **Add webhook**.

3. **Generate Personal Access Token**:
   - Go to **User Settings** -> **Access Tokens**.
   - Create a token with `api` and `read_repository` scopes.

---

## 3. Setup in Developer Workflow OS

Add your token to [`.env`](file:///d:/repos/agentic-os/.env):

```bash
WEBHOOK_HMAC_SECRET="your_shared_secret"
GITLAB_PRIVATE_TOKEN="glpat-your_gitlab_token"
```

---

## 4. Verification

1. Click **Test** -> **Push events** in GitLab Webhooks UI.
2. Confirm `200 OK` response.
