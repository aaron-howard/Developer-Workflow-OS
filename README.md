# Developer Workflow OS & V2 Cloud SDLC Monitoring Hub

A local Agentic OS and SDLC Monitoring Hub for engineering work: workspace memory, feature drill-down, branch summaries, release readiness, universal event ingestion, Cloudflare Workers/D1 workflows, and multi-adapter monitoring.

## Project Goal

This project provides a lightweight command centre for developers and engineering teams to understand repo state, issue context, change impact, release readiness, and multi-provider SDLC signals without manually hunting through disparate files, tools, and dashboards.

## Project Structure

- `app/dashboard`: Visual Command Centre UI & Second Brain graph
- `app/server`: FastAPI orchestration, REST endpoints, and Universal Event Engine (`app/server/events/`)
- `app/adapters`: Multi-provider SDLC adapters (SCM, CI/CD, Observability, Chat)
- `app/cloudflare`: Cloudflare Workers, Workflows, and D1 SQL edge persistence
- `memory`: Repo memory, workspace indexes, and generated artifacts
- `skills`: Targeted developer actions (branch summary, release notes, sprint digest)
- `docs`: Architectural Decision Records (ADRs) and SDLC How-To guides

## Current Status

Fully operational local Agentic OS and V2 Cloud SDLC Monitoring Hub backed by a 100% passing test suite (86 unit and integration tests).

## Key Features

1. **Universal Event Engine**: Async event routing with HMAC-SHA256 signature security and handler registry.
2. **SDLC Adapter Mesh**: 10+ integrations spanning GitHub, GitLab, Jira, Linear, Jenkins, GitHub Actions, Datadog, Sentry, PagerDuty, NewRelic, Slack, Teams, and Zoom.
3. **Cloudflare Edge Sync**: Workers dispatcher, Workflows execution, and D1 SQL relational event persistence.
4. **Visual Second Brain**: Interactive D3.js node graph displaying workspace files, dependencies, and router linkages.
5. **Release Readiness Engine**: Automated risk scoring, blocker tracking, and release note drafting.
6. **Headless Skill Runner**: Software buttons with selectable AI model and effort levels.
