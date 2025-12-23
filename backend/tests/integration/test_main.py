
import pytest
from fastapi.testclient import TestClient
from src.main import app
from unittest.mock import patch, AsyncMock

def test_app_lifespan():
    """Test the application lifespan events (startup/shutdown)."""
    with patch("src.database.check_db_connection", new_callable=AsyncMock) as mock_check:
        mock_check.return_value = True
        # Using TestClient as a context manager triggers lifespan events
        with TestClient(app) as client:
            response = client.get("/health")
            assert response.status_code == 200
        
        assert mock_check.called

def test_app_lifespan_db_failure():
    """Test the application lifespan events when database connection fails."""
    # We need to patch it in both places because of how it's imported
    with patch("src.database.check_db_connection", new_callable=AsyncMock) as mock_db_check:
        mock_db_check.return_value = False
        with TestClient(app) as client:
            # App should still start even if DB connection fails
            # We just check that the app started successfully
            pass

        assert mock_db_check.called
