"""API dependencies for authentication and request handling."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlmodel import Session

from ..config import settings
from ..db.session import get_db
from ..models.user import User

# HTTP Bearer security scheme for JWT tokens
security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: Annotated[Session, Depends(get_db)],
) -> User:
    """Extract and validate the current user from JWT token.

    Args:
        credentials: HTTP Bearer authorization credentials containing JWT token.
        session: Database session for user lookup.

    Returns:
        User: The authenticated user object.

    Raises:
        HTTPException: 401 if token is invalid or user not found.
    """
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id: str | None = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Query user from database
    user = session.get(User, user_id)

    if user is None:
        raise credentials_exception

    return user
