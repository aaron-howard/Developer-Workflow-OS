"""Visual Second Brain node-link graph generator for Memory Level 3."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def generate_repo_graph(repo_path: str = ".") -> dict[str, Any]:
    """
    Build structured node-link graph representation of repository memory.
    
    Returns nodes (directories, key files, router documents) and links
    for rendering in an interactive canvas (Visual Second Brain).
    """
    root = Path(repo_path).resolve()
    nodes: list[dict[str, Any]] = []
    links: list[dict[str, Any]] = []
    seen_nodes: set[str] = set()

    def add_node(node_id: str, label: str, node_type: str, category: str, path: str = "", extra: str = ""):
        if node_id in seen_nodes:
            return
        seen_nodes.add(node_id)
        nodes.append({
            "id": node_id,
            "label": label,
            "type": node_type,      # "root", "area", "file"
            "category": category,  # "router", "code", "doc", "skill", "test", "config"
            "path": path,
            "extra": extra,
        })

    def add_link(source: str, target: str, link_type: str = "contains"):
        links.append({
            "source": source,
            "target": target,
            "type": link_type,
        })

    # Root node
    add_node(
        node_id="root",
        label=root.name or "Developer-Workflow-OS",
        node_type="root",
        category="area",
        path="",
        extra="Repository Root",
    )

    # Key Areas
    areas = [
        ("app", "Application Core", "app"),
        ("docs", "Documentation & ADRs", "docs"),
        ("skills", "Skill Workflows", "skills"),
        (".agents", "Agent SOPs & Skills", ".agents"),
        ("tests", "Automated Test Suite", "tests"),
    ]

    for area_id, area_label, rel_path in areas:
        area_dir = root / rel_path
        if area_dir.exists():
            add_node(
                node_id=area_id,
                label=area_label,
                node_type="area",
                category="area",
                path=rel_path,
                extra=f"Directory: {rel_path}",
            )
            add_link("root", area_id, "contains")

    # Key Router Files
    routers = [
        ("CLAUDE.md", "CLAUDE.md Router", "router", "Master Agent Config & Index"),
        ("CONTEXT.md", "CONTEXT.md Domain Terms", "router", "Canonical Domain Terms"),
        ("TECHNICAL_ARCHITECTURE.md", "Technical Architecture", "doc", "Deep Module Specs"),
        ("DEVELOPER_WORKFLOW_OS_PLAN.md", "Build Plan", "doc", "v1 Roadmap & Objectives"),
        ("ARMS-Agentic-OS-Guide.pdf", "ARMS Framework Guide", "doc", "RoboNuggets OS Reference"),
    ]

    for rel_path, label, category, extra in routers:
        file_path = root / rel_path
        if file_path.exists():
            node_id = f"file_{rel_path.replace('.', '_').replace('/', '_')}"
            add_node(
                node_id=node_id,
                label=label,
                node_type="file",
                category=category,
                path=rel_path,
                extra=extra,
            )
            add_link("root", node_id, "contains")

    # Sub-file traversal for main areas
    interesting_extensions = {".py", ".html", ".js", ".css", ".md", ".pdf", ".json"}
    
    for area_id, _, rel_path in areas:
        area_dir = root / rel_path
        if not area_dir.exists():
            continue

        for p in area_dir.rglob("*"):
            if p.is_file() and p.suffix in interesting_extensions:
                if any(part.startswith(".") and part != ".agents" for part in p.parts):
                    continue
                if "__pycache__" in p.parts:
                    continue

                rel_p = str(p.relative_to(root)).replace("\\", "/")
                file_id = f"file_{rel_p.replace('.', '_').replace('/', '_')}"
                
                cat = "code"
                if rel_p.endswith((".md", ".pdf", ".txt")):
                    cat = "doc"
                elif rel_p.endswith((".json", ".toml", ".yaml")):
                    cat = "config"
                elif "skill" in rel_p.lower():
                    cat = "skill"
                elif "test" in rel_p.lower():
                    cat = "test"

                add_node(
                    node_id=file_id,
                    label=p.name,
                    node_type="file",
                    category=cat,
                    path=rel_p,
                    extra=f"Relative path: {rel_p}",
                )
                add_link(area_id, file_id, "contains")

    # Cross-reference router linkages
    claude_id = "file_CLAUDE_md"
    context_id = "file_CONTEXT_md"
    tech_id = "file_TECHNICAL_ARCHITECTURE_md"

    if claude_id in seen_nodes and context_id in seen_nodes:
        add_link(claude_id, context_id, "references")
    if context_id in seen_nodes and tech_id in seen_nodes:
        add_link(context_id, tech_id, "references")

    return {
        "repo_name": root.name,
        "total_nodes": len(nodes),
        "total_links": len(links),
        "nodes": nodes,
        "links": links,
    }
