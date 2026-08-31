# 0001: Developer Workflow OS uses a local command centre with repo memory and structured skills

- Status: Accepted
- Date: 2026-08-31

## Context

The project is aiming to become a developer-focused Agentic OS, not a generic chatbot. The core problem is that developers lose time moving between repository state, issue tracking, branch context, and release preparation. The system needs to give a user fast answers to operational questions without requiring a deep dive through files and tickets.

The design goal is to create a persistent operating environment around the developer's work. The user needs:

- a workspace map of the codebase
- a clear understanding of active work
- rapid feature-to-file mapping
- concise branch and PR summaries
- release readiness guidance
- recurring scheduled digests

These capabilities are not a single feature; they form a workflow system. The project must therefore be shaped as an operating layer with explicit memory, routines, skills, and a front door.

## Decision

We will build the Developer Workflow OS as a local command centre with a small set of deep modules and explicit seams:

1. Repo memory module
   - indexes the repository and keeps a usable workspace map
   - owns the file and area routing model

2. Feature context module
   - connects issues/features to relevant files and implementation surface
   - produces implementation checklists and risk notes

3. Branch summary module
   - analyzes git diffs and summarizes branch impact
   - identifies change scope and review risk

4. Release readiness module
   - aggregates work state, blockers, and notes into a release decision
   - drafts release notes based on recent work

5. Routine scheduler module
   - runs recurring digests and checks without manual prompting

6. Command centre module
   - provides the stable user-facing dashboard and action entry point

The key design choice is to keep the interfaces small and intention-revealing while burying the complexity behind those modules. The front-end and integrations are adapters at the seams, not the source of the product logic.

## Why this decision

This decision satisfies the core product requirements while keeping the system maintainable:

- The developer's value comes from operational clarity, not general chatbot behavior.
- A command centre gives a single place to inspect work and initiate actions.
- Repo memory makes the system grounded in files and real project structure.
- Structured skills produce repeatable outputs instead of vague conversational answers.
- Scheduled routines turn the network of work into a live operating layer.

The architecture follows a deep-module design: a small interface, a large amount of behavior behind it, and clear seams where real-world variation enters the system.

## Alternatives considered

### Alternative 1: Build a single monolithic chat assistant
This would be the fastest shape to prototype, but it would not provide strong locality or leverage. The logic for repo understanding, feature mapping, release analysis, and routine generation would be spread across prompts and ad hoc scripts rather than organized around a stable interface.

Why rejected:
- weak separation of concerns
- hard to test and reason about
- weak long-term maintainability
- poor fit for recurring operational workflows

### Alternative 2: Build a heavy SaaS platform from day one
This would give a polished user experience, but it adds substantial complexity before the minimal product value is proven.

Why rejected:
- not needed for the first working workflow
- slower to validate with real project data
- increases operational cost before the main benefit is clear

### Alternative 3: Build only a dashboard with no memory or routine layer
This would make the system look impressive but would not create the underlying operating system behavior. The dashboard would become a thin layer over manual prompting rather than an active developer workflow.

Why rejected:
- too shallow and too dependent on user effort
- weak memory discipline
- no recurring value beyond direct prompting

## Consequences

### Positive

- The project stays grounded in real repo and workflow context.
- Modules can be tested through their interfaces rather than through scattered implementation details.
- New source adapters can be added without rewriting the core product logic.
- The system remains small and high-leverage for the initial MVP.

### Negative

- The design requires disciplined module boundaries and careful interface maintenance.
- Some functionality will be intentionally postponed until the core memory and command-centre structure are proven.
- The first version will not be a full app platform; it is a focused operating layer for engineering work.

## Follow-up

This ADR establishes the basic product shape. Follow-up ADRs should address:

- the exact data model for repo memory
- the first skill interface set
- scheduler implementation strategy
- dashboard design and widget contract
