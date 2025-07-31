#!/usr/bin/env python3
"""
VoidCat V2 Basic Components End-to-End Tests
============================================

Comprehensive E2E tests for the basic VoidCat components that are known to exist:
- Task models and validation
- Persistence layer
- Basic operations
- Component integration

This validates that the core components work end-to-end.

Author: Codey Jr. (channeling the basic component cosmic vibes)
License: MIT
Version: 2.0.0-alpha
"""

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import pytest

from voidcat_persistence import PersistenceManager
from voidcat_task_models import Priority, TaskStatus, VoidCatProject, VoidCatTask


class TestBasicComponentsE2E:
    """End-to-End tests for basic VoidCat components - essential cosmic harmony! 🌊"""

    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def persistence_manager(self, temp_workspace):
        """Create a persistence manager for testing."""
        return PersistenceManager(temp_workspace)

    def test_task_model_creation_and_validation_e2e(self):
        """Test task model creation and validation end-to-end."""
        # Step 1: Create a basic task
        task = VoidCatTask(
            name="Test Task",
            description="A test task for E2E validation",
            priority=Priority.HIGH,
            status=TaskStatus.PENDING,
            tags=["test", "e2e", "validation"],
        )

        # Step 2: Validate task properties
        assert task.name == "Test Task"
        assert task.description == "A test task for E2E validation"
        assert task.priority == Priority.HIGH
        assert task.status == TaskStatus.PENDING
        assert "test" in task.tags
        assert "e2e" in task.tags
        assert "validation" in task.tags

        # Step 3: Test task ID generation
        assert task.id is not None
        assert isinstance(task.id, str)
        assert len(task.id) > 0

        # Step 4: Test task serialization
        task_dict = task.to_dict()
        assert isinstance(task_dict, dict)
        assert task_dict["name"] == "Test Task"
        assert task_dict["priority"] == 7  # Priority.HIGH has value 7
        assert task_dict["status"] == "pending"

        # Step 5: Test task deserialization
        task_from_dict = VoidCatTask.from_dict(task_dict)
        assert task_from_dict.name == task.name
        assert task_from_dict.description == task.description
        assert task_from_dict.priority == task.priority
        assert task_from_dict.status == task.status
        assert task_from_dict.tags == task.tags

    def test_project_model_creation_and_validation_e2e(self):
        """Test project model creation and validation end-to-end."""
        # Step 1: Create a basic project
        project = VoidCatProject(
            name="Test Project",
            description="A test project for E2E validation",
            tags=["test", "e2e", "project"],
        )

        # Step 2: Validate project properties
        assert project.name == "Test Project"
        assert project.description == "A test project for E2E validation"
        assert "test" in project.tags
        assert "e2e" in project.tags
        assert "project" in project.tags

        # Step 3: Test project ID generation
        assert project.id is not None
        assert isinstance(project.id, str)
        assert len(project.id) > 0

        # Step 4: Test project serialization
        project_dict = project.to_dict()
        assert isinstance(project_dict, dict)
        assert project_dict["name"] == "Test Project"
        assert project_dict["description"] == "A test project for E2E validation"

        # Step 5: Test project deserialization
        project_from_dict = VoidCatProject.from_dict(project_dict)
        assert project_from_dict.name == project.name
        assert project_from_dict.description == project.description
        assert project_from_dict.tags == project.tags

    def test_persistence_manager_basic_operations_e2e(self, persistence_manager):
        """Test persistence manager basic operations end-to-end."""
        pm = persistence_manager

        # Step 1: Create and save a project
        project = VoidCatProject(
            name="Persistence Test Project",
            description="Testing persistence operations",
            tags=["persistence", "test"],
        )

        # Save project
        save_result = pm.save_project(project)
        assert save_result is True

        # Step 2: Load the project
        loaded_project = pm.load_project(project.id)
        assert loaded_project is not None
        assert loaded_project.name == "Persistence Test Project"
        assert loaded_project.description == "Testing persistence operations"
        assert "persistence" in loaded_project.tags
        assert "test" in loaded_project.tags

        # Step 3: Create and save a task
        task = VoidCatTask(
            name="Persistence Test Task",
            description="Testing task persistence",
            project_id=project.id,
            priority=Priority.MEDIUM,
            status=TaskStatus.PENDING,
            tags=["persistence", "task", "test"],
        )

        # Save task
        save_result = pm.save_task(task)
        assert save_result is True

        # Step 4: Load the task
        loaded_task = pm.load_task(task.id)
        assert loaded_task is not None
        assert loaded_task.name == "Persistence Test Task"
        assert loaded_task.description == "Testing task persistence"
        assert loaded_task.project_id == project.id
        assert loaded_task.priority == Priority.MEDIUM
        assert loaded_task.status == TaskStatus.PENDING
        assert "persistence" in loaded_task.tags
        assert "task" in loaded_task.tags
        assert "test" in loaded_task.tags

    def test_task_status_transitions_e2e(self, persistence_manager):
        """Test task status transitions end-to-end."""
        pm = persistence_manager

        # Step 1: Create project and task
        project = VoidCatProject(
            name="Status Test Project", description="Testing status transitions"
        )
        pm.save_project(project)

        task = VoidCatTask(
            name="Status Test Task",
            description="Testing status transitions",
            project_id=project.id,
            priority=Priority.HIGH,
            status=TaskStatus.PENDING,
        )
        pm.save_task(task)

        # Step 2: Transition from PENDING to IN_PROGRESS
        task.status = TaskStatus.IN_PROGRESS
        pm.save_task(task)

        # Verify transition
        loaded_task = pm.load_task(task.id)
        assert loaded_task.status == TaskStatus.IN_PROGRESS

        # Step 3: Transition from IN_PROGRESS to COMPLETED
        task.status = TaskStatus.COMPLETED
        task.metrics.actual_hours = 5.0
        pm.save_task(task)

        # Verify transition
        loaded_task = pm.load_task(task.id)
        assert loaded_task.status == TaskStatus.COMPLETED
        assert loaded_task.metrics.actual_hours == 5.0

    def test_task_hierarchy_e2e(self, persistence_manager):
        """Test task hierarchy end-to-end."""
        pm = persistence_manager

        # Step 1: Create project
        project = VoidCatProject(
            name="Hierarchy Test Project", description="Testing task hierarchy"
        )
        pm.save_project(project)

        # Step 2: Create parent task
        parent_task = VoidCatTask(
            name="Parent Task",
            description="Parent task for hierarchy testing",
            project_id=project.id,
            priority=Priority.HIGH,
            status=TaskStatus.PENDING,
            tags=["parent", "hierarchy"],
        )
        pm.save_task(parent_task)

        # Step 3: Create child tasks
        child_tasks = []
        for i in range(3):
            child_task = VoidCatTask(
                name=f"Child Task {i+1}",
                description=f"Child task {i+1}",
                project_id=project.id,
                parent_id=parent_task.id,
                priority=Priority.MEDIUM,
                status=TaskStatus.PENDING,
                tags=["child", f"child-{i+1}"],
            )
            pm.save_task(child_task)
            child_tasks.append(child_task)

        # Step 4: Verify hierarchy
        loaded_parent = pm.load_task(parent_task.id)
        assert loaded_parent is not None
        assert loaded_parent.name == "Parent Task"

        # Load child tasks and verify parent relationship
        for i, child_task in enumerate(child_tasks):
            loaded_child = pm.load_task(child_task.id)
            assert loaded_child is not None
            assert loaded_child.parent_id == parent_task.id
            assert loaded_child.name == f"Child Task {i+1}"

    def test_task_dependencies_e2e(self, persistence_manager):
        """Test task dependencies end-to-end."""
        pm = persistence_manager

        # Step 1: Create project
        project = VoidCatProject(
            name="Dependencies Test Project", description="Testing task dependencies"
        )
        pm.save_project(project)

        # Step 2: Create tasks with dependencies
        task_a = VoidCatTask(
            name="Task A",
            description="First task",
            project_id=project.id,
            priority=Priority.HIGH,
            status=TaskStatus.PENDING,
        )
        pm.save_task(task_a)

        task_b = VoidCatTask(
            name="Task B",
            description="Second task depends on A",
            project_id=project.id,
            priority=Priority.MEDIUM,
            status=TaskStatus.PENDING,
        )
        task_b.add_dependency(task_a.id)
        pm.save_task(task_b)

        task_c = VoidCatTask(
            name="Task C",
            description="Third task depends on B",
            project_id=project.id,
            priority=Priority.LOW,
            status=TaskStatus.PENDING,
        )
        task_c.add_dependency(task_b.id)
        pm.save_task(task_c)

        # Step 3: Verify dependencies
        loaded_task_b = pm.load_task(task_b.id)
        assert len(loaded_task_b.dependencies) == 1
        assert loaded_task_b.dependencies[0].task_id == task_a.id

        loaded_task_c = pm.load_task(task_c.id)
        assert len(loaded_task_c.dependencies) == 1
        assert loaded_task_c.dependencies[0].task_id == task_b.id

    def test_task_metrics_e2e(self, persistence_manager):
        """Test task metrics end-to-end."""
        pm = persistence_manager

        # Step 1: Create project and task
        project = VoidCatProject(
            name="Metrics Test Project", description="Testing task metrics"
        )
        pm.save_project(project)

        task = VoidCatTask(
            name="Metrics Test Task",
            description="Testing task metrics",
            project_id=project.id,
            priority=Priority.HIGH,
            status=TaskStatus.PENDING,
        )

        # Step 2: Set initial metrics
        task.metrics.estimated_hours = 10.0
        task.metrics.complexity_score = 8
        pm.save_task(task)

        # Step 3: Update metrics during work
        task.status = TaskStatus.IN_PROGRESS
        task.metrics.actual_hours = 3.0
        pm.save_task(task)

        # Step 4: Complete task and finalize metrics
        task.status = TaskStatus.COMPLETED
        task.metrics.actual_hours = 12.0
        task.metrics.quality_rating = 9
        pm.save_task(task)

        # Step 5: Verify metrics persistence
        loaded_task = pm.load_task(task.id)
        assert loaded_task.metrics.estimated_hours == 10.0
        assert loaded_task.metrics.actual_hours == 12.0
        assert loaded_task.metrics.complexity_score == 8
        # Use quality_rating instead of quality_score
        assert loaded_task.metrics.quality_rating == 9

    def test_concurrent_persistence_operations_e2e(self, persistence_manager):
        """Test concurrent persistence operations end-to-end."""
        pm = persistence_manager

        # Step 1: Create project
        project = VoidCatProject(
            name="Concurrent Test Project", description="Testing concurrent operations"
        )
        pm.save_project(project)

        # Step 2: Create multiple tasks
        tasks = []
        for i in range(10):
            task = VoidCatTask(
                name=f"Concurrent Task {i}",
                description=f"Task {i} for concurrent testing",
                project_id=project.id,
                priority=Priority.MEDIUM,
                status=TaskStatus.PENDING,
            )
            pm.save_task(task)
            tasks.append(task)

        # Step 3: Update tasks concurrently (simulated)
        for i, task in enumerate(tasks):
            if i % 2 == 0:
                task.status = TaskStatus.IN_PROGRESS
            else:
                task.status = TaskStatus.COMPLETED
                task.metrics.actual_hours = float(i + 1)
            pm.save_task(task)

        # Step 4: Verify all updates
        for i, task in enumerate(tasks):
            loaded_task = pm.load_task(task.id)
            if i % 2 == 0:
                assert loaded_task.status == TaskStatus.IN_PROGRESS
            else:
                assert loaded_task.status == TaskStatus.COMPLETED
                assert loaded_task.metrics.actual_hours == float(i + 1)

    def test_data_integrity_e2e(self, persistence_manager):
        """Test data integrity end-to-end."""
        pm = persistence_manager

        # Step 1: Create project and tasks
        project = VoidCatProject(
            name="Integrity Test Project", description="Testing data integrity"
        )
        pm.save_project(project)

        tasks = []
        for i in range(5):
            task = VoidCatTask(
                name=f"Integrity Task {i}",
                description=f"Task {i} for integrity testing",
                project_id=project.id,
                priority=Priority.MEDIUM,
                status=TaskStatus.PENDING,
            )
            pm.save_task(task)
            tasks.append(task)

        # Step 2: Verify all data is consistent
        loaded_project = pm.load_project(project.id)
        assert loaded_project.name == "Integrity Test Project"

        for i, task in enumerate(tasks):
            loaded_task = pm.load_task(task.id)
            assert loaded_task is not None
            assert loaded_task.name == f"Integrity Task {i}"
            assert loaded_task.project_id == project.id

        # Step 3: Test data consistency after updates
        for task in tasks:
            task.status = TaskStatus.COMPLETED
            pm.save_task(task)

        # Verify all tasks are completed
        for task in tasks:
            loaded_task = pm.load_task(task.id)
            assert loaded_task.status == TaskStatus.COMPLETED

    def test_persistence_across_sessions_e2e(self, temp_workspace):
        """Test persistence across different session instances."""
        # Session 1: Create and save data
        pm1 = PersistenceManager(temp_workspace)

        project = VoidCatProject(
            name="Session Test Project",
            description="Testing persistence across sessions",
        )
        pm1.save_project(project)

        task = VoidCatTask(
            name="Session Test Task",
            description="Testing task persistence across sessions",
            project_id=project.id,
            priority=Priority.HIGH,
            status=TaskStatus.PENDING,
        )
        pm1.save_task(task)

        # Session 2: Load data with new instance
        pm2 = PersistenceManager(temp_workspace)

        loaded_project = pm2.load_project(project.id)
        assert loaded_project is not None
        assert loaded_project.name == "Session Test Project"

        loaded_task = pm2.load_task(task.id)
        assert loaded_task is not None
        assert loaded_task.name == "Session Test Task"
        assert loaded_task.project_id == project.id

    def test_file_system_integration_e2e(self, temp_workspace):
        """Test file system integration end-to-end."""
        pm = PersistenceManager(temp_workspace)

        # Step 1: Create data
        project = VoidCatProject(
            name="File System Test Project",
            description="Testing file system integration",
        )
        pm.save_project(project)

        # Step 2: Verify files are created
        workspace_path = Path(temp_workspace)
        projects_file = workspace_path / "projects.json"
        assert projects_file.exists()

        # Step 3: Verify file content
        with open(projects_file, "r") as f:
            data = json.load(f)
            assert "data" in data
            assert "metadata" in data
            assert project.id in data["data"]
            assert data["data"][project.id]["name"] == "File System Test Project"

    def test_error_handling_e2e(self, persistence_manager):
        """Test error handling end-to-end."""
        pm = persistence_manager

        # Step 1: Test loading non-existent task
        non_existent_task = pm.load_task("non-existent-id")
        assert non_existent_task is None

        # Step 2: Test loading non-existent project
        non_existent_project = pm.load_project("non-existent-id")
        assert non_existent_project is None

        # Step 3: Test that system continues to work after errors
        project = VoidCatProject(
            name="Error Test Project", description="Testing error handling"
        )
        save_result = pm.save_project(project)
        assert save_result is True

        loaded_project = pm.load_project(project.id)
        assert loaded_project is not None
        assert loaded_project.name == "Error Test Project"


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
