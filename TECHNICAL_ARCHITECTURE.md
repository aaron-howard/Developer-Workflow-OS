# Developer Workflow OS — Technical Architecture

## 1. Overview

This project is a local, developer-centric Agentic OS designed to help a builder understand and operate their engineering work through a single dashboard. The system brings together:
- repo context
- issue and feature understanding
- branch and PR summaries
- release readiness
- scheduled team digests
- a visual command centre

The architecture follows the ARMS pattern from the guide:
- Applications: GitHub, Jira, Slack, terminal tooling
- Routines: scheduled repo digests and weekly summaries
- Memory: router files, repo index, feature metadata
- Skills: feature analysis, branch summary, release prep, issue triage

## 2. Goals

### Primary goals
- turn repo and issue context into structured workflow intelligence
- reduce manual investigation before shipping
- give engineers a single place to inspect work at a glance
- create a lightweight, useful local operating layer rather than an oversized agent platform

### Non-goals for v1
- large multi-user orchestration system
- generalized autonomous agent swarm
- heavily centralized SaaS backend
- advanced permissioning and multi-tenant operations

## 3. Core product flow

The system operates in a simple loop:

1. Discover repo and workspace structure
2. Build and maintain project memory
3. Capture active work items from GitHub/Jira/branch state
4. Run developer tasks through targeted skills
5. Write structured outputs to artifacts/logs
6. Surface those results in a local dashboard
7. Trigger scheduled routines for recurring updates

## 4. Deep module design

The architecture should be shaped as a set of deep modules with narrow, stable interfaces and concentrated implementation behind the seam.

### 4.1 Module map

- RepoMemoryModule
  - Interface: indexRepo, getAreaIndex, getFeatureMap, updateArtifactLog
  - Implementation: filesystem scanning, markdown routers, repo indexing logic
  - Seam: workspace-memory storage
  - Adapters: local filesystem adapter, markdown index adapter

- FeatureContextModule
  - Interface: findRelevantFiles, buildImplementationChecklist, summarizeFeatureRisk
  - Implementation: issue parsing, file searching, grep heuristics, dependency tracing
  - Seam: project-context source
  - Adapters: GitHub issue adapter, local repo adapter, Jira adapter

- BranchSummaryModule
  - Interface: summarizeBranch, compareWithBase, surfaceRiskAreas
  - Implementation: git diff analysis, file grouping, impact classification
  - Seam: source-control diff provider
  - Adapters: Git adapter, GitHub PR adapter

- ReleaseReadinessModule
  - Interface: assessReleaseReadiness, draftReleaseNotes, listBlockers
  - Implementation: merge aggregation, changelog assembly, risk scoring
  - Seam: release signal data source
  - Adapters: GitHub release adapter, CI adapter, ticket adapter

- RoutineSchedulerModule
  - Interface: registerRoutine, runNow, pauseRoutine, listRoutineStatus
  - Implementation: clock scheduling, task orchestration, artifact persistence
  - Seam: execution scheduler
  - Adapters: cron adapter, local scheduler adapter, background worker adapter

- CommandCentreModule
  - Interface: renderOverview, launchAction, showArtifacts, showWorkspaceMap
  - Implementation: dashboard rendering, action orchestration, status aggregation
  - Seam: user-facing interaction layer
  - Adapters: local web app adapter, static HTML adapter, CLI adapter

### 4.2 Design principles applied

- Depth is a property of the interface, not the implementation. Each module exposes a small, intention-revealing interface while hiding the complexity of repo scanning, scheduling, and summaries behind it.
- The deletion test matters. If the module disappeared, would the work reappear elsewhere? For example, if BranchSummaryModule was removed, the developer would have to re-create branch inspection logic in many callers; that is evidence the module earns its keep.
- The interface is the test surface. Tests should exercise the module through its interface, not by reaching into its internals.
- One adapter means a hypothetical seam; two adapters means a real seam. We only introduce a seam when more than one provider is likely to vary, such as GitHub and GitLab, or local Markdown and database-backed memory.

### 4.3 Important seams

The architecture should keep seams at the points where technology or source varies:

- repo-memory seam: local disk vs database-backed index
- source-control seam: git CLI vs GitHub API
- issue-source seam: Jira vs Linear vs local markdown tickets
- notification seam: Slack vs email vs no-op adapter
- UI seam: local web dashboard vs CLI tool

This keeps the rest of the system stable and reduces churn.

### 4.4 Deepening strategy

Prefer the following shapes:

- one orchestrator that routes requests
- deep modules that own a single capability and expose a small interface
- thin adapters at the seams
- artifact outputs stored as plain markdown or JSON, not spread across callers

Avoid:
- shallow modules that expose large parameter lists and pass through logic
- duplicated feature logic spread across the dashboard, scheduler, and skill runner
- custom adapters with no real variation behind them

### 4.5 Interface-first design recommendation

The first design pass should define interfaces before implementation. Example:

```typescript
interface RepoMemoryModule {
  indexRepo(repoPath: string): Promise<RepoIndex>;
  getAreaIndex(area: string): Promise<AreaIndex>;
  getFeatureMap(): Promise<FeatureMap>;
  appendArtifact(artifact: Artifact): Promise<void>;
}
```

This keeps the module deep and testable because callers only need to learn the operation and contracts, not the implementation details of repo traversal or markdown generation.

### 4.6 Suggested internal seam placement

- Repo scanning belongs behind RepoMemoryModule
- Git interaction belongs behind BranchSummaryModule and FeatureContextModule
- UI rendering belongs behind CommandCentreModule
- recurring scheduling belongs behind RoutineSchedulerModule

This creates locality: changes to repo indexing, issue analysis, or release logic stay in their owning module, not across the whole application.

## 5. High-level system architecture

```text
+----------------------------+
| User / Developer           |
| Command Center UI          |
+-------------+--------------+
              |
              v
+----------------------------+
| Agent Orchestration Layer   |
| - skill router              |
| - event scheduler          |
| - artifact store           |
+-------------+--------------+
              |
      +-------+--------+
      |                |
      v                v
+----------------+  +----------------------+
| Repo Memory   |  | Integration Layer    |
| - router files |  | GitHub/Jira/Slack    |
| - indexes     |  | terminal / git       |
| - feature map |  | docs / markdown      |
+----------------+  +----------------------+
      |
      v
+----------------------------+
| Skill Execution Layer       |
| - branch summary            |
| - feature drill-down       |
| - release note generation  |
| - issue triage             |
| - sprint recap             |
+----------------------------+
```

## 5. System components

### 5.1 Repo memory layer
Responsible for storing and organizing repo context.

Components:
- repo router
- area indexes
- feature map
- changed-file tracker
- recent artifact log

Examples:
- root router file listing the main work areas
- per-area index listing important files
- feature metadata file linking issue, tests, docs, and code

### 5.2 Integration layer
Responsible for external signals from the developer environment.

Examples:
- GitHub pull requests and repositories
- Jira or Linear issue data
- Slack updates
- local git metadata and CI/test status

### 5.3 Skill layer
Responsible for specific developer tasks.

Key skills:
- summarize branch changes
- find files related to a feature
- generate an implementation checklist
- triage issue or PR
- draft release notes
- summarize test failures
- create sprint recap

Each skill should work from structured context and emit a standard output format.

### 5.4 Routine layer
Responsible for recurring system actions.

Examples:
- nightly repo digest
- release readiness scan
- weekly sprint recap
- stale work check

### 5.5 Command centre layer
Responsible for presenting the system to the user.

Examples:
- active issues
- branch summary card
- release status card
- recent artifacts list
- quick action buttons
- workspace map link

## 6. Functional architecture by responsibility

### 6.1 User interface
The frontend is a lightweight local dashboard.

Primary responsibilities:
- show active work
- allow quick actions
- show recent artifacts
- display repo health and release readiness
- expose the project map

Good initial UI patterns:
- card-based layout
- action buttons
- summary panels
- artifact list
- simple search filter

### 6.2 Orchestration service
Coordinates all work between user actions, skill execution, and external systems.

Responsibilities:
- route user requests to the right skill
- fetch repo and issue context
- call assistant prompts with structured context
- store outputs
- trigger routines

### 6.3 Memory services
Repository memory keeps the system grounded in the real project.

Responsibilities:
- keep router files current
- maintain file-to-area mapping
- store feature metadata
- store recent outputs and artifacts

### 6.4 Task execution services
These implement the skill workflows.

Examples:
- BranchSummaryService
- FeatureDrillDownService
- ReleaseReadinessService
- SprintDigestService

Each service should accept structured input and output a JSON or markdown artifact.

## 7. Data model

### 7.1 Repo context
```json
{
  "repo_name": "example-repo",
  "root_path": "/workspace/example-repo",
  "areas": [
    {
      "name": "frontend",
      "path": "apps/web",
      "tags": ["ui", "client"]
    },
    {
      "name": "backend",
      "path": "services/api",
      "tags": ["api", "server"]
    }
  ],
  "key_files": [],
  "recent_changes": []
}
```

### 7.2 Feature record
```json
{
  "feature_id": "feature-123",
  "title": "Onboarding flow",
  "issue_link": "https://jira.example.com/browse/feature-123",
  "related_files": [
    "apps/web/src/onboarding.tsx",
    "services/api/src/onboardingService.ts"
  ],
  "tests": ["apps/web/src/onboarding.spec.tsx"],
  "docs": ["docs/onboarding.md"],
  "risk_notes": ["requires auth and profile sync"],
  "checklist": [
    "review auth gating",
    "validate profile updates",
    "test migration path"
  ]
}
```

### 7.3 Artifact record
```json
{
  "artifact_id": "branch-summary-001",
  "type": "branch_summary",
  "created_at": "2026-08-31T12:00:00Z",
  "source": "feature-branch",
  "content": "...markdown summary...",
  "status": "ready"
}
```

### 7.4 Release status
```json
{
  "version": "1.4.2",
  "status": "ready",
  "confidence": 0.86,
  "blockers": [],
  "notes": "Includes onboarding improvements and API stability fixes",
  "last_checked": "2026-08-31T12:00:00Z"
}
```

## 8. Skill design pattern

Every skill should follow the same pattern:

1. fetch structured context
2. analyze the relevant files and metadata
3. summarize findings
4. generate a draft artifact
5. save it to the artifacts directory
6. return the result in a UI-friendly format

### Example skill contract
```json
{
  "skill_name": "summarize_branch_changes",
  "input": {
    "repo_path": "/workspace/repo",
    "base_branch": "main",
    "target_branch": "feature/onboarding"
  },
  "output": {
    "summary": "...",
    "changed_files": [],
    "risk_areas": [],
    "suggested_reviewers": []
  }
}
```

## 9. Routine design pattern

Each routine should have:
- schedule configuration
- trigger condition
- context collector
- summary generator
- artifact writer
- notification target

Example routine config:
```json
{
  "name": "nightly_repo_digest",
  "schedule": "0 20 * * *",
  "enabled": true,
  "repo": "/workspace/repo",
  "notify": ["slack"]
}
```

## 10. Security and privacy model

For v1, keep the model local and explicit.

Rules:
- no secrets stored in the repo memory
- credentials only live in environment variables or secure local config
- all integrations should be opt-in
- private folders can be excluded from routing
- no internet exposure required for local use

## 11. Local file layout

Suggested repo structure:
```text
agentic-os/
  app/
    dashboard/
    server/
    agents/
  memory/
    routers/
    indexes/
    artifacts/
    feature_map/
  integrations/
    github/
    jira/
    slack/
  routines/
    nightly_digest/
    weekly_summary/
    release_readiness/
  config/
    settings.json
  docs/
    architecture.md
  README.md
```

## 12. Technology choices

### Recommended stack for v1
- Python for orchestration logic and skills
- FastAPI for service endpoints if needed
- SQLite for local state
- Markdown + JSON for memory and artifacts
- simple HTML/JS dashboard or lightweight React app
- git CLI and API clients for integrations

### Why this stack
- fast to build
- good for AI-driven workflows
- simple local deployment
- easy to iterate with real user feedback

## 13. Execution architecture

The app has two main execution modes:

### 13.1 Interactive mode
User opens the dashboard and triggers a skill manually.

Flow:
- user clicks action
- orchestration fetches relevant context
- skill runs
- result is rendered to UI
- artifact is saved to disk

### 13.2 Scheduled mode
Routine worker runs automatically.

Flow:
- scheduler wakes
- routine loads repo+issue context
- summary is generated
- output saved to artifacts
- optional notification sent to Slack or user inbox

## 14. Implementation priority order

### Priority 1: repo indexing + feature drill-down
This is the first useful workflow.

### Priority 2: branch summaries
This creates immediate value for day-to-day engineering work.

### Priority 3: release readiness
This turns the system into a decision support tool.

### Priority 4: weekly digest and Slack notification
This moves the tool into real operational automation.

## 15. Risks and mitigations

### Risk: noisy repo context
Mitigation:
- maintain concise routers and indexes
- exclude private or generated directories
- keep summary prompts structured and bounded

### Risk: weak feature-to-file mapping
Mitigation:
- rely on git history, issue titles, and file names
- allow human review for final confidence

### Risk: summaries are too generic
Mitigation:
- constrain outputs to clear sections and actionable bullets
- require risk and next-step fields

### Risk: too much integration complexity
Mitigation:
- keep v1 integrations narrow and stable
- add features when usage proves value

## 16. v1 success metrics

The MVP is successful if the system can:
- map the repo correctly
- connect a feature to relevant files
- summarize PR or branch changes clearly
- draft release notes from recent work
- run at least one scheduled digest without manual involvement

## 17. Recommended first feature set

For initial shipping, build these five things:
1. repo indexer
2. feature drill-down
3. branch summary
4. release readiness draft
5. nightly digest

This is the smallest useful version of the Developer Workflow OS.

## 18. Summary

The Developer Workflow OS is best thought of as a local engineering command centre: a system that reads the repo, understands active work, and helps the engineer move from signal to action without hunting through files and tickets.

The architecture is intentionally simple, modular, and grounded in local memory and scheduled routines. This makes it practical to build quickly, test with real work, and evolve into a stronger product over time.

## 19. Next implementation step

The next phase is to scaffold the actual codebase to support:
- repo indexing
- feature context lookup
- branch summary generation
- local dashboard shell

This will create the first working build of the Developer Workflow OS.
