"""
test_metrics_exposure.py

End-to-end test for validating Prometheus metrics endpoint exposure.

This module ensures that the `/metrics` endpoint is live and returns
expected Prometheus-formatted metric keys, such as request counts.
"""

import httpx
import pytest


@pytest.mark.e2e
def test_metrics_endpoint():
    """
    Verify that the /metrics endpoint is accessible and exposes expected Prometheus keys.

    This test checks:
        - The endpoint returns HTTP 200 OK
        - The output includes `request_count_total`, indicating metric export is functional

    Raises:
        AssertionError: If the endpoint is unreachable or metrics are missing.
    """
    res = httpx.get("http://localhost:8000/metrics")
    assert res.status_code == 200
    assert "request_count_total" in res.text
