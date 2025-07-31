# FastMCP Debug Notifications

## Overview

This document explains how to properly send debug messages from within FastMCP tools without breaking the JSON-RPC protocol.

## Problem

When developing FastMCP tools, using `print()` or standard logging to stdout causes JSON parsing errors on the client side because it's expecting structured JSON-RPC messages, not raw text.

```python
# DON'T DO THIS - breaks the JSON-RPC protocol
@mcp.tool()
async def broken_tool(ctx: Context, arg: str) -> str:
    print(f"Debug: Starting with {arg}")  # This breaks the JSON-RPC protocol!
    # ...
    return "Result"
```

## Solution

Use the `send_debug_notification` function to send properly formatted JSON-RPC 2.0 notifications for debug messages:

```python
from mcp.server.fastmcp import FastMCP, Context
import json
import sys

async def send_debug_notification(ctx: Context, message: str) -> None:
    """Send a properly formatted JSON-RPC 2.0 debug notification to the client."""
    notification = {
        "jsonrpc": "2.0",
        "method": "window/logMessage",
        "params": {
            "type": 4,  # 4 = Debug level
            "message": message
        }
    }
    
    # Use sys.stdout to ensure we're writing to the correct stream
    sys.stdout.write(json.dumps(notification) + "\n")
    sys.stdout.flush()

@mcp.tool()
async def proper_tool(ctx: Context, arg: str) -> str:
    await send_debug_notification(ctx, f"Starting with {arg}")  # Proper JSON-RPC notification
    # ...
    return "Result"
```

## Implementation Details

The `send_debug_notification` function creates a JSON-RPC 2.0 notification with:

```json
{
  "jsonrpc": "2.0",
  "method": "window/logMessage",
  "params": {
    "type": 4,
    "message": "Your debug message here"
  }
}
```

Where `type: 4` represents a debug log level.

## Log Levels

You can use different log levels with the `send_log_notification` function:

```python
# Define log levels
class LogLevel:
    ERROR = 1
    WARNING = 2
    INFO = 3
    DEBUG = 4

async def send_log_notification(ctx: Context, message: str, level: int = LogLevel.DEBUG) -> None:
    notification = {
        "jsonrpc": "2.0",
        "method": "window/logMessage",
        "params": {
            "type": level,
            "message": message
        }
    }
    
    sys.stdout.write(json.dumps(notification) + "\n")
    sys.stdout.flush()

# Error level
await send_log_notification(ctx, "This is an error", LogLevel.ERROR)

# Warning level
await send_log_notification(ctx, "This is a warning", LogLevel.WARNING)

# Info level
await send_log_notification(ctx, "This is info", LogLevel.INFO)

# Debug level
await send_log_notification(ctx, "This is debug", LogLevel.DEBUG)
```

## Complete Example Usage

```python
from mcp.server.fastmcp import FastMCP, Context
import json
import sys
import asyncio

# Define log levels
class LogLevel:
    ERROR = 1
    WARNING = 2
    INFO = 3
    DEBUG = 4

async def send_debug_notification(ctx: Context, message: str) -> None:
    notification = {
        "jsonrpc": "2.0",
        "method": "window/logMessage",
        "params": {
            "type": 4,  # 4 = Debug level
            "message": message
        }
    }
    
    sys.stdout.write(json.dumps(notification) + "\n")
    sys.stdout.flush()

mcp = FastMCP("MyServer")

@mcp.tool()
async def my_tool(ctx: Context, some_arg: str) -> str:
    # Send debug notification
    await send_debug_notification(ctx, f"Starting my_tool with arg: {some_arg}")
    
    # ... tool logic ...
    
    # Send completion notification
    await send_debug_notification(ctx, "Finished my_tool.")
    
    return "Tool executed successfully."

if __name__ == "__main__":
    mcp.start()
```

## Benefits

- Maintains JSON-RPC protocol integrity
- Properly structured debug messages
- Client can display debug messages in appropriate UI elements
- Supports different log levels
- No more "Unexpected token" JSON parsing errors

## Integration with Existing Logging

If you have an existing logging system, you can integrate this notification system:

```python
import logging
import asyncio
from functools import partial

class FastMCPLogHandler(logging.Handler):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        
    def emit(self, record):
        # Convert log level to MCP log level
        level_map = {
            logging.ERROR: LogLevel.ERROR,
            logging.WARNING: LogLevel.WARNING,
            logging.INFO: LogLevel.INFO,
            logging.DEBUG: LogLevel.DEBUG
        }
        level = level_map.get(record.levelno, LogLevel.DEBUG)
        
        # Get the formatted message
        msg = self.format(record)
        
        # Schedule the notification (since emit can't be async)
        asyncio.create_task(send_log_notification(self.ctx, msg, level))
```