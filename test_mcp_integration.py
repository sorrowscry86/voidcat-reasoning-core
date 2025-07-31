#!/usr/bin/env python3
"""
VoidCat V2 MCP Server Integration Tests
======================================

Comprehensive integration tests for the complete VoidCat V2 MCP server including
task management tools, reasoning engine, and all MCP protocol compliance.

Test Coverage:
- MCP server initialization with task tools
- Tool discovery and schema validation
- Task management workflow integration
- Error handling and response formatting
- Protocol compliance validation
- End-to-end task lifecycle testing

Author: Codey Jr. (testing the cosmic integration vibes)
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

from mcp_server import VoidCatMCPServer
from voidcat_mcp_tools import create_mcp_task_tools


class TestMCPServerIntegration:
    """Test complete MCP server integration with task management - cosmic harmony! 🌊"""

    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest_asyncio.fixture
    async def mcp_server(self, temp_workspace):
        """Create MCP server instance for testing."""
        server = VoidCatMCPServer()
        await server.initialize()
        return server

    @pytest.mark.asyncio
    async def test_server_initialization(self, mcp_server):
        """Test MCP server initializes with task tools."""
        assert mcp_server is not None
        assert mcp_server.engine is not None
        assert mcp_server.task_tools is not None
        assert len(mcp_server.tools) > 0

        # Check that task management tools are included
        tool_names = [tool.name for tool in mcp_server.tools]
        expected_task_tools = [
            "voidcat_task_create",
            "voidcat_task_list",
            "voidcat_task_update",
            "voidcat_task_delete",
            "voidcat_project_manage",
            "voidcat_dependency_analyze",
            "voidcat_task_recommend",
        ]

        for expected_tool in expected_task_tools:
            assert expected_tool in tool_names

    @pytest.mark.asyncio
    async def test_tool_discovery(self, mcp_server):
        """Test MCP tool discovery protocol."""
        # Simulate tools/list request
        await mcp_server.handle_list_tools(request_id="test-001")

        # Verify tools are properly registered
        assert len(mcp_server.tools) >= 13  # Original tools + 7 task tools

    @pytest.mark.asyncio
    async def test_project_creation_workflow(self, mcp_server):
        """Test complete project creation workflow via MCP."""
        # Create project
        project_result = await mcp_server.handle_call_tool(
            "voidcat_project_manage",
            {
                "action": "create",
                "name": "Integration Test Project",
                "description": "Testing the cosmic MCP integration",
            },
            "test-project-001",
        )

        # Verify project creation response format
        assert project_result is None  # handle_call_tool sends response directly

        # List projects to verify creation
        list_result = await mcp_server.handle_call_tool(
            "voidcat_project_manage", {"action": "list"}, "test-project-002"
        )

        assert list_result is None  # Response sent directly

    @pytest.mark.asyncio
    async def test_task_creation_workflow(self, mcp_server):
        """Test complete task creation workflow via MCP."""
        # First create a project
        await mcp_server.handle_call_tool(
            "voidcat_project_manage",
            {
                "action": "create",
                "name": "Task Test Project",
                "description": "For testing task creation",
            },
            "test-task-project-001",
        )

        # Get project ID (would normally be extracted from response)
        # For testing, we'll create a task tools instance to get the project
        task_tools = create_mcp_task_tools()
        projects = task_tools.storage.list_projects()
        test_project = next(
            (p for p in projects if p.name == "Task Test Project"), None
        )
        assert test_project is not None

        # Create task
        await mcp_server.handle_call_tool(
            "voidcat_task_create",
            {
                "name": "Integration Test Task",
                "description": "Testing task creation via MCP",
                "project_id": test_project.id,
                "priority": 8,
                "complexity": 6,
                "tags": ["integration", "test", "cosmic"],
            },
            "test-task-001",
        )

        # List tasks to verify creation
        await mcp_server.handle_call_tool(
            "voidcat_task_list", {"project_id": test_project.id}, "test-task-list-001"
        )

    @pytest.mark.asyncio
    async def test_task_hierarchy_workflow(self, mcp_server):
        """Test hierarchical task creation via MCP."""
        # Create project
        await mcp_server.handle_call_tool(
            "voidcat_project_manage",
            {
                "action": "create",
                "name": "Hierarchy Test Project",
                "description": "For testing task hierarchy",
            },
            "test-hierarchy-project-001",
        )

        # Get project ID
        task_tools = create_mcp_task_tools()
        projects = task_tools.storage.list_projects()
        test_project = next(
            (p for p in projects if p.name == "Hierarchy Test Project"), None
        )
        assert test_project is not None

        # Create parent task
        await mcp_server.handle_call_tool(
            "voidcat_task_create",
            {
                "name": "Parent Task",
                "description": "The cosmic parent",
                "project_id": test_project.id,
                "priority": 9,
            },
            "test-parent-001",
        )

        # Get parent task ID
        tasks = task_tools.storage.list_tasks(project_id=test_project.id)
        parent_task = next((t for t in tasks if t.name == "Parent Task"), None)
        assert parent_task is not None

        # Create child task
        await mcp_server.handle_call_tool(
            "voidcat_task_create",
            {
                "name": "Child Task",
                "description": "The cosmic child",
                "project_id": test_project.id,
                "parent_id": parent_task.id,
                "priority": 6,
            },
            "test-child-001",
        )

        # List tasks with hierarchy
        await mcp_server.handle_call_tool(
            "voidcat_task_list",
            {"project_id": test_project.id, "show_hierarchy": True},
            "test-hierarchy-list-001",
        )

    @pytest.mark.asyncio
    async def test_task_update_workflow(self, mcp_server):
        """Test task update workflow via MCP."""
        # Create project and task
        await mcp_server.handle_call_tool(
            "voidcat_project_manage",
            {
                "action": "create",
                "name": "Update Test Project",
                "description": "For testing task updates",
            },
            "test-update-project-001",
        )

        task_tools = create_mcp_task_tools()
        projects = task_tools.storage.list_projects()
        test_project = next(
            (p for p in projects if p.name == "Update Test Project"), None
        )

        await mcp_server.handle_call_tool(
            "voidcat_task_create",
            {
                "name": "Update Test Task",
                "description": "Original description",
                "project_id": test_project.id,
                "priority": 5,
            },
            "test-update-task-001",
        )

        # Get task ID
        tasks = task_tools.storage.list_tasks(project_id=test_project.id)
        test_task = next((t for t in tasks if t.name == "Update Test Task"), None)

        # Update task
        await mcp_server.handle_call_tool(
            "voidcat_task_update",
            {
                "task_id": test_task.id,
                "name": "Updated Test Task",
                "description": "Updated description",
                "priority": 8,
                "status": "in-progress",
            },
            "test-update-001",
        )

    @pytest.mark.asyncio
    async def test_task_recommendations(self, mcp_server):
        """Test task recommendation workflow via MCP."""
        # Create project with multiple tasks
        await mcp_server.handle_call_tool(
            "voidcat_project_manage",
            {
                "action": "create",
                "name": "Recommendation Test Project",
                "description": "For testing recommendations",
            },
            "test-rec-project-001",
        )

        task_tools = create_mcp_task_tools()
        projects = task_tools.storage.list_projects()
        test_project = next(
            (p for p in projects if p.name == "Recommendation Test Project"), None
        )

        # Create multiple tasks with different priorities
        await mcp_server.handle_call_tool(
            "voidcat_task_create",
            {
                "name": "High Priority Task",
                "project_id": test_project.id,
                "priority": 9,
                "complexity": 4,
                "estimated_hours": 2.0,
            },
            "test-rec-task-001",
        )

        await mcp_server.handle_call_tool(
            "voidcat_task_create",
            {
                "name": "Medium Priority Task",
                "project_id": test_project.id,
                "priority": 6,
                "complexity": 7,
                "estimated_hours": 8.0,
            },
            "test-rec-task-002",
        )

        # Get recommendations
        await mcp_server.handle_call_tool(
            "voidcat_task_recommend",
            {"project_id": test_project.id, "max_recommendations": 3},
            "test-recommendations-001",
        )

    @pytest.mark.asyncio
    async def test_dependency_analysis(self, mcp_server):
        """Test dependency analysis workflow via MCP."""
        # Create project with tasks
        await mcp_server.handle_call_tool(
            "voidcat_project_manage",
            {
                "action": "create",
                "name": "Dependency Test Project",
                "description": "For testing dependencies",
            },
            "test-dep-project-001",
        )

        task_tools = create_mcp_task_tools()
        projects = task_tools.storage.list_projects()
        test_project = next(
            (p for p in projects if p.name == "Dependency Test Project"), None
        )

        # Create tasks
        await mcp_server.handle_call_tool(
            "voidcat_task_create",
            {"name": "Ready Task 1", "project_id": test_project.id, "priority": 8},
            "test-dep-task-001",
        )

        await mcp_server.handle_call_tool(
            "voidcat_task_create",
            {"name": "Ready Task 2", "project_id": test_project.id, "priority": 6},
            "test-dep-task-002",
        )

        # Analyze ready tasks
        await mcp_server.handle_call_tool(
            "voidcat_dependency_analyze",
            {"action": "ready", "project_id": test_project.id},
            "test-dep-ready-001",
        )

        # Analyze blocked tasks
        await mcp_server.handle_call_tool(
            "voidcat_dependency_analyze",
            {"action": "blocked", "project_id": test_project.id},
            "test-dep-blocked-001",
        )

    @pytest.mark.asyncio
    async def test_project_analytics(self, mcp_server):
        """Test project analytics workflow via MCP."""
        # Create project with tasks
        await mcp_server.handle_call_tool(
            "voidcat_project_manage",
            {
                "action": "create",
                "name": "Analytics Test Project",
                "description": "For testing analytics",
            },
            "test-analytics-project-001",
        )

        task_tools = create_mcp_task_tools()
        projects = task_tools.storage.list_projects()
        test_project = next(
            (p for p in projects if p.name == "Analytics Test Project"), None
        )

        # Create tasks with different properties
        await mcp_server.handle_call_tool(
            "voidcat_task_create",
            {
                "name": "Analytics Task 1",
                "project_id": test_project.id,
                "priority": 9,
                "complexity": 5,
            },
            "test-analytics-task-001",
        )

        await mcp_server.handle_call_tool(
            "voidcat_task_create",
            {
                "name": "Analytics Task 2",
                "project_id": test_project.id,
                "priority": 6,
                "complexity": 8,
            },
            "test-analytics-task-002",
        )

        # Get project analytics
        await mcp_server.handle_call_tool(
            "voidcat_project_manage",
            {"action": "analytics", "project_id": test_project.id},
            "test-analytics-001",
        )

    @pytest.mark.asyncio
    async def test_error_handling(self, mcp_server):
        """Test error handling in MCP integration."""
        # Test invalid tool name
        await mcp_server.handle_call_tool(
            "voidcat_invalid_tool", {"some_arg": "some_value"}, "test-error-001"
        )

        # Test invalid arguments
        await mcp_server.handle_call_tool(
            "voidcat_task_create", {"invalid_field": "invalid_value"}, "test-error-002"
        )

        # Test missing required arguments
        await mcp_server.handle_call_tool(
            "voidcat_project_manage",
            {"action": "create"},  # Missing name
            "test-error-003",
        )

    @pytest.mark.asyncio
    async def test_mixed_workflow(self, mcp_server):
        """Test mixed workflow combining reasoning and task management."""
        # Create project
        await mcp_server.handle_call_tool(
            "voidcat_project_manage",
            {
                "action": "create",
                "name": "Mixed Workflow Project",
                "description": "Combining reasoning and task management",
            },
            "test-mixed-project-001",
        )

        # Use reasoning engine
        await mcp_server.handle_call_tool(
            "voidcat_query",
            {
                "query": "What are the key principles of task management?",
                "context_depth": 2,
            },
            "test-mixed-query-001",
        )

        # Get engine status
        await mcp_server.handle_call_tool(
            "voidcat_status", {"detailed": True}, "test-mixed-status-001"
        )

        # Analyze knowledge base
        await mcp_server.handle_call_tool(
            "voidcat_analyze_knowledge",
            {"analysis_type": "summary"},
            "test-mixed-knowledge-001",
        )


class TestMCPProtocolCompliance:
    """Test MCP protocol compliance - cosmic standards! 📋"""

    @pytest_asyncio.fixture
    async def mcp_server(self):
        """Create MCP server instance for testing."""
        server = VoidCatMCPServer()
        await server.initialize()
        return server

    @pytest.mark.asyncio
    async def test_tool_schema_compliance(self, mcp_server):
        """Test that all tools have compliant schemas."""
        for tool in mcp_server.tools:
            # Validate required fields
            assert hasattr(tool, "name")
            assert hasattr(tool, "description")
            assert hasattr(tool, "inputSchema")

            # Validate schema structure
            schema = tool.inputSchema
            assert isinstance(schema, dict)
            assert schema.get("type") == "object"
            assert "properties" in schema

            # Validate properties
            properties = schema["properties"]
            assert isinstance(properties, dict)

            for prop_name, prop_schema in properties.items():
                assert isinstance(prop_schema, dict)
                assert "type" in prop_schema
                assert "description" in prop_schema

    @pytest.mark.asyncio
    async def test_response_format_compliance(self, mcp_server):
        """Test that all responses follow MCP format."""
        # This would require capturing actual responses
        # For now, we verify the server can handle requests without crashing

        # Test various tool calls
        test_calls = [
            ("voidcat_status", {}),
            ("voidcat_project_manage", {"action": "list"}),
            ("voidcat_task_recommend", {"project_id": "non-existent"}),
        ]

        for tool_name, args in test_calls:
            try:
                await mcp_server.handle_call_tool(tool_name, args, f"test-{tool_name}")
            except Exception as e:
                # Should not raise unhandled exceptions
                pytest.fail(f"Tool {tool_name} raised unhandled exception: {e}")


if __name__ == "__main__":
    # Run the integration tests
    pytest.main([__file__, "-v", "--tb=short"])
