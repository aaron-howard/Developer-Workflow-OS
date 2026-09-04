# Deployment Options & Multi-Repository Monitoring Architecture

**Date**: September 2026  
**Status**: Completed  
**Primary Sources Inspected**:
- [`wrangler.jsonc`](file:///d:/repos/agentic-os/wrangler.jsonc)
- [`app/server/api.py`](file:///d:/repos/agentic-os/app/server/api.py)
- [`app/server/events/schema.py`](file:///d:/repos/agentic-os/app/server/events/schema.py)
- [`app/server/db/d1_adapter.py`](file:///d:/repos/agentic-os/app/server/db/d1_adapter.py)
- [`app/server/repo_memory.py`](file:///d:/repos/agentic-os/app/server/repo_memory.py)
- [`docs/adr/0002-v2-sdlc-integration-hub-and-event-engine.md`](file:///d:/repos/agentic-os/docs/adr/0002-v2-sdlc-integration-hub-and-event-engine.md)
- [`docs/guides/sdlc-integration-how-to-guide.md`](file:///d:/repos/agentic-os/docs/guides/sdlc-integration-how-to-guide.md)

---

## Question 1: How and Where to Deploy for Public Webhooks

### The Problem
External third-party engineering tools (GitHub, GitLab, Jira, Jenkins, Datadog, Sentry, Slack, Linear, etc.) cannot deliver HTTP POST webhooks to `https://localhost` because `localhost` is loopback-only to your local machine and inaccessible across the public internet.

---

### Option A: Serverless Edge Deployment via Cloudflare Workers & D1 (Recommended for Production)

- **Primary Sources**: [`wrangler.jsonc`](file:///d:/repos/agentic-os/wrangler.jsonc), [`docs/adr/0002-v2-sdlc-integration-hub-and-event-engine.md`](file:///d:/repos/agentic-os/docs/adr/0002-v2-sdlc-integration-hub-and-event-engine.md#L25-L27).
- **Mechanism**: The repository includes native Cloudflare Workers configuration (`wrangler.jsonc`) and D1 SQL database integration (`d1_adapter.py`).
- **Deploy Command**:
  ```bash
  npx wrangler deploy
  ```
- **Webhook Endpoint**: `https://<your-worker-name>.<subdomain>.workers.dev/api/v1/ingest/<category>/<provider>`
- **Advantages**:
  1. Instant, globally distributed public HTTPS URL out-of-the-box.
  2. Built-in HMAC-SHA256 cryptographic signature validation ([`security.py`](file:///d:/repos/agentic-os/app/server/events/security.py)).
  3. Serverless zero-maintenance persistence via Cloudflare D1 SQL.

---

### Option B: Local HTTP Tunneling (Recommended for Local Development & Testing)

- **Primary Sources**: [`app/server/run.py`](file:///d:/repos/agentic-os/app/server/run.py), [`docs/guides/sdlc-integration-how-to-guide.md`](file:///d:/repos/agentic-os/docs/guides/sdlc-integration-how-to-guide.md#L10-L13).
- **Mechanism**: Expose your local running Flask application (port `5000`) using a secure tunnel provider like `cloudflared` or `ngrok`.
- **Setup**:
  1. Start the Flask server locally:
     ```bash
     python -m app.server.run
     ```
  2. Launch a secure public tunnel:
     ```bash
     # Using Cloudflare Tunnel
     cloudflared tunnel --url http://localhost:5000

     # OR using ngrok
     ngrok http 5000
     ```
- **Webhook Endpoint**: `https://<random-id>.ngrok-free.app/api/v1/ingest/<category>/<provider>`
- **Advantages**:
  1. Zero cloud deployment required; run and debug directly on your machine.
  2. Instant live payload inspection in local terminal logs.

---

### Option C: Containerized Cloud PaaS (Render, Railway, Fly.io, AWS App Runner)

- **Primary Sources**: [`app/server/api.py`](file:///d:/repos/agentic-os/app/server/api.py#L37-L46), [`requirements.txt`](file:///d:/repos/agentic-os/requirements.txt).
- **Mechanism**: Deploy `create_app()` as a standard Python WSGI service using Gunicorn or Uvicorn.
- **Webhook Endpoint**: `https://<your-app-name>.onrender.com/api/v1/ingest/<category>/<provider>`

---

## Question 2: Multi-Project & Multi-Repository Monitoring Capabilities

### Answer: YES. The system natively supports monitoring multiple repositories and projects concurrently.

---

### 1. Canonical Event Schema (`SDLCEvent`)
- **Primary Source**: [`app/server/events/schema.py`](file:///d:/repos/agentic-os/app/server/events/schema.py#L97-L123).
- Every event ingested by the Universal Event Engine includes a required `repository` string field:
  ```python
  @dataclass
  class SDLCEvent:
      id: str
      repository: str = "unknown"  # e.g., "org/service-alpha", "org/service-beta"
      category: SDLCCategory
      event_type: SDLCEventType
      ...
  ```
- Whether receiving webhooks from GitHub `repository.full_name`, GitLab `project.path_with_namespace`, or Jira `issue.fields.project.key`, each incoming event is tagged with its originating project/repository.

---

### 2. Database Persistence & Storage Indexing
- **Primary Source**: [`app/server/db/d1_adapter.py`](file:///d:/repos/agentic-os/app/server/db/d1_adapter.py#L22-L37).
- The database schema indexes `repository TEXT NOT NULL` for all events:
  ```sql
  CREATE TABLE IF NOT EXISTS sdlc_events (
      id TEXT PRIMARY KEY,
      timestamp TEXT NOT NULL,
      repository TEXT NOT NULL,  -- Enables multi-repo queries
      event_type TEXT NOT NULL,
      ...
  );
  ```
- This enables filtering risk scores, build events, deployment status, and release readiness across multiple projects simultaneously.

---

### 3. Local Workspace Memory Scoping (`RepoMemory`)
- **Primary Source**: [`app/server/repo_memory.py`](file:///d:/repos/agentic-os/app/server/repo_memory.py#L29-L40).
- `RepoMemory(repo_path)` accepts a target repository path dynamically, allowing the Developer Workflow OS to instantiate separate memory maps and workspace graphs for multiple repositories side by side.

---

## Summary & Recommendations

1. **For Public Webhook Ingestion**:
   - Use **Cloudflare Workers** (`npx wrangler deploy`) for production hosting, or **ngrok / cloudflared tunnel** (`ngrok http 5000`) for rapid local development.
2. **For Multi-Project Monitoring**:
   - Use the **Universal Ingestion Hub** (`/api/v1/ingest/<category>/<provider>`). All incoming tool signals will automatically tag and isolate events by `repository` name in the database.
