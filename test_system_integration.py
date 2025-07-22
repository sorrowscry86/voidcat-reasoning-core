#!/usr/bin/env python3
"""
VoidCat V2 System Integration Tests
==================================

Comprehensive integration tests for the complete VoidCat V2 system including:
- Task management system
- Context integration
- MCP server with context-aware tools
- RAG processing with task context
- End-to-end workflow validation

This validates that Task 5 (VoidCat System Integration) is complete and working.

Author: Codey Jr. (testing the cosmic system integration vibes)
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

import pytest
import pytest_asyncio

from voidcat_context_integration import VoidCatContextIntegration
from voidcat_mcp_tools import VoidCatMCPTaskTools
from voidcat_operations import VoidCatOperationsEngine
from voidcat_persistence import VoidCatStorage
from voidcat_task_models import Priority, TaskStatus, VoidCatProject, VoidCatTask


class TestVoidCatSystemIntegration:
    """Test complete system integration - the cosmic harmony! 🌊"""

    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def integrated_system(self, temp_workspace):
        """Create a complete integrated system for testing."""
        storage = VoidCatStorage(temp_workspace)
        operations = VoidCatOperationsEngine(storage)
        context_integration = VoidCatContextIntegration(temp_workspace)
        mcp_tools = VoidCatMCPTaskTools(temp_workspace)

        return {
            "storage": storage,
            "operations": operations,
            "context": context_integration,
            "mcp_tools": mcp_tools,
            "workspace": temp_workspace,
        }

    @pytest.fixture
    def sample_project_data(self, integrated_system):
        """Create sample project and tasks for integration testing."""
        system = integrated_system

        # Create project
        project = VoidCatProject(
            name="VoidCat V2 Integration Test",
            description="Testing the cosmic integration of all systems",
        )
        system["storage"].save_project(project)

        # Create hierarchical tasks
        tasks = []

        # Parent task
        parent_task = VoidCatTask(
            name="Implement Context Integration",
            description="Add context awareness to RAG processing",
            project_id=project.id,
            priority=Priority.HIGH,
            status=TaskStatus.IN_PROGRESS,
            tags=["integration", "context", "rag"],
        )
        parent_task.metrics.complexity_score = 8
        parent_task.metrics.estimated_hours = 12.0
        system["storage"].save_task(parent_task)
        tasks.append(parent_task)

        # Child task 1
        child_task1 = VoidCatTask(
            name="Create Context Integration Module",
            description="Build the context integration layer",
            project_id=project.id,
            parent_id=parent_task.id,
            priority=Priority.HIGH,
            status=TaskStatus.COMPLETED,
            tags=["implementation", "context"],
        )
        child_task1.metrics.complexity_score = 6
        child_task1.metrics.actual_hours = 4.0
        system["storage"].save_task(child_task1)
        tasks.append(child_task1)

        # Child task 2
        child_task2 = VoidCatTask(
            name="Integrate with MCP Server",
            description="Add context-aware tools to MCP server",
            project_id=project.id,
            parent_id=parent_task.id,
            priority=Priority.MEDIUM,
            status=TaskStatus.IN_PROGRESS,
            tags=["mcp", "integration"],
        )
        child_task2.metrics.complexity_score = 7
        child_task2.metrics.estimated_hours = 6.0
        system["storage"].save_task(child_task2)
        tasks.append(child_task2)

        # Blocked task
        blocked_task = VoidCatTask(
            name="Performance Optimization",
            description="Optimize context retrieval performance",
            project_id=project.id,
            priority=Priority.URGENT,
            status=TaskStatus.BLOCKED,
            tags=["performance", "optimization"],
        )
        blocked_task.metrics.complexity_score = 9
        system["storage"].save_task(blocked_task)
        tasks.append(blocked_task)

        # Add a pending task for recommendations
        pending_task = VoidCatTask(
            name="Write Documentation",
            description="Document the context integration features",
            project_id=project.id,
            priority=Priority.MEDIUM,
            status=TaskStatus.PENDING,
            tags=["documentation", "context"],
        )
        pending_task.metrics.complexity_score = 4
        pending_task.metrics.estimated_hours = 3.0
        system["storage"].save_task(pending_task)
        tasks.append(pending_task)

        return {
            "project": project,
            "tasks": tasks,
            "parent_task": parent_task,
            "child_tasks": [child_task1, child_task2],
            "blocked_task": blocked_task,
            "pending_task": pending_task,
        }

    def test_storage_operations_integration(
        self, integrated_system, sample_project_data
    ):
        """Test that storage and operations work together seamlessly."""
        system = integrated_system
        data = sample_project_data

        # Test project operations
        projects = system["storage"].list_projects()
        assert len(projects) == 1
        assert projects[0].name == "VoidCat V2 Integration Test"

        # Test task operations
        tasks = system["storage"].list_tasks(project_id=data["project"].id)
        assert len(tasks) == 5

        # Test hierarchical queries using query_tasks
        from voidcat_operations import QueryFilter

        parent_filter = QueryFilter(project_ids=[data["project"].id], parent_id=None)
        parent_tasks = system["operations"].query_tasks(parent_filter)
        assert (
            len(parent_tasks) == 3
        )  # Parent task, blocked task, and pending task (no parent)

        child_filter = QueryFilter(
            project_ids=[data["project"].id], parent_id=data["parent_task"].id
        )
        child_tasks = system["operations"].query_tasks(child_filter)
        assert len(child_tasks) == 2

    def test_context_integration_with_data(
        self, integrated_system, sample_project_data
    ):
        """Test context integration with real project data."""
        system = integrated_system
        data = sample_project_data

        # Get active context
        context = system["context"].get_active_context()

        # Verify project context
        assert len(context["active_projects"]) == 1
        active_project = context["active_projects"][0]
        assert active_project["name"] == "VoidCat V2 Integration Test"
        assert active_project["active_task_count"] == 4  # Excluding completed task

        # Verify task context
        current_tasks = context["current_tasks"]
        high_priority_tasks = [t for t in current_tasks if "High" in t["priority"]]
        assert len(high_priority_tasks) >= 1

        # Verify workflow state
        workflow = context["workflow_state"]
        assert workflow["total_tasks"] == 5
        assert workflow["in_progress_tasks"] == 2
        assert workflow["completed_tasks"] == 1
        assert workflow["blocked_tasks"] == 1
        assert workflow["pending_tasks"] == 1

        # Verify blockers
        assert len(context["blockers"]) == 1
        blocker = context["blockers"][0]
        assert blocker["task_name"] == "Performance Optimization"

    def test_query_enhancement_integration(
        self, integrated_system, sample_project_data
    ):
        """Test query enhancement with context integration."""
        system = integrated_system
        data = sample_project_data

        original_query = "What should I work on next?"

        # Test query enhancement
        enhanced_query = system["context"].enhance_query_with_context(
            original_query, include_tasks=True, include_projects=True
        )

        assert len(enhanced_query) > len(original_query)
        assert "CONTEXT:" in enhanced_query
        assert "VoidCat V2 Integration Test" in enhanced_query
        assert (
            "Implement Context Integration" in enhanced_query
            or "Integrate with MCP Server" in enhanced_query
        )
        assert original_query in enhanced_query

    def test_task_specific_context_integration(
        self, integrated_system, sample_project_data
    ):
        """Test task-specific context retrieval."""
        system = integrated_system
        data = sample_project_data

        parent_task = data["parent_task"]
        context = system["context"].get_task_specific_context(parent_task.id)

        # Verify task context
        assert context["task"]["name"] == "Implement Context Integration"
        assert context["task"]["status"] == "in-progress"
        assert context["project"]["name"] == "VoidCat V2 Integration Test"

        # Verify related tasks (children)
        related_tasks = context["related_tasks"]
        child_names = [t["name"] for t in related_tasks if t["relationship"] == "child"]
        assert "Create Context Integration Module" in child_names
        assert "Integrate with MCP Server" in child_names

    def test_project_specific_context_integration(
        self, integrated_system, sample_project_data
    ):
        """Test project-specific context retrieval."""
        system = integrated_system
        data = sample_project_data

        project = data["project"]
        context = system["context"].get_project_specific_context(project.id)

        # Verify project context
        assert context["project"]["name"] == "VoidCat V2 Integration Test"

        # Verify task summary
        task_summary = context["task_summary"]
        assert task_summary["total_tasks"] == 5

        # Status distribution
        status_dist = task_summary["status_distribution"]
        assert status_dist["in-progress"] == 2
        assert status_dist["completed"] == 1
        assert status_dist["blocked"] == 1

        # Priority distribution
        priority_dist = task_summary["priority_distribution"]
        assert "HIGH" in priority_dist
        assert "MEDIUM" in priority_dist
        assert "URGENT" in priority_dist

    @pytest.mark.asyncio
    async def test_mcp_tools_integration(self, integrated_system, sample_project_data):
        """Test MCP tools integration with the complete system."""
        system = integrated_system
        data = sample_project_data

        mcp_tools = system["mcp_tools"]

        # Test project listing
        result = await mcp_tools.handle_tool_call(
            "voidcat_project_manage", {"action": "list"}
        )

        assert "content" in result
        content_text = result["content"][0]["text"]
        assert "VoidCat V2 Integration Test" in content_text

        # Test task listing
        result = await mcp_tools.handle_tool_call(
            "voidcat_task_list", {"project_id": data["project"].id}
        )

        assert "content" in result
        content_text = result["content"][0]["text"]
        assert "Implement Context Integration" in content_text
        assert "Create Context Integration Module" in content_text

        # Test task creation
        result = await mcp_tools.handle_tool_call(
            "voidcat_task_create",
            {
                "name": "Integration Test Task",
                "description": "A task created during integration testing",
                "project_id": data["project"].id,
                "priority": 8,
                "parent_id": data["parent_task"].id,
            },
        )

        assert "content" in result
        content_text = result["content"][0]["text"]
        assert "✅ **Task Created Successfully**" in content_text
        assert "Integration Test Task" in content_text

    @pytest.mark.asyncio
    async def test_task_recommendations_integration(
        self, integrated_system, sample_project_data
    ):
        """Test task recommendation system integration."""
        system = integrated_system
        data = sample_project_data

        mcp_tools = system["mcp_tools"]

        # Test task recommendations
        result = await mcp_tools.handle_tool_call(
            "voidcat_task_recommend",
            {"project_id": data["project"].id, "max_recommendations": 3},
        )

        assert "content" in result
        content_text = result["content"][0]["text"]
        # Should either have recommendations or explain why there are none
        assert (
            "📋 **Task Recommendations**" in content_text
            or "No task recommendations available" in content_text
            or "Write Documentation" in content_text
        )

    @pytest.mark.asyncio
    async def test_dependency_analysis_integration(
        self, integrated_system, sample_project_data
    ):
        """Test dependency analysis integration."""
        system = integrated_system
        data = sample_project_data

        mcp_tools = system["mcp_tools"]

        # Test dependency analysis
        result = await mcp_tools.handle_tool_call(
            "voidcat_dependency_analyze",
            {"project_id": data["project"].id, "action": "ready"},
        )

        assert "content" in result
        content_text = result["content"][0]["text"]
        assert "🎯 **Ready Tasks**" in content_text or "No ready tasks" in content_text

    def test_context_cache_performance(self, integrated_system, sample_project_data):
        """Test context caching performance with integrated system."""
        system = integrated_system
        data = sample_project_data

        # First call should populate cache
        import time

        start_time = time.time()
        context1 = system["context"].get_active_context()
        first_call_time = time.time() - start_time

        # Second call should use cache (faster)
        start_time = time.time()
        context2 = system["context"].get_active_context()
        second_call_time = time.time() - start_time

        # Cache should make second call faster
        assert second_call_time < first_call_time
        assert context1 == context2

    def test_error_handling_integration(self, integrated_system):
        """Test error handling across integrated components."""
        system = integrated_system

        # Test context with non-existent task
        context = system["context"].get_task_specific_context("non-existent-id")
        assert "error" in context

        # Test context with non-existent project
        context = system["context"].get_project_specific_context("non-existent-id")
        assert "error" in context

        # System should remain stable after errors
        active_context = system["context"].get_active_context()
        assert "timestamp" in active_context
        assert "workflow_state" in active_context

    def test_backward_compatibility(self, integrated_system, sample_project_data):
        """Test that integration maintains backward compatibility."""
        system = integrated_system
        data = sample_project_data

        # Test that basic storage operations still work
        projects = system["storage"].list_projects()
        assert len(projects) == 1

        tasks = system["storage"].list_tasks(project_id=data["project"].id)
        assert len(tasks) == 5

        # Test that operations engine still works
        from voidcat_operations import QueryFilter

        filter_criteria = QueryFilter(
            project_ids=[data["project"].id], status_filter=[TaskStatus.IN_PROGRESS]
        )
        filtered_tasks = system["operations"].query_tasks(filter_criteria)
        assert len(filtered_tasks) == 2

    def test_end_to_end_workflow(self, integrated_system):
        """Test complete end-to-end workflow integration."""
        system = integrated_system

        # 1. Create project
        project = VoidCatProject(
            name="End-to-End Test Project", description="Testing complete workflow"
        )
        system["storage"].save_project(project)

        # 2. Create task
        task = VoidCatTask(
            name="E2E Test Task",
            description="End-to-end testing task",
            project_id=project.id,
            priority=Priority.HIGH,
            status=TaskStatus.PENDING,
        )
        system["storage"].save_task(task)

        # 3. Get context
        context = system["context"].get_active_context()
        assert len(context["active_projects"]) == 1
        assert context["active_projects"][0]["name"] == "End-to-End Test Project"

        # 4. Enhance query with context
        enhanced_query = system["context"].enhance_query_with_context(
            "What's the status of my project?",
            include_tasks=True,
            include_projects=True,
        )
        assert "End-to-End Test Project" in enhanced_query
        assert "E2E Test Task" in enhanced_query

        # 5. Update task status
        task.status = TaskStatus.IN_PROGRESS
        system["storage"].save_task(task)

        # 6. Clear cache and verify updated context
        system["context"].clear_context_cache()
        updated_context = system["context"].get_active_context()
        assert updated_context["workflow_state"]["in_progress_tasks"] == 1

        # 7. Complete task
        task.status = TaskStatus.COMPLETED
        system["storage"].save_task(task)

        # 8. Verify final context
        system["context"].clear_context_cache()
        final_context = system["context"].get_active_context()
        assert final_context["workflow_state"]["completed_tasks"] == 1
        assert len(final_context["active_projects"]) == 0  # No active tasks


if __name__ == "__main__":
    # Run the system integration tests
    pytest.main([__file__, "-v", "--tb=short"])
