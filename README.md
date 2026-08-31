# Developer Workflow OS

A local Agentic OS for engineering work: workspace memory, feature drill-down, branch summaries, release readiness, and daily routines.

## Project goal

This project aims to provide a lightweight command centre for developers and startup builders so they can understand repo state, issue context, change impact, and release readiness without manually hunting through files and tickets.

## Planned structure

- app/dashboard: command centre UI
- app/server: orchestration and API layer
- memory: repo memory, indexes, and artifacts
- skills: targeted developer actions
- docs/adr: architectural decisions

## Current status

This repository currently contains the planning and architecture artifacts for the first MVP. The next step is to scaffold the reusable modules and a working dashboard shell.

## MVP focus

1. repo indexing and workspace map
2. feature-to-file analysis
3. branch summary generation
4. release readiness draft
5. nightly digest routine
