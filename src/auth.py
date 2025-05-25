"""
auth.py

This module provides JWT-based authentication for FastAPI routes.

It defines a `verify_jwt_token` dependency that can be used to secure API endpoints
by requiring a valid Bearer token. The JWT is expected to include a `sub` (subject)
claim identifying the user.

Environment Variables:
- JWT_SECRET: Secret key used to sign and verify JWT tokens.
"""

import os

import jwt
from dotenv import load_dotenv
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWTError

# Load environment variables from .env file
load_dotenv()

# Secret key used to sign/verify JWTs
JWT_SECRET = os.getenv("JWT_SECRET", "supersecretkey")

# JWT signing algorithm
JWT_ALGORITHM = "HS256"

# FastAPI security scheme for extracting Bearer tokens from the Authorization header
security = HTTPBearer()


def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Verifies a JWT token passed via the Authorization header.

    Args:
        credentials (HTTPAuthorizationCredentials): Automatically injected
            by FastAPI's Security dependency using HTTPBearer.

    Returns:
        str: The user ID (`sub` field) extracted from the token.

    Raises:
        HTTPException: If the token is missing, invalid, expired, or lacks a subject.
    """
    try:
        # Decode the JWT and validate its signature and expiration
        payload = jwt.decode(
            credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM]
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token missing subject")
        return user_id
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
