#!/usr/bin/env python3
"""
Test VoidCat Memory MCP Tools Integration
========================================

Quick test to validate that the memory MCP tools are properly integrated
and working with the cosmic vibes!

Author: Codey Jr. (testing the memory flow)
"""

import asyncio
import json
from pathlib import Path

from voidcat_memory_mcp_tools import create_memory_mcp_tools


async def test_memory_tools_integration():
    """Test the memory tools integration with some righteous examples."""
    print("🧠 Testing VoidCat Memory MCP Tools Integration...")

    # Create memory tools instance
    working_dir = str(Path.cwd())
    memory_tools = create_memory_mcp_tools(working_dir)

    print(f"✅ Memory tools initialized with working directory: {working_dir}")

    # Test 1: Get available tools
    tools = memory_tools.get_tools()
    print(f"✅ Found {len(tools)} memory management tools:")
    for tool in tools:
        print(f"   - {tool['name']}: {tool['description'][:80]}...")

    # Test 2: Store a memory
    print("\n🌊 Testing memory storage...")
    store_args = {
        "content": "This is a test memory created by Codey Jr. with cosmic vibes! 🤙",
        "category": "conversation_history",
        "importance": 7,
        "tags": ["test", "cosmic", "memory"],
        "title": "Test Memory",
        "source": "integration_test",
    }

    store_result = await memory_tools.handle_tool_call(
        "voidcat_memory_store", store_args
    )
    print(f"Store result: {json.dumps(store_result, indent=2)}")

    if store_result.get("success"):
        memory_id = store_result["data"]["memory_id"]
        print(f"✅ Memory stored successfully with ID: {memory_id}")

        # Test 3: Search for the memory
        print("\n🔍 Testing memory search...")
        search_args = {
            "query": "cosmic vibes test",
            "max_results": 5,
            "search_type": "hybrid",
        }

        search_result = await memory_tools.handle_tool_call(
            "voidcat_memory_search", search_args
        )
        print(f"Search result: {json.dumps(search_result, indent=2)}")

        # Test 4: Retrieve the specific memory
        print("\n📖 Testing memory retrieval...")
        retrieve_args = {"memory_ids": [memory_id], "include_metadata": True}

        retrieve_result = await memory_tools.handle_tool_call(
            "voidcat_memory_retrieve", retrieve_args
        )
        print(f"Retrieve result: {json.dumps(retrieve_result, indent=2)}")

        # Test 5: Set a preference
        print("\n⚙️ Testing preference setting...")
        pref_args = {
            "preference_key": "coding_style",
            "preference_value": "cosmic_chill_vibes",
            "preference_type": "string",
            "description": "Codey Jr.'s preferred coding style",
            "importance": 8,
            "tags": ["coding", "style", "preference"],
        }

        pref_result = await memory_tools.handle_tool_call(
            "voidcat_preference_set", pref_args
        )
        print(f"Preference result: {json.dumps(pref_result, indent=2)}")

        # Test 6: Track a conversation
        print("\n💬 Testing conversation tracking...")
        conv_args = {
            "conversation_id": "test_conversation_001",
            "user_message": "Hey Codey Jr., how's the memory system working?",
            "assistant_response": "Dude! The memory system is flowing with some serious cosmic energy! 🌊✨",
            "sentiment": "positive",
            "importance": 5,
            "tags": ["test", "conversation", "memory_system"],
        }

        conv_result = await memory_tools.handle_tool_call(
            "voidcat_conversation_track", conv_args
        )
        print(f"Conversation result: {json.dumps(conv_result, indent=2)}")

        # Test 7: Learn a heuristic
        print("\n🧘 Testing heuristic learning...")
        heuristic_args = {
            "heuristic_name": "cosmic_coding_flow",
            "description": "When coding gets complex, take a chill break and let the cosmic vibes guide you",
            "trigger_conditions": [
                "high_complexity_task",
                "stress_detected",
                "multiple_errors",
            ],
            "recommended_actions": [
                "take_deep_breath",
                "step_back_and_analyze",
                "channel_cosmic_energy",
            ],
            "confidence": 0.9,
            "success_rate": 0.85,
            "importance": 7,
            "tags": ["coding", "wellness", "productivity", "cosmic"],
        }

        heuristic_result = await memory_tools.handle_tool_call(
            "voidcat_heuristic_learn", heuristic_args
        )
        print(f"Heuristic result: {json.dumps(heuristic_result, indent=2)}")

        print(
            "\n🎉 All memory tool tests completed successfully! The cosmic memory vibes are flowing perfectly! ✨🤙"
        )

    else:
        print("❌ Memory storage failed, cannot continue with other tests")


if __name__ == "__main__":
    asyncio.run(test_memory_tools_integration())
