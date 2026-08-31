# Server layer

This directory is reserved for the orchestration layer, API endpoints, and skill routing logic.

Planned responsibilities:
- route requests to the correct skill
- manage structured context inputs
- save result artifacts
- expose a lightweight local API for the dashboard

Planned modules:
- orchestrator.py
- routes.py
- skill_registry.py
- artifact_store.py
