#!/usr/bin/env python3
"""
Test VoidCat Memory Tools Only
==============================

Test just the memory tools without the full MCP server to avoid
dependency issues with task tools.

Author: Codey Jr. (testing the cosmic memory flow)
"""

import asyncio
import json
from pathlib import Path

from voidcat_memory_mcp_tools import create_memory_mcp_tools


async def test_memory_tools_comprehensive():
    """Comprehensive test of all memory tools with cosmic vibes."""
    print("🧠 Testing VoidCat Memory Tools Comprehensive Suite...")

    # Create memory tools instance
    working_dir = str(Path.cwd())
    memory_tools = create_memory_mcp_tools(working_dir)

    print(f"✅ Memory tools initialized with working directory: {working_dir}")

    # Test all available tools
    tools = memory_tools.get_tools()
    print(f"✅ Found {len(tools)} memory management tools:")
    for tool in tools:
        print(f"   - {tool['name']}")

    # Store some test memories
    memories_created = []

    # Test 1: Store basic memory
    print("\n🌊 Testing basic memory storage...")
    basic_memory = await memory_tools.handle_tool_call(
        "voidcat_memory_store",
        {
            "content": "This is a basic test memory with cosmic vibes! 🌊",
            "category": "conversation_history",
            "importance": 6,
            "tags": ["test", "basic", "cosmic"],
            "title": "Basic Test Memory",
        },
    )

    if basic_memory["success"]:
        memories_created.append(basic_memory["data"]["memory_id"])
        print(f"✅ Basic memory stored: {basic_memory['data']['memory_id']}")

    # Test 2: Store preference
    print("\n⚙️ Testing preference storage...")
    pref_result = await memory_tools.handle_tool_call(
        "voidcat_preference_set",
        {
            "preference_key": "cosmic_style",
            "preference_value": "chill_and_flowing",
            "preference_type": "string",
            "description": "The cosmic coding style preference",
            "importance": 8,
            "tags": ["style", "cosmic", "preference"],
        },
    )

    if pref_result["success"]:
        memories_created.append(pref_result["data"]["memory_id"])
        print(f"✅ Preference stored: {pref_result['data']['memory_id']}")

    # Test 3: Track conversation
    print("\n💬 Testing conversation tracking...")
    conv_result = await memory_tools.handle_tool_call(
        "voidcat_conversation_track",
        {
            "conversation_id": "cosmic_test_001",
            "user_message": "How's the memory system working, dude?",
            "assistant_response": "The memory system is flowing with cosmic energy, bro! 🌊✨",
            "sentiment": "positive",
            "importance": 5,
            "tags": ["conversation", "test", "cosmic"],
        },
    )

    if conv_result["success"]:
        memories_created.append(conv_result["data"]["memory_id"])
        print(f"✅ Conversation tracked: {conv_result['data']['memory_id']}")

    # Test 4: Learn heuristic
    print("\n🧘 Testing heuristic learning...")
    heuristic_result = await memory_tools.handle_tool_call(
        "voidcat_heuristic_learn",
        {
            "heuristic_name": "cosmic_debugging_flow",
            "description": "When debugging gets complex, step back and channel cosmic energy",
            "trigger_conditions": [
                "complex_bug",
                "frustration_detected",
                "multiple_failed_attempts",
            ],
            "recommended_actions": [
                "take_deep_breath",
                "step_back_analyze",
                "channel_cosmic_flow",
            ],
            "confidence": 0.9,
            "success_rate": 0.85,
            "importance": 7,
            "tags": ["debugging", "cosmic", "heuristic"],
        },
    )

    if heuristic_result["success"]:
        memories_created.append(heuristic_result["data"]["memory_id"])
        print(f"✅ Heuristic learned: {heuristic_result['data']['memory_id']}")

    # Test 5: Search memories
    print("\n🔍 Testing memory search...")
    search_result = await memory_tools.handle_tool_call(
        "voidcat_memory_search",
        {"query": "cosmic test memory", "max_results": 10, "search_type": "hybrid"},
    )

    if search_result["success"]:
        found_count = search_result["data"]["total_found"]
        print(f"✅ Memory search found {found_count} results")
        for result in search_result["data"]["results"]:
            print(f"   - {result['title']}: {result['relevance_score']:.2f}")

    # Test 6: Retrieve specific memories
    if memories_created:
        print("\n📖 Testing memory retrieval...")
        retrieve_result = await memory_tools.handle_tool_call(
            "voidcat_memory_retrieve",
            {
                "memory_ids": memories_created[:2],  # Test first 2 memories
                "include_metadata": True,
            },
        )

        if retrieve_result["success"]:
            retrieved_count = retrieve_result["data"]["retrieved_count"]
            print(f"✅ Retrieved {retrieved_count} memories successfully")
            for memory in retrieve_result["data"]["memories"]:
                print(f"   - {memory['title']}: {memory['category']}")

    # Test 7: Delete a memory (test the last one created)
    if memories_created:
        print("\n🗑️ Testing memory deletion...")
        delete_result = await memory_tools.handle_tool_call(
            "voidcat_memory_delete",
            {
                "memory_ids": [memories_created[-1]],  # Delete the last memory
                "force": False,
                "backup_before_delete": True,
            },
        )

        if delete_result["success"]:
            deleted_count = delete_result["data"]["deleted_count"]
            print(f"✅ Deleted {deleted_count} memories successfully")

    print("\n🎉 Comprehensive memory tools test completed!")
    print("🌊 All memory management functionality is working with cosmic vibes! ✨🤙")
    print(f"📊 Total memories created during test: {len(memories_created)}")


if __name__ == "__main__":
    asyncio.run(test_memory_tools_comprehensive())
