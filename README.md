# UniFi Network API MCP Server
# seva@sevatech.com

A Model Context Protocol (MCP) server that provides access to UniFi Network Controller API functionality.

## Demo

![UniFi Network API MCP Demo](docs/demo/claude.gif)

### Available Tools

#### Read Operations
- `application_info()` - Get application version info
- `sites()` - List all sites
- `devices(site_id)` - List devices in a site
- `device_details(site_id, device_id)` - Get device details
- `device_statistics(site_id, device_id)` - Get device statistics
- `clients(site_id)` - List connected clients
- `client_details(site_id, client_id)` - Get client details
- `vouchers(site_id)` - List hotspot vouchers
- `networks(site_id)` - List networks (LANs/VLANs)
- `network_details(site_id, network_id)` - Get network VLAN, subnet and DHCP settings
- `wifi_broadcasts(site_id)` - List WiFi networks (SSIDs)
- `wifi_broadcast_details(site_id, wifi_broadcast_id)` - Get WiFi security and options (passphrases redacted)
- `firewall_zones(site_id)` - List firewall zones and their networks
- `firewall_policies(site_id)` - List zone-based firewall policies
- `port_forwards(site_id)` - List port forwarding rules
- `traffic_matching_lists(site_id)` - List IP/port/domain groups used by firewall policies
- `network_services(site_id)` - Get DHCP options, DHCP DNS servers, IGMP snooping and mDNS settings
- `wifi_advanced_settings(site_id)` - Get per-SSID network binding, AP groups, bands, multicast and roaming options
- `vpn(site_id)` - Get VPN servers and their firewall zone, VPN client networks and Teleport settings
- `threat_management(site_id)` - Get IDS/IPS, ad blocking, DNS filtering and content filtering settings
- `switch_ports(site_id, device_id)` - Get each port's native/tagged VLANs, port profile and PoE settings

`client_details` also returns `uplinkPortIdx` (the switch port) for wired clients.

Tools that read settings the official integration API doesn't expose (port forwards, the last five
above, and `uplinkPortIdx`) use the classic Network API, which is undocumented and may change between
Network versions. Secrets such as WiFi passphrases and VPN private keys are redacted in all tool output.

#### Write Operations

##### Device Management
- `restart_device(site_id, device_id)` - Restart a device
- `power_cycle_port(site_id, device_id, port_idx)` - Power cycle a PoE port
- `search_devices(site_id, name_pattern, model, state)` - Search devices with filters

##### Guest Management
- `authorize_guest(site_id, client_id, ...)` - Authorize guest access with optional limits
- `unauthorize_guest(site_id, client_id)` - Revoke guest access

##### Voucher Management
- `create_vouchers(site_id, name, time_limit_minutes, ...)` - Create hotspot vouchers
- `delete_voucher(site_id, voucher_id)` - Delete a voucher

## Installation

### From Source
```bash
# Clone the repository
git clone https://github.com/yourusername/unifi_network_api_mcp.git
cd unifi_network_api_mcp

# Using uv (recommended)
uv sync
```

## Configuration

Set the following environment variables:

```bash
# Required
export UNIFI_CONTROLLER_URL="https://your-controller.unifi-hosting.ui.com"
export UNIFI_API_KEY="your-api-key-here"

# Optional
export UNIFI_API_TIMEOUT=30.0
export UNIFI_API_RETRY_ATTEMPTS=3
export UNIFI_API_RETRY_DELAY=1.0
export UNIFI_DEFAULT_PAGE_SIZE=25
export UNIFI_LOG_LEVEL="INFO"
```

You can also create a `.env` file in your project root:

```env
UNIFI_CONTROLLER_URL=https://your-controller.unifi-hosting.ui.com
UNIFI_API_KEY=your-api-key-here
```

## Usage

### Running the Server

```bash
# Using uv (if installed from source)
uv run unifi-network-api-mcp
```

### Using with Claude Desktop

Add MCP server to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

#### Using uv
```json
{
  "mcpServers": {
    "unifi": {
      "command": "uv",
      "args": [
        "run",
        "--project",
        "/path/to/unifi_network_api_mcp",
        "unifi-network-api-mcp"
      ],
      "env": {
        "UNIFI_CONTROLLER_URL": "https://your-controller.unifi-hosting.ui.com",
        "UNIFI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/sevaepsteyn/unifi_network_api_mcp.git
cd unifi_network_api_mcp

# Install dependencies with uv
uv sync

# Run in development mode
uv run unifi-network-api-mcp

# Or use uv with --project from any directory
uv run --project /path/to/unifi_network_api_mcp unifi-network-api-mcp
```

### Testing

```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=unifi_network_api_mcp
```

## API Reference

For detailed API documentation, see [UNIFI_NETWORK_API.md](UNIFI_NETWORK_API.md).

## License

MIT License - see LICENSE file for details
