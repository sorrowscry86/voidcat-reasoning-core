#!/usr/bin/env python3
"""
FastMCP Debug Utilities
Provides utilities for proper debug logging in FastMCP environments

This module implements JSON-RPC compliant debug notification utilities
for FastMCP servers, ensuring that debug messages are properly formatted
as JSON-RPC notifications rather than raw text.

License: MIT
Version: 0.1.0
"""

import json
import sys
from typing import Any, Dict, Optional, Union

from mcp.server.fastmcp import Context


async def send_debug_notification(ctx: Context, message: str) -> None:
    """
    Send a properly formatted JSON-RPC 2.0 debug notification to the client.

    Instead of using print() or logging directly to stdout, which would break
    the JSON-RPC protocol, this function creates a valid JSON-RPC notification
    that the client can properly parse.

    Args:
        ctx: The FastMCP Context object
        message: The debug message to send

    The function constructs a JSON-RPC 2.0 notification with:
        - jsonrpc: "2.0"
        - method: "window/logMessage"
        - params: {"type": 4, "message": your_message}

    Where type 4 represents a debug log level.
    """
    # Create the JSON-RPC 2.0 notification payload
    notification = {
        "jsonrpc": "2.0",
        "method": "window/logMessage",
        "params": {"type": 4, "message": message},  # 4 = Debug level
    }

    # Use sys.stdout to ensure we're writing to the correct stream
    # This maintains the JSON-RPC protocol integrity
    sys.stdout.write(json.dumps(notification) + "\n")
    sys.stdout.flush()


# Log level constants for the notification system
class LogLevel:
    ERROR = 1
    WARNING = 2
    INFO = 3
    DEBUG = 4


async def send_log_notification(
    ctx: Context, message: str, level: int = LogLevel.DEBUG
) -> None:
    """
    Send a log notification with the specified log level.

    Args:
        ctx: The FastMCP Context object
        message: The log message to send
        level: Log level (1=Error, 2=Warning, 3=Info, 4=Debug)
    """
    notification = {
        "jsonrpc": "2.0",
        "method": "window/logMessage",
        "params": {"type": level, "message": message},
    }

    sys.stdout.write(json.dumps(notification) + "\n")
    sys.stdout.flush()
