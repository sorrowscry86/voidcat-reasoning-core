#!/usr/bin/env python3
"""
VoidCat V2 MCP Server End-to-End Tests
=====================================

Comprehensive E2E tests for the MCP (Model Context Protocol) server including:
- MCP protocol compliance
- Task management tool integration
- Context-aware reasoning tools
- Memory and persistence operations
- Error handling and recovery
- Real MCP client simulation

This validates that the MCP server works end-to-end with actual MCP clients.

Author: Codey Jr. (channeling the MCP cosmic protocol vibes)
License: MIT
Version: 2.0.0-alpha
"""

import asyncio
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

# Add the current directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_server import VoidCatMCPServer
from voidcat_operations import VoidCatOperationsEngine
from voidcat_persistence import VoidCatStorage
from voidcat_task_models import Priority, TaskStatus, VoidCatProject, VoidCatTask


class TestMCPServerE2E:
    """End-to-End tests for the VoidCat MCP Server - cosmic protocol harmony! 🌊"""

    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mcp_server(self, temp_workspace):
        """Create an MCP server instance for testing."""
        server = VoidCatMCPServer(working_directory=temp_workspace)
        return server

    @pytest.fixture
    def sample_project(self, temp_workspace):
        """Create a sample project for testing."""
        storage = VoidCatStorage(temp_workspace)
        project = VoidCatProject(
            name="Test Project", description="A test project for E2E testing"
        )
        storage.save_project(project)
        return project

    @pytest.fixture
    def sample_task(self, temp_workspace, sample_project):
        """Create a sample task for testing."""
        storage = VoidCatStorage(temp_workspace)
        task = VoidCatTask(
            name="Test Task",
            description="A test task for E2E testing",
            project_id=sample_project.id,
            priority=Priority.HIGH,
            status=TaskStatus.PENDING,
        )
        storage.save_task(task)
        return task

    @pytest.mark.asyncio
    async def test_mcp_server_initialization(self, mcp_server):
        """Test MCP server initializes correctly."""
        assert mcp_server is not None
        assert mcp_server.working_directory is not None
        assert hasattr(mcp_server, "task_tools")
        assert hasattr(mcp_server, "context_integration")

    @pytest.mark.asyncio
    async def test_mcp_tools_list_available(self, mcp_server):
        """Test that MCP tools are properly registered and available."""
        # This would test the MCP tools/list endpoint
        tools = mcp_server.get_available_tools()

        expected_tools = [
            "voidcat_query",
            "voidcat_status",
            "voidcat_sequential_thinking",
            "voidcat_enhanced_query",
            "voidcat_analyze_knowledge",
            "voidcat_task_create",
            "voidcat_task_list",
            "voidcat_task_update",
            "voidcat_task_delete",
            "voidcat_project_manage",
            "voidcat_context_query",
            "voidcat_get_context",
            "voidcat_task_context",
            "voidcat_project_context",
        ]

        for tool in expected_tools:
            assert tool in tools

    @pytest.mark.asyncio
    async def test_voidcat_query_tool_e2e(self, mcp_server):
        """Test the voidcat_query tool end-to-end."""
        with patch("mcp_server.VoidCatEngine") as mock_engine:
            mock_instance = AsyncMock()
            mock_instance.query.return_value = "Test response from engine"
            mock_engine.return_value = mock_instance

            result = await mcp_server.handle_tool_call(
                "voidcat_query",
                {"query": "What are the core MCP primitives?", "model": "gpt-4o-mini"},
            )

            assert result["success"] is True
            assert "response" in result
            assert isinstance(result["response"], str)

    @pytest.mark.asyncio
    async def test_voidcat_status_tool_e2e(self, mcp_server):
        """Test the voidcat_status tool end-to-end."""
        with patch("mcp_server.VoidCatEngine") as mock_engine:
            mock_instance = AsyncMock()
            mock_instance.get_diagnostics.return_value = {"documents_loaded": 5}
            mock_engine.return_value = mock_instance

            result = await mcp_server.handle_tool_call("voidcat_status", {})

            assert result["success"] is True
            assert "status" in result
            assert "engine_ready" in result

    @pytest.mark.asyncio
    async def test_task_management_tools_e2e(self, mcp_server, sample_project):
        """Test task management tools end-to-end workflow."""
        # Test task creation
        create_result = await mcp_server.handle_tool_call(
            "voidcat_task_create",
            {
                "name": "E2E Test Task",
                "description": "Created during E2E testing",
                "project_id": sample_project.id,
                "priority": 8,
                "tags": ["e2e", "testing"],
            },
        )

        assert create_result["success"] is True
        assert "task_id" in create_result
        task_id = create_result["task_id"]

        # Test task listing
        list_result = await mcp_server.handle_tool_call(
            "voidcat_task_list", {"project_id": sample_project.id}
        )

        assert list_result["success"] is True
        assert "tasks" in list_result
        assert len(list_result["tasks"]) > 0

        # Test task update
        update_result = await mcp_server.handle_tool_call(
            "voidcat_task_update",
            {"task_id": task_id, "status": "in-progress", "priority": 9},
        )

        assert update_result["success"] is True

        # Test task deletion
        delete_result = await mcp_server.handle_tool_call(
            "voidcat_task_delete", {"task_id": task_id}
        )

        assert delete_result["success"] is True

    @pytest.mark.asyncio
    async def test_context_integration_tools_e2e(
        self, mcp_server, sample_project, sample_task
    ):
        """Test context integration tools end-to-end."""
        # Test context query
        context_result = await mcp_server.handle_tool_call(
            "voidcat_context_query",
            {"query": "What tasks are currently in progress?", "include_context": True},
        )

        assert context_result["success"] is True
        assert "response" in context_result

        # Test get context
        get_context_result = await mcp_server.handle_tool_call(
            "voidcat_get_context",
            {"context_type": "project", "project_id": sample_project.id},
        )

        assert get_context_result["success"] is True
        assert "context" in get_context_result

    @pytest.mark.asyncio
    async def test_project_management_e2e(self, mcp_server):
        """Test project management operations end-to-end."""
        # Test project creation
        create_result = await mcp_server.handle_tool_call(
            "voidcat_project_manage",
            {
                "operation": "create",
                "name": "E2E Test Project",
                "description": "Created during E2E testing",
            },
        )

        assert create_result["success"] is True
        assert "project_id" in create_result
        project_id = create_result["project_id"]

        # Test project listing
        list_result = await mcp_server.handle_tool_call(
            "voidcat_project_manage", {"operation": "list"}
        )

        assert list_result["success"] is True
        assert "projects" in list_result
        assert len(list_result["projects"]) > 0

        # Test project update
        update_result = await mcp_server.handle_tool_call(
            "voidcat_project_manage",
            {
                "operation": "update",
                "project_id": project_id,
                "name": "Updated E2E Test Project",
            },
        )

        assert update_result["success"] is True

        # Test project deletion
        delete_result = await mcp_server.handle_tool_call(
            "voidcat_project_manage", {"operation": "delete", "project_id": project_id}
        )

        assert delete_result["success"] is True

    @pytest.mark.asyncio
    async def test_error_handling_e2e(self, mcp_server):
        """Test error handling across all tools."""
        # Test invalid tool name
        result = await mcp_server.handle_tool_call("invalid_tool", {})
        assert result["success"] is False
        assert "error" in result

        # Test invalid parameters
        result = await mcp_server.handle_tool_call(
            "voidcat_task_create", {"invalid_param": "value"}
        )
        assert result["success"] is False
        assert "error" in result

        # Test missing required parameters
        result = await mcp_server.handle_tool_call("voidcat_task_create", {})
        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_concurrent_tool_calls_e2e(self, mcp_server, sample_project):
        """Test concurrent tool calls don't interfere with each other."""
        # Create multiple tasks concurrently
        tasks = []
        for i in range(5):
            task = mcp_server.handle_tool_call(
                "voidcat_task_create",
                {
                    "name": f"Concurrent Task {i}",
                    "description": f"Task {i} created concurrently",
                    "project_id": sample_project.id,
                    "priority": 5,
                },
            )
            tasks.append(task)

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)

        # All should succeed
        for result in results:
            assert result["success"] is True
            assert "task_id" in result

    @pytest.mark.asyncio
    async def test_data_persistence_e2e(self, mcp_server, sample_project):
        """Test that data persists across server operations."""
        # Create a task
        create_result = await mcp_server.handle_tool_call(
            "voidcat_task_create",
            {
                "name": "Persistence Test Task",
                "description": "Testing data persistence",
                "project_id": sample_project.id,
                "priority": 7,
            },
        )

        assert create_result["success"] is True
        task_id = create_result["task_id"]

        # Create a new server instance (simulating restart)
        new_server = VoidCatMCPServer(working_directory=mcp_server.working_directory)

        # Verify task still exists
        list_result = await new_server.handle_tool_call(
            "voidcat_task_list", {"project_id": sample_project.id}
        )

        assert list_result["success"] is True
        task_ids = [task["id"] for task in list_result["tasks"]]
        assert task_id in task_ids

    @pytest.mark.asyncio
    async def test_sequential_thinking_integration_e2e(self, mcp_server):
        """Test sequential thinking integration end-to-end."""
        with patch("mcp_server.SequentialThinkingEngine") as mock_engine:
            mock_instance = AsyncMock()
            mock_instance.process_query.return_value = {
                "final_answer": "Sequential thinking result",
                "reasoning_trace": ["Step 1", "Step 2", "Step 3"],
            }
            mock_engine.return_value = mock_instance

            result = await mcp_server.handle_tool_call(
                "voidcat_sequential_thinking",
                {
                    "query": "Test sequential thinking",
                    "max_thoughts": 5,
                    "include_reasoning_trace": True,
                },
            )

            assert result["success"] is True
            assert "final_answer" in result
            assert "reasoning_trace" in result

    @pytest.mark.asyncio
    async def test_enhanced_query_pipeline_e2e(self, mcp_server):
        """Test the enhanced query pipeline end-to-end."""
        with patch("mcp_server.VoidCatEnhancedEngine") as mock_engine:
            mock_instance = AsyncMock()
            mock_instance.enhanced_query.return_value = "Enhanced query result"
            mock_engine.return_value = mock_instance

            result = await mcp_server.handle_tool_call(
                "voidcat_enhanced_query",
                {"query": "Test enhanced query", "model": "gpt-4o-mini"},
            )

            assert result["success"] is True
            assert "response" in result

    @pytest.mark.asyncio
    async def test_knowledge_analysis_e2e(self, mcp_server):
        """Test knowledge analysis tool end-to-end."""
        with patch("mcp_server.VoidCatEngine") as mock_engine:
            mock_instance = AsyncMock()
            mock_instance.analyze_knowledge_base.return_value = {
                "document_count": 10,
                "total_tokens": 5000,
                "knowledge_domains": ["MCP", "AI", "Testing"],
            }
            mock_engine.return_value = mock_instance

            result = await mcp_server.handle_tool_call("voidcat_analyze_knowledge", {})

            assert result["success"] is True
            assert "analysis" in result

    @pytest.mark.asyncio
    async def test_mcp_protocol_compliance_e2e(self, mcp_server):
        """Test MCP protocol compliance end-to-end."""
        # Test initialization message
        init_result = await mcp_server.handle_initialization(
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": True}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            }
        )

        assert init_result["success"] is True
        assert "capabilities" in init_result
        assert "serverInfo" in init_result

    @pytest.mark.asyncio
    async def test_resource_cleanup_e2e(self, mcp_server, sample_project):
        """Test proper resource cleanup during operations."""
        # Create and delete multiple tasks
        task_ids = []

        for i in range(3):
            create_result = await mcp_server.handle_tool_call(
                "voidcat_task_create",
                {
                    "name": f"Cleanup Test Task {i}",
                    "description": f"Task {i} for cleanup testing",
                    "project_id": sample_project.id,
                    "priority": 5,
                },
            )
            task_ids.append(create_result["task_id"])

        # Delete all tasks
        for task_id in task_ids:
            delete_result = await mcp_server.handle_tool_call(
                "voidcat_task_delete", {"task_id": task_id}
            )
            assert delete_result["success"] is True

        # Verify cleanup
        list_result = await mcp_server.handle_tool_call(
            "voidcat_task_list", {"project_id": sample_project.id}
        )

        remaining_task_ids = [task["id"] for task in list_result["tasks"]]
        for task_id in task_ids:
            assert task_id not in remaining_task_ids


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
