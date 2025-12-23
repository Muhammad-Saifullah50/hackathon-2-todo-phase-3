from datetime import datetime
import json
from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from jwt.algorithms import get_default_algorithms
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.db.session import get_db
from src.models.user import User

# Better Auth JWT plugin uses EdDSA (Ed25519) by default
ALGORITHM = "EdDSA"
ISSUER = "todo-auth"
AUDIENCE = "todo-api"

security = HTTPBearer()

# Cache for public key
_public_key_cache: str | dict[str, Any] | None = None


class TokenData(BaseModel):
    
    """Payload data from the JWT token."""

    sub: str
    email: str | None = None
    name: str | None = None
    email_verified: bool = False


async def get_public_key(session: AsyncSession) -> str | dict[str, Any]:
    """
    Get the public key from the jwks table for JWT verification.

    Args:
        session: The database session.

    Returns:
        str | dict: The public key (PEM format or JWK dict).

    Raises:
        HTTPException: If no public key is found.
    """
    global _public_key_cache

    # Return cached key if available
    if _public_key_cache is not None:
        return _public_key_cache

    # Query the jwks table for the public key
    from sqlalchemy import text

    result = await session.execute(
        text("SELECT \"publicKey\" FROM jwks ORDER BY \"createdAt\" DESC LIMIT 1")
    )
    row = result.fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No public key found in database. Please ensure Better Auth is properly configured.",
        )

    public_key_raw = row[0]
    
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

    _public_key_cache = public_key
    return public_key


async def get_current_user(
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency to verify the JWT token and return the current user.

    Args:
        token: The Bearer token from the Authorization header.
        session: The database session.

    Returns:
        User: The authenticated user object.

    Raises:
        HTTPException: If the token is invalid, expired, or the user doesn't exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Get the public key from the database
        public_key_data = await get_public_key(session)
        
        # Prepare the key for PyJWT
        key = public_key_data
        if isinstance(public_key_data, dict):
            # Convert JWK to a key object using PyJWT's PyJWK
            py_jwk = jwt.PyJWK(public_key_data)
            key = py_jwk.key

        # Decode and verify the JWT token using the public key
        # Better Auth JWT plugin uses EdDSA (Ed25519) by default
        payload = jwt.decode(
            token.credentials,
            key,
            algorithms=["EdDSA"],
            audience=AUDIENCE,
            issuer=ISSUER,
            options={"verify_aud": True, "verify_iss": True}
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(
            sub=user_id,
            email=payload.get("email"),
            name=payload.get("name"),
            email_verified=payload.get("email_verified", False),
        )
    except jwt.PyJWTError as e:
        print(f"JWT verification error: {e}")  # Debug logging
        print(f"Public Key used: {public_key_data}")
        print(f"Token (first 50 chars): {token.credentials[:50]}")
        raise credentials_exception

    # Fetch user from database to ensure they still exist
    user = await session.get(User, token_data.sub)
    if user is None:
        raise credentials_exception

    return user
