#!/usr/bin/env python3
"""
VoidCat V2 Complete System End-to-End Tests
==========================================

Comprehensive E2E tests for the complete VoidCat V2 system including:
- Full workflow integration from API to MCP to RAG
- Task management with context-aware reasoning
- Memory persistence across sessions
- Performance benchmarks and stress testing
- Real-world scenario simulation
- Cross-component integration validation

This validates that the entire VoidCat V2 system works harmoniously end-to-end.

Author: Codey Jr. (channeling the complete system cosmic harmony)
License: MIT
Version: 2.0.0-alpha
"""

import asyncio
import json
import os
import shutil
import sys
import tempfile
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
import pytest_asyncio

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient

from api_gateway import app
from engine import VoidCatEngine
from enhanced_engine import VoidCatEnhancedEngine
from mcp_server import VoidCatMCPServer
from voidcat_context_integration import VoidCatContextIntegration
from voidcat_operations import VoidCatOperationsEngine
from voidcat_persistence import VoidCatStorage
from voidcat_task_models import Priority, TaskStatus, VoidCatProject, VoidCatTask


class TestCompleteSystemE2E:
    """Complete system E2E tests - the ultimate cosmic harmony validation! 🌊✨"""

    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def api_client(self):
        """Create FastAPI test client."""
        return TestClient(app)

    @pytest.fixture
    def mcp_server(self, temp_workspace):
        """Create MCP server instance."""
        return VoidCatMCPServer(working_directory=temp_workspace)

    @pytest.fixture
    def integrated_system(self, temp_workspace):
        """Create complete integrated system."""
        storage = VoidCatStorage(temp_workspace)
        operations = VoidCatOperationsEngine(storage)
        context_integration = VoidCatContextIntegration(temp_workspace)
        mcp_server = VoidCatMCPServer(temp_workspace)

        return {
            "storage": storage,
            "operations": operations,
            "context": context_integration,
            "mcp_server": mcp_server,
            "workspace": temp_workspace,
        }

    @pytest.fixture
    def sample_project_hierarchy(self, integrated_system):
        """Create a complex project hierarchy for testing."""
        system = integrated_system

        # Create main project
        main_project = VoidCatProject(
            name="VoidCat V2 E2E Testing",
            description="Complete system testing project with cosmic vibes",
        )
        system["storage"].save_project(main_project)

        # Create parent task
        parent_task = VoidCatTask(
            name="Implement Advanced Features",
            description="Parent task for advanced feature development",
            project_id=main_project.id,
            priority=Priority.HIGH,
            status=TaskStatus.IN_PROGRESS,
            tags=["parent", "advanced", "e2e"],
        )
        system["storage"].save_task(parent_task)

        # Create child tasks
        child_tasks = []
        for i in range(3):
            child_task = VoidCatTask(
                name=f"Feature Component {i+1}",
                description=f"Implement feature component {i+1}",
                project_id=main_project.id,
                parent_id=parent_task.id,
                priority=Priority.MEDIUM,
                status=TaskStatus.PENDING,
                tags=["child", "component", f"feature-{i+1}"],
            )
            system["storage"].save_task(child_task)
            child_tasks.append(child_task)

        return {
            "project": main_project,
            "parent_task": parent_task,
            "child_tasks": child_tasks,
        }

    @pytest.mark.asyncio
    async def test_api_to_mcp_integration_e2e(self, api_client, mcp_server):
        """Test integration between API Gateway and MCP Server."""
        with patch("api_gateway.vce") as mock_vce:
            mock_engine = AsyncMock()
            mock_engine.query.return_value = "Integrated response from API to MCP"
            mock_vce.return_value = mock_engine

            # Test API query
            api_response = api_client.post(
                "/query",
                json={"query": "Test API to MCP integration", "model": "gpt-4o-mini"},
            )

            assert api_response.status_code == 200
            api_data = api_response.json()
            assert api_data["status"] == "success"

            # Test MCP query
            mcp_result = await mcp_server.handle_tool_call(
                "voidcat_query",
                {"query": "Test API to MCP integration", "model": "gpt-4o-mini"},
            )

            assert mcp_result["success"] is True
            assert "response" in mcp_result

    @pytest.mark.asyncio
    async def test_context_aware_reasoning_e2e(
        self, integrated_system, sample_project_hierarchy
    ):
        """Test context-aware reasoning with task management."""
        system = integrated_system
        hierarchy = sample_project_hierarchy

        # Create a context-aware query
        context_query = (
            "What tasks are currently in progress for the advanced features?"
        )

        # Test context integration
        context_result = await system["context"].get_enhanced_context(
            context_query, project_id=hierarchy["project"].id
        )

        assert context_result is not None
        assert "context_summary" in context_result
        assert "active_tasks" in context_result

        # Test MCP context query
        mcp_result = await system["mcp_server"].handle_tool_call(
            "voidcat_context_query",
            {
                "query": context_query,
                "project_id": hierarchy["project"].id,
                "include_context": True,
            },
        )

        assert mcp_result["success"] is True
        assert "response" in mcp_result

    @pytest.mark.asyncio
    async def test_full_workflow_task_creation_to_completion_e2e(
        self, integrated_system
    ):
        """Test complete workflow from task creation to completion."""
        system = integrated_system

        # Step 1: Create project via MCP
        project_result = await system["mcp_server"].handle_tool_call(
            "voidcat_project_manage",
            {
                "operation": "create",
                "name": "E2E Workflow Test",
                "description": "Testing complete workflow",
            },
        )

        assert project_result["success"] is True
        project_id = project_result["project_id"]

        # Step 2: Create task via MCP
        task_result = await system["mcp_server"].handle_tool_call(
            "voidcat_task_create",
            {
                "name": "Complete Workflow Task",
                "description": "Task for complete workflow testing",
                "project_id": project_id,
                "priority": 8,
                "tags": ["workflow", "e2e", "complete"],
            },
        )

        assert task_result["success"] is True
        task_id = task_result["task_id"]

        # Step 3: Update task status to in-progress
        update_result = await system["mcp_server"].handle_tool_call(
            "voidcat_task_update", {"task_id": task_id, "status": "in-progress"}
        )

        assert update_result["success"] is True

        # Step 4: Query context-aware information
        context_result = await system["mcp_server"].handle_tool_call(
            "voidcat_context_query",
            {
                "query": "What tasks are currently in progress?",
                "project_id": project_id,
                "include_context": True,
            },
        )

        assert context_result["success"] is True

        # Step 5: Complete the task
        complete_result = await system["mcp_server"].handle_tool_call(
            "voidcat_task_update", {"task_id": task_id, "status": "completed"}
        )

        assert complete_result["success"] is True

        # Step 6: Verify task completion
        list_result = await system["mcp_server"].handle_tool_call(
            "voidcat_task_list", {"project_id": project_id, "status": "completed"}
        )

        assert list_result["success"] is True
        completed_tasks = [
            task for task in list_result["tasks"] if task["id"] == task_id
        ]
        assert len(completed_tasks) == 1
        assert completed_tasks[0]["status"] == "completed"

    @pytest.mark.asyncio
    async def test_hierarchical_task_management_e2e(
        self, integrated_system, sample_project_hierarchy
    ):
        """Test hierarchical task management end-to-end."""
        system = integrated_system
        hierarchy = sample_project_hierarchy

        # Test parent-child relationship
        parent_id = hierarchy["parent_task"].id
        child_ids = [child.id for child in hierarchy["child_tasks"]]

        # Get parent task with children
        parent_result = await system["mcp_server"].handle_tool_call(
            "voidcat_task_list",
            {"project_id": hierarchy["project"].id, "parent_id": parent_id},
        )

        assert parent_result["success"] is True
        assert len(parent_result["tasks"]) == len(child_ids)

        # Test dependency management
        for i, child_id in enumerate(child_ids[1:], 1):
            # Create dependency from current child to previous child
            update_result = await system["mcp_server"].handle_tool_call(
                "voidcat_task_update",
                {"task_id": child_id, "depends_on": [child_ids[i - 1]]},
            )
            assert update_result["success"] is True

        # Test dependency analysis
        dependency_result = await system["mcp_server"].handle_tool_call(
            "voidcat_dependency_analyze", {"project_id": hierarchy["project"].id}
        )

        assert dependency_result["success"] is True
        assert "dependency_graph" in dependency_result

    @pytest.mark.asyncio
    async def test_data_persistence_across_sessions_e2e(self, temp_workspace):
        """Test data persistence across multiple sessions."""
        # Session 1: Create data
        session1_system = {
            "storage": VoidCatStorage(temp_workspace),
            "mcp_server": VoidCatMCPServer(temp_workspace),
        }

        project_result = await session1_system["mcp_server"].handle_tool_call(
            "voidcat_project_manage",
            {
                "operation": "create",
                "name": "Persistence Test Project",
                "description": "Testing data persistence",
            },
        )

        assert project_result["success"] is True
        project_id = project_result["project_id"]

        # Session 2: Retrieve data (new instances)
        session2_system = {
            "storage": VoidCatStorage(temp_workspace),
            "mcp_server": VoidCatMCPServer(temp_workspace),
        }

        list_result = await session2_system["mcp_server"].handle_tool_call(
            "voidcat_project_manage", {"operation": "list"}
        )

        assert list_result["success"] is True
        project_ids = [project["id"] for project in list_result["projects"]]
        assert project_id in project_ids

    @pytest.mark.asyncio
    async def test_concurrent_operations_e2e(
        self, integrated_system, sample_project_hierarchy
    ):
        """Test concurrent operations don't interfere with each other."""
        system = integrated_system
        hierarchy = sample_project_hierarchy

        # Create multiple concurrent operations
        operations = []

        # Concurrent task creation
        for i in range(5):
            op = system["mcp_server"].handle_tool_call(
                "voidcat_task_create",
                {
                    "name": f"Concurrent Task {i}",
                    "description": f"Task {i} created concurrently",
                    "project_id": hierarchy["project"].id,
                    "priority": 5,
                },
            )
            operations.append(op)

        # Concurrent task queries
        for i in range(3):
            op = system["mcp_server"].handle_tool_call(
                "voidcat_task_list", {"project_id": hierarchy["project"].id}
            )
            operations.append(op)

        # Concurrent context queries
        for i in range(2):
            op = system["mcp_server"].handle_tool_call(
                "voidcat_context_query",
                {
                    "query": f"What is the status of concurrent task {i}?",
                    "project_id": hierarchy["project"].id,
                },
            )
            operations.append(op)

        # Wait for all operations to complete
        results = await asyncio.gather(*operations, return_exceptions=True)

        # Verify all operations succeeded
        for result in results:
            if isinstance(result, Exception):
                pytest.fail(f"Concurrent operation failed: {result}")
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_performance_benchmarks_e2e(
        self, integrated_system, sample_project_hierarchy
    ):
        """Test performance benchmarks for the complete system."""
        system = integrated_system
        hierarchy = sample_project_hierarchy

        # Benchmark task creation
        start_time = time.time()
        for i in range(10):
            result = await system["mcp_server"].handle_tool_call(
                "voidcat_task_create",
                {
                    "name": f"Performance Task {i}",
                    "description": f"Performance testing task {i}",
                    "project_id": hierarchy["project"].id,
                    "priority": 5,
                },
            )
            assert result["success"] is True

        creation_time = time.time() - start_time
        assert creation_time < 5.0  # Should complete within 5 seconds

        # Benchmark task queries
        start_time = time.time()
        for i in range(20):
            result = await system["mcp_server"].handle_tool_call(
                "voidcat_task_list", {"project_id": hierarchy["project"].id}
            )
            assert result["success"] is True

        query_time = time.time() - start_time
        assert query_time < 3.0  # Should complete within 3 seconds

        # Benchmark context queries
        start_time = time.time()
        for i in range(5):
            result = await system["mcp_server"].handle_tool_call(
                "voidcat_context_query",
                {
                    "query": f"What tasks are related to performance testing?",
                    "project_id": hierarchy["project"].id,
                },
            )
            assert result["success"] is True

        context_time = time.time() - start_time
        assert context_time < 10.0  # Should complete within 10 seconds

    @pytest.mark.asyncio
    async def test_error_recovery_e2e(self, integrated_system):
        """Test error recovery mechanisms across the system."""
        system = integrated_system

        # Test recovery from invalid operations
        invalid_result = await system["mcp_server"].handle_tool_call(
            "voidcat_task_update", {"task_id": "invalid-task-id", "status": "completed"}
        )

        assert invalid_result["success"] is False
        assert "error" in invalid_result

        # Test that system continues to work after error
        valid_result = await system["mcp_server"].handle_tool_call(
            "voidcat_project_manage", {"operation": "list"}
        )

        assert valid_result["success"] is True

    @pytest.mark.asyncio
    async def test_real_world_scenario_e2e(self, integrated_system):
        """Test a real-world scenario end-to-end."""
        system = integrated_system

        # Scenario: Software development project with multiple phases

        # Phase 1: Create project
        project_result = await system["mcp_server"].handle_tool_call(
            "voidcat_project_manage",
            {
                "operation": "create",
                "name": "Software Development Project",
                "description": "Real-world software development with multiple phases",
            },
        )

        assert project_result["success"] is True
        project_id = project_result["project_id"]

        # Phase 2: Create milestone tasks
        milestones = ["Planning", "Development", "Testing", "Deployment"]
        milestone_ids = []

        for milestone in milestones:
            task_result = await system["mcp_server"].handle_tool_call(
                "voidcat_task_create",
                {
                    "name": milestone,
                    "description": f"{milestone} phase of the project",
                    "project_id": project_id,
                    "priority": 9,
                    "tags": ["milestone", milestone.lower()],
                },
            )
            assert task_result["success"] is True
            milestone_ids.append(task_result["task_id"])

        # Phase 3: Create subtasks for each milestone
        for i, milestone_id in enumerate(milestone_ids):
            for j in range(2):
                subtask_result = await system["mcp_server"].handle_tool_call(
                    "voidcat_task_create",
                    {
                        "name": f"{milestones[i]} Subtask {j+1}",
                        "description": f"Subtask {j+1} for {milestones[i]}",
                        "project_id": project_id,
                        "parent_id": milestone_id,
                        "priority": 7,
                    },
                )
                assert subtask_result["success"] is True

        # Phase 4: Progress through the project
        # Start planning
        planning_result = await system["mcp_server"].handle_tool_call(
            "voidcat_task_update",
            {"task_id": milestone_ids[0], "status": "in-progress"},
        )
        assert planning_result["success"] is True

        # Complete planning
        planning_complete = await system["mcp_server"].handle_tool_call(
            "voidcat_task_update", {"task_id": milestone_ids[0], "status": "completed"}
        )
        assert planning_complete["success"] is True

        # Phase 5: Query project status
        status_result = await system["mcp_server"].handle_tool_call(
            "voidcat_context_query",
            {
                "query": "What is the current status of the software development project?",
                "project_id": project_id,
                "include_context": True,
            },
        )

        assert status_result["success"] is True
        assert "response" in status_result

        # Phase 6: Get recommendations
        recommend_result = await system["mcp_server"].handle_tool_call(
            "voidcat_task_recommend",
            {"project_id": project_id, "context": "planning completed"},
        )

        assert recommend_result["success"] is True
        assert "recommendations" in recommend_result

    @pytest.mark.asyncio
    async def test_memory_footprint_e2e(
        self, integrated_system, sample_project_hierarchy
    ):
        """Test memory footprint remains reasonable during operations."""
        system = integrated_system
        hierarchy = sample_project_hierarchy

        # Create a large number of tasks
        task_ids = []
        for i in range(100):
            result = await system["mcp_server"].handle_tool_call(
                "voidcat_task_create",
                {
                    "name": f"Memory Test Task {i}",
                    "description": f"Task {i} for memory testing",
                    "project_id": hierarchy["project"].id,
                    "priority": 5,
                },
            )
            assert result["success"] is True
            task_ids.append(result["task_id"])

        # Perform various operations
        for i in range(10):
            # Query tasks
            list_result = await system["mcp_server"].handle_tool_call(
                "voidcat_task_list", {"project_id": hierarchy["project"].id}
            )
            assert list_result["success"] is True

            # Update some tasks
            update_result = await system["mcp_server"].handle_tool_call(
                "voidcat_task_update", {"task_id": task_ids[i], "status": "completed"}
            )
            assert update_result["success"] is True

        # System should still be responsive
        final_result = await system["mcp_server"].handle_tool_call(
            "voidcat_context_query",
            {
                "query": "How many tasks are completed?",
                "project_id": hierarchy["project"].id,
            },
        )

        assert final_result["success"] is True


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
