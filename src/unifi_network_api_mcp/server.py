"""UniFi Network API MCP Server."""

import logging
from typing import Annotated, Optional, List, Union
from urllib.parse import quote

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
    Network,
    NetworksResult,
    WifiBroadcast,
    WifiBroadcastsResult,
    FirewallZonesResult,
    FirewallPoliciesResult,
    PortForwardsResult,
    TrafficMatchingListsResult,
    NetworkServicesResult,
    WifiAdvancedSettingsResult,
    VpnResult,
    ThreatManagementResult,
    SwitchPortConfig,
    SwitchPortsResult,
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
            # The switch port is only in the classic API; don't fail the call if it's unavailable
            try:
                site_name = await _site_name(client, site_id)
                sta = await client.get_classic(site_name, f"stat/sta/{quote(data['macAddress'].lower())}")
                data["uplinkPortIdx"] = sta[0].get("sw_port") if sta else None
            except Exception as e:
                logger.warning(f"Could not look up switch port for client {client_id}: {e}")
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


@unifi_mcp.tool
async def networks(
    site_id: Annotated[str, Field(description="Site UUID")]
) -> NetworksResult:
    """List networks (LANs/VLANs) on a site. Use network_details for subnet and DHCP settings."""
    async with UniFiClient() as client:
        networks = await client.get_paginated(f"sites/{site_id}/networks")
        return NetworksResult(networks=networks, totalCount=len(networks))


@unifi_mcp.tool
async def network_details(
    site_id: Annotated[str, Field(description="Site UUID")],
    network_id: Annotated[str, Field(description="Network UUID")]
) -> Network:
    """Get a network's full configuration, including VLAN, IPv4/IPv6 subnet, DHCP and isolation settings."""
    async with UniFiClient() as client:
        data = await client.get(f"sites/{site_id}/networks/{network_id}")
        return Network(**data)


@unifi_mcp.tool
async def wifi_broadcasts(
    site_id: Annotated[str, Field(description="Site UUID")]
) -> WifiBroadcastsResult:
    """List WiFi networks (SSIDs) on a site. Use wifi_broadcast_details for security and radio settings."""
    async with UniFiClient() as client:
        broadcasts = await client.get_paginated(f"sites/{site_id}/wifi/broadcasts")
        return WifiBroadcastsResult(wifiBroadcasts=broadcasts, totalCount=len(broadcasts))


@unifi_mcp.tool
async def wifi_broadcast_details(
    site_id: Annotated[str, Field(description="Site UUID")],
    wifi_broadcast_id: Annotated[str, Field(description="WiFi broadcast UUID")]
) -> WifiBroadcast:
    """Get a WiFi network's full configuration (security mode, client isolation, hidden SSID, etc.). Passphrases are redacted."""
    async with UniFiClient() as client:
        data = await client.get(f"sites/{site_id}/wifi/broadcasts/{wifi_broadcast_id}")
        return WifiBroadcast(**data)


@unifi_mcp.tool
async def firewall_zones(
    site_id: Annotated[str, Field(description="Site UUID")]
) -> FirewallZonesResult:
    """List firewall zones on a site and the networks assigned to each."""
    async with UniFiClient() as client:
        zones = await client.get_paginated(f"sites/{site_id}/firewall/zones")
        return FirewallZonesResult(zones=zones, totalCount=len(zones))


@unifi_mcp.tool
async def firewall_policies(
    site_id: Annotated[str, Field(description="Site UUID")]
) -> FirewallPoliciesResult:
    """List zone-based firewall policies on a site, including system-defined ones. Zones are referenced by UUID; see firewall_zones."""
    async with UniFiClient() as client:
        policies = await client.get_paginated(f"sites/{site_id}/firewall/policies")
        return FirewallPoliciesResult(policies=policies, totalCount=len(policies))


@unifi_mcp.tool
async def port_forwards(
    site_id: Annotated[str, Field(description="Site UUID")]
) -> PortForwardsResult:
    """List port forwarding rules on a site."""
    async with UniFiClient() as client:
        # Port forwards are only in the classic API
        rules = await client.get_classic(await _site_name(client, site_id), "rest/portforward")
        return PortForwardsResult(portForwards=rules, totalCount=len(rules))


@unifi_mcp.tool
async def traffic_matching_lists(
    site_id: Annotated[str, Field(description="Site UUID")]
) -> TrafficMatchingListsResult:
    """List traffic matching lists (IP/port/domain groups) that firewall policies can reference."""
    async with UniFiClient() as client:
        lists = await client.get_paginated(f"sites/{site_id}/traffic-matching-lists")
        return TrafficMatchingListsResult(trafficMatchingLists=lists, totalCount=len(lists))


@unifi_mcp.tool
async def network_services(
    site_id: Annotated[str, Field(description="Site UUID")]
) -> NetworkServicesResult:
    """Get per-network DHCP options, DHCP DNS servers, IGMP snooping and mDNS flags, plus the
    site-wide mDNS, IGMP snooping and DNS-over-HTTPS settings. Complements network_details."""
    async with UniFiClient() as client:
        site_name = await _site_name(client, site_id)
        networks = await client.get_classic(site_name, "rest/networkconf")
        settings_by_key = await _classic_settings(client, site_name)
        return NetworkServicesResult(
            networks=[n for n in networks if n.get("purpose") != "wan"],
            mdns=settings_by_key.get("mdns"),
            igmpSnooping=settings_by_key.get("igmp_snooping"),
            dnsOverHttps=settings_by_key.get("doh"),
        )


@unifi_mcp.tool
async def wifi_advanced_settings(
    site_id: Annotated[str, Field(description="Site UUID")]
) -> WifiAdvancedSettingsResult:
    """Get per-SSID settings not in wifi_broadcast_details: bound network, AP group assignment,
    bands, multicast enhancement, BSS transition, proxy ARP, minimum data rates, PMF/WPA3 options.
    Passphrases are redacted."""
    async with UniFiClient() as client:
        site_name = await _site_name(client, site_id)
        wlans = await client.get_classic(site_name, "rest/wlanconf")
        network_names = {n["_id"]: n.get("name") for n in await client.get_classic(site_name, "rest/networkconf")}
        ap_groups = await client.get_classic(site_name, "apgroups", v2=True)
        group_names = {g["_id"]: g.get("name") for g in ap_groups}
        for wlan in wlans:
            wlan["networkName"] = network_names.get(wlan.get("networkconf_id"))
            wlan["apGroupNames"] = [group_names.get(g, g) for g in wlan.get("ap_group_ids") or []]
        return WifiAdvancedSettingsResult(wifiNetworks=wlans, apGroups=ap_groups)


@unifi_mcp.tool
async def vpn(
    site_id: Annotated[str, Field(description="Site UUID")]
) -> VpnResult:
    """Get VPN servers and their firewall zone, the networks assigned to VPN clients, and Teleport settings."""
    async with UniFiClient() as client:
        site_name = await _site_name(client, site_id)
        servers = await client.get_paginated(f"sites/{site_id}/vpn/servers")
        zones = await client.get_paginated(f"sites/{site_id}/firewall/zones")
        for server in servers:
            server["firewallZone"] = next((z["name"] for z in zones if server["id"] in z.get("networkIds", [])), None)
        networks = await client.get_classic(site_name, "rest/networkconf")
        settings_by_key = await _classic_settings(client, site_name)
        return VpnResult(
            servers=servers,
            clientNetworks=[n for n in networks if n.get("purpose") == "remote-user-vpn"],
            teleport=settings_by_key.get("teleport"),
            siteToSiteMagicVpnEnabled=(settings_by_key.get("magic_site_to_site_vpn") or {}).get("enabled"),
        )


@unifi_mcp.tool
async def threat_management(
    site_id: Annotated[str, Field(description="Site UUID")]
) -> ThreatManagementResult:
    """Get IDS/IPS mode and enabled categories, ad blocking, DNS filtering, content filtering,
    honeypot and DPI settings."""
    async with UniFiClient() as client:
        site_name = await _site_name(client, site_id)
        settings_by_key = await _classic_settings(client, site_name)
        return ThreatManagementResult(
            ips=settings_by_key.get("ips"),
            ipsSuppression=settings_by_key.get("ips_suppression"),
            contentFiltering=await client.get_classic(site_name, "content-filtering", v2=True),
            dpi=settings_by_key.get("dpi"),
        )


@unifi_mcp.tool
async def switch_ports(
    site_id: Annotated[str, Field(description="Site UUID")],
    device_id: Annotated[str, Field(description="Device UUID of a switch or gateway")]
) -> SwitchPortsResult:
    """Get each port's native VLAN, tagged VLANs, port profile and PoE settings."""
    async with UniFiClient() as client:
        site_name = await _site_name(client, site_id)
        device = await client.get(f"sites/{site_id}/devices/{device_id}")
        stats = await client.get_classic(site_name, f"stat/device/{quote(device['macAddress'].lower())}")
        if not stats or not stats[0].get("port_table"):
            raise ValueError(f"Device {device_id} has no switch ports")
        stat = stats[0]
        network_names = {n["_id"]: n.get("name") for n in await client.get_classic(site_name, "rest/networkconf")}
        profiles = await client.get_classic(site_name, "rest/portconf")
        profile_names = {p["_id"]: p.get("name") for p in profiles}
        overrides = {o["port_idx"]: o for o in stat.get("port_overrides") or []}
        names = lambda ids: [network_names.get(i, i) for i in ids] if ids else None
        
        ports = []
        for port in stat["port_table"]:
            override = overrides.get(port["port_idx"], {})
            ports.append(SwitchPortConfig(
                idx=port["port_idx"],
                name=port.get("name"),
                up=port.get("up"),
                enabled=port.get("enable"),
                speedMbps=port.get("speed"),
                isUplink=port.get("is_uplink"),
                overridden=bool(override),
                portProfile=profile_names.get(override.get("portconf_id")),
                forward=override.get("forward", port.get("forward")),
                nativeNetwork=network_names.get(override.get("native_networkconf_id")),
                taggedVlanMgmt=override.get("tagged_vlan_mgmt"),
                taggedNetworks=names(override.get("tagged_networkconf_ids")),
                excludedNetworks=names(override.get("excluded_networkconf_ids")),
                poeMode=override.get("poe_mode", port.get("poe_mode")) if port.get("port_poe") else None,
                poePowerW=float(port["poe_power"]) if port.get("port_poe") and port.get("poe_power") else None,
                portSecurityEnabled=override.get("port_security_enabled"),
            ))
        return SwitchPortsResult(
            deviceId=device_id,
            deviceName=device.get("name"),
            model=device.get("model"),
            ports=ports,
            portProfiles=profiles,
        )


async def _site_name(client: UniFiClient, site_id: str) -> str:
    """Map a site UUID to the name the classic API uses (its internalReference, e.g. "default")."""
    sites = await client.get_paginated("sites")
    site = next((s for s in sites if s["id"] == site_id), None)
    if site is None:
        raise ValueError(f"Site {site_id} not found")
    return site["internalReference"]


async def _classic_settings(client: UniFiClient, site_name: str) -> dict:
    """Return the classic site settings keyed by section (ips, mdns, teleport, ...)."""
    return {s["key"]: s for s in await client.get_classic(site_name, "rest/setting")}


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