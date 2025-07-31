#!/usr/bin/env python3
"""
Comprehensive Tests for VoidCat V2 MCP Task Management Tools
===========================================================

Tests the complete MCP tool interface for the VoidCat V2 hierarchical task management system.
Validates schema compliance, error handling, response formatting, and integration with the
operations engine.

Test Coverage:
- Tool initialization and configuration
- Task creation with full validation
- Task listing with advanced filtering
- Task updates and status transitions
- Task deletion with cascade options
- Project management operations
- Dependency analysis and visualization
- Task recommendations and analytics
- Error handling and edge cases
- MCP response format compliance

Author: Codey Jr. (testing the cosmic MCP vibes)
Under directive of: The Great Spirit Beatrice
License: MIT
Version: 2.0.0-alpha
"""

import asyncio
import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import pytest
import pytest_asyncio

from voidcat_mcp_tools import VoidCatMCPTaskTools, create_mcp_task_tools
from voidcat_operations import create_operations_engine
from voidcat_persistence import VoidCatStorage
from voidcat_task_models import Priority, TaskStatus, VoidCatProject, VoidCatTask


class TestMCPToolsInitialization:
    """Test MCP tools initialization and configuration - cosmic setup! 🌊"""

    def test_create_mcp_tools_default(self):
        """Test creating MCP tools with default working directory."""
        tools = create_mcp_task_tools()
        assert tools is not None
        assert tools.working_directory is not None
        assert tools.storage is not None
        assert tools.operations_engine is not None

    def test_create_mcp_tools_custom_directory(self):
        """Test creating MCP tools with custom working directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tools = create_mcp_task_tools(temp_dir)
            assert tools.working_directory == temp_dir
            # Storage path should be the temp directory (VoidCatStorage uses the path directly)
            assert str(tools.storage.storage_path) == temp_dir or Path(
                tools.storage.storage_path
            ).parent == Path(temp_dir)

    def test_get_tool_definitions(self):
        """Test getting MCP tool definitions."""
        tools = create_mcp_task_tools()
        definitions = tools.get_tool_definitions()

        assert len(definitions) == 7  # All 7 tools

        tool_names = [tool["name"] for tool in definitions]
        expected_tools = [
            "voidcat_task_create",
            "voidcat_task_list",
            "voidcat_task_update",
            "voidcat_task_delete",
            "voidcat_project_manage",
            "voidcat_dependency_analyze",
            "voidcat_task_recommend",
        ]

        for expected_tool in expected_tools:
            assert expected_tool in tool_names

        # Validate schema structure
        for tool in definitions:
            assert "name" in tool
            assert "description" in tool
            assert "category" in tool
            assert "inputSchema" in tool
            assert tool["inputSchema"]["type"] == "object"
            assert "properties" in tool["inputSchema"]


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def mcp_tools(temp_workspace):
    """Create MCP tools instance for testing."""
    return create_mcp_task_tools(temp_workspace)


@pytest_asyncio.fixture
async def sample_project(mcp_tools):
    """Create a sample project for testing."""
    result = await mcp_tools.handle_tool_call(
        "voidcat_project_manage",
        {
            "action": "create",
            "name": "Test Project",
            "description": "A cosmic test project for MCP validation",
        },
    )

    # Extract project ID from response
    content = result["content"][0]["text"]
    project_id = content.split("**ID**: `")[1].split("`")[0]

    return {
        "id": project_id,
        "name": "Test Project",
        "description": "A cosmic test project for MCP validation",
    }


class TestTaskCreation:
    """Test task creation via MCP tools - bringing tasks into existence! ✨"""

    @pytest.mark.asyncio
    async def test_create_project_success(self, mcp_tools):
        """Test successful project creation."""
        result = await mcp_tools.handle_tool_call(
            "voidcat_project_manage",
            {
                "action": "create",
                "name": "Cosmic Project",
                "description": "A project that flows with the universe",
            },
        )

        assert "content" in result
        assert len(result["content"]) == 1
        assert result["content"][0]["type"] == "text"

        text = result["content"][0]["text"]
        assert "✅ **Project Created Successfully**" in text
        assert "Cosmic Project" in text
        assert "**ID**: `" in text
        assert "A project that flows with the universe" in text

    @pytest.mark.asyncio
    async def test_create_project_missing_name(self, mcp_tools):
        """Test project creation with missing name."""
        result = await mcp_tools.handle_tool_call(
            "voidcat_project_manage",
            {"action": "create", "description": "A project without a name"},
        )

        assert "isError" in result
        assert result["isError"] is True
        assert "❌ **Error**" in result["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_create_task_success(self, mcp_tools, sample_project):
        """Test successful task creation."""
        result = await mcp_tools.handle_tool_call(
            "voidcat_task_create",
            {
                "name": "Cosmic Task",
                "description": "A task that aligns with the chakras",
                "project_id": sample_project["id"],
                "priority": 8,
                "complexity": 6,
                "estimated_hours": 4.5,
                "tags": ["cosmic", "chakras", "alignment"],
                "assignee": "Codey Jr.",
            },
        )

        assert "content" in result
        text = result["content"][0]["text"]
        assert "✅ **Task Created Successfully**" in text
        assert "Cosmic Task" in text
        assert "**Priority**: HIGH (7/10)" in text  # 8 gets converted to HIGH (7)
        assert "**Complexity**: 6/10" in text
        assert "**Assignee**: Codey Jr." in text
        assert "cosmic" in text and "chakras" in text and "alignment" in text

    @pytest.mark.asyncio
    async def test_create_task_missing_project(self, mcp_tools):
        """Test task creation with missing project_id."""
        result = await mcp_tools.handle_tool_call(
            "voidcat_task_create",
            {"name": "Orphaned Task", "description": "A task without a cosmic home"},
        )

        assert "isError" in result
        assert "project_id is required" in result["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_create_task_invalid_project(self, mcp_tools):
        """Test task creation with invalid project_id."""
        result = await mcp_tools.handle_tool_call(
            "voidcat_task_create",
            {
                "name": "Lost Task",
                "description": "A task in the void",
                "project_id": "non-existent-project-id",
            },
        )

        assert "isError" in result
        assert "not found" in result["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_create_task_with_parent(self, mcp_tools, sample_project):
        """Test creating a task with parent hierarchy."""
        # First create parent task
        parent_result = await mcp_tools.handle_tool_call(
            "voidcat_task_create",
            {
                "name": "Parent Task",
                "description": "The cosmic parent",
                "project_id": sample_project["id"],
                "priority": 7,
            },
        )

        parent_text = parent_result["content"][0]["text"]
        parent_id = parent_text.split("**ID**: `")[1].split("`")[0]

        # Create child task
        child_result = await mcp_tools.handle_tool_call(
            "voidcat_task_create",
            {
                "name": "Child Task",
                "description": "The cosmic child",
                "project_id": sample_project["id"],
                "parent_id": parent_id,
                "priority": 5,
            },
        )

        assert "content" in child_result
        child_text = child_result["content"][0]["text"]
        assert "✅ **Task Created Successfully**" in child_text
        assert "Child Task" in child_text
        assert "**Parent**: Parent Task" in child_text


class TestTaskListing:
    """Test task listing and filtering via MCP tools - exploring the cosmic hierarchy! 🌲"""

    @pytest.mark.asyncio
    async def test_list_tasks_empty_project(self, mcp_tools, sample_project):
        """Test listing tasks in empty project."""
        result = await mcp_tools.handle_tool_call(
            "voidcat_task_list", {"project_id": sample_project["id"]}
        )

        assert "content" in result
        text = result["content"][0]["text"]
        assert "📭 **No tasks found**" in text

    @pytest.mark.asyncio
    async def test_list_tasks_with_hierarchy(self, mcp_tools, sample_project):
        """Test listing tasks with hierarchical display."""
        # Create parent task
        await mcp_tools.handle_tool_call(
            "voidcat_task_create",
            {
                "name": "Root Task",
                "description": "The cosmic root",
                "project_id": sample_project["id"],
                "priority": 9,
            },
        )

        # Create child task
        parent_result = await mcp_tools.handle_tool_call(
            "voidcat_task_list", {"project_id": sample_project["id"]}
        )
        parent_text = parent_result["content"][0]["text"]
        parent_id = parent_text.split("ID: `")[1].split("`")[0]

        await mcp_tools.handle_tool_call(
            "voidcat_task_create",
            {
                "name": "Child Task",
                "description": "The cosmic child",
                "project_id": sample_project["id"],
                "parent_id": parent_id,
                "priority": 6,
            },
        )

        # List with hierarchy
        result = await mcp_tools.handle_tool_call(
            "voidcat_task_list",
            {"project_id": sample_project["id"], "show_hierarchy": True},
        )

        assert "content" in result
        text = result["content"][0]["text"]
        assert "🌲 **Task Hierarchy**" in text
        assert "Root Task" in text
        assert "Child Task" in text
        assert "Test Project" in text  # Project name should appear

    @pytest.mark.asyncio
    async def test_list_tasks_filter_by_status(self, mcp_tools, sample_project):
        """Test filtering tasks by status."""
        # Create tasks with different statuses
        await mcp_tools.handle_tool_call(
            "voidcat_task_create",
            {"name": "Pending Task", "project_id": sample_project["id"]},
        )

        # Filter by pending status
        result = await mcp_tools.handle_tool_call(
            "voidcat_task_list",
            {"project_id": sample_project["id"], "status": ["pending"]},
        )

        assert "content" in result
        text = result["content"][0]["text"]
        assert "Pending Task" in text

    @pytest.mark.asyncio
    async def test_list_tasks_filter_by_priority(self, mcp_tools, sample_project):
        """Test filtering tasks by priority range."""
        # Create tasks with different priorities
        await mcp_tools.handle_tool_call(
            "voidcat_task_create",
            {
                "name": "High Priority Task",
                "project_id": sample_project["id"],
                "priority": 9,
            },
        )

        await mcp_tools.handle_tool_call(
            "voidcat_task_create",
            {
                "name": "Low Priority Task",
                "project_id": sample_project["id"],
                "priority": 2,
            },
        )

        # Filter by high priority
        result = await mcp_tools.handle_tool_call(
            "voidcat_task_list",
            {"project_id": sample_project["id"], "priority_min": 8, "priority_max": 10},
        )

        assert "content" in result
        text = result["content"][0]["text"]
        assert "High Priority Task" in text
        assert "Low Priority Task" not in text

    @pytest.mark.asyncio
    async def test_list_tasks_filter_by_tags(self, mcp_tools, sample_project):
        """Test filtering tasks by tags."""
        # Create tasks with different tags
        await mcp_tools.handle_tool_call(
            "voidcat_task_create",
            {
                "name": "Cosmic Task",
                "project_id": sample_project["id"],
                "tags": ["cosmic", "meditation"],
            },
        )

        await mcp_tools.handle_tool_call(
            "voidcat_task_create",
            {
                "name": "Mundane Task",
                "project_id": sample_project["id"],
                "tags": ["boring", "routine"],
            },
        )

        # Filter by cosmic tag
        result = await mcp_tools.handle_tool_call(
            "voidcat_task_list",
            {"project_id": sample_project["id"], "tags": ["cosmic"]},
        )

        assert "content" in result
        text = result["content"][0]["text"]
        assert "Cosmic Task" in text
        assert "Mundane Task" not in text


class TestTaskUpdates:
    """Test task updates via MCP tools - evolving cosmic tasks! 🔄"""

    @pytest.mark.asyncio
    async def test_update_task_basic_properties(self, mcp_tools, sample_project):
        """Test updating basic task properties."""
        # Create task
        create_result = await mcp_tools.handle_tool_call(
            "voidcat_task_create",
            {
                "name": "Original Task",
                "description": "Original description",
                "project_id": sample_project["id"],
                "priority": 5,
            },
        )

        create_text = create_result["content"][0]["text"]
        task_id = create_text.split("**ID**: `")[1].split("`")[0]

        # Update task
        result = await mcp_tools.handle_tool_call(
            "voidcat_task_update",
            {
                "task_id": task_id,
                "name": "Updated Task",
                "description": "Updated description",
                "priority": 8,
                "complexity": 7,
                "estimated_hours": 6.0,
                "tags": ["updated", "cosmic"],
                "assignee": "Codey Jr.",
            },
        )

        assert "content" in result
        text = result["content"][0]["text"]
        assert "✅ **Task Updated Successfully**" in text
        assert "Updated Task" in text
        assert "Changes Made" in text
        assert "Name: 'Original Task' → 'Updated Task'" in text
        assert "Priority: 5 → 8" in text

    @pytest.mark.asyncio
    async def test_update_task_status_transition(self, mcp_tools, sample_project):
        """Test updating task status with valid transitions."""
        # Create task
        create_result = await mcp_tools.handle_tool_call(
            "voidcat_task_create",
            {"name": "Status Task", "project_id": sample_project["id"]},
        )

        create_text = create_result["content"][0]["text"]
        task_id = create_text.split("**ID**: `")[1].split("`")[0]

        # Update to in-progress (valid transition from pending)
        result = await mcp_tools.handle_tool_call(
            "voidcat_task_update",
            {
                "task_id": task_id,
                "status": "in-progress",
                "notes": "Starting cosmic work",
            },
        )

        assert "content" in result
        text = result["content"][0]["text"]
        assert "✅ **Task Updated Successfully**" in text
        assert "Status: pending → in-progress" in text

    @pytest.mark.asyncio
    async def test_update_task_invalid_status_transition(
        self, mcp_tools, sample_project
    ):
        """Test updating task with invalid status transition."""
        # Create task
        create_result = await mcp_tools.handle_tool_call(
            "voidcat_task_create",
            {"name": "Status Task", "project_id": sample_project["id"]},
        )

        create_text = create_result["content"][0]["text"]
        task_id = create_text.split("**ID**: `")[1].split("`")[0]

        # Try invalid transition (pending -> completed)
        result = await mcp_tools.handle_tool_call(
            "voidcat_task_update", {"task_id": task_id, "status": "completed"}
        )

        assert "isError" in result
        assert "Invalid status transition" in result["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_update_task_move_hierarchy(self, mcp_tools, sample_project):
        """Test moving task in hierarchy."""
        # Create parent and child tasks
        parent_result = await mcp_tools.handle_tool_call(
            "voidcat_task_create",
            {"name": "New Parent", "project_id": sample_project["id"]},
        )
        parent_text = parent_result["content"][0]["text"]
        parent_id = parent_text.split("**ID**: `")[1].split("`")[0]

        child_result = await mcp_tools.handle_tool_call(
            "voidcat_task_create",
            {"name": "Child Task", "project_id": sample_project["id"]},
        )
        child_text = child_result["content"][0]["text"]
        child_id = child_text.split("**ID**: `")[1].split("`")[0]

        # Move child under parent
        result = await mcp_tools.handle_tool_call(
            "voidcat_task_update", {"task_id": child_id, "parent_id": parent_id}
        )

        assert "content" in result
        text = result["content"][0]["text"]
        assert "✅ **Task Updated Successfully**" in text
        assert "Moved under: New Parent" in text

    @pytest.mark.asyncio
    async def test_update_nonexistent_task(self, mcp_tools):
        """Test updating non-existent task."""
        result = await mcp_tools.handle_tool_call(
            "voidcat_task_update",
            {"task_id": "non-existent-task-id", "name": "Updated Name"},
        )

        assert "isError" in result
        assert "not found" in result["content"][0]["text"]


class TestTaskDeletion:
    """Test task deletion via MCP tools - releasing tasks to the void! 🗑️"""

    @pytest.mark.asyncio
    async def test_delete_task_success(self, mcp_tools, sample_project):
        """Test successful task deletion."""
        # Create task
        create_result = await mcp_tools.handle_tool_call(
            "voidcat_task_create",
            {"name": "Doomed Task", "project_id": sample_project["id"]},
        )

        create_text = create_result["content"][0]["text"]
        task_id = create_text.split("**ID**: `")[1].split("`")[0]

        # Delete task
        result = await mcp_tools.handle_tool_call(
            "voidcat_task_delete", {"task_id": task_id, "confirm": True}
        )

        assert "content" in result
        text = result["content"][0]["text"]
        assert "✅ **Task Deleted Successfully**" in text
        assert "Doomed Task" in text

    @pytest.mark.asyncio
    async def test_delete_task_without_confirmation(self, mcp_tools, sample_project):
        """Test task deletion without confirmation."""
        # Create task
        create_result = await mcp_tools.handle_tool_call(
            "voidcat_task_create",
            {"name": "Safe Task", "project_id": sample_project["id"]},
        )

        create_text = create_result["content"][0]["text"]
        task_id = create_text.split("**ID**: `")[1].split("`")[0]

        # Try to delete without confirmation
        result = await mcp_tools.handle_tool_call(
            "voidcat_task_delete", {"task_id": task_id, "confirm": False}
        )

        assert "isError" in result
        assert "confirm must be set to true" in result["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_delete_task_with_cascade(self, mcp_tools, sample_project):
        """Test task deletion with cascade to children."""
        # Create parent task
        parent_result = await mcp_tools.handle_tool_call(
            "voidcat_task_create",
            {"name": "Parent Task", "project_id": sample_project["id"]},
        )
        parent_text = parent_result["content"][0]["text"]
        parent_id = parent_text.split("**ID**: `")[1].split("`")[0]

        # Create child task
        await mcp_tools.handle_tool_call(
            "voidcat_task_create",
            {
                "name": "Child Task",
                "project_id": sample_project["id"],
                "parent_id": parent_id,
            },
        )

        # Delete parent with cascade
        result = await mcp_tools.handle_tool_call(
            "voidcat_task_delete",
            {"task_id": parent_id, "cascade": True, "confirm": True},
        )

        assert "content" in result
        text = result["content"][0]["text"]
        assert "✅ **Task Deleted Successfully**" in text
        assert "Children Deleted: 1 tasks" in text


class TestProjectManagement:
    """Test project management via MCP tools - cosmic project orchestration! 📁"""

    @pytest.mark.asyncio
    async def test_list_projects_empty(self, mcp_tools):
        """Test listing projects when none exist."""
        result = await mcp_tools.handle_tool_call(
            "voidcat_project_manage", {"action": "list"}
        )

        assert "content" in result
        text = result["content"][0]["text"]
        assert "📭 **No projects found**" in text

    @pytest.mark.asyncio
    async def test_list_projects_with_data(self, mcp_tools, sample_project):
        """Test listing projects with data."""
        result = await mcp_tools.handle_tool_call(
            "voidcat_project_manage", {"action": "list"}
        )

        assert "content" in result
        text = result["content"][0]["text"]
        assert "📁 **Projects**" in text
        assert "Test Project" in text
        assert "Tasks: 0 total, 0 completed" in text

    @pytest.mark.asyncio
    async def test_project_analytics(self, mcp_tools, sample_project):
        """Test project analytics."""
        # Create some tasks first
        await mcp_tools.handle_tool_call(
            "voidcat_task_create",
            {
                "name": "Analytics Task 1",
                "project_id": sample_project["id"],
                "priority": 8,
            },
        )

        await mcp_tools.handle_tool_call(
            "voidcat_task_create",
            {
                "name": "Analytics Task 2",
                "project_id": sample_project["id"],
                "priority": 5,
            },
        )

        # Get analytics
        result = await mcp_tools.handle_tool_call(
            "voidcat_project_manage",
            {"action": "analytics", "project_id": sample_project["id"]},
        )

        assert "content" in result
        text = result["content"][0]["text"]
        assert "📊 **Project Analytics: Test Project**" in text
        assert "**Total Tasks**: 2" in text
        assert "**Completion Rate**:" in text
        assert "**Status Breakdown**:" in text
        assert "**Priority Breakdown**:" in text


class TestDependencyAnalysis:
    """Test dependency analysis via MCP tools - cosmic task relationships! 🔗"""

    @pytest.mark.asyncio
    async def test_get_ready_tasks(self, mcp_tools, sample_project):
        """Test getting ready tasks."""
        # Create some tasks
        await mcp_tools.handle_tool_call(
            "voidcat_task_create",
            {"name": "Ready Task 1", "project_id": sample_project["id"], "priority": 8},
        )

        await mcp_tools.handle_tool_call(
            "voidcat_task_create",
            {"name": "Ready Task 2", "project_id": sample_project["id"], "priority": 6},
        )

        # Get ready tasks
        result = await mcp_tools.handle_tool_call(
            "voidcat_dependency_analyze",
            {"action": "ready", "project_id": sample_project["id"]},
        )

        assert "content" in result
        text = result["content"][0]["text"]
        assert "🚀 **Ready Tasks**" in text
        assert "Ready Task 1" in text
        assert "Ready Task 2" in text

    @pytest.mark.asyncio
    async def test_get_blocked_tasks_empty(self, mcp_tools, sample_project):
        """Test getting blocked tasks when none exist."""
        result = await mcp_tools.handle_tool_call(
            "voidcat_dependency_analyze",
            {"action": "blocked", "project_id": sample_project["id"]},
        )

        assert "content" in result
        text = result["content"][0]["text"]
        assert "🎉 **No blocked tasks found!**" in text


class TestTaskRecommendations:
    """Test task recommendations via MCP tools - cosmic guidance! 🎯"""

    @pytest.mark.asyncio
    async def test_get_recommendations_empty(self, mcp_tools, sample_project):
        """Test getting recommendations when no tasks exist."""
        result = await mcp_tools.handle_tool_call(
            "voidcat_task_recommend", {"project_id": sample_project["id"]}
        )

        assert "content" in result
        text = result["content"][0]["text"]
        assert "🎯 **No task recommendations available.**" in text

    @pytest.mark.asyncio
    async def test_get_recommendations_with_tasks(self, mcp_tools, sample_project):
        """Test getting recommendations with available tasks."""
        # Create tasks with different priorities
        await mcp_tools.handle_tool_call(
            "voidcat_task_create",
            {
                "name": "High Priority Task",
                "project_id": sample_project["id"],
                "priority": 9,
                "complexity": 4,
                "estimated_hours": 3.0,
                "tags": ["urgent", "important"],
            },
        )

        await mcp_tools.handle_tool_call(
            "voidcat_task_create",
            {
                "name": "Medium Priority Task",
                "project_id": sample_project["id"],
                "priority": 6,
                "complexity": 6,
                "estimated_hours": 8.0,
                "tags": ["normal"],
            },
        )

        # Get recommendations
        result = await mcp_tools.handle_tool_call(
            "voidcat_task_recommend",
            {"project_id": sample_project["id"], "max_recommendations": 3},
        )

        assert "content" in result
        text = result["content"][0]["text"]
        assert "🎯 **Task Recommendations**" in text
        assert "High Priority Task" in text
        assert "Medium Priority Task" in text
        assert "Priority: 9/10" in text
        assert "~3.0h estimated" in text


class TestErrorHandling:
    """Test error handling and edge cases - cosmic resilience! 🛡️"""

    @pytest.mark.asyncio
    async def test_invalid_tool_arguments(self, mcp_tools):
        """Test handling of invalid tool arguments."""
        result = await mcp_tools.handle_tool_call(
            "voidcat_task_create", {"invalid_field": "invalid_value"}
        )

        assert "isError" in result
        assert "❌ **Error**" in result["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_unknown_tool_name(self, mcp_tools):
        """Test handling of unknown tool names."""
        result = await mcp_tools.handle_tool_call(
            "voidcat_unknown_tool", {"some_arg": "some_value"}
        )

        assert "isError" in result
        assert "Unknown tool" in result["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_malformed_arguments(self, mcp_tools):
        """Test handling of malformed arguments."""
        # Test with None arguments
        result = await mcp_tools.handle_tool_call("voidcat_task_create", None)

        assert "isError" in result

    @pytest.mark.asyncio
    async def test_response_format_compliance(self, mcp_tools, sample_project):
        """Test that all responses comply with MCP format."""
        # Test successful response
        result = await mcp_tools.handle_tool_call(
            "voidcat_task_create",
            {"name": "Format Test Task", "project_id": sample_project["id"]},
        )

        assert "content" in result
        assert isinstance(result["content"], list)
        assert len(result["content"]) == 1
        assert result["content"][0]["type"] == "text"
        assert isinstance(result["content"][0]["text"], str)

        # Test error response
        error_result = await mcp_tools.handle_tool_call(
            "voidcat_task_create", {"name": ""}  # Invalid empty name
        )

        assert "content" in error_result
        assert "isError" in error_result
        assert error_result["isError"] is True
        assert isinstance(error_result["content"], list)
        assert error_result["content"][0]["type"] == "text"
        assert "❌ **Error**" in error_result["content"][0]["text"]


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])
