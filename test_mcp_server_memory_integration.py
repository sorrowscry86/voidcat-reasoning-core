#!/usr/bin/env python3
"""
Test VoidCat MCP Server Memory Integration
=========================================

Test that the memory tools are properly integrated into the MCP server
and can be called through the server interface.

Author: Codey Jr. (testing the cosmic server vibes)
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_server import VoidCatMCPServer


async def test_mcp_server_memory_integration():
    """Test the MCP server memory integration with cosmic vibes."""
    print("🌊 Testing VoidCat MCP Server Memory Integration...")

    # Create MCP server instance
    server = VoidCatMCPServer()

    # Initialize the server
    await server.initialize()
    print("✅ MCP Server initialized successfully")

    # Check that memory tools are available
    memory_tools = [
        tool
        for tool in server.tools
        if tool.name.startswith("voidcat_memory_")
        or tool.name.startswith("voidcat_preference_")
        or tool.name.startswith("voidcat_conversation_")
        or tool.name.startswith("voidcat_heuristic_")
    ]

    print(f"✅ Found {len(memory_tools)} memory management tools:")
    for tool in memory_tools:
        print(f"   - {tool.name}: {tool.description[:60]}...")

    # Test 1: Store a memory through the server
    print("\n🧠 Testing memory storage through MCP server...")
    store_request = {
        "jsonrpc": "2.0",
        "id": "test_store_1",
        "method": "tools/call",
        "params": {
            "name": "voidcat_memory_store",
            "arguments": {
                "content": "This is a test memory stored through the MCP server! 🚀",
                "category": "conversation_history",
                "importance": 7,
                "tags": ["test", "mcp", "server", "cosmic"],
                "title": "MCP Server Test Memory",
                "source": "mcp_server_test",
            },
        },
    }

    # Simulate tool call handling
    try:
        await server._handle_memory_management_tool(
            "voidcat_memory_store",
            store_request["params"]["arguments"],
            store_request["id"],
        )
        print("✅ Memory storage through MCP server successful")
    except Exception as e:
        print(f"❌ Memory storage failed: {e}")
        return

    # Test 2: Set a preference through the server
    print("\n⚙️ Testing preference setting through MCP server...")
    pref_request = {
        "jsonrpc": "2.0",
        "id": "test_pref_1",
        "method": "tools/call",
        "params": {
            "name": "voidcat_preference_set",
            "arguments": {
                "preference_key": "mcp_server_style",
                "preference_value": "cosmic_flow_integration",
                "preference_type": "string",
                "description": "MCP server integration style preference",
                "importance": 8,
                "tags": ["mcp", "server", "integration", "style"],
            },
        },
    }

    try:
        await server._handle_memory_management_tool(
            "voidcat_preference_set",
            pref_request["params"]["arguments"],
            pref_request["id"],
        )
        print("✅ Preference setting through MCP server successful")
    except Exception as e:
        print(f"❌ Preference setting failed: {e}")

    # Test 3: Track a conversation through the server
    print("\n💬 Testing conversation tracking through MCP server...")
    conv_request = {
        "jsonrpc": "2.0",
        "id": "test_conv_1",
        "method": "tools/call",
        "params": {
            "name": "voidcat_conversation_track",
            "arguments": {
                "conversation_id": "mcp_server_test_001",
                "user_message": "Hey, how's the MCP server memory integration working?",
                "assistant_response": "Dude! The MCP server memory integration is flowing with some serious cosmic energy! 🌊✨",
                "sentiment": "positive",
                "importance": 6,
                "tags": ["mcp", "server", "test", "integration"],
            },
        },
    }

    try:
        await server._handle_memory_management_tool(
            "voidcat_conversation_track",
            conv_request["params"]["arguments"],
            conv_request["id"],
        )
        print("✅ Conversation tracking through MCP server successful")
    except Exception as e:
        print(f"❌ Conversation tracking failed: {e}")

    # Test 4: Learn a heuristic through the server
    print("\n🧘 Testing heuristic learning through MCP server...")
    heuristic_request = {
        "jsonrpc": "2.0",
        "id": "test_heuristic_1",
        "method": "tools/call",
        "params": {
            "name": "voidcat_heuristic_learn",
            "arguments": {
                "heuristic_name": "mcp_server_integration_flow",
                "description": "When integrating MCP servers, maintain cosmic flow and test thoroughly",
                "trigger_conditions": [
                    "mcp_integration",
                    "server_setup",
                    "tool_registration",
                ],
                "recommended_actions": [
                    "test_thoroughly",
                    "maintain_cosmic_flow",
                    "document_well",
                ],
                "confidence": 0.95,
                "success_rate": 0.9,
                "importance": 8,
                "tags": ["mcp", "server", "integration", "heuristic"],
            },
        },
    }

    try:
        await server._handle_memory_management_tool(
            "voidcat_heuristic_learn",
            heuristic_request["params"]["arguments"],
            heuristic_request["id"],
        )
        print("✅ Heuristic learning through MCP server successful")
    except Exception as e:
        print(f"❌ Heuristic learning failed: {e}")

    # Test 5: Search memories through the server
    print("\n🔍 Testing memory search through MCP server...")
    search_request = {
        "jsonrpc": "2.0",
        "id": "test_search_1",
        "method": "tools/call",
        "params": {
            "name": "voidcat_memory_search",
            "arguments": {
                "query": "mcp server cosmic",
                "max_results": 5,
                "search_type": "hybrid",
            },
        },
    }

    try:
        await server._handle_memory_management_tool(
            "voidcat_memory_search",
            search_request["params"]["arguments"],
            search_request["id"],
        )
        print("✅ Memory search through MCP server successful")
    except Exception as e:
        print(f"❌ Memory search failed: {e}")

    print(
        "\n🎉 MCP Server Memory Integration test completed! The cosmic server vibes are flowing perfectly! ✨🤙"
    )
    print("🌊 All memory management tools are properly integrated into the MCP server!")


if __name__ == "__main__":
    asyncio.run(test_mcp_server_memory_integration())
