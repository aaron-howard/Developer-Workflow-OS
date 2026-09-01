# Domain Documentation Configuration

**Layout:** Single-context  
**Root CONTEXT.md:** [`CONTEXT.md`](../../CONTEXT.md)  
**Architecture Decision Records:** [`docs/adr/`](../adr/)

## Overview

This project uses a **single-context layout**: one canonical `CONTEXT.md` at the repo root, plus ADRs in `docs/adr/`.

This layout works well for:
- Single-service projects
- Projects with a unified domain model
- Teams where all contexts are shared

## Files and their purposes

### CONTEXT.md (root)

The single source of truth for domain terminology, key concepts, and project constraints. All agent skills read this file to ground their work in the project's language and vision.

**Consumer rules:**
- **Read on startup:** Every agent skill reads `CONTEXT.md` once to load canonical terms
- **Use for grounding:** All generated code, specs, and reviews reference terms from the context
- **Update when:** New domain concepts emerge, terminology changes, or key constraints shift
- **Format:** Markdown with sections: Purpose, Canonical terms, Clarified distinctions, Constraints

### docs/adr/

Architecture Decision Records live here. Each file documents a significant decision: what was decided, why, and what tradeoffs were made.

**Naming convention:** `NNNN-decision-title.md` (e.g., `0001-developer-workflow-os-core-architecture.md`)

**Consumer rules:**
- **Scanned by:** Architecture analysis workflows; linked in code reviews and implementation specs
- **Lifecycle:** Once written, ADRs are immutable (prefer new ADRs for reversals, not edits)
- **Format:** Follow the [ADR template](https://github.com/joelparkerhenderson/architecture_decision_record)

## Reading the domain

1. Start with `CONTEXT.md` to understand the project's purpose and key terms
2. Reference ADRs when implementing significant features or architectural changes
3. Cite terms from `CONTEXT.md` in code comments, commit messages, and spec documents

## Editing the domain

- **Minor updates** (typos, new canonical terms): Edit `CONTEXT.md` directly
- **Significant decisions** (new architecture, major constraint): Create a new ADR in `docs/adr/`
- **Reversals** (undoing a prior decision): Create a new ADR that supersedes the old one; don't delete

## Related skills

- `domain-modeling` – Build and sharpen domain models; edit CONTEXT.md and ADRs
- `feature-inventory` – Catalog existing features and generate specs grounded in domain terms
- `to-spec` – Convert issues to specs using domain terminology
