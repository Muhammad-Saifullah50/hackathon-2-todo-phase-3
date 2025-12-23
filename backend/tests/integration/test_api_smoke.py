import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_app_startup_and_health(client: AsyncClient) -> None:
    """Test that the app starts correctly and the health endpoint is accessible."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "todo-api"
