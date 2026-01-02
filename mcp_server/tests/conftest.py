"""Pytest configuration and shared fixtures for MCP server tests."""

import pytest
import os
from unittest.mock import patch

# Set test environment variables before importing main
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test_db"
os.environ["FRONTEND_URL"] = "http://localhost:3000"


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    # Environment is already set above
    yield


@pytest.fixture
def mock_database_url():
    """Provide mock database URL for tests."""
    return "postgresql://test:test@localhost:5432/test_db"


@pytest.fixture
def clean_environment():
    """Provide clean environment for tests."""
    original_env = os.environ.copy()
    yield
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)
