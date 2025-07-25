"""Custom exceptions for UniFi Network API MCP server."""

from typing import Optional, Dict, Any


class UniFiError(Exception):
    """Base exception for all UniFi-related errors."""
    pass


class UniFiAuthError(UniFiError):
    """Raised when authentication fails."""
    pass


class UniFiAPIError(UniFiError):
    """Raised when the UniFi API returns an error."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        status_name: Optional[str] = None,
        request_id: Optional[str] = None,
        request_path: Optional[str] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.status_name = status_name
        self.request_id = request_id
        self.request_path = request_path
        self.response_data = response_data
    
    def __str__(self) -> str:
        parts = [str(self.args[0])]
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        if self.status_name:
            parts.append(f"Status Name: {self.status_name}")
        if self.request_id:
            parts.append(f"Request ID: {self.request_id}")
        if self.request_path:
            parts.append(f"Path: {self.request_path}")
        return " | ".join(parts)


class UniFiNotFoundError(UniFiAPIError):
    """Raised when a requested resource is not found."""
    pass


class UniFiValidationError(UniFiAPIError):
    """Raised when request validation fails."""
    pass


class UniFiRateLimitError(UniFiAPIError):
    """Raised when rate limit is exceeded."""
    pass


class UniFiTimeoutError(UniFiError):
    """Raised when a request times out."""
    pass


class UniFiConnectionError(UniFiError):
    """Raised when connection to UniFi controller fails."""
    pass