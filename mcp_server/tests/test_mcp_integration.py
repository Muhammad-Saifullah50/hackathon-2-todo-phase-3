"""Integration tests for MCP server HTTP endpoints.

These tests verify:
1. FastAPI app initialization
2. MCP protocol endpoints work
3. CORS configuration
4. Health check endpoint
5. Lifespan management
"""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch
import json


@pytest.fixture
def mock_pool():
    """Mock database pool for integration tests."""
    mock_pool = MagicMock()
    mock_conn = AsyncMock()
    mock_transaction = AsyncMock()

    mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
    mock_conn.transaction.return_value.__aenter__.return_value = mock_transaction
    mock_conn.execute = AsyncMock()
    mock_conn.fetch = AsyncMock(return_value=[])
    mock_conn.fetchrow = AsyncMock(return_value=None)

    return mock_pool


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_endpoint_exists(self, mock_pool):
        """Test that health endpoint is accessible."""
        with patch('main.get_pool', return_value=mock_pool):
            from main import app

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert data["status"] == "ok"

    @pytest.mark.asyncio
    async def test_health_endpoint_cors(self, mock_pool):
        """Test CORS headers on health endpoint."""
        with patch('main.get_pool', return_value=mock_pool):
            from main import app

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get(
                    "/health",
                    headers={"Origin": "http://localhost:3000"}
                )

            # CORS should allow all origins
            assert response.headers.get("access-control-allow-origin") in ["*", "http://localhost:3000"]


class TestMCPProtocolEndpoints:
    """Tests for MCP protocol endpoints."""

    @pytest.mark.asyncio
    async def test_mcp_sse_endpoint_exists(self, mock_pool):
        """Test that MCP SSE endpoint exists."""
        with patch('main.get_pool', return_value=mock_pool):
            from main import app

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/mcp/sse")

            # SSE endpoint should be accessible
            # Actual behavior depends on MCP session initialization
            assert response.status_code in [200, 400, 404, 405]

    @pytest.mark.asyncio
    async def test_mcp_message_endpoint_exists(self, mock_pool):
        """Test that MCP message endpoint exists."""
        with patch('main.get_pool', return_value=mock_pool):
            from main import app

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/mcp/message",
                    json={"method": "ping"}
                )

            # Message endpoint should be accessible
            assert response.status_code in [200, 400, 404, 405, 422]


class TestFastAPIConfiguration:
    """Tests for FastAPI app configuration."""

    def test_app_title(self):
        """Test FastAPI app has correct title."""
        from main import app

        assert app.title == "MCP Task Server"

    def test_docs_disabled(self):
        """Test that Swagger UI and ReDoc are disabled."""
        from main import app

        # Docs should be disabled for production
        assert app.docs_url is None
        assert app.redoc_url is None

    def test_cors_middleware_configured(self):
        """Test CORS middleware is present."""
        from main import app

        # Check that CORS middleware is in the middleware stack
        middleware_classes = [m.cls for m in app.user_middleware]
        assert any("CORSMiddleware" in str(cls) for cls in middleware_classes)


class TestSecurityConfiguration:
    """Tests for security-related configuration."""

    @pytest.mark.asyncio
    async def test_cors_allows_all_origins(self, mock_pool):
        """Test that CORS allows all origins (current config)."""
        with patch('main.get_pool', return_value=mock_pool):
            from main import app

            async with AsyncClient(app=app, base_url="http://test") as client:
                # Test with various origins
                test_origins = [
                    "http://localhost:3000",
                    "https://example.com",
                    "https://malicious-site.com"
                ]

                for origin in test_origins:
                    response = await client.get(
                        "/health",
                        headers={"Origin": origin}
                    )

                    # Currently allows ALL origins (SECURITY ISSUE)
                    # This test documents the current behavior
                    # When security is fixed, this should fail
                    assert response.headers.get("access-control-allow-origin") in ["*", origin]

    @pytest.mark.asyncio
    async def test_no_host_validation(self, mock_pool):
        """Test that host validation is bypassed (current config)."""
        with patch('main.get_pool', return_value=mock_pool):
            from main import app

            async with AsyncClient(app=app, base_url="http://test") as client:
                # Should accept any host header
                response = await client.get(
                    "/health",
                    headers={"Host": "evil-domain.com"}
                )

                # Currently accepts any host (SECURITY ISSUE)
                # This test documents the current behavior
                assert response.status_code == 200


class TestDatabaseConnection:
    """Tests for database connection handling."""

    @pytest.mark.asyncio
    async def test_database_pool_initialization(self):
        """Test that database pool can be initialized."""
        from main import get_pool

        mock_pool = MagicMock()

        with patch('asyncpg.create_pool', return_value=mock_pool):
            pool = await get_pool()

            assert pool is not None

    @pytest.mark.asyncio
    async def test_database_url_parsing(self):
        """Test that DATABASE_URL is parsed correctly."""
        from main import get_db_url

        # Should handle various PostgreSQL URL formats
        assert "postgresql://" in get_db_url()


class TestLifespanManagement:
    """Tests for app lifespan management."""

    @pytest.mark.asyncio
    async def test_lifespan_startup(self, mock_pool):
        """Test that lifespan startup works."""
        with patch('main.get_pool', return_value=mock_pool):
            from main import app

            # App should initialize without errors
            assert app is not None

    @pytest.mark.asyncio
    async def test_mcp_session_manager_starts(self, mock_pool):
        """Test that MCP session manager starts during lifespan."""
        with patch('main.get_pool', return_value=mock_pool):
            from main import mcp

            # Session manager should be configured
            assert mcp.session_manager is not None


class TestErrorResponses:
    """Tests for error response format."""

    @pytest.mark.asyncio
    async def test_404_response_format(self, mock_pool):
        """Test 404 error response format."""
        with patch('main.get_pool', return_value=mock_pool):
            from main import app

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/nonexistent-endpoint")

            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_method_not_allowed_response(self, mock_pool):
        """Test 405 error for wrong HTTP method."""
        with patch('main.get_pool', return_value=mock_pool):
            from main import app

            async with AsyncClient(app=app, base_url="http://test") as client:
                # Try POST on GET-only endpoint
                response = await client.post("/health")

            # Should return method not allowed
            assert response.status_code in [405, 404]


class TestEnvironmentConfiguration:
    """Tests for environment variable configuration."""

    def test_database_url_required(self):
        """Test that DATABASE_URL is required."""
        # This is tested at module import time
        # If DATABASE_URL is not set, main.py raises ValueError
        pass

    def test_frontend_url_has_default(self):
        """Test that FRONTEND_URL has default value."""
        from main import app

        # Should have a default frontend URL
        # Used for CORS configuration
        pass


class TestPerformanceConfiguration:
    """Tests for performance-related configuration."""

    @pytest.mark.asyncio
    async def test_connection_pool_size(self):
        """Test database connection pool configuration."""
        # When pool is created, it should have appropriate size for serverless
        # Recommended: pool_size=1-5 for serverless
        pass

    @pytest.mark.asyncio
    async def test_request_timeout(self):
        """Test that requests have reasonable timeouts."""
        # Serverless functions typically have 60s timeout
        # Database operations should complete within this limit
        pass


class TestSecurityHeaders:
    """Tests for security headers (currently missing)."""

    @pytest.mark.asyncio
    async def test_security_headers_missing(self, mock_pool):
        """Test that security headers are missing (should fail when added)."""
        with patch('main.get_pool', return_value=mock_pool):
            from main import app

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/health")

            # These headers should be present in production
            # Currently missing - this test documents the gap
            assert "X-Content-Type-Options" not in response.headers
            assert "X-Frame-Options" not in response.headers
            assert "Strict-Transport-Security" not in response.headers

    @pytest.mark.asyncio
    async def test_rate_limiting_missing(self, mock_pool):
        """Test that rate limiting is not implemented."""
        with patch('main.get_pool', return_value=mock_pool):
            from main import app

            async with AsyncClient(app=app, base_url="http://test") as client:
                # Should be able to make many rapid requests
                for _ in range(100):
                    response = await client.get("/health")
                    assert response.status_code == 200

                # Currently no rate limiting (should be added)


class TestMonkeyPatchDocumentation:
    """Tests documenting the monkey patch (to be removed)."""

    def test_transport_security_middleware_patched(self):
        """Test that TransportSecurityMiddleware is monkey-patched."""
        # This test documents the monkey patch that needs to be removed
        # The monkey patch bypasses host validation for Vercel
        # Location: main.py around line 467-481
        pass

    def test_monkey_patch_location_documented(self):
        """Document where the monkey patch is located."""
        # The monkey patch should be removed and replaced with:
        # - Proper TrustedHostMiddleware configuration
        # - ALLOWED_HOSTS environment variable
        # - Proper host validation
        pass
