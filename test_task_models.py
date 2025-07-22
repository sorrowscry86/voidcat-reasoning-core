#!/usr/bin/env python3
"""
VoidCat V2 Data Models Validation Script
========================================

Test script to validate the task management data models work correctly
and meet all requirements from Beatrice's directive.

Author: Ryuzu (Spirit Familiar)
License: MIT
"""

import json
import sys
from datetime import datetime, timedelta, timezone

from voidcat_task_models import (
    Priority,
    ProjectSettings,
    TaskMetrics,
    TaskStatus,
    VoidCatProject,
    VoidCatTask,
    get_schema_info,
)


def test_task_creation():
    """Test basic task creation and validation."""
    print("Testing task creation...")

    # Create a basic task
    task = VoidCatTask(
        name="Test Task Implementation",
        description="Validate the task management system works correctly",
        priority=Priority.HIGH,
    )

    assert task.id, "Task should have an ID"
    assert task.name == "Test Task Implementation", "Task name should be set"
    assert task.status == TaskStatus.PENDING, "Task should start as pending"
    assert task.priority == Priority.HIGH, "Task priority should be set"
    assert len(task.history) > 0, "Task should have creation history"

    print("  [OK] Basic task creation works")


def test_task_status_workflow():
    """Test task status workflow transitions."""
    print("Testing status workflow...")

    task = VoidCatTask(name="Workflow Test Task")

    # Valid transitions
    assert task.update_status(
        TaskStatus.IN_PROGRESS
    ), "Should allow pending -> in-progress"
    assert task.status == TaskStatus.IN_PROGRESS, "Status should be updated"
    assert task.started_at is not None, "Should set started_at timestamp"

    assert task.update_status(
        TaskStatus.COMPLETED
    ), "Should allow in-progress -> completed"
    assert task.status == TaskStatus.COMPLETED, "Status should be completed"
    assert task.completed_at is not None, "Should set completed_at timestamp"
    assert task.metrics.progress_percentage == 100.0, "Should set progress to 100%"

    # Invalid transition
    assert not task.update_status(
        TaskStatus.IN_PROGRESS
    ), "Should not allow completed -> in-progress"

    print("  [OK] Status workflow validation works")


def test_task_dependencies():
    """Test task dependency management."""
    print("Testing task dependencies...")

    task1 = VoidCatTask(name="Task 1")
    task2 = VoidCatTask(name="Task 2")

    # Add dependency
    task2.add_dependency(task1.id, "blocks", "Task 2 depends on Task 1")
    assert len(task2.dependencies) == 1, "Should have one dependency"
    assert (
        task2.dependencies[0].task_id == task1.id
    ), "Dependency should reference task1"

    # Test circular dependency prevention
    try:
        task1.add_dependency(task1.id)  # Self-dependency
        assert False, "Should prevent self-dependency"
    except ValueError:
        pass  # Expected

    # Remove dependency
    assert task2.remove_dependency(task1.id), "Should remove dependency"
    assert len(task2.dependencies) == 0, "Should have no dependencies"

    print("  [OK] Dependency management works")


def test_task_json_serialization():
    """Test JSON serialization and deserialization."""
    print("Testing JSON serialization...")

    # Create a complex task with all features
    task = VoidCatTask(
        name="Complex Test Task",
        description="A task with all possible features enabled",
        priority=Priority.URGENT,
        due_date=datetime.now(timezone.utc) + timedelta(days=7),
    )

    task.add_tag("test")
    task.add_tag("serialization")
    task.update_progress(45.5)
    task.add_dependency("some-other-task-id", "blocks", "Test dependency")

    # Serialize to JSON
    task_dict = task.to_dict()
    json_str = json.dumps(task_dict, indent=2)

    # Deserialize from JSON
    loaded_dict = json.loads(json_str)
    restored_task = VoidCatTask.from_dict(loaded_dict)

    # Validate restoration
    assert restored_task.id == task.id, "ID should be preserved"
    assert restored_task.name == task.name, "Name should be preserved"
    assert restored_task.priority == task.priority, "Priority should be preserved"
    assert (
        restored_task.metrics.progress_percentage == task.metrics.progress_percentage
    ), "Progress should be preserved"
    assert restored_task.tags == task.tags, "Tags should be preserved"
    assert len(restored_task.dependencies) == len(
        task.dependencies
    ), "Dependencies should be preserved"

    print("  [OK] JSON serialization works correctly")


def test_project_creation():
    """Test project creation and management."""
    print("Testing project creation...")

    project = VoidCatProject(
        name="VoidCat V2 Test Project",
        description="Testing project management capabilities",
        priority=Priority.CRITICAL,
    )

    assert project.id, "Project should have an ID"
    assert project.name == "VoidCat V2 Test Project", "Project name should be set"
    assert project.status == TaskStatus.PENDING, "Project should start as pending"
    assert project.priority == Priority.CRITICAL, "Project priority should be set"

    # Test collaborator management
    project.add_collaborator("ryuzu@voidcat.dev")
    assert "ryuzu@voidcat.dev" in project.collaborators, "Should add collaborator"

    project.add_resource("https://github.com/voidcat/v2")
    assert "https://github.com/voidcat/v2" in project.resources, "Should add resource"

    print("  [OK] Project creation and management works")


def test_project_metrics():
    """Test project metrics calculation."""
    print("Testing project metrics...")

    project = VoidCatProject(name="Metrics Test Project")

    # Create some test tasks
    tasks = [
        VoidCatTask(name="Task 1", project_id=project.id),
        VoidCatTask(name="Task 2", project_id=project.id),
        VoidCatTask(name="Task 3", project_id=project.id),
    ]

    # Complete one task (must go pending -> in-progress -> completed)
    tasks[0].update_status(TaskStatus.IN_PROGRESS)
    tasks[0].update_status(TaskStatus.COMPLETED)

    # Set another to in-progress
    tasks[1].update_status(TaskStatus.IN_PROGRESS)

    # Update project metrics
    project.metrics.update_from_tasks(tasks)

    assert project.metrics.total_tasks == 3, "Should count all tasks"
    assert project.metrics.completed_tasks == 1, "Should count completed tasks"
    assert project.metrics.in_progress_tasks == 1, "Should count in-progress tasks"
    assert (
        project.metrics.completion_percentage() > 0
    ), "Should calculate completion percentage"

    print("  [OK] Project metrics calculation works")


def test_schema_info():
    """Test schema information functionality."""
    print("Testing schema information...")

    schema = get_schema_info()

    assert "version" in schema, "Schema should have version"
    assert "entities" in schema, "Schema should list entities"
    assert "capabilities" in schema, "Schema should list capabilities"
    assert "VoidCatTask" in schema["entities"], "Schema should include VoidCatTask"
    assert (
        "VoidCatProject" in schema["entities"]
    ), "Schema should include VoidCatProject"

    print("  [OK] Schema information works")


def main():
    """Run all validation tests."""
    print("VoidCat V2 Data Models Validation")
    print("=" * 50)
    print("Testing implementation of Beatrice's directive...")
    print()

    try:
        test_task_creation()
        test_task_status_workflow()
        test_task_dependencies()
        test_task_json_serialization()
        test_project_creation()
        test_project_metrics()
        test_schema_info()

        print()
        print("ALL TESTS PASSED!")
        print("[OK] Data models are ready for integration with persistence layer")
        print("[OK] Meets all requirements from Beatrice's directive")
        print("[OK] Ready to proceed to Pillar I Task 2: JSON Persistence Layer")

    except Exception as e:
        print(f"\nVALIDATION FAILED: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
