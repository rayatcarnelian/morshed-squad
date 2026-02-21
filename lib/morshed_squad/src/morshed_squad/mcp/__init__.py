"""MCP (Model Context Protocol) client support for Morshed Squad agents.

This module provides native MCP client functionality, allowing Morshed Squad agents
to connect to any MCP-compliant server using various transport types.
"""

from morshed_squad.mcp.client import MCPClient
from morshed_squad.mcp.config import (
    MCPServerConfig,
    MCPServerHTTP,
    MCPServerSSE,
    MCPServerStdio,
)
from morshed_squad.mcp.filters import (
    StaticToolFilter,
    ToolFilter,
    ToolFilterContext,
    create_dynamic_tool_filter,
    create_static_tool_filter,
)
from morshed_squad.mcp.transports.base import BaseTransport, TransportType


__all__ = [
    "BaseTransport",
    "MCPClient",
    "MCPServerConfig",
    "MCPServerHTTP",
    "MCPServerSSE",
    "MCPServerStdio",
    "StaticToolFilter",
    "ToolFilter",
    "ToolFilterContext",
    "TransportType",
    "create_dynamic_tool_filter",
    "create_static_tool_filter",
]
