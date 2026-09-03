# Context

## Purpose

This project is a Developer Workflow OS: a system that helps a developer understand active work, repo context, likely impact, and release readiness from one operating surface.

## Canonical terms

### Developer Workflow OS
The operating layer that turns day-to-day engineering work into a visible, reviewable workflow. It is not a chatbot. It is a persistent working environment for understanding what is happening, what matters, and what should happen next.

### Work item
Any unit of engineering effort that needs to be tracked, reviewed, or shipped. This includes a feature, bug, issue, task, request, or branch outcome.

### Feature
A coherent slice of product or platform change that delivers user or team value. A feature can span code, tests, docs, and release notes.

### Repo memory
The organized understanding of a repository and its surrounding work. It keeps the system grounded in the real project rather than relying on a single conversation thread.

### Workspace map
A structured view of the repo and its areas: where the meaningful work lives, which folders matter, and how a feature connects back to the project.

### Release readiness
The degree to which work is ready to be shipped. It depends on completeness, risk, testing, and clarity of the user-facing change.

### Branch summary
A concise description of what changed in a branch, what it likely intended to accomplish, and what should be reviewed before merge.

### Implementation checklist
The ordered set of actions needed to complete or validate a feature or change. It is used to reduce uncertainty, not to replace engineering judgment.

### Artifact
Any generated record of work that can be reviewed or reused later, such as a summary, release note, or recap.

### Routine
A recurring workflow that runs on schedule to keep the operating layer current without a manual trigger.

### Command centre
The front door to the operating system: a stable place where the user sees current work, key artifacts, and the most useful actions.

### Universal Event Engine
The centralized async event dispatch and routing subsystem that ingests normalized events from external engineering tools, validates authentication signatures, and dispatches to registered handler modules.

### HMAC Signature Verification
The cryptographic authentication mechanism (HMAC-SHA256) used to ensure incoming webhooks originate from authorized external providers before being processed by the system.

### SDLC Integration Adapter
A standardized adapter module translating external signals (from SCM, CI/CD, Observability, or Chat platforms) into normalized event envelopes consumed by the Event Engine.

### Cloudflare Dispatcher & D1 Store
The serverless edge dispatcher and relational SQLite store (Cloudflare D1) used for offloading event webhooks and executing cloud-native workflows outside the local environment.

## Clarified distinctions

### Feature vs work item
A work item is the general concept. A feature is a specific type of work item that has a coherent user or product outcome.

### Repo memory vs workspace map
Repo memory is the overall understanding of the project. A workspace map is one concrete representation of that memory.

### Artifact vs summary
A summary is a kind of artifact. Not every artifact is a summary, but every artifact records a decision or result that was produced for later review.

### Release readiness vs release note
Release readiness is a judgment about shipping confidence. A release note is a communication artifact describing what shipped.

### Routine vs skill
A skill is a discrete action a user or system can perform. A routine is a scheduled workflow built from one or more skills or repeated observations.

### Event vs Artifact
An event is a point-in-time signal emitted by an external system or internal state change. An artifact is a persistent record produced by analyzing one or more events or workspace states.

### Webhook Adapter vs Polling Adapter
A webhook adapter receives push events via signed HTTP payloads. A polling adapter periodically queries external APIs to pull status changes into the event pipeline.

### Local Repo Memory vs Cloudflare D1 Store
Local repo memory indexes files and metadata stored within the workspace filesystem. Cloudflare D1 is an edge-replicated SQL store for remote event logging and cross-environment sync.

## Relationship rules

- A work item may relate to many files, artifacts, and decisions.
- A feature may produce one or more artifacts, but it is not the same thing as the artifact.
- Repo memory is the source of truth for the system's understanding of the project.
- The command centre is a view over the project, not the place where the project itself lives.
- Release readiness is a function of the work that exists, the risk it carries, and the confidence in the review and validation process.
- Events trigger handlers, which update Repo Memory and may generate Artifacts.

## Invariants

- The project is defined by the work it is helping to deliver, not by the UI alone.
- A developer should be able to understand what changed without reading the entire repository.
- A routine should improve clarity, not add more noise.
- An artifact should be reviewable in one pass and easily discoverable later.
- Unauthenticated or invalidly signed webhooks must be rejected at the boundary before event handler dispatch.

## Out of scope

This context does not define specific third-party API SDKs, internal database table indices, or CSS styling details. Those belong in implementation code and architecture documents.
