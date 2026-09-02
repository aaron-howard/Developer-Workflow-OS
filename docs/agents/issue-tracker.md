# Issue Tracker Configuration

**Tracker type:** GitHub Issues  
**Repository:** https://github.com/aaron-howard/Developer-Workflow-OS

## Overview

Issues for this project live in GitHub Issues. Engineering skills (`triage`, `to-spec`, `to-tickets`) interact with issues via the `gh` CLI.

## Workflow

### Creating issues

Use `gh issue create` or the GitHub web UI. Issues are readable by all skills immediately.

### Reading issues

Skills scan issue titles, bodies, and labels to understand current work, blockers, and triage state. Labels are the primary metadata signal (see `docs/agents/triage-labels.md`).

### Updating issues

Skills may add labels, comments, or close issues based on triage or spec workflows. All changes are auditable in GitHub's issue history.

## Consumer rules

- **Triage workflow** reads and writes labels only (via `gh issue edit`)
- **Spec workflow** reads issue bodies and titles; may post comments with spec artifacts
- **To-tickets workflow** creates new issues from specifications; reads existing issues to avoid duplicates
- **PRs as request surface** is currently **disabled** (issues are the sole entry point; external PRs won't appear in triage)

## CLI prerequisites

The `gh` CLI must be installed and authenticated:

```bash
gh auth status  # Verify login
gh issue list   # Test read access to this repo
```

If not installed, see [GitHub CLI docs](https://cli.github.com/).
