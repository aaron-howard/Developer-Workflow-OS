#!/usr/bin/env python
"""
Developer Workflow OS - Local API Server

Runs the command centre API server on a configurable port.
Serves repo memory, branch summaries, release readiness, and weekly digests.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from app.server.api import create_app


def main():
    parser = argparse.ArgumentParser(
        description="Developer Workflow OS local API server"
    )
    parser.add_argument(
        "--repo",
        type=str,
        default=".",
        help="Path to the git repository (default: current directory)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to bind to (default: 5000)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run in debug mode (default: False)",
    )

    args = parser.parse_args()

    repo_path = Path(args.repo).resolve()
    if not repo_path.exists():
        print(f"Error: Repository path does not exist: {repo_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Starting Developer Workflow OS")
    print(f"Repository: {repo_path}")
    print(f"Server: http://{args.host}:{args.port}")
    print()
    print("Available endpoints:")
    print("  GET  /api/repo/index")
    print("  GET  /api/repo/feature?feature=<name>")
    print("  GET  /api/branch/summary?base=main&target=<branch>")
    print("  GET  /api/release/readiness?base=main")
    print("  GET  /api/digest/weekly?base=main")
    print()

    app = create_app(repo_path=str(repo_path))
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
