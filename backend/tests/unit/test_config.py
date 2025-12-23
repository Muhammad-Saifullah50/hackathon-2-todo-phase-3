from src.config import Settings
from pytest import MonkeyPatch

def test_settings_load_defaults(monkeypatch: MonkeyPatch) -> None:
    """Test that settings load default values correctly."""
    # Set env vars to override .env file and ensure defaults or specific values are tested
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("CORS_ORIGINS", '["http://localhost:3000"]')

    db_url = "postgresql+asyncpg://user:pass@localhost/db"
    settings = Settings(DATABASE_URL=db_url, SECRET_KEY="test", BETTER_AUTH_SECRET="test-auth-secret")
    assert settings.ENVIRONMENT == "development"
    assert settings.LOG_LEVEL == "INFO"
    assert "http://localhost:3000" in settings.CORS_ORIGINS


def test_assemble_cors_origins_from_string() -> None:
    """Test that CORS_ORIGINS can be assembled from a comma-separated string."""
    settings = Settings(
        DATABASE_URL="db",
        SECRET_KEY="key",
        BETTER_AUTH_SECRET="auth-secret",
        CORS_ORIGINS="http://localhost:3000,http://example.com",  # type: ignore
    )
    assert settings.CORS_ORIGINS == ["http://localhost:3000", "http://example.com"]
