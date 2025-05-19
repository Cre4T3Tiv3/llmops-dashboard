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
from fastapi import FastAPI, Request, Depends
from fastapi.responses import Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from src.auth import verify_jwt_token
from src.routes import llm_proxy
from src.routes import token_issuer

# Initialize FastAPI app
app = FastAPI()

# Prometheus counter for number of requests by endpoint, method, and user
REQUEST_COUNT = Counter(
    "request_count",
    "Total API Requests",
    ["endpoint", "method", "user"]
)

# Prometheus histogram for request latency by endpoint and user
REQUEST_LATENCY = Histogram(
    "request_latency_seconds",
    "API Request latency",
    ["endpoint", "user"]
)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """
    Middleware that tracks metrics for every incoming HTTP request.
    Captures latency and request count with consistent label cardinality.

    Args:
        request (Request): The incoming FastAPI request object.
        call_next (Callable): The next handler in the ASGI chain.

    Returns:
        Response: The final HTTP response after processing the request.
    """
    start_time = time.time()

    # Limit label cardinality to known user IDs
    ALLOWED_USERS = {"demo-user", "admin", "test-user"}
    raw_user = request.headers.get("x-user-id", "anonymous")
    user = raw_user if raw_user in ALLOWED_USERS else "anonymous"

    response = await call_next(request)
    process_time = time.time() - start_time

    # Update Prometheus metrics
    REQUEST_COUNT.labels(
        endpoint=request.url.path,
        method=request.method,
        user=user
    ).inc()

    REQUEST_LATENCY.labels(
        endpoint=request.url.path,
        user=user
    ).observe(process_time)

    return response

@app.get("/metrics")
def metrics():
    """
    Exposes Prometheus metrics in plain text format at `/metrics`.

    Returns:
        Response: A plain-text HTTP response with all current metric data.
    """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Register API routes
app.include_router(token_issuer.router)
app.include_router(llm_proxy.router, dependencies=[Depends(verify_jwt_token)])
