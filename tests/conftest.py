"""
conftest.py

Global pytest fixtures shared across all test modules.

This module includes a reusable fixture that returns a valid JWT token
signed with the JWT_SECRET env var.

Environment:
    JWT_SECRET (str): Must be set in the test environment or .env.

⚠️ This fixture should be securely configured in CI/CD environments.
"""

import datetime
import os

import jwt
import pytest


@pytest.fixture
def jwt_token():
    """
    Generates a valid JWT token for the user `demo-user`.

    The token is signed using HS256 and expires in 5 minutes from the time of creation.

    Returns:
        str: A JWT string encoded using the environment-provided secret key.

    Raises:
        RuntimeError: If JWT_SECRET is not defined in the environment.
    """
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise RuntimeError(
            "❌ JWT_SECRET not set in environment. Required for token fixture."
        )

    payload = {
        "sub": "demo-user",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
    }
    return jwt.encode(payload, secret, algorithm="HS256")
