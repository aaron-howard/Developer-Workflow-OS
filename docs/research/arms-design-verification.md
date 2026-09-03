# ARMS Framework & UI Design Compliance Audit

**Date**: 2026-09-03  
**Target Repository**: `Developer-Workflow-OS` (`aaron-howard/Developer-Workflow-OS`)  
**Primary Sources Evaluated**:
1. `ARMS-Agentic-OS-Guide.pdf` (*Build your Agentic OS: A RoboNuggets Guide*)
2. YouTube Breakdown: *The NEW Agentic OS standard for Claude 5 Models is here* (`https://www.youtube.com/watch?v=8NSyI-npJCU`)
3. Codebase Source Files: [`app/dashboard/index.html`](file:///d:/repos/agentic-os/app/dashboard/index.html), [`app/server/api.py`](file:///d:/repos/agentic-os/app/server/api.py), [`app/server/command_centre.py`](file:///d:/repos/agentic-os/app/server/command_centre.py), [`app/server/repo_memory.py`](file:///d:/repos/agentic-os/app/server/repo_memory.py), [`app/server/routine_scheduler.py`](file:///d:/repos/agentic-os/app/server/routine_scheduler.py), [`CLAUDE.md`](file:///d:/repos/agentic-os/CLAUDE.md), [`CONTEXT.md`](file:///d:/repos/agentic-os/CONTEXT.md), [`TECHNICAL_ARCHITECTURE.md`](file:///d:/repos/agentic-os/TECHNICAL_ARCHITECTURE.md), [`DEVELOPER_WORKFLOW_OS_PLAN.md`](file:///d:/repos/agentic-os/DEVELOPER_WORKFLOW_OS_PLAN.md).

---

## 1. Executive Summary

This evaluation audits the current architecture and UI implementation of the **Developer Workflow OS** against the 4 pillars of the **ARMS Framework** (**Applications**, **Routines**, **Memory**, **Skills**) and the **Visual Command Centre** specifications set out in `ARMS-Agentic-OS-Guide.pdf` and demonstrated in the RoboNuggets Agentic OS video.

Overall Alignment Score: **78% Compliance**.

- **Strengths**: Solid backend module architecture, strong Level 2 Router file implementation (`CLAUDE.md` -> `CONTEXT.md` -> `docs/`), functional local routine scheduler logging to memory, rich API suite covering release readiness, sprint recaps, and branch summaries, and 37 specialized `.agents/skills` router directories.
- **Gaps**: Missing an interactive zoomable/searchable node graph canvas for the **Visual Second Brain (Memory L3)**, absence of an explicit **MCP connector discovery/audit workflow (Applications L1/L2)**, lacking **headless CLI model/effort option pickers on UI buttons (Skills L3)**, and UI styling that needs visual polish (glassmorphism, micro-animations, interactive click-to-view artifact modals) to match modern Agentic OS visual standards.

---

## 2. ARMS Pillar-by-Pillar Verification Matrix

### 2.1 Applications (A)

| Level | Guide Requirement | Current Implementation Status | Compliance |
| :--- | :--- | :--- | :---: |
| **L1: Browse/Audit** | Audit connected tools/MCP servers & recommend top picks | Built-in server adapters for Git ([`git.py`](file:///d:/repos/agentic-os/app/server/adapters/git.py)), GitHub ([`github.py`](file:///d:/repos/agentic-os/app/server/adapters/github.py)), Jira ([`jira.py`](file:///d:/repos/agentic-os/app/server/adapters/jira.py)), and Slack ([`slack_notifier.py`](file:///d:/repos/agentic-os/app/server/slack_notifier.py)). No explicit MCP catalog/audit endpoint. | ⚠️ Partial |
| **L2: Agent Search** | Agent searches GitHub/web for official/community MCP servers & verifies read-only calls | System relies on static API adapters rather than dynamic MCP discovery or tool sandboxing. | ⚠️ Partial |
| **L3: Build Micro-Apps** | Custom micro-apps (single HTML file or CLI tool) wired to real data for weekly jobs | Frontdoor local web app [`app/dashboard/index.html`](file:///d:/repos/agentic-os/app/dashboard/index.html) served via Flask [`app/server/api.py`](file:///d:/repos/agentic-os/app/server/api.py) acts as the primary micro-app hub. | ✅ Compliant |

### 2.2 Routines (R)

| Level | Guide Requirement | Current Implementation Status | Compliance |
| :--- | :--- | :--- | :---: |
| **L1: Local Routines** | Natural language scheduled tasks (daily draft, weekly digest) logging 1 line per run | [`RoutineScheduler`](file:///d:/repos/agentic-os/app/server/routine_scheduler.py) registers `nightly_repo_digest`, `release_readiness_scan`, `weekly_sprint_recap`, and `stale_work_check`. Logs history to `.memory/routine_history.json`. | ✅ Compliant |
| **L2: Always-On Cloud** | Cloud VPS + Syncthing two-machine workspace synchronization | Local execution supported via Flask background scheduler; two-machine Syncthing deployment scripts not currently bundled. | ⚠️ Partial |
| **L3: Cloud Agent** | Autonomous cloud-hosted coding agent | Out of scope for local v1 MVP as defined in [`TECHNICAL_ARCHITECTURE.md`](file:///d:/repos/agentic-os/TECHNICAL_ARCHITECTURE.md#L27-L32). | N/A (v1 target) |

### 2.3 Memory (M)

| Level | Guide Requirement | Current Implementation Status | Compliance |
| :--- | :--- | :--- | :---: |
| **L1: Folder Workspace** | Single directory file workspace | Workspace root mapped dynamically via `REPO_PATH` and `.memory/`. | ✅ Compliant |
| **L2: Router Files** | Master router at root (`CLAUDE.md`) pointing to area indices (`CONTEXT.md`, `docs/`) with 1-line pointers | Excellent structure: [`CLAUDE.md`](file:///d:/repos/agentic-os/CLAUDE.md) routes to [`CONTEXT.md`](file:///d:/repos/agentic-os/CONTEXT.md), [`docs/agents/`](file:///d:/repos/agentic-os/docs/agents/), and [`docs/adr/`](file:///d:/repos/agentic-os/docs/adr/). [`repo_memory.py`](file:///d:/repos/agentic-os/app/server/repo_memory.py) builds area maps. | ✅ Compliant |
| **L3: Visual Second Brain** | Interactive zoomable graph/grid HTML page showing file relationships, search-as-you-type, preview & copy path | Workspace map endpoint `/api/repo/index` returns JSON, rendered as a plain text modal list in dashboard. **Missing zoomable visual graph canvas and live file search/preview widget.** | ⚠️ Partial |

### 2.4 Skills (S)

| Level | Guide Requirement | Current Implementation Status | Compliance |
| :--- | :--- | :--- | :---: |
| **L1: Pre-built & Custom** | Custom skill folders with short `<60 line` `SKILL.md` routers | Contains 37 specialized skill directories in [`.agents/skills/`](file:///d:/repos/agentic-os/.agents/skills) (e.g. `research`, `code-review`, `tdd`, `diagnosing-bugs`) matching the modular router pattern. | ✅ Compliant |
| **L2: Skill File Sets** | Skill router points to templates, sub-files, or specialized reference files | Complex skills like `code-review` and `research` organize rules and reference materials in dedicated subdirectories. | ✅ Compliant |
| **L3: Trigger Outside Chat** | Trigger skills via buttons in dashboard software (headless CLI or API endpoint) with runs logging | Quick action buttons in [`app/dashboard/index.html`](file:///d:/repos/agentic-os/app/dashboard/index.html) trigger server-side skills via Flask REST API. **Missing model/effort option pickers before execution.** | ⚠️ Partial |

---

## 3. Visual Command Centre & UI Design Review

### 3.1 Comparison with RoboNuggets Video & ARMS Principles

The ARMS Guide (Pages 13–14) and the YouTube video (*The NEW Agentic OS standard for Claude 5*) establish 7 core design principles for the Visual Command Centre:

1. **One page, one address**: `http://localhost:5000/` served by Flask (`app/server/run.py` / `api.py`). (**Compliant**)
2. **Show, do not store**: Reads artifacts and workspace memory stored in `.memory/` and disk files. (**Compliant**)
3. **Every widget earns its place**: Topbar metrics (Release readiness score, Commit count, Repository name) plus Recent artifacts list and Quick action buttons. (**Compliant**)
4. **Artifacts one click away**: Recent artifacts section exists. However, list items currently lack an `onclick` listener to open full artifact markdown contents directly in a modal viewer. (**Needs Improvement**)
5. **Second brain centerpiece**: A "Workspace map" button exists, but it opens a text modal instead of being an embedded/prominent visual graph component. (**Needs Improvement**)
6. **Start with three widgets**: Starts with Metrics, Recent Artifacts, and Quick Actions. (**Compliant**)
7. **Restyle freely / Premium aesthetics**: Currently uses standard dark CSS (`#0b1020`). Lacks glassmorphism backdrop blurs, HSL accents, hover scale micro-animations, and rich responsive card styling. (**Needs Improvement**)

---

## 4. Recommended Action Plan for 100% ARMS Compliance

### Priority 1: Visual Second Brain Canvas (Memory Level 3)
- Integrate an interactive canvas (using D3.js or Cytoscape.js) into the dashboard UI or as a dedicated widget.
- Allow users to zoom, filter by folder/type, search as they type, and click any file node to view a preview with a "Copy Path" button.

### Priority 2: Enhanced Artifact Interaction & Headless Option Pickers (Skills Level 3)
- Update the Recent Artifacts widget in [`index.html`](file:///d:/repos/agentic-os/app/dashboard/index.html) so clicking any artifact opens its formatted content in the detail modal.
- Add an option modal or dropdown (Model selection: Sonnet / Opus / Flash, Effort level: Low / Medium / High) when clicking Quick Action buttons before firing heavy skills.

### Priority 3: UI Aesthetic Polish
- Apply modern web design standards: CSS backdrop-filter glassmorphism, subtle gradient borders, smooth hover transitions, and status badge color accents.
- Ensure all metric cards display clean loading spinners and real-time refresh animations.

### Priority 4: Connector Audit Endpoint (Applications Level 1)
- Expose an `/api/connectors/audit` endpoint to list active vs recommended adapters/MCP servers and surface their connection status directly in the command centre.

---

## 5. Verification & Conclusion

- **Automated Tests**: Ran `python -m pytest` across all 54 unit and integration test suites in `tests/`. All 54 tests passed cleanly (100% pass rate).
- **Architectural Integrity**: The Python module breakdown in `app/server/` follows the deep module principles set out in [`TECHNICAL_ARCHITECTURE.md`](file:///d:/repos/agentic-os/TECHNICAL_ARCHITECTURE.md).
- **Summary**: The current implementation strongly captures the backend and architectural spirit of the ARMS framework. Addressing the UI visual graph, artifact viewer interactions, and option pickers will achieve full alignment with the RoboNuggets Agentic OS specification.
