from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    BETTER_AUTH_SECRET: str
    OPENROUTER_API_KEY: str
    GEMINI_API_KEY: str
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"
    # Frontend URL for revalidation calls
    FRONTEND_URL: str = "http://localhost:3000"
    # MCP Server Configuration
    MCP_SERVER_URL: str = "http://localhost:8000/mcp"
    MCP_SERVER_TOKEN: str = "default-mcp-token"
    # Alternative: Use root path (MCP app runs at /mcp internally)
    MCP_SERVER_ROOT_URL: str = "http://localhost:8000"

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
