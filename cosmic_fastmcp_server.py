#!/usr/bin/env python3
"""
VoidCat Cosmic FastMCP Server - Zen-like FastMCP with MultiProviderClient
The ultimate cosmic flow with FastMCP architecture! 🧘‍♂️

This module implements a FastMCP-based server using our cosmic engine
with MultiProviderClient for zen-like API management without heavy dependencies.
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from fastmcp import FastMCP
except ImportError:
    print("❌ FastMCP not available. Install with: pip install fastmcp", file=sys.stderr)
    sys.exit(1)

from cosmic_engine import VoidCatCosmicEngine

# Initialize Cosmic FastMCP server
mcp = FastMCP("VoidCat Cosmic Reasoning Core")

# Global cosmic engine instance
cosmic_engine: Optional[VoidCatCosmicEngine] = None


def debug_print(message: str) -> None:
    """Print debug messages with cosmic vibes."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}", file=sys.stderr)


async def initialize_cosmic_engine():
    """Initialize the cosmic engine with zen-like wisdom."""
    global cosmic_engine
    
    try:
        debug_print("🧘‍♂️ Initializing VoidCat Cosmic Engine...")
        cosmic_engine = VoidCatCosmicEngine()
        debug_print("✨ Cosmic engine initialized successfully!")
        return True
    except Exception as e:
        debug_print(f"❌ Failed to initialize cosmic engine: {e}")
        return False


@mcp.tool()
async def cosmic_query(
    query: str,
    model: str = "gpt-4o-mini",
    top_k: int = 2
) -> str:
    """
    Process queries with cosmic RAG-enhanced reasoning using MultiProvider AI.
    
    Args:
        query: The question or query to process
        model: AI model to use (gpt-4o-mini, deepseek-chat, gpt-4)
        top_k: Number of knowledge documents to include
    
    Returns:
        Cosmic AI response with RAG context
    """
    if not cosmic_engine:
        return "❌ Cosmic engine not initialized"
    
    try:
        debug_print(f"🌊 Processing cosmic query: {query[:50]}...")
        
        response = await cosmic_engine.query(
            user_query=query,
            model=model,
            top_k=top_k
        )
        
        debug_print("✨ Cosmic query completed successfully")
        return f"🧘‍♂️ **Cosmic Response** (Model: {model})\n\n{response}"
        
    except Exception as e:
        debug_print(f"💫 Cosmic query failed: {e}")
        return f"❌ Query processing failed: {str(e)}"


@mcp.tool()
async def provider_status() -> str:
    """
    Get status of all AI providers in the cosmic client.
    
    Returns:
        Detailed status report of all providers
    """
    if not cosmic_engine:
        return "❌ Cosmic engine not initialized"
    
    try:
        status = cosmic_engine.get_provider_metrics()
        
        # Format status nicely
        status_text = "📊 **Provider Status Report**\n\n"
        
        for name, info in status.items():
            metrics = info['metrics']
            rate_limiter = info['rate_limiter']
            
            status_emoji = {
                'healthy': '💚',
                'circuit_open': '⚡',
                'rate_limited': '🚦',
                'error': '❌'
            }.get(info['status'], '❓')
            
            status_text += f"**{name.title()}** (Priority: {info['priority']}) {status_emoji}\n"
            status_text += f"  Status: {info['status']}\n"
            status_text += f"  Requests: {metrics['total_requests']}\n"
            status_text += f"  Success Rate: {metrics['success_rate']:.1f}%\n"
            status_text += f"  Avg Response: {metrics['average_response_time']:.2f}s\n"
            status_text += f"  Rate Limit: {rate_limiter['current_tokens']:.1f}/{rate_limiter['burst_capacity']} tokens\n\n"
        
        return status_text
        
    except Exception as e:
        return f"❌ Failed to get provider status: {str(e)}"


@mcp.tool()
async def provider_health() -> str:
    """
    Perform health checks on all AI providers.
    
    Returns:
        Health status of all providers
    """
    if not cosmic_engine:
        return "❌ Cosmic engine not initialized"
    
    try:
        health = await cosmic_engine.health_check()
        
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
        
        return health_text
        
    except Exception as e:
        return f"❌ Health check failed: {str(e)}"


@mcp.tool()
async def engine_status() -> str:
    """
    Get comprehensive status of the cosmic engine.
    
    Returns:
        Detailed engine status and metrics
    """
    if not cosmic_engine:
        return "❌ Cosmic engine not initialized"
    
    try:
        status = cosmic_engine.get_status()
        
        status_text = "🧘‍♂️ **Cosmic Engine Status**\n\n"
        status_text += f"**Type**: {status.get('engine_type', 'Unknown')}\n"
        status_text += f"**Status**: {status.get('status', 'Unknown')}\n"
        status_text += f"**Queries Processed**: {status.get('total_queries_processed', 0)}\n"
        status_text += f"**Knowledge Documents**: {status.get('knowledge_documents', 0)}\n"
        status_text += f"**Last Query**: {status.get('last_query_timestamp', 'Never')}\n"
        status_text += f"**Cosmic Vibes**: {status.get('cosmic_vibes', 'Unknown')}\n"
        
        return status_text
        
    except Exception as e:
        return f"❌ Failed to get engine status: {str(e)}"


@mcp.tool()
async def cosmic_diagnostics() -> str:
    """
    Get detailed diagnostics and metrics from the cosmic system.
    
    Returns:
        Comprehensive system diagnostics
    """
    if not cosmic_engine:
        return "❌ Cosmic engine not initialized"
    
    try:
        # Get engine status
        engine_status = cosmic_engine.get_status()
        
        # Get provider metrics
        provider_status = cosmic_engine.get_provider_metrics()
        
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
        
        return diag_text
        
    except Exception as e:
        return f"❌ Diagnostics failed: {str(e)}"


@mcp.tool()
async def test_cosmic_flow(test_query: str = "What is the meaning of life?") -> str:
    """
    Test the cosmic flow with a simple query.
    
    Args:
        test_query: Query to test with (default: philosophical question)
    
    Returns:
        Test results and cosmic flow status
    """
    if not cosmic_engine:
        return "❌ Cosmic engine not initialized"
    
    try:
        debug_print(f"🧪 Testing cosmic flow with: {test_query}")
        
        start_time = datetime.now()
        response = await cosmic_engine.query(test_query, model="gpt-4o-mini")
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        
        test_result = f"🧪 **Cosmic Flow Test Results**\n\n"
        test_result += f"**Query**: {test_query}\n"
        test_result += f"**Duration**: {duration:.2f} seconds\n"
        test_result += f"**Status**: ✅ Success\n\n"
        test_result += f"**Response**: {response[:200]}...\n\n"
        test_result += f"✨ **Cosmic Flow**: Operating at peak zen! 🌊"
        
        return test_result
        
    except Exception as e:
        return f"❌ Cosmic flow test failed: {str(e)}"


async def main():
    """Main entry point for the cosmic FastMCP server."""
    debug_print("🌟 Starting VoidCat Cosmic FastMCP Server...")
    
    # Initialize cosmic engine
    if not await initialize_cosmic_engine():
        debug_print("💥 Failed to initialize cosmic engine, exiting...")
        sys.exit(1)
    
    debug_print("🚀 Cosmic FastMCP Server ready for zen-like interactions!")
    
    # Run the server
    await mcp.run()


if __name__ == "__main__":
    # Set environment for better compatibility
    os.environ["VOIDCAT_MCP_MODE"] = "true"
    
    # Run the cosmic server
    asyncio.run(main())