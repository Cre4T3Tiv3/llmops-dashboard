"""
token_issuer.py

This module defines an authentication route for issuing JWT tokens using FastAPI.

It provides a simple endpoint `/auth/token` that generates a short-lived JWT for a fixed demo user.
This is primarily used for testing and local development scenarios requiring authentication via Bearer tokens.

Environment Variables:
    JWT_SECRET (str): Secret key used for signing JWTs. Must be defined in the environment.
                      🚨 WARNING: Never hardcode secrets in production environments.

Dependencies:
    - fastapi.APIRouter: Routing utility for modular endpoint grouping.
    - jwt.encode: Encodes and signs the JWT using HS256.
"""

import datetime
import os

import jwt
from fastapi import APIRouter

# Require JWT secret from env
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError(
        "❌ JWT_SECRET is not set in the environment. Please define it in your .env file or environment variables."
    )

# JWT signing algorithm
JWT_ALGORITHM = "HS256"

# FastAPI router for this module
router = APIRouter()


@router.post("/auth/token")
def issue_token():
    """
    Issues a short-lived demo JWT token for the hardcoded user "demo-user".

    The token:
    - Uses `sub: demo-user` as the subject claim.
    - Is signed using HS256 and a secret key.
    - Expires in 15 minutes.

    Returns:
        dict: Dictionary with a single key `access_token` containing the signed JWT.
    """
    demo_user = "demo-user"
    payload = {
        "sub": demo_user,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {"access_token": token}
