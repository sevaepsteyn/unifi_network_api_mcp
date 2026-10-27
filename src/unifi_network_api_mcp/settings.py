"""Configuration settings for UniFi Network API MCP server."""

from functools import cached_property
from pathlib import Path
from typing import Optional

import certifi
import httpx
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, HttpUrl, field_validator


CLOUD_API_URL = "https://api.ui.com"


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    # UniFi Controller settings
    unifi_controller_url: Optional[HttpUrl] = Field(
        None,
        description="UniFi controller URL (e.g., https://xxx.unifi-hosting.ui.com)",
        alias="UNIFI_CONTROLLER_URL"
    )
    
    unifi_console_id: Optional[str] = Field(
        None,
        description=(
            "Console ID for the UniFi cloud connector (api.ui.com). Set this when using a "
            "Site Manager key from unifi.ui.com; 'auto' picks the first console the key owns. "
            "Leave unset to call the local console at UNIFI_CONTROLLER_URL."
        ),
        alias="UNIFI_CONSOLE_ID"
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
    
    verify_ssl: bool = Field(
        True,
        description="Verify the controller TLS certificate (set false for a local console with a self-signed cert)",
        alias="UNIFI_VERIFY_SSL"
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
    def uses_cloud_connector(self) -> bool:
        """Whether requests go through the api.ui.com cloud connector."""
        return bool(self.unifi_console_id)
    
    @cached_property
    def api_base_url(self) -> str:
        """Get the full API base URL."""
        if self.uses_cloud_connector:
            console_id = self.unifi_console_id
            if console_id.lower() == "auto":
                console_id = _discover_console_id(self.unifi_api_key)
            return f"{CLOUD_API_URL}/v1/connector/consoles/{console_id}/proxy/network/integration/v1"
        if not self.unifi_controller_url:
            raise ValueError("Set UNIFI_CONTROLLER_URL or UNIFI_CONSOLE_ID")
        return f"{str(self.unifi_controller_url).rstrip('/')}/proxy/network/integration/v1"


def _discover_console_id(api_key: str) -> str:
    """Return the ID of the first console the Site Manager key owns."""
    response = httpx.get(
        f"{CLOUD_API_URL}/v1/hosts",
        headers={"X-API-KEY": api_key, "Accept": "application/json"},
        verify=certifi.where(),
        timeout=30.0,
    )
    response.raise_for_status()
    hosts = response.json().get("data", [])
    consoles = [h for h in hosts if h.get("type") == "console" and h.get("owner")] or hosts
    if not consoles:
        raise ValueError("No UniFi consoles found for this API key")
    return consoles[0]["id"]


# Global settings instance
settings = Settings()