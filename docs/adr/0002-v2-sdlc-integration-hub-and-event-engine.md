# ADR 0002: V2 Cloud SDLC Monitoring Hub and Universal Event Engine

## Status

Accepted

## Context

The initial MVP of the Developer Workflow OS focused on local workspace indexing, git branch change summaries, and release notes generation. As engineering workflows expanded, there was a clear need to integrate real-time signals from external SCM, CI/CD, Observability, and Chat systems without creating tight coupling or fragile custom API handlers spread across the codebase.

Furthermore, receiving incoming webhooks securely requires cryptographic signature verification (HMAC-SHA256) to ensure unauthenticated payload rejection at the boundary before execution.

## Decision

We decided to establish a **Universal Event Engine** and **Decoupled Adapter Architecture** with Cloudflare serverless edge capabilities:

1. **Universal Event Engine (`app/server/events/`)**:
   - Centralized handler registry (`registry.py`) providing `register_handler(event_type, handler)` and `dispatch_event(event)`.
   - Security Seam (`hmac_verifier.py`) enforcing HMAC-SHA256 signature verification (`verify_hmac_signature`).

2. **Standardized SDLC Adapter Layer (`app/adapters/`)**:
   - Modular adapters translating raw provider webhooks into normalized `Event` payloads.
   - SCM (GitHub, GitLab), Issue Trackers (Jira, Linear), CI/CD (Jenkins, GitHub Actions), Observability (Datadog, Sentry, PagerDuty, NewRelic), and Chat (Slack, Microsoft Teams, Zoom).

3. **Cloudflare Edge Sync (`app/cloudflare/`)**:
   - Serverless Workers dispatcher (`worker.js`), Workflows orchestrator (`workflows.js`), and D1 SQL schema (`schema.sql`) for edge event ingestion and persistence.

## Consequences

### Positive
- **Security**: Ingress traffic is cryptographically verified prior to dispatching events to internal handlers.
- **Maintainability**: Adding a new engineering tool provider requires only implementing a discrete adapter module conforming to the adapter interface.
- **Extensibility**: Cloudflare Workers & D1 integration allow remote event ingestion and edge replication alongside local operations.
- **Testability**: The decoupled seam enables isolated unit and integration testing (86/86 passing tests).

### Negative
- **Secrets Management**: Requires managing shared secret keys (`WEBHOOK_HMAC_SECRET`, API tokens) across environments.
- **Schema Management**: D1 SQL schema updates require migration script coordination alongside local database state.
