"""Configuration settings for UniFi Network API MCP server."""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, HttpUrl, field_validator


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    # UniFi Controller settings
    unifi_controller_url: HttpUrl = Field(
        ...,
        description="UniFi controller URL (e.g., https://xxx.unifi-hosting.ui.com)",
        alias="UNIFI_CONTROLLER_URL"
    )
    
    unifi_api_key: str = Field(
        ...,
        description="UniFi API key for authentication",
        alias="UNIFI_API_KEY"
    )
    
    # API settings
    api_timeout: float = Field(
        30.0,
        description="API request timeout in seconds",
        alias="UNIFI_API_TIMEOUT"
    )
    
    api_retry_attempts: int = Field(
        3,
        description="Number of retry attempts for failed API requests",
        alias="UNIFI_API_RETRY_ATTEMPTS"
    )
    
    api_retry_delay: float = Field(
        1.0,
        description="Delay between retry attempts in seconds",
        alias="UNIFI_API_RETRY_DELAY"
    )
    
    # Default pagination settings
    default_page_size: int = Field(
        25,
        ge=1,
        le=200,
        description="Default page size for paginated requests",
        alias="UNIFI_DEFAULT_PAGE_SIZE"
    )
    
    # Logging settings
    log_level: str = Field(
        "INFO",
        description="Logging level",
        alias="UNIFI_LOG_LEVEL"
    )
    
    @field_validator("unifi_controller_url", mode="before")
    @classmethod
    def validate_controller_url(cls, v):
        """Ensure controller URL ends without trailing slash."""
        if isinstance(v, str):
            return v.rstrip("/")
        return v
    
    @property
    def api_base_url(self) -> str:
        """Get the full API base URL."""
        return f"{self.unifi_controller_url}/proxy/network/integration/v1"


# Global settings instance
settings = Settings()