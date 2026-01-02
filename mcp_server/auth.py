"""JWT authentication for MCP server using Better Auth.

This module provides JWT token verification compatible with Better Auth's
EdDSA (Ed25519) tokens. Public keys are fetched from the database jwks table.
"""

import json
import logging
import time
from typing import Any, Optional, Tuple

import jwt
import asyncpg

logger = logging.getLogger(__name__)

# Better Auth JWT configuration
ALGORITHM = "EdDSA"
ISSUER = "todo-auth"
AUDIENCE = "todo-api"

# Cache for public key with TTL (Time To Live)
_public_key_cache: Optional[Tuple[str | dict[str, Any], float]] = None
CACHE_TTL_SECONDS = 3600  # 1 hour


async def get_public_key(pool: asyncpg.Pool) -> str | dict[str, Any]:
    """Get the public key from the jwks table for JWT verification.

    Uses a TTL-based cache (1 hour) to avoid repeated database queries while
    ensuring key rotation works properly without server restart.

    Args:
        pool: Database connection pool.

    Returns:
        The public key (PEM format or JWK dict).

    Raises:
        ValueError: If no public key is found.
    """
    global _public_key_cache

    # Check if cache is valid
    if _public_key_cache is not None:
        cached_key, cached_timestamp = _public_key_cache
        cache_age = time.time() - cached_timestamp

        if cache_age < CACHE_TTL_SECONDS:
            logger.debug(f"Using cached public key (age: {cache_age:.0f}s)")
            return cached_key
        else:
            logger.debug(f"Public key cache expired (age: {cache_age:.0f}s), refetching")

    # Query the jwks table for the public key
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            'SELECT "publicKey" FROM jwks ORDER BY "createdAt" DESC LIMIT 1'
        )

    if row is None:
        raise ValueError("No public key found in database. Please ensure Better Auth is configured.")

    public_key_raw = row["publicKey"]

    try:
        # Try to parse as JWK (JSON Web Key)
        public_key = json.loads(public_key_raw)
        if isinstance(public_key, dict) and "alg" not in public_key:
            # Better Auth uses EdDSA for Ed25519 keys
            if public_key.get("kty") == "OKP" and public_key.get("crv") == "Ed25519":
                public_key["alg"] = "EdDSA"
    except (json.JSONDecodeError, TypeError):
        # Fallback to raw string (PEM)
        public_key = public_key_raw

    # Cache the key
    _public_key_cache = (public_key, time.time())
    logger.debug("Public key cached successfully")
    return public_key


async def verify_jwt_token(token: str, pool: asyncpg.Pool) -> dict[str, Any]:
    """Verify JWT token and extract user information.

    Args:
        token: JWT token string (without "Bearer " prefix).
        pool: Database connection pool for fetching public key.

    Returns:
        Dictionary containing user information from token claims.

    Raises:
        ValueError: If token is invalid, expired, or verification fails.
    """
    if not token:
        raise ValueError("No token provided")

    try:
        # Get public key from database
        public_key_data = await get_public_key(pool)

        # Prepare the key for PyJWT
        key = public_key_data
        if isinstance(public_key_data, dict):
            # Convert JWK to a key object using PyJWT's PyJWK
            py_jwk = jwt.PyJWK(public_key_data)
            key = py_jwk.key

        # Decode and verify the JWT token using the public key
        payload = jwt.decode(
            token,
            key,
            algorithms=[ALGORITHM],
            audience=AUDIENCE,
            issuer=ISSUER,
            options={"verify_aud": True, "verify_iss": True, "verify_exp": True}
        )

        # Extract user ID (Better Auth uses 'sub' claim)
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Token missing 'sub' claim (user ID)")

        return {
            "user_id": user_id,
            "email": payload.get("email"),
            "name": payload.get("name"),
            "email_verified": payload.get("email_verified", False),
            "claims": payload
        }

    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid token: {str(e)}")
    except Exception as e:
        raise ValueError(f"Token verification failed: {str(e)}")


async def extract_user_id_from_authorization(
    authorization: Optional[str],
    pool: asyncpg.Pool
) -> str:
    """Extract and verify user ID from Authorization header.

    Args:
        authorization: Authorization header value (e.g., "Bearer <token>").
        pool: Database connection pool.

    Returns:
        Verified user ID from token.

    Raises:
        ValueError: If authorization is missing, invalid, or token verification fails.
    """
    if not authorization:
        raise ValueError("Authorization header required. Please provide: 'Bearer <token>'")

    # Extract token from "Bearer <token>" format
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise ValueError(
            "Invalid authorization header format. Expected: 'Bearer <token>'"
        )

    token = parts[1]

    # Verify token and extract user ID
    user_info = await verify_jwt_token(token, pool)
    return user_info["user_id"]
