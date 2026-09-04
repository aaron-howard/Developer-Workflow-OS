"""
Cloudflare Workers & Serverless Entrypoint for Developer Workflow OS
"""
import sys
from pathlib import Path

# Ensure root repository directory is on sys.path for Pyodide / Cloudflare Workers
root_dir = Path(__file__).resolve().parents[1]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.server.api import create_app

# Create serverless application instance
app = create_app()

try:
    from mangum import Mangum
    handler = Mangum(app)
except ImportError:
    # Fallback handler if mangum is not installed in local environment
    handler = app


def get_serverless_app():
    return app

