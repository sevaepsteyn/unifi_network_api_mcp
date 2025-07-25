"""UniFi Network API HTTP client."""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from urllib.parse import urljoin, quote

import httpx
from httpx import HTTPStatusError, TimeoutException, ConnectError

from unifi_network_api_mcp.settings import settings
from unifi_network_api_mcp.exceptions import (
    UniFiAPIError,
    UniFiAuthError,
    UniFiConnectionError,
    UniFiNotFoundError,
    UniFiTimeoutError,
    UniFiValidationError,
    UniFiRateLimitError,
)

logger = logging.getLogger(__name__)


class UniFiClient:
    """HTTP client for UniFi Network API."""
    
    def __init__(self):
        """Initialize the UniFi client."""
        self.base_url = settings.api_base_url
        self.headers = {
            "x-api-key": settings.unifi_api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=httpx.Timeout(settings.api_timeout),
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
    
    def _build_url(self, path: str) -> str:
        """Build full URL from path."""
        # Remove leading slash if present
        if path.startswith("/"):
            path = path[1:]
        return urljoin(self.base_url + "/", path)
    
    def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle error responses from the API."""
        try:
            error_data = response.json()
        except Exception:
            error_data = {}
        
        status_code = response.status_code
        message = error_data.get("message", f"HTTP {status_code} error")
        status_name = error_data.get("statusName", "")
        request_id = error_data.get("requestId")
        request_path = error_data.get("requestPath")
        
        # Map status codes to specific exceptions
        if status_code == 401:
            raise UniFiAuthError(
                message,
                status_code=status_code,
                status_name=status_name,
                request_id=request_id,
                request_path=request_path,
                response_data=error_data,
            )
        elif status_code == 404:
            raise UniFiNotFoundError(
                message,
                status_code=status_code,
                status_name=status_name,
                request_id=request_id,
                request_path=request_path,
                response_data=error_data,
            )
        elif status_code == 400:
            raise UniFiValidationError(
                message,
                status_code=status_code,
                status_name=status_name,
                request_id=request_id,
                request_path=request_path,
                response_data=error_data,
            )
        elif status_code == 429:
            raise UniFiRateLimitError(
                message,
                status_code=status_code,
                status_name=status_name,
                request_id=request_id,
                request_path=request_path,
                response_data=error_data,
            )
        else:
            raise UniFiAPIError(
                message,
                status_code=status_code,
                status_name=status_name,
                request_id=request_id,
                request_path=request_path,
                response_data=error_data,
            )
    
    async def _request_with_retry(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> httpx.Response:
        """Make HTTP request with retry logic."""
        if not self._client:
            raise UniFiConnectionError("Client not initialized. Use async context manager.")
        
        url = self._build_url(path)
        last_error = None
        
        for attempt in range(settings.api_retry_attempts):
            try:
                logger.debug(f"Attempt {attempt + 1}: {method} {url}")
                response = await self._client.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            
            except TimeoutException as e:
                last_error = UniFiTimeoutError(f"Request timeout: {str(e)}")
                logger.warning(f"Timeout on attempt {attempt + 1}: {str(e)}")
            
            except ConnectError as e:
                last_error = UniFiConnectionError(f"Connection failed: {str(e)}")
                logger.warning(f"Connection error on attempt {attempt + 1}: {str(e)}")
            
            except HTTPStatusError as e:
                # Don't retry on client errors (4xx)
                if e.response.status_code < 500:
                    self._handle_error_response(e.response)
                last_error = e
                logger.warning(f"HTTP error on attempt {attempt + 1}: {str(e)}")
            
            # Wait before retrying (except on last attempt)
            if attempt < settings.api_retry_attempts - 1:
                await asyncio.sleep(settings.api_retry_delay * (attempt + 1))
        
        # If we get here, all retries failed
        if isinstance(last_error, (UniFiTimeoutError, UniFiConnectionError)):
            raise last_error
        elif isinstance(last_error, HTTPStatusError):
            self._handle_error_response(last_error.response)
        else:
            raise UniFiAPIError(f"Request failed after {settings.api_retry_attempts} attempts")
    
    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make GET request."""
        response = await self._request_with_retry("GET", path, params=params)
        return response.json()
    
    async def post(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Make POST request."""
        response = await self._request_with_retry("POST", path, json=json)
        
        # Handle empty responses (204 No Content or empty body)
        if response.status_code == 204 or not response.content:
            return None
        
        # Try to parse JSON, return None if it fails
        try:
            return response.json()
        except Exception:
            logger.debug(f"Response is not JSON: {response.text}")
            return None
    
    async def delete(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Make DELETE request."""
        response = await self._request_with_retry("DELETE", path, params=params)
        
        # Handle empty responses (204 No Content or empty body)
        if response.status_code == 204 or not response.content:
            return None
        
        # Try to parse JSON, return None if it fails
        try:
            return response.json()
        except Exception:
            logger.debug(f"Response is not JSON: {response.text}")
            return None
    
    async def get_paginated(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        max_items: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Get all items from a paginated endpoint."""
        if params is None:
            params = {}
        
        all_items = []
        offset = 0
        limit = params.get("limit", settings.default_page_size)
        
        while True:
            page_params = {**params, "offset": offset, "limit": limit}
            response = await self.get(path, params=page_params)
            
            items = response.get("data", [])
            all_items.extend(items)
            
            # Check if we've reached the desired number of items
            if max_items and len(all_items) >= max_items:
                return all_items[:max_items]
            
            # Check if there are more pages
            total_count = response.get("totalCount", 0)
            if offset + len(items) >= total_count or not items:
                break
            
            offset += limit
        
        return all_items


# Global client instance
_client: Optional[UniFiClient] = None


async def get_client() -> UniFiClient:
    """Get or create the global UniFi client."""
    global _client
    if _client is None:
        _client = UniFiClient()
    return _client