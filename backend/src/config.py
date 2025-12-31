import os
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _get_mcp_server_url() -> str:
    """Build MCP server URL dynamically based on environment.

    Priority:
    1. MCP_VERCEL_URL (separate MCP deployment)
    2. Localhost if set via MCP_HOST/PORT
    3. Production Vercel URL (Fallback)
    """
    # Check for separate MCP server deployment URL
    mcp_url = os.getenv("MCP_VERCEL_URL")
    if mcp_url:
        return f"https://{mcp_url}/mcp"

    # For local development
    host = os.getenv("MCP_HOST", "localhost")
    port = os.getenv("MCP_PORT", "8000")
    if os.getenv("ENVIRONMENT") != "production":
        return f"http://{host}:{port}/mcp"

    # Fall back to current vercel URL (mostly for legacy/monolith mode)
    vercel_url = os.getenv("VERCEL_URL")
    if vercel_url:
        return f"https://{vercel_url}/mcp"

    return f"http://{host}:{port}/mcp"


def _get_mcp_root_url() -> str:
    """Build MCP root URL dynamically based on environment."""
    vercel_url = os.getenv("VERCEL_URL")
    if vercel_url:
        return f"https://{vercel_url}"
    host = os.getenv("MCP_HOST", "localhost")
    port = os.getenv("MCP_PORT", "8000")
    return f"http://{host}:{port}"


def _get_default_cors_origins() -> List[str]:
    """Build CORS origins dynamically based on environment."""
    vercel_url = os.getenv("VERCEL_URL")
    if vercel_url:
        return [f"https://{vercel_url}", "https://*.vercel.app"]
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    return ["http://localhost:3000", frontend_url]


class Settings(BaseSettings):
    DATABASE_URL: str
    BETTER_AUTH_SECRET: str
    OPENROUTER_API_KEY: str
    GEMINI_API_KEY: str
    CORS_ORIGINS: List[str] = _get_default_cors_origins()
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"
    # Frontend URL for revalidation calls
    FRONTEND_URL: str = "http://localhost:3000"
    # MCP Server Configuration - dynamically computed
    MCP_SERVER_URL: str = _get_mcp_server_url()
    MCP_SERVER_TOKEN: str = "default-mcp-token"
    # Alternative: Use root path (MCP app runs at /mcp internally)
    MCP_SERVER_ROOT_URL: str = _get_mcp_root_url()

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return []

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )


settings = Settings()  # type: ignore[call-arg]
