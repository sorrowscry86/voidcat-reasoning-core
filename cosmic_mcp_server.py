#!/usr/bin/env python3
"""
VoidCat Cosmic MCP Server - Zen-like MCP integration with MultiProviderClient
A lightweight MCP server that flows without heavy dependencies! 🧘‍♂️

This module implements a Model Context Protocol (MCP) server using our
cosmic engine with MultiProviderClient for zen-like API management.
"""

import asyncio
import json
import os
import sys
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cosmic_engine import VoidCatCosmicEngine

# MCP imports
try:
    import mcp.types as types
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
except ImportError as e:
    print(f"❌ MCP imports failed: {e}", file=sys.stderr)
    print("Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)


def debug_print(message: str, force: bool = False) -> None:
    """Enhanced debug printing with cosmic vibes."""
    debug_enabled = os.getenv("VOIDCAT_DEBUG", "true").lower() == "true"
    
    if debug_enabled or force:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}", file=sys.stderr)


class VoidCatCosmicMCPServer:
    """
    Cosmic MCP Server with zen-like MultiProvider integration.
    
    Provides intelligent reasoning capabilities through MCP protocol
    without heavy dependencies - pure cosmic flow! 🌊
    """
    
    def __init__(self):
        """Initialize the cosmic MCP server."""
        debug_print("🧘‍♂️ Initializing VoidCat Cosmic MCP Server...")
        
        # Initialize the cosmic engine
        try:
            self.engine = VoidCatCosmicEngine()
            debug_print("✨ Cosmic engine initialized successfully")
        except Exception as e:
            debug_print(f"❌ Failed to initialize cosmic engine: {e}", force=True)
            raise
        
        # Initialize MCP server
        self.server = Server("voidcat-cosmic-reasoning")
        debug_print("🌟 MCP server initialized")
        
        # Register tools
        self._register_tools()
        debug_print("🔧 Tools registered")
        
        debug_print("🎉 VoidCat Cosmic MCP Server ready!")
    
    def _register_tools(self):
        """Register all cosmic tools with the MCP server."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List all available cosmic tools."""
            return [
                types.Tool(
                    name="cosmic_query",
                    description="Process queries with cosmic RAG-enhanced reasoning using MultiProvider AI",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The question or query to process"
                            },
                            "model": {
                                "type": "string",
                                "description": "AI model to use (gpt-4o-mini, deepseek-chat, gpt-4)",
                                "default": "gpt-4o-mini"
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Number of knowledge documents to include",
                                "default": 2
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="provider_status",
                    description="Get status of all AI providers in the cosmic client",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="provider_health",
                    description="Perform health checks on all AI providers",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="engine_status",
                    description="Get comprehensive status of the cosmic engine",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="cosmic_diagnostics",
                    description="Get detailed diagnostics and metrics from the cosmic system",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Dict[str, Any]
        ) -> List[types.TextContent]:
            """Handle tool calls with cosmic wisdom."""
            debug_print(f"🔧 Tool called: {name} with args: {arguments}")
            
            try:
                if name == "cosmic_query":
                    return await self._handle_cosmic_query(arguments)
                elif name == "provider_status":
                    return await self._handle_provider_status(arguments)
                elif name == "provider_health":
                    return await self._handle_provider_health(arguments)
                elif name == "engine_status":
                    return await self._handle_engine_status(arguments)
                elif name == "cosmic_diagnostics":
                    return await self._handle_cosmic_diagnostics(arguments)
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"❌ Unknown tool: {name}"
                    )]
                    
            except Exception as e:
                debug_print(f"💫 Tool {name} failed: {e}", force=True)
                return [types.TextContent(
                    type="text",
                    text=f"❌ Tool execution failed: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
                )]
    
    async def _handle_cosmic_query(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle cosmic query processing."""
        query = arguments.get("query", "")
        model = arguments.get("model", "gpt-4o-mini")
        top_k = arguments.get("top_k", 2)
        
        if not query:
            return [types.TextContent(
                type="text",
                text="❌ Query parameter is required"
            )]
        
        debug_print(f"🌊 Processing cosmic query: {query[:50]}...")
        
        try:
            response = await self.engine.query(
                user_query=query,
                model=model,
                top_k=top_k
            )
            
            debug_print("✨ Cosmic query completed successfully")
            
            return [types.TextContent(
                type="text",
                text=f"🧘‍♂️ **Cosmic Response** (Model: {model})\n\n{response}"
            )]
            
        except Exception as e:
            debug_print(f"💫 Cosmic query failed: {e}")
            return [types.TextContent(
                type="text",
                text=f"❌ Query processing failed: {str(e)}"
            )]
    
    async def _handle_provider_status(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle provider status requests."""
        try:
            status = self.engine.get_provider_metrics()
            
            # Format status nicely
            status_text = "📊 **Provider Status Report**\n\n"
            
            for name, info in status.items():
                metrics = info['metrics']
                rate_limiter = info['rate_limiter']
                
                status_text += f"**{name.title()}** (Priority: {info['priority']})\n"
                status_text += f"  Status: {info['status']} {self._get_status_emoji(info['status'])}\n"
                status_text += f"  Requests: {metrics['total_requests']}\n"
                status_text += f"  Success Rate: {metrics['success_rate']:.1f}%\n"
                status_text += f"  Avg Response: {metrics['average_response_time']:.2f}s\n"
                status_text += f"  Rate Limit: {rate_limiter['current_tokens']:.1f}/{rate_limiter['burst_capacity']} tokens\n\n"
            
            return [types.TextContent(type="text", text=status_text)]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ Failed to get provider status: {str(e)}"
            )]
    
    async def _handle_provider_health(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle provider health check requests."""
        try:
            health = await self.engine.health_check()
            
            health_text = "💚 **Provider Health Check**\n\n"
            
            for name, is_healthy in health.items():
                emoji = "💚" if is_healthy else "💔"
                status = "Healthy" if is_healthy else "Unhealthy"
                health_text += f"{emoji} **{name.title()}**: {status}\n"
            
            healthy_count = sum(1 for h in health.values() if h)
            total_count = len(health)
            
            health_text += f"\n📊 **Summary**: {healthy_count}/{total_count} providers healthy"
            
            if health.get('engine_status') == 'healthy':
                health_text += "\n✨ **Cosmic Energy**: Flowing strong! 🌊"
            
            return [types.TextContent(type="text", text=health_text)]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ Health check failed: {str(e)}"
            )]
    
    async def _handle_engine_status(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle engine status requests."""
        try:
            status = self.engine.get_status()
            
            status_text = "🧘‍♂️ **Cosmic Engine Status**\n\n"
            status_text += f"**Type**: {status.get('engine_type', 'Unknown')}\n"
            status_text += f"**Status**: {status.get('status', 'Unknown')}\n"
            status_text += f"**Queries Processed**: {status.get('total_queries_processed', 0)}\n"
            status_text += f"**Knowledge Documents**: {status.get('knowledge_documents', 0)}\n"
            status_text += f"**Last Query**: {status.get('last_query_timestamp', 'Never')}\n"
            status_text += f"**Cosmic Vibes**: {status.get('cosmic_vibes', 'Unknown')}\n"
            
            return [types.TextContent(type="text", text=status_text)]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ Failed to get engine status: {str(e)}"
            )]
    
    async def _handle_cosmic_diagnostics(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle comprehensive diagnostics requests."""
        try:
            # Get engine status
            engine_status = self.engine.get_status()
            
            # Get provider metrics
            provider_status = self.engine.get_provider_metrics()
            
            # Build comprehensive diagnostics
            diag_text = "🔍 **Cosmic System Diagnostics**\n\n"
            
            # Engine info
            diag_text += "**🧘‍♂️ Engine Status**\n"
            diag_text += f"  Type: {engine_status.get('engine_type', 'Unknown')}\n"
            diag_text += f"  Status: {engine_status.get('status', 'Unknown')}\n"
            diag_text += f"  Queries: {engine_status.get('total_queries_processed', 0)}\n"
            diag_text += f"  Knowledge Docs: {engine_status.get('knowledge_documents', 0)}\n\n"
            
            # Provider summary
            diag_text += "**🌐 Provider Summary**\n"
            total_requests = 0
            total_providers = len(provider_status)
            healthy_providers = 0
            
            for name, info in provider_status.items():
                if info['status'] == 'healthy':
                    healthy_providers += 1
                total_requests += info['metrics']['total_requests']
            
            diag_text += f"  Total Providers: {total_providers}\n"
            diag_text += f"  Healthy Providers: {healthy_providers}\n"
            diag_text += f"  Total Requests: {total_requests}\n\n"
            
            # Detailed provider info
            diag_text += "**📊 Provider Details**\n"
            for name, info in provider_status.items():
                metrics = info['metrics']
                diag_text += f"  **{name.title()}**: {info['status']} "
                diag_text += f"({metrics['total_requests']} reqs, {metrics['success_rate']:.1f}% success)\n"
            
            diag_text += f"\n✨ **Cosmic Energy**: {engine_status.get('cosmic_vibes', 'Flowing smoothly')} 🌊"
            
            return [types.TextContent(type="text", text=diag_text)]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ Diagnostics failed: {str(e)}"
            )]
    
    def _get_status_emoji(self, status: str) -> str:
        """Get emoji for provider status."""
        status_emojis = {
            'healthy': '💚',
            'circuit_open': '⚡',
            'rate_limited': '🚦',
            'error': '❌'
        }
        return status_emojis.get(status, '❓')
    
    async def run(self):
        """Run the cosmic MCP server."""
        debug_print("🚀 Starting VoidCat Cosmic MCP Server...", force=True)
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="voidcat-cosmic-reasoning",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities={}
                    )
                )
            )


async def main():
    """Main entry point for the cosmic MCP server."""
    try:
        server = VoidCatCosmicMCPServer()
        await server.run()
    except KeyboardInterrupt:
        debug_print("🛑 Server stopped by user", force=True)
    except Exception as e:
        debug_print(f"💥 Server crashed: {e}", force=True)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Set environment for better MCP compatibility
    os.environ["VOIDCAT_MCP_MODE"] = "true"
    
    # Run the server
    asyncio.run(main())