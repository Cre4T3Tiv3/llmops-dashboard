"""
test_llm_flow.py

End-to-end test for the `/llm` route in the LLMOps FastAPI service.

This test:
- Generates a valid JWT using the `make generate-jwt` command.
- Sends a POST request to the `/llm` endpoint with a test prompt and token.
- Asserts a successful 200 response and the presence of a 'response' field in the returned JSON.

Requires the FastAPI app to be running locally at http://localhost:8000
and that the test environment supports `make generate-jwt`.
"""

import subprocess

import httpx
import pytest


@pytest.mark.e2e
def test_llm_flow():
    """
    End-to-end test to verify the `/llm` endpoint returns a valid response.

    Steps:
    - Generates a short-lived JWT token using the Makefile command.
    - Sends a POST request with the token and a dummy prompt.
    - Asserts that the response code is 200 and the payload contains a 'response' key.
    """
    # Generate a demo JWT token by invoking the Makefile task
    jwt = subprocess.check_output(["make", "-s", "generate-jwt"])
    token = jwt.decode("utf-8").strip()

    # POST to the `/llm` route with proper headers and dummy prompt
    res = httpx.post(
        "http://localhost:8000/llm",
        headers={
            "Authorization": f"Bearer {token}",
            "x-user-id": "e2e-user",
            "Content-Type": "application/json",
        },
        json={"prompt": "test prompt"},
    )

    # Verify 200 OK response and that the payload includes a response field
    assert res.status_code == 200
    assert "response" in res.json()
