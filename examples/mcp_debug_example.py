#!/usr/bin/env python3
"""
Example of using the debug notification system with FastMCP

This example demonstrates how to properly send debug messages from within
a FastMCP tool without breaking the JSON-RPC protocol.

Usage:
    python mcp_debug_example.py

License: MIT
"""

import asyncio
import json
import sys

from mcp.server.fastmcp import Context, FastMCP

# Import our debug notification utility
from voidcat_reasoning_core.mcp_debug_utils import (
    LogLevel,
    send_debug_notification,
    send_log_notification,
)

# Create the FastMCP server
mcp = FastMCP("MyServer")


@mcp.tool()
async def my_tool(ctx: Context, some_arg: str) -> str:
    """
    Example tool that demonstrates proper debug logging.

    Args:
        ctx: The FastMCP Context object
        some_arg: An example argument

    Returns:
        A success message
    """
    # Instead of print() or logger.debug(), use the notification function
    await send_debug_notification(ctx, f"Starting my_tool with arg: {some_arg}")

    # Do some work...
    await asyncio.sleep(1)  # Simulate processing

    # Log different levels
    await send_log_notification(ctx, "This is an error message", LogLevel.ERROR)
    await send_log_notification(ctx, "This is a warning message", LogLevel.WARNING)
    await send_log_notification(ctx, "This is an info message", LogLevel.INFO)

    # Log completion
    await send_debug_notification(ctx, "Finished my_tool.")

    # Return the actual result (this goes through the normal JSON-RPC response)
    return "Tool executed successfully."


@mcp.tool()
async def complex_tool(ctx: Context, input_data: dict) -> dict:
    """
    A more complex example tool with structured input/output.

    Args:
        ctx: The FastMCP Context object
        input_data: A dictionary of input data

    Returns:
        A dictionary with the processed results
    """
    # Log the start with input data details
    await send_debug_notification(
        ctx, f"Starting complex_tool with {len(input_data)} input items"
    )

    # Process each item with debug logs
    results = {}
    for key, value in input_data.items():
        await send_debug_notification(ctx, f"Processing item: {key}")

        # Simulate processing
        await asyncio.sleep(0.5)

        # Add to results
        results[key] = f"Processed: {value}"

        await send_debug_notification(ctx, f"Completed processing: {key}")

    # Log completion
    await send_debug_notification(
        ctx, f"Finished complex_tool with {len(results)} result items"
    )

    return {"status": "success", "processed_count": len(results), "results": results}


# Create a standalone implementation of the function as requested
async def send_debug_notification_standalone(ctx: Context, message: str) -> None:
    """
    Send a properly formatted JSON-RPC 2.0 debug notification to the client.

    This is the standalone implementation as requested in the original prompt.

    Args:
        ctx: The FastMCP Context object
        message: The debug message to send
    """
    # Create the JSON-RPC 2.0 notification payload
    notification = {
        "jsonrpc": "2.0",
        "method": "window/logMessage",
        "params": {"type": 4, "message": message},  # 4 = Debug level
    }

    # Use sys.stdout to ensure we're writing to the correct stream
    sys.stdout.write(json.dumps(notification) + "\n")
    sys.stdout.flush()


if __name__ == "__main__":
    # Start the FastMCP server
    mcp.start()
