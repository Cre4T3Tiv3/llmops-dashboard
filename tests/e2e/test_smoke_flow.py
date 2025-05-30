"""
test_smoke_flow.py

Smoke test to verify basic service availability for the LLMOps stack.

Checks include:
- FastAPI service responding at the root endpoint (`/`)
- Prometheus metrics endpoint (`/metrics`) is exposed and populated
"""

import time

import httpx
import pytest


@pytest.mark.e2e
def test_smoke_stack_health():
    """
    Verifies core service availability for the LLMOps stack.

    This test ensures:
        - The FastAPI app is reachable at `http://localhost:8000`
        - The root endpoint (`/`) returns 200 OK and expected content
        - The `/metrics` endpoint returns 200 OK and includes Prometheus data

    Raises:
        AssertionError: If any of the expected responses or contents are missing.
    """
    # Wait for backend to be ready (retry for up to 5s)
    url = "http://localhost:8000"
    for _ in range(10):
        try:
            res = httpx.get(url)
            if res.status_code == 200:
                break
        except httpx.ConnectError:
            time.sleep(0.5)
    else:
        pytest.fail("FastAPI backend not running on localhost:8000")

    # Check root
    res_root = httpx.get(url)
    assert res_root.status_code == 200
    assert "LLMOps Dashboard" in res_root.text

    # Check metrics
    res_metrics = httpx.get(f"{url}/metrics")
    assert res_metrics.status_code == 200
    assert "http_requests_total" in res_metrics.text
