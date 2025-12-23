from typing import Any

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db

router = APIRouter()


@router.get("")
async def health_check(
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Basic health check endpoint with database validation."""
    db_connected = False
    alembic_version = None
    
    try:
        # Check connection
        await db.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        db_connected = False

    if db_connected:
        try:
            # Check alembic version (optional, might not exist in tests or fresh DB)
            result = await db.execute(text("SELECT version_num FROM alembic_version"))
            alembic_version = result.scalar()
        except Exception:
            # Table might not exist yet
            pass

    if not db_connected:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "healthy" if db_connected else "degraded",
        "service": "todo-api",
        "database": {
            "connected": db_connected,
            "migration_version": alembic_version,
        }
    }
