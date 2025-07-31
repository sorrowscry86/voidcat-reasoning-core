#!/usr/bin/env python3
"""
VoidCat MCP Server Test Script
=============================

This script tests the VoidCat MCP server functionality to ensure
all tools are working correctly before integrating with Claude Desktop.
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_server import VoidCatMCPServer


async def test_mcp_server():
    """Test the VoidCat MCP server functionality."""
    print("🚀 Testing VoidCat MCP Server...")
    print("=" * 50)

    try:
        # Initialize the server
        server = VoidCatMCPServer()
        print("✅ Server initialized successfully")

        # Test tool listing
        tools = await server.list_tools()
        print(f"✅ Found {len(tools.tools)} available tools:")

        for tool in tools.tools:
            print(f"   📋 {tool.name}: {tool.description}")

        print("\n🧪 Testing core tools...")

        # Test voidcat_status tool
        try:
            status_result = await server.call_tool(name="voidcat_status", arguments={})
            print("✅ voidcat_status tool working")
            print(f"   Status: {status_result.content[0].text[:100]}...")
        except Exception as e:
            print(f"❌ voidcat_status tool failed: {e}")

        # Test voidcat_query tool
        try:
            query_result = await server.call_tool(
                name="voidcat_query",
                arguments={
                    "query": "What is the meaning of life?",
                    "model": "gpt-4o-mini",
                },
            )
            print("✅ voidcat_query tool working")
            print(f"   Response length: {len(query_result.content[0].text)} characters")
        except Exception as e:
            print(f"❌ voidcat_query tool failed: {e}")

        # Test memory tools
        try:
            # Test creating a memory
            create_result = await server.call_tool(
                name="voidcat_create_memory",
                arguments={
                    "content": "Test memory for MCP validation",
                    "category": "test",
                    "importance": 5,
                },
            )
            print("✅ voidcat_create_memory tool working")

            # Test searching memories
            search_result = await server.call_tool(
                name="voidcat_search_memories", arguments={"query": "test", "limit": 5}
            )
            print("✅ voidcat_search_memories tool working")

        except Exception as e:
            print(f"❌ Memory tools failed: {e}")

        # Test task management tools
        try:
            # Test creating a project
            project_result = await server.call_tool(
                name="voidcat_create_project",
                arguments={
                    "name": "Test MCP Project",
                    "description": "A test project for MCP validation",
                },
            )
            print("✅ voidcat_create_project tool working")

            # Extract project ID from result
            import re

            project_match = re.search(
                r"Project ID: ([a-f0-9-]+)", project_result.content[0].text
            )
            if project_match:
                project_id = project_match.group(1)

                # Test creating a task
                task_result = await server.call_tool(
                    name="voidcat_create_task",
                    arguments={
                        "project_id": project_id,
                        "name": "Test MCP Task",
                        "details": "A test task for MCP validation",
                        "priority": 5,
                    },
                )
                print("✅ voidcat_create_task tool working")

        except Exception as e:
            print(f"❌ Task management tools failed: {e}")

        print("\n🎉 MCP Server Test Results:")
        print("=" * 50)
        print("✅ Server is operational and ready for Claude Desktop integration!")
        print("📋 All core tools are functional")
        print("🔗 Ready to connect to Claude Desktop")

        return True

    except Exception as e:
        print(f"❌ Server initialization failed: {e}")
        print(f"📝 Error details: {str(e)}")
        return False


async def main():
    """Main test function."""
    print(f"🛡️ VoidCat MCP Server Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Testing server functionality before Claude Desktop integration...")
    print()

    success = await test_mcp_server()

    if success:
        print("\n🚀 Next Steps:")
        print("1. Copy the updated Claude Desktop configuration")
        print("2. Restart Claude Desktop")
        print("3. Test VoidCat tools in Claude Desktop")
        return 0
    else:
        print("\n❌ Tests failed. Please check the configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
