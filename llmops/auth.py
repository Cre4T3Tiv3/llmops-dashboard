"""
auth.py

This module provides JWT-based authentication for FastAPI routes.

Environment Variables:
    JWT_SECRET (str): Secret key used to sign and verify JWT tokens.
                      This must be defined in the environment.
                      🚨 WARNING: Do not hardcode secrets in production.

Dependencies:
    - fastapi.security.HTTPBearer: Used to extract Bearer token from request headers.
    - jwt.decode: Verifies and decodes the token.
"""

import os

import jwt
from dotenv import load_dotenv
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWTError

# Load environment variables from .env file
load_dotenv()

# Get JWT_SECRET from environment (required)
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError(
        "❌ JWT_SECRET is not set in the environment. Please define it in your .env"
    )

# JWT signing algorithm
JWT_ALGORITHM = "HS256"

# FastAPI security scheme to extract Bearer tokens from Authorization header
security = HTTPBearer()


def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Dependency function to verify a JWT token passed via Authorization header.

    Returns:
        str: User identifier (`sub` claim) extracted from the token.

    Raises:
        HTTPException: If the token is:
            - Invalid
            - Expired
            - Missing the required `sub` claim
    """
    try:
        # Decode and validate JWT
        payload = jwt.decode(
            credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM]
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token missing subject")
        return user_id

    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
