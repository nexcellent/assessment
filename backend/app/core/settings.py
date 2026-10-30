"""Configuration management for the application."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic import field_validator
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

# backend/ is the root of the service; the repository root above it holds the fixtures.
ROOT_PATH: Path = Path(__file__).parent.parent.parent
REPOSITORY_ROOT: Path = ROOT_PATH.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables and the repository's ``.env`` file."""

    project_name: str = Field(default="Profile Backend", alias="PROJECT_NAME", description="Name of the project")
    api_base_url: str = Field(default="/api/v1", alias="API_BASE_URL", description="Base URL for the API")
    environment: str = Field(default="dev", alias="ENVIRONMENT", description="Application environment (dev, uat, prd)")
    debug: bool = Field(default=False, alias="DEBUG", description="Enable debug mode")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL", description="Logging level (DEBUG, INFO, WARNING, ERROR)")
    fixtures_dir: Path = Field(
        default=REPOSITORY_ROOT / "fixtures" / "profiles",
        alias="FIXTURES_DIR",
        description="Directory of the profile documents the in-memory repository loads at start-up",
    )

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment setting."""
        allowed = ["dev", "uat", "prd"]
        if v not in allowed:
            msg = f"Environment must be one of: {allowed}"
            raise ValueError(msg)
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR"]
        if v.upper() not in allowed:
            msg = f"Log level must be one of: {allowed}"
            raise ValueError(msg)
        return v.upper()

    model_config = SettingsConfigDict(
        # The one .env of the repository; environment variables win over it.
        env_file=REPOSITORY_ROOT / ".env",
        # Allow both field names and aliases when loading from environment
        populate_by_name=True,
        # Environment variable names must match the aliases' case exactly
        case_sensitive=True,
        # Variables meant for other tools may share the .env; only the fields above are read.
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get application settings singleton instance: environment variables first, then the .env file."""
    return Settings()
