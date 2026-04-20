"""FastAPI application entry point for OS-APOW.

Provides the main ASGI application with:
- Webhook endpoint for GitHub events (POST /webhooks/github)
- Health check endpoint (GET /health)
- Auto-generated API documentation at /docs
"""

from fastapi import FastAPI

from osapow.ear.webhook import router as webhook_router

app = FastAPI(
    title="OS-APOW",
    description="Orchestration System - Automated Pipeline Orchestration Workflow",
    version="0.1.0",
)

app.include_router(webhook_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns a JSON payload indicating the service is online.
    Used by Docker healthcheck and load balancers.
    """
    return {"status": "online", "system": "OS-APOW Notifier"}
