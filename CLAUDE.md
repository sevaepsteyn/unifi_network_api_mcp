# UniFi Network API MCP Server - Development Notes

This document captures key learnings and important information discovered during the development of the UniFi Network API MCP Server.

## Project Overview

This project implements a Model Context Protocol (MCP) server that exposes UniFi Network Controller API.

## Development Environment

- Python 3.11+
- FastMCP 2.10.6
- httpx for async HTTP
- Pydantic v2 for data validation
- pydantic-settings for configuration
- MCP protocol 1.12.2