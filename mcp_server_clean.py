#!/usr/bin/env python3
"""
VoidCat Reasoning Core MCP Server - Clean Simplified Version
Reliable MCP protocol implementation for Claude Desktop integration
"""

import asyncio
import json
import os
import sys
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional

# Import our clean engine
from engine_simple import VoidCatEngine


def debug_print(message: str) -> None:
    """Print debug messages to stderr for MCP compatibility."""
    print(f"[VoidCat-MCP] {message}", file=sys.stderr, flush=True)


class VoidCatMCPServer:
    """Clean, reliable MCP server for VoidCat Reasoning Core."""

    def __init__(self):
        """Initialize the MCP server."""
        self.engine: Optional[VoidCatEngine] = None
        self.server_version = "1.0.0-clean"
        self.initialization_time = None
        self.query_count = 0
        self.error_count = 0

        # Define available tools
        self.tools = [
            {
                "name": "voidcat_query",
                "description": "Process intelligent queries using RAG-enhanced reasoning",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The question or prompt to process",
                        },
                        "model": {
                            "type": "string",
                            "description": "AI model to use",
                            "default": "gpt-4o-mini",
                            "enum": ["gpt-4o-mini", "gpt-4o", "deepseek-chat"],
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "voidcat_status",
                "description": "Get VoidCat engine status and diagnostics",
                "inputSchema": {"type": "object", "properties": {}, "required": []},
            },
        ]

    async def initialize(self, request_id: Optional[str] = None) -> None:
        """Initialize the VoidCat engine."""
        try:
            debug_print("Initializing VoidCat Reasoning Core...")
            self.initialization_time = datetime.now().isoformat()

            self.engine = VoidCatEngine()
            debug_print("Engine initialization completed successfully")

            await self._send_response(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}, "resources": {}, "prompts": {}},
                        "serverInfo": {
                            "name": "voidcat-reasoning-core",
                            "version": self.server_version,
                            "description": "Clean RAG-enhanced reasoning engine",
                        },
                    },
                }
            )

        except Exception as e:
            self.error_count += 1
            error_msg = f"Failed to initialize: {str(e)}"
            debug_print(f"Initialization error: {error_msg}")
            await self._send_error(error_msg, request_id)

    async def handle_list_tools(self, request_id: Optional[str] = None) -> None:
        """Handle tools list request."""
        await self._send_response(
            {"jsonrpc": "2.0", "id": request_id, "result": {"tools": self.tools}}
        )

    async def handle_call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        request_id: Optional[str] = None,
    ) -> None:
        """Handle tool execution request."""
        if not self.engine:
            await self._send_error("Engine not initialized", request_id)
            return

        try:
            debug_print(f"Executing tool: {tool_name}")

            if tool_name == "voidcat_query":
                await self._handle_query_tool(arguments, request_id)
            elif tool_name == "voidcat_status":
                await self._handle_status_tool(arguments, request_id)
            else:
                await self._send_error(f"Unknown tool: {tool_name}", request_id)

        except Exception as e:
            self.error_count += 1
            error_msg = f"Tool execution failed: {str(e)}"
            debug_print(f"Tool error: {error_msg}")
            await self._send_error(error_msg, request_id)

    async def _handle_query_tool(
        self, arguments: Dict[str, Any], request_id: Optional[str] = None
    ) -> None:
        """Handle voidcat_query tool."""
        query = arguments.get("query", "")
        model = arguments.get("model", "gpt-4o-mini")

        if not query:
            await self._send_error("Query parameter required", request_id)
            return

        try:
            debug_print(f"Processing query with model: {model}")
            response = await self.engine.query(query, model=model)
            self.query_count += 1

            await self._send_response(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"🧠 **VoidCat RAG Response**\n\n{response}\n\n---\n*Model: {model} | Queries processed: {self.query_count}*",
                            }
                        ]
                    },
                }
            )

        except Exception as e:
            await self._send_error(f"Query processing failed: {str(e)}", request_id)

    async def _handle_status_tool(
        self, arguments: Dict[str, Any], request_id: Optional[str] = None
    ) -> None:
        """Handle voidcat_status tool."""
        try:
            if self.engine:
                diagnostics = self.engine.get_diagnostics()
                status = {
                    "engine_initialized": True,
                    "server_version": self.server_version,
                    "initialization_time": self.initialization_time,
                    "query_count": self.query_count,
                    "error_count": self.error_count,
                    "engine_diagnostics": diagnostics,
                }
                status_text = f"✅ **VoidCat System Status**\n\n```json\n{json.dumps(status, indent=2)}\n```"
            else:
                status_text = "❌ **VoidCat Engine Not Initialized**"

            await self._send_response(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"content": [{"type": "text", "text": status_text}]},
                }
            )

        except Exception as e:
            await self._send_error(f"Status check failed: {str(e)}", request_id)

    async def _send_response(self, response: Dict[str, Any]) -> None:
        """Send JSON-RPC response to stdout."""
        print(json.dumps(response), flush=True)

    async def _send_error(
        self, error_message: str, request_id: Optional[str] = None
    ) -> None:
        """Send JSON-RPC error response."""
        await self._send_response(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -1, "message": error_message},
            }
        )

    async def handle_request(self, request: Dict[str, Any]) -> None:
        """Handle incoming MCP request."""
        method = request.get("method", "")
        params = request.get("params", {})
        request_id = request.get("id")

        if method == "initialize":
            await self.initialize(request_id)
        elif method == "tools/list":
            await self.handle_list_tools(request_id)
        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            await self.handle_call_tool(tool_name, arguments, request_id)
        else:
            await self._send_error(f"Unknown method: {method}", request_id)


async def main():
    """Main MCP server entry point."""
    server = VoidCatMCPServer()
    debug_print("🚀 VoidCat Clean MCP Server starting...")

    try:
        # Read from stdin line by line
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                if not line:
                    break

                line = line.strip()
                if line:
                    debug_print(f"📥 Received: {line[:100]}...")
                    try:
                        request = json.loads(line)
                        await server.handle_request(request)
                    except json.JSONDecodeError as e:
                        debug_print(f"❌ JSON decode error: {str(e)}")
                        await server._send_error(f"Invalid JSON: {str(e)}")
                    except Exception as e:
                        debug_print(f"❌ Request error: {str(e)}")
                        await server._send_error(f"Request failed: {str(e)}")

            except Exception as e:
                debug_print(f"❌ Main loop error: {str(e)}")
                break

    except KeyboardInterrupt:
        debug_print("🛑 Server stopped by user")
    except Exception as e:
        debug_print(f"❌ Server error: {str(e)}")
    finally:
        debug_print("🔚 VoidCat MCP Server shutting down")


if __name__ == "__main__":
    asyncio.run(main())
