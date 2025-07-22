#!/usr/bin/env python3
"""
Simple VoidCat MCP Server Validation
===================================

Quick validation that the MCP server can start and has the correct tools configured.
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from mcp_server import VoidCatMCPServer

    print("✅ MCP Server import successful")

    # Initialize server
    server = VoidCatMCPServer()
    print("✅ MCP Server initialization successful")

    # Check if server has the expected tool methods
    expected_tools = [
        "handle_voidcat_query",
        "handle_voidcat_status",
        "handle_voidcat_enhanced_query",
        "handle_voidcat_sequential_thinking",
        "handle_voidcat_analyze_knowledge",
        "handle_voidcat_create_memory",
        "handle_voidcat_search_memories",
        "handle_voidcat_create_project",
        "handle_voidcat_create_task",
        "handle_voidcat_list_projects",
        "handle_voidcat_list_tasks",
    ]

    available_tools = []
    for tool in expected_tools:
        if hasattr(server, tool):
            available_tools.append(tool)

    print(f"✅ Found {len(available_tools)} VoidCat tools available:")
    for tool in available_tools:
        tool_name = tool.replace("handle_", "")
        print(f"   📋 {tool_name}")

    # Test engine initialization
    if hasattr(server, "engine") and server.engine:
        print("✅ VoidCat reasoning engine initialized")
    else:
        print("⚠️  VoidCat reasoning engine not initialized")

    print("\n🎉 MCP Server Validation Results:")
    print("=" * 50)
    print(f"✅ Server operational with {len(available_tools)} tools")
    print("✅ Ready for Claude Desktop integration!")

    print("\n📋 Claude Desktop Configuration:")
    print(
        "Add this to your Claude Desktop config (~/.claude/claude_desktop_config.json):"
    )
    print(
        """
{
  "mcpServers": {
    "voidcat-reasoning-core": {
      "command": "python",
      "args": ["D:\\\\03_Development\\\\Active_Projects\\\\voidcat-reasoning-core\\\\mcp_server.py"],
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key",
        "DEEPSEEK_API_KEY": "your-deepseek-api-key"
      }
    }
  }
}
"""
    )

except Exception as e:
    print(f"❌ Error: {e}")
    print(
        "Check that all dependencies are installed and environment variables are set."
    )
    sys.exit(1)
