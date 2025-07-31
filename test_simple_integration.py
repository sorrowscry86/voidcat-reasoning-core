#!/usr/bin/env python3
"""
Simple VoidCat V2 MCP Integration Test
=====================================

Quick validation that our MCP tools integration is working properly.
"""

import shutil
import tempfile

import pytest

from voidcat_mcp_tools import create_mcp_task_tools


def test_mcp_tools_creation():
    """Test that MCP tools can be created successfully."""
    with tempfile.TemporaryDirectory() as temp_dir:
        tools = create_mcp_task_tools(temp_dir)
        assert tools is not None
        assert tools.storage is not None
        assert tools.operations_engine is not None


def test_tool_definitions():
    """Test that tool definitions are properly formatted."""
    with tempfile.TemporaryDirectory() as temp_dir:
        tools = create_mcp_task_tools(temp_dir)
        definitions = tools.get_tool_definitions()

        assert len(definitions) == 7

        expected_tools = [
            "voidcat_task_create",
            "voidcat_task_list",
            "voidcat_task_update",
            "voidcat_task_delete",
            "voidcat_project_manage",
            "voidcat_dependency_analyze",
            "voidcat_task_recommend",
        ]

        tool_names = [tool["name"] for tool in definitions]
        for expected_tool in expected_tools:
            assert expected_tool in tool_names


@pytest.mark.asyncio
async def test_project_creation():
    """Test project creation via MCP tools."""
    with tempfile.TemporaryDirectory() as temp_dir:
        tools = create_mcp_task_tools(temp_dir)

        result = await tools.handle_tool_call(
            "voidcat_project_manage",
            {
                "action": "create",
                "name": "Test Project",
                "description": "A test project",
            },
        )

        assert "content" in result
        assert "✅ **Project Created Successfully**" in result["content"][0]["text"]


@pytest.mark.asyncio
async def test_task_creation():
    """Test task creation via MCP tools."""
    with tempfile.TemporaryDirectory() as temp_dir:
        tools = create_mcp_task_tools(temp_dir)

        # Create project first
        project_result = await tools.handle_tool_call(
            "voidcat_project_manage",
            {
                "action": "create",
                "name": "Task Test Project",
                "description": "For testing tasks",
            },
        )

        # Extract project ID
        project_text = project_result["content"][0]["text"]
        project_id = project_text.split("**ID**: `")[1].split("`")[0]

        # Create task
        task_result = await tools.handle_tool_call(
            "voidcat_task_create",
            {
                "name": "Test Task",
                "description": "A test task",
                "project_id": project_id,
                "priority": 7,
            },
        )

        assert "content" in task_result
        assert "✅ **Task Created Successfully**" in task_result["content"][0]["text"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
