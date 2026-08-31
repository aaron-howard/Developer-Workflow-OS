# Developer Workflow OS — Build Plan

## 1. Product summary

This project is a developer-focused Agentic OS built around the ARMS pattern:
- Skills: repeatable engineering actions
- Memory: workspace map and project routing
- Routines: scheduled repo and team summaries
- Applications: GitHub, Jira, Slack, local tooling
- Command centre: one page that exposes the system to the user

The goal is to create a local operating layer for engineers and startup builders that helps them understand what changed, what matters, what is risky, and what should be released next.

## 2. User problem

Engineering work is spread across:
- repositories
- issues and PRs
- release notes
- team updates
- docs and implementation context

Most engineers struggle to answer questions like:
- What changed in this branch?
- Which files belong to this feature?
- What is the likely implementation surface?
- What is blocking release?
- What should the team know this week?

This product turns that operational overhead into a lightweight workflow assistant.

## 3. Core concept

The system acts like a developer operating system:
- it indexes the repo and workspace
- it routes work to relevant files and issues
- it generates summaries and checklists
- it triggers daily or weekly routines
- it exposes actions from a single command centre page

## 4. Definition of done for v1

The MVP is successful when a user can:
1. point the app at a repo
2. see a workspace map and active work overview
3. ask for a feature or issue summary
4. get relevant files, likely risk areas, and an implementation checklist
5. generate a branch or PR summary
6. build a release note draft and release-readiness view
7. view scheduled digests and weekly summaries

## 5. Target user

Primary user:
- founder or product engineer
- startup building product while shipping fast
- team with multiple moving parts but no formal ops layer

Secondary users:
- engineering leads
- solo builders
- small teams with limited internal tooling

## 6. Target experience

A user opens one local dashboard and sees:
- repo health
- current work
- open issues/PRs
- feature drill-down
- release readiness
- recent artifacts

The system should feel like a developer control room, not a generic chat UI.

## 7. Product promise

The product helps the user answer:
- What changed?
- What matters?
- What is risky?
- What is ready to ship?
- What should the team know?

This is the core value proposition.

## 8. Core modules

### 8.1 Repo indexer
Purpose:
- map the repository structure into meaningful areas
- identify core modules and components
- track relevant docs and config files

Inputs:
- repository tree
- package manifests
- config files
- git metadata

Outputs:
- workspace router
- module map
- file index
- recent changed-file log

### 8.2 Feature context engine
Purpose:
- connect a feature or issue to implementation context

Inputs:
- issue or ticket title
- branch name or PR metadata
- repo files
- recent git history

Outputs:
- relevant files list
- likely implementation surface
- test files impacted
- docs impacted
- implementation checklist
- risk notes

### 8.3 Branch and PR summary engine
Purpose:
- explain what changed without requiring a human to read the full diff

Outputs:
- change summary by module
- likely intent of work
- risk areas
- reviewer checklist
- concise release note draft

### 8.4 Release readiness agent
Purpose:
- evaluate whether a change is ready to ship

Checks:
- completed work vs open blockers
- test status and CI health
- changelog coverage
- issue completeness
- rollout risk

Outputs:
- release confidence indicator
- release notes
- blocker list
- final recommendations

### 8.5 Sprint digest agent
Purpose:
- produce a human-friendly weekly summary

Inputs:
- merged PRs
- ticket updates
- issue notes
- deployment results

Outputs:
- what shipped
- what changed
- what is at risk
- blockers and follow-ups

### 8.6 Command centre UI
Purpose:
- present the system as an always-on local dashboard

Widgets:
- active work
- repo health
- recent artifacts
- feature drill-down
- branch summaries
- release status
- quick actions

## 9. Skills to build first

Build these as the first-generation skill set:

1. Summarize branch changes
   - detect the changed modules
   - explain the business or technical intent
   - surface risk and test gaps

2. Find files related to a feature
   - connect issue to code paths
   - identify tests and docs
   - generate the likely implementation surface

3. Generate implementation checklist
   - list required steps for the task
   - note missing pieces or blockers
   - include validation steps

4. Triage issue or PR
   - classify problem, scope, and risk
   - identify likely owners and affected files

5. Draft release notes
   - summarize shipped work in plain language
   - cluster improvements and fixes

6. Summarize test failures
   - locate failing areas
   - identify likely root cause
   - propose the next validation action

7. Weekly sprint recap
   - summarize completed work and remaining risks

## 10. Routines to build first

### 10.1 Nightly repo digest
When:
- every night

Purpose:
- summarize what changed today
- list changed files and modules
- highlight risk and release impact

### 10.2 Release readiness scan
When:
- daily or before release

Purpose:
- assess launch readiness
- flag blockers and missing coverage

### 10.3 Weekly sprint recap
When:
- Friday or end-of-week

Purpose:
- show delivered work, current blockers, and next steps

### 10.4 Stale-branch or dead-work check
When:
- weekly

Purpose:
- identify branches or work that may be forgotten

## 11. Application integrations

For the first release, keep integrations focused and practical:

- GitHub / GitLab: PRs, branch status, changed files
- Jira / Linear: issue state, delivery context
- Slack: daily digest and release updates
- local terminal: repo status, git diff, test commands
- docs storage: Markdown and local docs folders

Do not overbuild integrations in v1. The goal is usable visibility and summaries, not a massive platform.

## 12. Suggested stack

### Frontend
- lightweight local web app or static dashboard
- simple UI with cards and action buttons

### Backend
- Python preferred for quick AI workflows and scripting
- Node acceptable if the repo or team prefers it

### Storage
- local Markdown files for memory and artifacts
- JSON for structured indexes and metadata
- SQLite for local state if needed later

### Integration layer
- GitHub API
- Jira or Linear API
- Slack webhooks
- shell wrappers for repo commands

### Agent layer
- LLM calls with structured prompts
- file-based context assembly
- deterministic summaries and outputs

## 13. Data model

Keep the data model simple at first.

### Repo index
- repo name
- modules
- folder areas
- key files
- tags
- recent change data

### Feature record
- feature name
- issue id
- branch or PR link
- related files
- related tests
- docs refs
- risk notes
- checklist

### Artifact record
- type: summary, release note, sprint recap, feature brief
- source
- created_at
- owner
- status

### Release record
- version
- notes
- blockers
- confidence
- last checked date

## 14. UX structure

The UI should be intentionally small and useful.

### Main dashboard widgets
1. Active issues
2. Changed files / branch summary
3. Release readiness
4. Recent artifacts
5. Feature drill-down
6. Workspace map

### Action buttons
- Summarize branch
- Find feature files
- Build implementation checklist
- Draft release notes
- Run weekly digest

## 15. High-priority user flows

### Flow A: branch summary
User action:
- select branch or PR

System result:
- repo diff summary
- changed modules
- likely intent
- impacted files
- risk notes

### Flow B: issue-to-code mapping
User action:
- select issue or feature name

System result:
- relevant files
- associated tests
- docs references
- checklist
- blockers

### Flow C: release prep
User action:
- click release readiness

System result:
- release summary
- open blocker list
- issue coverage
- changelog draft
- recommended actions

### Flow D: weekly team digest
User action:
- run weekly digest

System result:
- summary of shipped work
- remaining ambiguity
- key risks
- next focus areas

## 16. First sprint plan

### Sprint 1 — foundation
Goals:
- repo indexing
- workspace map
- basic dashboard shell
- feature file lookup
- branch summary generation

Tasks:
1. initialize project structure
2. create repo indexer
3. create simple repo router and project metadata files
4. build local dashboard shell
5. add feature file lookup skill
6. add branch summary skill
7. validate with one real repository

Success criteria:
- user can point app at a repo
- app maps the repo structure
- it returns relevant files for a feature request
- it produces a readable summary of a branch change

### Sprint 2 — planning and release intelligence
Goals:
- issue-to-feature mapping
- implementation checklist generation
- release note draft generation
- release readiness logic

Tasks:
1. add issue-to-code mapping workflow
2. add implementation checklist generation
3. add release notes generation
4. add blocker and risk detection
5. hook into dashboard actions

Success criteria:
- selecting a feature produces a structured output
- release notes can be generated from merged work
- dashboard shows readiness status

### Sprint 3 — automation and recurring insight
Goals:
- scheduled routines
- weekly digest
- Slack updates
- artifact storage and navigation

Tasks:
1. add nightly repo digest routine
2. add weekly sprint recap routine
3. add artifact log and recent outputs
4. add Slack/email notification support
5. validate recurring workflow on a test repo

Success criteria:
- the OS generates scheduled outputs without manual prompting
- team members can see outputs in one place

## 17. Risks and mitigations

### 17.1 Risk: too much generic AI behavior
Mitigation:
- keep workflows narrow and structured
- set clear output formats
- prioritize deterministic summaries

### 17.2 Risk: repo indexing becomes noisy
Mitigation:
- keep routers simple
- focus on top folders and key areas
- avoid over-documenting

### 17.3 Risk: outputs are not actionable
Mitigation:
- require each skill to output structured action items
- keep summaries short and decision-oriented

### 17.4 Risk: too many integrations too early
Mitigation:
- only include the top three integrations first
- add more later based on real usage

## 18. Minimal viable operating principle

The product should do one simple thing extremely well:
- help the developer understand what is happening in the work, and what is next.

That is the foundation of the Agentic OS.

## 19. Recommended first milestone

The milestone to target first is:

Project name: Developer Workflow OS MVP

User value:
- repo map
- feature file lookup
- branch summary generation
- release readiness draft

This is the smallest meaningful product that matches the ARMS framework and gives a user immediate operational value.

## 20. Next action

The next immediate implementation step is:
1. scaffold the project
2. build the repo indexer
3. build the feature file lookup
4. build the branch summary action
5. connect them to a local dashboard

This sequence gives the fastest route to a usable first build.
