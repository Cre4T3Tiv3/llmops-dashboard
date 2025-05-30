"""
main.py

This module initializes the FastAPI application, sets up Prometheus instrumentation,
and configures authentication-protected LLM endpoints.

Key Features:
- Exposes a `/metrics` endpoint for Prometheus scraping.
- Automatically tracks request count and latency with labeled metrics.
- Includes token issuance and LLM proxy routes.
- Uses middleware to log Prometheus-compatible metrics with label cardinality control.
"""

import time

from fastapi import Depends, FastAPI, Request
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator

from llmops.auth import verify_jwt_token
from llmops.routes import llm_proxy, token_issuer
from llmops.routes.llm_proxy import (
    router as llm_router,  # ✅ Explicit router import for echo
)

# Initialize FastAPI app
app = FastAPI()

# Attach Prometheus instrumentation
Instrumentator().instrument(app).expose(app)

# Prometheus counter: tracks total requests by endpoint, method, and user
REQUEST_COUNT = Counter(
    "request_count", "Total number of API requests", ["endpoint", "method", "user"]
)

# Prometheus histogram: tracks request latency by endpoint and user
REQUEST_LATENCY = Histogram(
    "request_latency_seconds", "Latency of API requests", ["endpoint", "user"]
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """
    Middleware to capture Prometheus metrics for each request.

    Metrics tracked:
        - REQUEST_COUNT: Total API requests by endpoint, method, and user.
        - REQUEST_LATENCY: Latency per request in seconds.

    Args:
        request (Request): Incoming FastAPI request.
        call_next (Callable): Next ASGI application handler.

    Returns:
        Response: Processed HTTP response from downstream handlers.
    """
    start_time = time.time()

    # Normalize user ID to reduce label cardinality
    ALLOWED_USERS = {"demo-user", "admin", "test-user"}
    raw_user = request.headers.get("x-user-id", "anonymous")
    user = raw_user if raw_user in ALLOWED_USERS else "anonymous"

    response = await call_next(request)
    process_time = time.time() - start_time

    REQUEST_COUNT.labels(
        endpoint=request.url.path, method=request.method, user=user
    ).inc()

    REQUEST_LATENCY.labels(endpoint=request.url.path, user=user).observe(process_time)

    return response


@app.get("/metrics")
def metrics():
    """
    Expose current Prometheus metrics at `/metrics`.

    Returns:
        Response: Plain text response formatted for Prometheus scraping.
    """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
def health_check():
    """
    Health check endpoint for readiness and uptime monitoring.

    Returns:
        dict: Basic JSON response indicating application is running.
    """
    return {"status": "ok", "message": "Welcome to LLMOps Dashboard"}


# Register token issuance route
app.include_router(token_issuer.router)

# Register protected LLM proxy routes
app.include_router(llm_proxy.router, dependencies=[Depends(verify_jwt_token)])

# ✅ Register public /llm/echo endpoint directly
app.include_router(llm_router, prefix="/llm")
