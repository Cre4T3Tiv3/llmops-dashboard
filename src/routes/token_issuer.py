"""
token_issuer.py

This module defines an authentication route for issuing JWT tokens using FastAPI.

It provides a simple endpoint `/auth/token` that generates a short-lived JWT for a fixed demo user.
This is primarily used for testing and local development scenarios requiring authentication via Bearer tokens.

Environment Variables:
- JWT_SECRET: The secret key used to sign JWTs. Falls back to "supersecretkey" if not set.
"""

import datetime
import os

import jwt
from fastapi import APIRouter

# Secret key used for signing JWT tokens
JWT_SECRET = os.getenv("JWT_SECRET", "supersecretkey")

# Signing algorithm for JWT (HMAC SHA256)
JWT_ALGORITHM = "HS256"

# Create a FastAPI router instance
router = APIRouter()


@router.post("/auth/token")
def issue_token():
    """
    Issues a demo JWT token with a fixed user ID ("demo-user").

    The token is signed using the HS256 algorithm and includes an expiration time of 15 minutes from issuance.

    Returns:
        dict: A dictionary containing the `access_token` string.
    """
    demo_user = "demo-user"
    payload = {
        "sub": demo_user,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {"access_token": token}
