"""Main entry point for the UniFi Network API MCP server."""

import sys
from unifi_network_api_mcp.server import unifi_mcp


def main():
    """Run the UniFi Network API MCP server."""
    sys.exit(unifi_mcp.run())


if __name__ == "__main__":
    main()