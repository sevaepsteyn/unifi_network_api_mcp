"""UniFi Network API MCP Server."""

import logging
from typing import Annotated, Optional, List, Union

from fastmcp import FastMCP
from pydantic import Field

from unifi_network_api_mcp.client import UniFiClient
from unifi_network_api_mcp.models import (
    ApplicationInfo,
    SitesResult,
    DevicesResult,
    DeviceDetails,
    DeviceStatistics,
    ClientsResult,
    Client,
    WiredClient,
    WirelessClient,
    VouchersResult,
    CreateVoucherRequest,
    CreateVoucherResponse,
    DeviceActionRequest,
    PortActionRequest,
    AuthorizeGuestRequest,
    UnauthorizeGuestRequest,
    ClientAction,
)
from unifi_network_api_mcp.settings import settings

logger = logging.getLogger(__name__)

# Create the MCP server
unifi_mcp = FastMCP(
    "UniFi Network API MCP Server",
    dependencies=[
        "httpx>=0.27.0",
        "pydantic>=2.7.0",
        "pydantic-settings>=2.3.0",
    ],
)


# Tools - Read-only operations (converted from resources for Claude Desktop UI access)

@unifi_mcp.tool
async def application_info() -> ApplicationInfo:
    """Get general information about the UniFi Network application."""
    async with UniFiClient() as client:
        data = await client.get("info")
        return ApplicationInfo(**data)


@unifi_mcp.tool
async def sites() -> SitesResult:
    """List all sites managed by this UniFi Network application."""
    async with UniFiClient() as client:
        sites = await client.get_paginated("sites")
        return SitesResult(sites=sites, totalCount=len(sites))


@unifi_mcp.tool
async def devices(
    site_id: Annotated[str, Field(description="Site UUID")]
) -> DevicesResult:
    """List all adopted devices on a site."""
    async with UniFiClient() as client:
        devices = await client.get_paginated(f"sites/{site_id}/devices")
        return DevicesResult(devices=devices, totalCount=len(devices))


@unifi_mcp.tool
async def device_details(
    site_id: Annotated[str, Field(description="Site UUID")],
    device_id: Annotated[str, Field(description="Device UUID")]
) -> DeviceDetails:
    """Get detailed information about a specific device."""
    async with UniFiClient() as client:
        data = await client.get(f"sites/{site_id}/devices/{device_id}")
        return DeviceDetails(**data)


@unifi_mcp.tool
async def device_statistics(
    site_id: Annotated[str, Field(description="Site UUID")],
    device_id: Annotated[str, Field(description="Device UUID")]
) -> DeviceStatistics:
    """Get the latest statistics for a specific device."""
    async with UniFiClient() as client:
        data = await client.get(f"sites/{site_id}/devices/{device_id}/statistics/latest")
        return DeviceStatistics(**data)


@unifi_mcp.tool
async def clients(
    site_id: Annotated[str, Field(description="Site UUID")]
) -> ClientsResult:
    """List all connected clients on a site."""
    async with UniFiClient() as client:
        clients_data = await client.get_paginated(f"sites/{site_id}/clients")
        
        # Parse clients based on their type
        clients = []
        for client_data in clients_data:
            client_type = client_data.get("type")
            if client_type == "WIRED":
                clients.append(WiredClient(**client_data))
            elif client_type == "WIRELESS":
                clients.append(WirelessClient(**client_data))
            else:
                clients.append(Client(**client_data))
        
        return ClientsResult(clients=clients, totalCount=len(clients))


@unifi_mcp.tool
async def client_details(
    site_id: Annotated[str, Field(description="Site UUID")],
    client_id: Annotated[str, Field(description="Client UUID")]
) -> Client:
    """Get detailed information about a specific client."""
    async with UniFiClient() as client:
        data = await client.get(f"sites/{site_id}/clients/{client_id}")
        
        # Parse client based on type
        client_type = data.get("type")
        if client_type == "WIRED":
            return WiredClient(**data)
        elif client_type == "WIRELESS":
            return WirelessClient(**data)
        else:
            return Client(**data)


@unifi_mcp.tool
async def vouchers(
    site_id: Annotated[str, Field(description="Site UUID")]
) -> VouchersResult:
    """List all hotspot vouchers for a site."""
    async with UniFiClient() as client:
        vouchers = await client.get_paginated(f"sites/{site_id}/hotspot/vouchers")
        return VouchersResult(vouchers=vouchers, totalCount=len(vouchers))


# Tools - State-modifying operations

@unifi_mcp.tool
async def restart_device(
    site_id: Annotated[str, Field(description="Site UUID")],
    device_id: Annotated[str, Field(description="Device UUID")]
) -> str:
    """Restart a specific device.
    
    This will cause the device to reboot, temporarily disconnecting any connected clients.
    """
    async with UniFiClient() as client:
        request = DeviceActionRequest(action="RESTART")
        result = await client.post(
            f"sites/{site_id}/devices/{device_id}/actions",
            json=request.model_dump()
        )
        return f"Device restart initiated for device {device_id}"


@unifi_mcp.tool
async def power_cycle_port(
    site_id: Annotated[str, Field(description="Site UUID")],
    device_id: Annotated[str, Field(description="Device UUID")],
    port_idx: Annotated[int, Field(description="Port index (1-based)", ge=1)]
) -> str:
    """Power cycle a specific port on a device.
    
    This will temporarily disable PoE power on the port and then re-enable it.
    Useful for restarting PoE-powered devices like access points or cameras.
    """
    async with UniFiClient() as client:
        request = PortActionRequest(action="POWER_CYCLE")
        result = await client.post(
            f"sites/{site_id}/devices/{device_id}/interfaces/ports/{port_idx}/actions",
            json=request.model_dump()
        )
        return f"Port {port_idx} power cycle initiated on device {device_id}"


@unifi_mcp.tool
async def authorize_guest(
    site_id: Annotated[str, Field(description="Site UUID")],
    client_id: Annotated[str, Field(description="Client UUID")],
    time_limit_minutes: Annotated[
        Optional[Union[int, str]],
        Field(None, description="Time limit in minutes (1-1000000)")
    ] = None,
    data_usage_limit_mb: Annotated[
        Optional[Union[int, str]],
        Field(None, description="Data usage limit in MB (1-1048576)")
    ] = None,
    download_rate_limit_kbps: Annotated[
        Optional[Union[int, str]],
        Field(None, description="Download rate limit in Kbps (2-100000)")
    ] = None,
    upload_rate_limit_kbps: Annotated[
        Optional[Union[int, str]],
        Field(None, description="Upload rate limit in Kbps (2-100000)")
    ] = None,
) -> str:
    """Authorize guest access for a client.
    
    This allows a client to access the network through the guest portal.
    You can optionally set limits on time, data usage, and bandwidth.
    """
    # Convert string parameters to integers
    try:
        if time_limit_minutes is not None:
            time_limit_minutes = int(time_limit_minutes)
        if data_usage_limit_mb is not None:
            data_usage_limit_mb = int(data_usage_limit_mb)
        if download_rate_limit_kbps is not None:
            download_rate_limit_kbps = int(download_rate_limit_kbps)
        if upload_rate_limit_kbps is not None:
            upload_rate_limit_kbps = int(upload_rate_limit_kbps)
    except ValueError as e:
        raise ValueError(f"Invalid numeric parameter: {e}")
    
    # Validate ranges
    if time_limit_minutes is not None and not 1 <= time_limit_minutes <= 1000000:
        raise ValueError("time_limit_minutes must be between 1 and 1000000")
    if data_usage_limit_mb is not None and not 1 <= data_usage_limit_mb <= 1048576:
        raise ValueError("data_usage_limit_mb must be between 1 and 1048576")
    if download_rate_limit_kbps is not None and not 2 <= download_rate_limit_kbps <= 100000:
        raise ValueError("download_rate_limit_kbps must be between 2 and 100000")
    if upload_rate_limit_kbps is not None and not 2 <= upload_rate_limit_kbps <= 100000:
        raise ValueError("upload_rate_limit_kbps must be between 2 and 100000")
    
    async with UniFiClient() as client:
        request = AuthorizeGuestRequest(
            timeLimitMinutes=time_limit_minutes,
            dataUsageLimitMBytes=data_usage_limit_mb,
            rxRateLimitKbps=download_rate_limit_kbps,
            txRateLimitKbps=upload_rate_limit_kbps,
        )
        result = await client.post(
            f"sites/{site_id}/clients/{client_id}/actions",
            json=request.model_dump()
        )
        
        limits = []
        if time_limit_minutes:
            limits.append(f"time limit: {time_limit_minutes} minutes")
        if data_usage_limit_mb:
            limits.append(f"data limit: {data_usage_limit_mb} MB")
        if download_rate_limit_kbps:
            limits.append(f"download limit: {download_rate_limit_kbps} Kbps")
        if upload_rate_limit_kbps:
            limits.append(f"upload limit: {upload_rate_limit_kbps} Kbps")
        
        limit_str = f" with {', '.join(limits)}" if limits else ""
        return f"Guest access authorized for client {client_id}{limit_str}"


@unifi_mcp.tool
async def unauthorize_guest(
    site_id: Annotated[str, Field(description="Site UUID")],
    client_id: Annotated[str, Field(description="Client UUID")]
) -> str:
    """Revoke guest access for a client.
    
    This will immediately disconnect the client from the guest network.
    """
    async with UniFiClient() as client:
        request = UnauthorizeGuestRequest()
        result = await client.post(
            f"sites/{site_id}/clients/{client_id}/actions",
            json=request.model_dump()
        )
        return f"Guest access revoked for client {client_id}"


@unifi_mcp.tool
async def create_vouchers(
    site_id: Annotated[str, Field(description="Site UUID")],
    name: Annotated[str, Field(description="Voucher note/description")],
    time_limit_minutes: Annotated[
        Union[int, str],
        Field(description="Time limit per voucher in minutes (1-1000000)")
    ],
    count: Annotated[
        Union[int, str],
        Field(1, description="Number of vouchers to create (1-1000)")
    ] = 1,
    authorized_guest_limit: Annotated[
        Union[int, str],
        Field(1, description="Number of guests per voucher (min 1)")
    ] = 1,
    data_usage_limit_mb: Annotated[
        Optional[Union[int, str]],
        Field(None, description="Data usage limit in MB (1-1048576)")
    ] = None,
    download_rate_limit_kbps: Annotated[
        Optional[Union[int, str]],
        Field(None, description="Download rate limit in Kbps (2-100000)")
    ] = None,
    upload_rate_limit_kbps: Annotated[
        Optional[Union[int, str]],
        Field(None, description="Upload rate limit in Kbps (2-100000)")
    ] = None,
) -> CreateVoucherResponse:
    """Create one or more hotspot vouchers.
    
    Vouchers allow guests to access the network by entering a code.
    Each voucher can be used by multiple guests up to the authorized limit.
    """
    # Convert string parameters to integers
    try:
        time_limit_minutes = int(time_limit_minutes)
        count = int(count)
        authorized_guest_limit = int(authorized_guest_limit)
        
        if data_usage_limit_mb is not None:
            data_usage_limit_mb = int(data_usage_limit_mb)
        if download_rate_limit_kbps is not None:
            download_rate_limit_kbps = int(download_rate_limit_kbps)
        if upload_rate_limit_kbps is not None:
            upload_rate_limit_kbps = int(upload_rate_limit_kbps)
    except ValueError as e:
        raise ValueError(f"Invalid numeric parameter: {e}")
    
    # Validate ranges
    if not 1 <= time_limit_minutes <= 1000000:
        raise ValueError("time_limit_minutes must be between 1 and 1000000")
    if not 1 <= count <= 1000:
        raise ValueError("count must be between 1 and 1000")
    if not authorized_guest_limit >= 1:
        raise ValueError("authorized_guest_limit must be at least 1")
    if data_usage_limit_mb is not None and not 1 <= data_usage_limit_mb <= 1048576:
        raise ValueError("data_usage_limit_mb must be between 1 and 1048576")
    if download_rate_limit_kbps is not None and not 2 <= download_rate_limit_kbps <= 100000:
        raise ValueError("download_rate_limit_kbps must be between 2 and 100000")
    if upload_rate_limit_kbps is not None and not 2 <= upload_rate_limit_kbps <= 100000:
        raise ValueError("upload_rate_limit_kbps must be between 2 and 100000")
    
    async with UniFiClient() as client:
        request = CreateVoucherRequest(
            count=count,
            name=name,
            authorizedGuestLimit=authorized_guest_limit,
            timeLimitMinutes=time_limit_minutes,
            dataUsageLimitMBytes=data_usage_limit_mb,
            rxRateLimitKbps=download_rate_limit_kbps,
            txRateLimitKbps=upload_rate_limit_kbps,
        )
        data = await client.post(
            f"sites/{site_id}/hotspot/vouchers",
            json=request.model_dump(exclude_none=True)
        )
        return CreateVoucherResponse(**data)


@unifi_mcp.tool
async def delete_voucher(
    site_id: Annotated[str, Field(description="Site UUID")],
    voucher_id: Annotated[str, Field(description="Voucher UUID")]
) -> str:
    """Delete a specific hotspot voucher.
    
    This will invalidate the voucher code and disconnect any guests using it.
    """
    async with UniFiClient() as client:
        result = await client.delete(f"sites/{site_id}/hotspot/vouchers/{voucher_id}")
        return f"Voucher {voucher_id} deleted successfully"


@unifi_mcp.tool
async def search_devices(
    site_id: Annotated[str, Field(description="Site UUID")],
    name_pattern: Annotated[
        Optional[str],
        Field(None, description="Device name pattern (supports wildcards)")
    ] = None,
    model: Annotated[
        Optional[str],
        Field(None, description="Device model to filter by")
    ] = None,
    state: Annotated[
        Optional[str],
        Field(None, description="Device state to filter by (ONLINE, OFFLINE, etc)")
    ] = None,
) -> DevicesResult:
    """Search for devices with optional filters.
    
    Use wildcards in name_pattern: * matches any characters, . matches single character.
    Example: "AP-*" matches all devices starting with "AP-"
    """
    async with UniFiClient() as client:
        # Get all devices first
        devices = await client.get_paginated(f"sites/{site_id}/devices")
        
        # Apply filters
        filtered = devices
        
        if name_pattern:
            import re
            # Convert wildcard pattern to regex
            regex_pattern = name_pattern.replace(".", r"\.").replace("*", ".*")
            regex = re.compile(regex_pattern, re.IGNORECASE)
            filtered = [d for d in filtered if regex.match(d.get("name", ""))]
        
        if model:
            filtered = [d for d in filtered if d.get("model") == model]
        
        if state:
            filtered = [d for d in filtered if d.get("state") == state]
        
        return DevicesResult(devices=filtered, totalCount=len(filtered))