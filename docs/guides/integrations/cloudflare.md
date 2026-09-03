# Cloudflare Workers & D1 Integration Guide

Deploy serverless edge webhook ingestion, background workflow execution, and relational D1 SQL persistence with **Cloudflare Workers**.

---

## 1. Overview & Architecture

- **Workers Dispatcher**: `app/cloudflare/worker.js` handles edge webhook routing and HMAC validation.
- **Workflows Engine**: `app/cloudflare/workflows.js` runs asynchronous event processing.
- **D1 SQL Database**: `app/cloudflare/schema.sql` stores normalized event records.

---

## 2. Setup in Cloudflare

1. **Install Wrangler CLI**:
   ```bash
   npm install -g wrangler
   wrangler login
   ```

2. **Initialize D1 Database**:
   ```bash
   npx wrangler d1 create sdlc-db
   ```
   Copy the generated `database_id` into [`wrangler.jsonc`](file:///d:/repos/agentic-os/wrangler.jsonc).

3. **Execute Database Schema Migration**:
   ```bash
   npx wrangler d1 execute sdlc-db --file=app/cloudflare/schema.sql
   ```

4. **Deploy Cloudflare Worker**:
   ```bash
   npx wrangler deploy
   ```

---

## 3. Setup in Developer Workflow OS

Add credentials to [`.env`](file:///d:/repos/agentic-os/.env):

```bash
CLOUDFLARE_API_TOKEN="your_cloudflare_api_token"
CLOUDFLARE_ACCOUNT_ID="your_cloudflare_account_id"
CLOUDFLARE_D1_DATABASE_ID="your_d1_database_id"
```

---

## 4. Verification

Perform health check on deployed worker:
```bash
curl https://developer-workflow-os.<your-subdomain>.workers.dev/api/v1/health
```
Expected output:
```json
{"status": "healthy", "service": "Cloudflare SDLC Event Worker"}
```
