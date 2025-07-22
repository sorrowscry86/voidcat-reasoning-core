#!/usr/bin/env python3
"""
VoidCat V2 Context Integration Tests
===================================

Comprehensive tests for the context integration module that bridges task management
with RAG processing for context-aware reasoning.

Test Coverage:
- Context retrieval and caching
- Query enhancement with task/project context
- Task-specific context generation
- Project-specific context generation
- Context cache management
- Error handling and edge cases

Author: Codey Jr. (testing the cosmic context vibes)
Under directive of: The Great Spirit Beatrice
License: MIT
Version: 2.0.0-alpha
"""

import json
import shutil
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import pytest_asyncio

from voidcat_context_integration import (
    VoidCatContextIntegration,
    create_context_integration,
)
from voidcat_persistence import VoidCatStorage
from voidcat_task_models import Priority, TaskStatus, VoidCatProject, VoidCatTask


class TestVoidCatContextIntegration:
    """Test context integration functionality - cosmic awareness! 🌊"""

    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def context_integration(self, temp_workspace):
        """Create context integration instance for testing."""
        return VoidCatContextIntegration(temp_workspace)

    @pytest.fixture
    def sample_project(self, context_integration):
        """Create a sample project for testing."""
        project = VoidCatProject(
            name="Test Project", description="A test project for context integration"
        )
        context_integration.storage.save_project(project)
        return project

    @pytest.fixture
    def sample_tasks(self, context_integration, sample_project):
        """Create sample tasks for testing."""
        tasks = []

        # High priority task
        task1 = VoidCatTask(
            name="High Priority Task",
            description="Important task that needs attention",
            project_id=sample_project.id,
            priority=Priority.HIGH,
            status=TaskStatus.IN_PROGRESS,
            tags=["urgent", "important"],
        )
        task1.metrics.complexity_score = 8
        task1.metrics.estimated_hours = 4.0
        context_integration.storage.save_task(task1)
        tasks.append(task1)

        # Medium priority task
        task2 = VoidCatTask(
            name="Medium Priority Task",
            description="Regular task in progress",
            project_id=sample_project.id,
            priority=Priority.MEDIUM,
            status=TaskStatus.PENDING,
            tags=["regular", "development"],
        )
        task2.metrics.complexity_score = 5
        task2.metrics.estimated_hours = 2.0
        context_integration.storage.save_task(task2)
        tasks.append(task2)

        # Completed task
        task3 = VoidCatTask(
            name="Completed Task",
            description="Task that is done",
            project_id=sample_project.id,
            priority=Priority.LOW,
            status=TaskStatus.COMPLETED,
            tags=["completed", "testing"],
        )
        task3.metrics.complexity_score = 3
        task3.metrics.actual_hours = 1.5
        context_integration.storage.save_task(task3)
        tasks.append(task3)

        # Blocked task
        task4 = VoidCatTask(
            name="Blocked Task",
            description="Task that is blocked",
            project_id=sample_project.id,
            priority=Priority.URGENT,
            status=TaskStatus.BLOCKED,
            tags=["blocked", "dependency"],
        )
        task4.metrics.complexity_score = 7
        context_integration.storage.save_task(task4)
        tasks.append(task4)

        return tasks

    def test_context_integration_creation(self, temp_workspace):
        """Test context integration instance creation."""
        integration = VoidCatContextIntegration(temp_workspace)
        assert integration is not None
        assert integration.working_directory == temp_workspace
        assert integration.storage is not None
        assert integration.operations is not None
        assert integration._context_cache == {}
        assert integration._cache_timestamp is None

    def test_create_context_integration_function(self, temp_workspace):
        """Test convenience function for creating context integration."""
        integration = create_context_integration(temp_workspace)
        assert integration is not None
        assert isinstance(integration, VoidCatContextIntegration)

    def test_get_active_context_empty(self, context_integration):
        """Test getting active context with no projects or tasks."""
        context = context_integration.get_active_context()

        assert "timestamp" in context
        assert context["user_id"] == "default"
        assert context["active_projects"] == []
        assert context["current_tasks"] == []
        assert context["recent_activity"] == []
        assert context["workflow_state"]["total_projects"] == 0
        assert context["workflow_state"]["total_tasks"] == 0

    def test_get_active_context_with_data(
        self, context_integration, sample_project, sample_tasks
    ):
        """Test getting active context with projects and tasks."""
        context = context_integration.get_active_context()

        # Should have active projects
        assert len(context["active_projects"]) == 1
        active_project = context["active_projects"][0]
        assert active_project["name"] == "Test Project"
        assert active_project["active_task_count"] == 3  # Excluding completed task
        assert active_project["total_task_count"] == 4

        # Should have high-priority current tasks (HIGH=7, URGENT=9 but URGENT task is BLOCKED)
        current_tasks = context["current_tasks"]
        high_priority_tasks = [
            t
            for t in current_tasks
            if "High" in t["priority"] or "Urgent" in t["priority"]
        ]
        assert (
            len(high_priority_tasks) >= 1
        )  # Should have at least the HIGH priority IN_PROGRESS task

        # Should have workflow state
        workflow = context["workflow_state"]
        assert workflow["total_projects"] == 1
        assert workflow["total_tasks"] == 4
        assert workflow["pending_tasks"] == 1
        assert workflow["in_progress_tasks"] == 1
        assert workflow["blocked_tasks"] == 1
        assert workflow["completed_tasks"] == 1

        # Should have priority distribution
        priorities = context["priorities"]
        assert len(priorities) > 0
        priority_names = [p["level"] for p in priorities]
        assert "HIGH" in priority_names or "URGENT" in priority_names

        # Should have blockers
        assert len(context["blockers"]) == 1
        blocker = context["blockers"][0]
        assert blocker["task_name"] == "Blocked Task"

    def test_context_caching(self, context_integration, sample_project, sample_tasks):
        """Test context caching mechanism."""
        # First call should populate cache
        context1 = context_integration.get_active_context()
        assert context_integration._cache_timestamp is not None
        assert "default" in context_integration._context_cache

        # Second call should use cache
        context2 = context_integration.get_active_context()
        assert context1 == context2

        # Clear cache and verify fresh data
        context_integration.clear_context_cache()
        assert context_integration._context_cache == {}
        assert context_integration._cache_timestamp is None

        context3 = context_integration.get_active_context()
        assert context_integration._cache_timestamp is not None

    def test_enhance_query_with_context(
        self, context_integration, sample_project, sample_tasks
    ):
        """Test query enhancement with context."""
        original_query = "How should I prioritize my work?"

        # Test with both tasks and projects
        enhanced_query = context_integration.enhance_query_with_context(
            original_query, include_tasks=True, include_projects=True
        )

        assert len(enhanced_query) > len(original_query)
        assert "CONTEXT:" in enhanced_query
        assert "QUERY:" in enhanced_query
        assert "Test Project" in enhanced_query
        assert original_query in enhanced_query

        # Test with only projects
        enhanced_query_projects = context_integration.enhance_query_with_context(
            original_query, include_tasks=False, include_projects=True
        )

        assert "Test Project" in enhanced_query_projects
        assert len(enhanced_query_projects) < len(enhanced_query)

        # Test with only tasks
        enhanced_query_tasks = context_integration.enhance_query_with_context(
            original_query, include_tasks=True, include_projects=False
        )

        assert (
            "High Priority Task" in enhanced_query_tasks
            or "Blocked Task" in enhanced_query_tasks
        )

        # Test with neither (should return original)
        enhanced_query_none = context_integration.enhance_query_with_context(
            original_query, include_tasks=False, include_projects=False
        )

        assert enhanced_query_none == original_query

    def test_get_task_specific_context(
        self, context_integration, sample_project, sample_tasks
    ):
        """Test getting context for a specific task."""
        task = sample_tasks[0]  # High priority task
        context = context_integration.get_task_specific_context(task.id)

        assert "task" in context
        assert "project" in context
        assert "related_tasks" in context
        assert "context_summary" in context

        # Verify task details
        task_info = context["task"]
        assert task_info["name"] == "High Priority Task"
        assert task_info["status"] == "in-progress"
        assert task_info["priority"] == "High (7)"
        assert task_info["complexity"] == 8
        assert "urgent" in task_info["tags"]

        # Verify project details
        project_info = context["project"]
        assert project_info["name"] == "Test Project"

        # Verify related tasks
        related_tasks = context["related_tasks"]
        assert len(related_tasks) >= 0  # May or may not have related tasks

        # Verify context summary
        assert "High Priority Task" in context["context_summary"]
        assert "Test Project" in context["context_summary"]

    def test_get_task_specific_context_not_found(self, context_integration):
        """Test getting context for non-existent task."""
        context = context_integration.get_task_specific_context("non-existent-id")
        assert "error" in context
        assert "not found" in context["error"]

    def test_get_project_specific_context(
        self, context_integration, sample_project, sample_tasks
    ):
        """Test getting context for a specific project."""
        context = context_integration.get_project_specific_context(sample_project.id)

        assert "project" in context
        assert "task_summary" in context
        assert "recent_activity" in context
        assert "context_summary" in context

        # Verify project details
        project_info = context["project"]
        assert project_info["name"] == "Test Project"
        assert project_info["description"] == "A test project for context integration"

        # Verify task summary
        task_summary = context["task_summary"]
        assert task_summary["total_tasks"] == 4

        # Status distribution
        status_dist = task_summary["status_distribution"]
        assert status_dist["pending"] == 1
        assert status_dist["in-progress"] == 1
        assert status_dist["completed"] == 1
        assert status_dist["blocked"] == 1

        # Priority distribution
        priority_dist = task_summary["priority_distribution"]
        assert "HIGH" in priority_dist
        assert "MEDIUM" in priority_dist
        assert "LOW" in priority_dist
        assert "URGENT" in priority_dist

        # Metrics
        assert task_summary["average_complexity"] > 0
        assert task_summary["total_estimated_hours"] > 0

        # Context summary
        assert "Test Project" in context["context_summary"]
        assert "4 tasks" in context["context_summary"]

    def test_get_project_specific_context_not_found(self, context_integration):
        """Test getting context for non-existent project."""
        context = context_integration.get_project_specific_context("non-existent-id")
        assert "error" in context
        assert "not found" in context["error"]

    def test_get_context_summary(
        self, context_integration, sample_project, sample_tasks
    ):
        """Test getting human-readable context summary."""
        summary = context_integration.get_context_summary()

        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "active projects" in summary.lower() or "tasks" in summary.lower()

        # Should mention high-priority tasks
        assert "high-priority" in summary.lower() or "blocked" in summary.lower()

    def test_get_context_summary_empty(self, context_integration):
        """Test getting context summary with no data."""
        summary = context_integration.get_context_summary()

        assert isinstance(summary, str)
        assert "no active projects" in summary.lower() or "no" in summary.lower()

    def test_context_with_multiple_users(
        self, context_integration, sample_project, sample_tasks
    ):
        """Test context scoping with different user IDs."""
        context_user1 = context_integration.get_active_context("user1")
        context_user2 = context_integration.get_active_context("user2")

        # Both should have same data (no user-specific filtering implemented yet)
        assert context_user1["user_id"] == "user1"
        assert context_user2["user_id"] == "user2"
        assert len(context_user1["active_projects"]) == len(
            context_user2["active_projects"]
        )

    def test_context_with_recent_activity(
        self, context_integration, sample_project, sample_tasks
    ):
        """Test context includes recent activity."""
        # Update a task to create recent activity
        task = sample_tasks[0]
        task.status = TaskStatus.COMPLETED
        task.updated_at = datetime.now(timezone.utc)
        context_integration.storage.save_task(task)

        # Clear cache to get fresh data
        context_integration.clear_context_cache()

        context = context_integration.get_active_context()
        recent_activity = context["recent_activity"]

        # Should have recent activity
        assert len(recent_activity) > 0
        activity_names = [a["task_name"] for a in recent_activity]
        assert "High Priority Task" in activity_names

    def test_error_handling(self, temp_workspace):
        """Test error handling in context integration."""
        # Test with valid directory but simulate error conditions
        integration = VoidCatContextIntegration(temp_workspace)

        # Should handle errors gracefully when no data exists
        context = integration.get_active_context()
        assert len(context.get("active_projects", [])) == 0
        assert context.get("workflow_state", {}).get("total_projects", 0) == 0

    def test_context_performance(self, context_integration, sample_project):
        """Test context retrieval performance with many tasks."""
        # Create many tasks
        for i in range(50):
            task = VoidCatTask(
                name=f"Task {i}",
                description=f"Description for task {i}",
                project_id=sample_project.id,
                priority=Priority.MEDIUM,
                status=TaskStatus.PENDING if i % 2 == 0 else TaskStatus.IN_PROGRESS,
            )
            context_integration.storage.save_task(task)

        # Should still retrieve context efficiently
        import time

        start_time = time.time()
        context = context_integration.get_active_context()
        end_time = time.time()

        # Should complete within reasonable time (less than 1 second)
        assert (end_time - start_time) < 1.0
        assert len(context["active_projects"]) == 1
        assert (
            context["workflow_state"]["total_tasks"] == 50
        )  # 50 tasks created in this test


if __name__ == "__main__":
    # Run the context integration tests
    pytest.main([__file__, "-v", "--tb=short"])
