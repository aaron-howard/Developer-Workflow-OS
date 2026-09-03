"""
Cloudflare Workers & Serverless Entrypoint for Developer Workflow OS
"""
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
