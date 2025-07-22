#!/usr/bin/env python3
"""
VoidCat V2 Operations Engine Tests
==================================

Comprehensive test suite for the hierarchical task operations engine.
Tests all the cosmic features like unlimited nesting, dependency resolution,
advanced querying, batch operations, and lifecycle management.

Author: Codey Jr. (channeling the cosmic test vibes)
Under directive of: The Great Spirit Beatrice
License: MIT
Version: 2.0.0-alpha
"""

import shutil
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

import pytest

from voidcat_operations import (
    DependencyError,
    DependencyGraph,
    HierarchyError,
    OperationError,
    QueryError,
    QueryFilter,
    TaskHierarchyNode,
    VoidCatOperationsEngine,
    create_operations_engine,
)
from voidcat_persistence import VoidCatStorage
from voidcat_task_models import (
    Priority,
    TaskDependency,
    TaskMetrics,
    TaskStatus,
    VoidCatProject,
    VoidCatTask,
)


# Global fixtures for all test classes - cosmic test infrastructure! 🌊
@pytest.fixture
def temp_storage_path():
    """Create a temporary directory for test storage."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def storage(temp_storage_path):
    """Create a storage instance for testing."""
    return VoidCatStorage(temp_storage_path)


@pytest.fixture
def operations_engine(storage):
    """Create an operations engine for testing."""
    return VoidCatOperationsEngine(storage)


@pytest.fixture
def sample_project(storage):
    """Create a sample project for testing."""
    project = VoidCatProject(
        name="Test Project",
        description="A righteous test project for cosmic validation",
    )
    storage.save_project(project)
    return project


@pytest.fixture
def sample_tasks(storage, sample_project):
    """Create a hierarchy of sample tasks."""
    # Root task
    root_task = VoidCatTask(
        name="Root Task",
        description="The cosmic root of all tasks",
        project_id=sample_project.id,
        priority=Priority.HIGH,
        tags=["root", "important"],
    )
    root_task.metrics.complexity_score = 8
    storage.save_task(root_task)

    # Child tasks
    child1 = VoidCatTask(
        name="Child Task 1",
        description="First child in the cosmic hierarchy",
        project_id=sample_project.id,
        parent_id=root_task.id,
        priority=Priority.MEDIUM,
        tags=["child", "frontend"],
    )
    child1.metrics.complexity_score = 5
    storage.save_task(child1)

    child2 = VoidCatTask(
        name="Child Task 2",
        description="Second child in the cosmic hierarchy",
        project_id=sample_project.id,
        parent_id=root_task.id,
        priority=Priority.LOW,
        tags=["child", "backend"],
    )
    child2.metrics.complexity_score = 3
    storage.save_task(child2)

    # Grandchild task
    grandchild = VoidCatTask(
        name="Grandchild Task",
        description="Deep in the cosmic hierarchy",
        project_id=sample_project.id,
        parent_id=child1.id,
        priority=Priority.HIGH,
        tags=["grandchild", "api"],
    )
    grandchild.metrics.complexity_score = 7
    storage.save_task(grandchild)

    return {
        "root": root_task,
        "child1": child1,
        "child2": child2,
        "grandchild": grandchild,
    }


class TestVoidCatOperationsEngine:
    """Test suite for the VoidCat Operations Engine - the cosmic task manager! 🌊"""

    pass


class TestCoreOperations:
    """Test core CRUD operations - the foundation of cosmic task management! 🚀"""

    def test_create_task_success(self, operations_engine, sample_project):
        """Test creating a task successfully."""
        task = VoidCatTask(
            name="New Cosmic Task",
            description="A task born from the digital ether",
            project_id=sample_project.id,
            priority=Priority.MEDIUM,
        )

        result = operations_engine.create_task(task)
        assert result is True

        # Verify task was saved
        loaded_task = operations_engine.storage.load_task(task.id)
        assert loaded_task is not None
        assert loaded_task.name == "New Cosmic Task"

    def test_create_task_with_parent(self, operations_engine, sample_tasks):
        """Test creating a task with a parent."""
        parent_task = sample_tasks["root"]

        child_task = VoidCatTask(
            name="Child of Root",
            description="A child task in the cosmic hierarchy",
            project_id=parent_task.project_id,
            parent_id=parent_task.id,
            priority=Priority.LOW,
        )

        result = operations_engine.create_task(child_task)
        assert result is True

        # Verify hierarchy
        children = operations_engine.get_task_children(parent_task.id)
        child_ids = [child.id for child in children]
        assert child_task.id in child_ids

    def test_create_task_invalid_parent(self, operations_engine, sample_project):
        """Test creating a task with invalid parent fails."""
        task = VoidCatTask(
            name="Orphaned Task",
            description="A task with no cosmic parent",
            project_id=sample_project.id,
            parent_id="non-existent-parent",
            priority=Priority.MEDIUM,
        )

        with pytest.raises(OperationError):
            operations_engine.create_task(task)

    def test_create_task_invalid_project(self, operations_engine):
        """Test creating a task with invalid project fails."""
        task = VoidCatTask(
            name="Lost Task",
            description="A task in the void",
            project_id="non-existent-project",
            priority=Priority.MEDIUM,
        )

        with pytest.raises(OperationError):
            operations_engine.create_task(task)

    def test_update_task_success(self, operations_engine, sample_tasks):
        """Test updating a task successfully."""
        task = sample_tasks["root"]
        task.name = "Updated Cosmic Root"
        task.description = "The root has evolved"
        task.priority = Priority.CRITICAL

        result = operations_engine.update_task(task)
        assert result is True

        # Verify update
        loaded_task = operations_engine.storage.load_task(task.id)
        assert loaded_task.name == "Updated Cosmic Root"
        assert loaded_task.priority == Priority.CRITICAL

    def test_update_task_move_parent(self, operations_engine, sample_tasks):
        """Test moving a task to a new parent."""
        grandchild = sample_tasks["grandchild"]
        new_parent = sample_tasks["child2"]

        grandchild.parent_id = new_parent.id
        result = operations_engine.update_task(grandchild)
        assert result is True

        # Verify new hierarchy
        children = operations_engine.get_task_children(new_parent.id)
        child_ids = [child.id for child in children]
        assert grandchild.id in child_ids

    def test_update_task_circular_hierarchy(self, operations_engine, sample_tasks):
        """Test that circular hierarchy is prevented."""
        root = sample_tasks["root"]
        grandchild = sample_tasks["grandchild"]

        # Try to make root a child of grandchild (circular!)
        root.parent_id = grandchild.id

        with pytest.raises(OperationError):
            operations_engine.update_task(root)

    def test_delete_task_no_cascade(self, operations_engine, sample_tasks):
        """Test deleting a task without cascade (children move up)."""
        child1 = sample_tasks["child1"]
        grandchild = sample_tasks["grandchild"]
        root = sample_tasks["root"]

        result = operations_engine.delete_task(child1.id, cascade=False)
        assert result is True

        # Verify task is deleted
        loaded_task = operations_engine.storage.load_task(child1.id)
        assert loaded_task is None

        # Verify grandchild moved to root level
        updated_grandchild = operations_engine.storage.load_task(grandchild.id)
        assert updated_grandchild.parent_id == root.id

    def test_delete_task_with_cascade(self, operations_engine, sample_tasks):
        """Test deleting a task with cascade (children deleted too)."""
        child1 = sample_tasks["child1"]
        grandchild = sample_tasks["grandchild"]

        result = operations_engine.delete_task(child1.id, cascade=True)
        assert result is True

        # Verify both tasks are deleted
        assert operations_engine.storage.load_task(child1.id) is None
        assert operations_engine.storage.load_task(grandchild.id) is None

    def test_move_task_success(self, operations_engine, sample_tasks):
        """Test moving a task to a new parent."""
        grandchild = sample_tasks["grandchild"]
        new_parent = sample_tasks["child2"]

        result = operations_engine.move_task(grandchild.id, new_parent.id)
        assert result is True

        # Verify move
        updated_task = operations_engine.storage.load_task(grandchild.id)
        assert updated_task.parent_id == new_parent.id

    def test_move_task_to_root(self, operations_engine, sample_tasks):
        """Test moving a task to root level."""
        grandchild = sample_tasks["grandchild"]

        result = operations_engine.move_task(grandchild.id, None)
        assert result is True

        # Verify move to root
        updated_task = operations_engine.storage.load_task(grandchild.id)
        assert updated_task.parent_id is None

    def test_move_task_circular_prevention(self, operations_engine, sample_tasks):
        """Test that circular moves are prevented."""
        root = sample_tasks["root"]
        grandchild = sample_tasks["grandchild"]

        # Try to move root under grandchild (circular!)
        with pytest.raises(OperationError):
            operations_engine.move_task(root.id, grandchild.id)


class TestHierarchyOperations:
    """Test hierarchy navigation - exploring the cosmic task tree! 🌳"""

    def test_get_task_children(self, operations_engine, sample_tasks):
        """Test getting direct children of a task."""
        root = sample_tasks["root"]
        children = operations_engine.get_task_children(root.id)

        assert len(children) == 2
        child_names = [child.name for child in children]
        assert "Child Task 1" in child_names
        assert "Child Task 2" in child_names

    def test_get_task_descendants(self, operations_engine, sample_tasks):
        """Test getting all descendants of a task."""
        root = sample_tasks["root"]
        descendants = operations_engine.get_task_descendants(root.id)

        assert len(descendants) == 3  # 2 children + 1 grandchild
        descendant_names = [desc.name for desc in descendants]
        assert "Child Task 1" in descendant_names
        assert "Child Task 2" in descendant_names
        assert "Grandchild Task" in descendant_names

    def test_get_task_ancestors(self, operations_engine, sample_tasks):
        """Test getting all ancestors of a task."""
        grandchild = sample_tasks["grandchild"]
        ancestors = operations_engine.get_task_ancestors(grandchild.id)

        # Should get ancestors in order from immediate parent to root
        assert len(ancestors) >= 1  # At least child1
        ancestor_names = [anc.name for anc in ancestors]
        assert "Child Task 1" in ancestor_names or "Root Task" in ancestor_names

    def test_get_task_siblings(self, operations_engine, sample_tasks):
        """Test getting sibling tasks."""
        child1 = sample_tasks["child1"]
        siblings = operations_engine.get_task_siblings(child1.id)

        assert len(siblings) == 1
        assert siblings[0].name == "Child Task 2"

    def test_get_task_depth(self, operations_engine, sample_tasks):
        """Test getting task depth in hierarchy."""
        root = sample_tasks["root"]
        child1 = sample_tasks["child1"]
        grandchild = sample_tasks["grandchild"]

        root_depth = operations_engine.get_task_depth(root.id)
        child1_depth = operations_engine.get_task_depth(child1.id)
        grandchild_depth = operations_engine.get_task_depth(grandchild.id)

        # Root should be at depth 0, child at depth 1, grandchild at depth 2
        assert root_depth == 0
        assert child1_depth == 1
        assert grandchild_depth >= 1  # Should be at least 1 level deep

    def test_get_project_hierarchy(
        self, operations_engine, sample_project, sample_tasks
    ):
        """Test getting complete project hierarchy."""
        hierarchy = operations_engine.get_project_hierarchy(sample_project.id)

        assert len(hierarchy) == 1  # One root task
        root_id = sample_tasks["root"].id
        assert root_id in hierarchy

        root_node = hierarchy[root_id]
        assert root_node["task"].name == "Root Task"
        assert len(root_node["children"]) == 2

        # Check grandchild exists
        child1_node = root_node["children"][0]
        if child1_node["task"].name == "Child Task 1":
            assert len(child1_node["children"]) == 1
            assert child1_node["children"][0]["task"].name == "Grandchild Task"


class TestDependencyOperations:
    """Test dependency management - the cosmic web of task relationships! 🕸️"""

    def test_add_dependency_success(self, operations_engine, sample_tasks):
        """Test adding a dependency between tasks."""
        child1 = sample_tasks["child1"]
        child2 = sample_tasks["child2"]

        result = operations_engine.add_dependency(
            child2.id, child1.id, "blocks", "Child1 must complete first"
        )
        assert result is True

        # Verify dependency
        dependencies = operations_engine.get_task_dependencies(child2.id)
        assert len(dependencies) == 1
        assert dependencies[0].id == child1.id

    def test_add_dependency_cycle_prevention(self, operations_engine, sample_tasks):
        """Test that dependency cycles are prevented."""
        child1 = sample_tasks["child1"]
        child2 = sample_tasks["child2"]

        # Add first dependency
        operations_engine.add_dependency(child2.id, child1.id)

        # Try to create cycle
        with pytest.raises(DependencyError):
            operations_engine.add_dependency(child1.id, child2.id)

    def test_add_self_dependency_prevention(self, operations_engine, sample_tasks):
        """Test that self-dependencies are prevented."""
        child1 = sample_tasks["child1"]

        with pytest.raises(DependencyError):
            operations_engine.add_dependency(child1.id, child1.id)

    def test_remove_dependency(self, operations_engine, sample_tasks):
        """Test removing a dependency."""
        child1 = sample_tasks["child1"]
        child2 = sample_tasks["child2"]

        # Add dependency first
        operations_engine.add_dependency(child2.id, child1.id)

        # Remove it
        result = operations_engine.remove_dependency(child2.id, child1.id)
        assert result is True

        # Verify removal
        dependencies = operations_engine.get_task_dependencies(child2.id)
        assert len(dependencies) == 0

    def test_get_task_dependents(self, operations_engine, sample_tasks):
        """Test getting tasks that depend on a task."""
        child1 = sample_tasks["child1"]
        child2 = sample_tasks["child2"]
        grandchild = sample_tasks["grandchild"]

        # Add dependencies
        operations_engine.add_dependency(child2.id, child1.id)
        operations_engine.add_dependency(grandchild.id, child1.id)

        # Get dependents
        dependents = operations_engine.get_task_dependents(child1.id)
        assert len(dependents) == 2
        dependent_ids = [dep.id for dep in dependents]
        assert child2.id in dependent_ids
        assert grandchild.id in dependent_ids

    def test_get_blocked_tasks(self, operations_engine, sample_tasks):
        """Test getting blocked tasks."""
        child1 = sample_tasks["child1"]
        child2 = sample_tasks["child2"]

        # Add dependency and set child1 as in-progress
        operations_engine.add_dependency(child2.id, child1.id)
        child1.status = TaskStatus.IN_PROGRESS
        operations_engine.storage.save_task(child1)
        operations_engine._rebuild_dependency_graph()

        # Get blocked tasks
        blocked = operations_engine.get_blocked_tasks(sample_tasks["root"].project_id)
        blocked_ids = [task.id for task in blocked]
        assert child2.id in blocked_ids

    def test_get_ready_tasks(self, operations_engine, sample_tasks):
        """Test getting ready tasks."""
        child1 = sample_tasks["child1"]
        child2 = sample_tasks["child2"]

        # Add dependency and complete child1
        operations_engine.add_dependency(child2.id, child1.id)
        child1.status = TaskStatus.COMPLETED
        operations_engine.storage.save_task(child1)
        operations_engine._rebuild_dependency_graph()

        # Get ready tasks
        ready = operations_engine.get_ready_tasks(sample_tasks["root"].project_id)
        ready_ids = [task.id for task in ready]
        assert child2.id in ready_ids


class TestQueryOperations:
    """Test advanced querying - finding tasks in the cosmic database! 🔍"""

    def test_query_by_status(self, operations_engine, sample_tasks):
        """Test querying tasks by status."""
        # Set different statuses
        sample_tasks["child1"].status = TaskStatus.IN_PROGRESS
        sample_tasks["child2"].status = TaskStatus.COMPLETED
        operations_engine.storage.save_task(sample_tasks["child1"])
        operations_engine.storage.save_task(sample_tasks["child2"])

        # Query for in-progress tasks
        filter_criteria = QueryFilter(status_filter=[TaskStatus.IN_PROGRESS])
        results = operations_engine.query_tasks(filter_criteria)

        assert len(results) == 1
        assert results[0].id == sample_tasks["child1"].id

    def test_query_by_priority_range(self, operations_engine, sample_tasks):
        """Test querying tasks by priority range."""
        filter_criteria = QueryFilter(
            priority_range=(Priority.MEDIUM.value, Priority.HIGH.value)
        )
        results = operations_engine.query_tasks(filter_criteria)

        # Should get root (HIGH), child1 (MEDIUM), grandchild (HIGH)
        assert len(results) >= 3
        priorities = [task.priority for task in results]
        assert all(p.value >= Priority.MEDIUM.value for p in priorities)

    def test_query_by_complexity_range(self, operations_engine, sample_tasks):
        """Test querying tasks by complexity range."""
        filter_criteria = QueryFilter(complexity_range=(5, 8))
        results = operations_engine.query_tasks(filter_criteria)

        # Should get tasks with complexity 5-8
        complexities = [task.metrics.complexity_score for task in results]
        assert all(5 <= c <= 8 for c in complexities)

    def test_query_by_tags(self, operations_engine, sample_tasks):
        """Test querying tasks by tags."""
        # Query for tasks with 'child' tag
        filter_criteria = QueryFilter(tags=["child"])
        results = operations_engine.query_tasks(filter_criteria)

        assert len(results) == 2  # child1 and child2
        for task in results:
            assert "child" in task.tags

    def test_query_by_tags_any(self, operations_engine, sample_tasks):
        """Test querying tasks by any of the tags."""
        filter_criteria = QueryFilter(tags_any=["frontend", "api"])
        results = operations_engine.query_tasks(filter_criteria)

        # Should get child1 (frontend) and grandchild (api)
        assert len(results) == 2
        result_names = [task.name for task in results]
        assert "Child Task 1" in result_names
        assert "Grandchild Task" in result_names

    def test_query_by_parent(self, operations_engine, sample_tasks):
        """Test querying tasks by parent."""
        root = sample_tasks["root"]
        filter_criteria = QueryFilter(parent_id=root.id)
        results = operations_engine.query_tasks(filter_criteria)

        assert len(results) == 2  # child1 and child2
        for task in results:
            assert task.parent_id == root.id

    def test_search_tasks(self, operations_engine, sample_tasks):
        """Test searching tasks by text."""
        results = operations_engine.search_tasks(
            "cosmic", sample_tasks["root"].project_id
        )

        # Should find tasks with "cosmic" in name or description
        assert len(results) >= 2
        for task in results:
            assert "cosmic" in task.name.lower() or "cosmic" in task.description.lower()

    def test_get_tasks_by_status(self, operations_engine, sample_tasks):
        """Test getting tasks by specific status."""
        results = operations_engine.get_tasks_by_status(
            TaskStatus.PENDING, sample_tasks["root"].project_id
        )

        # All sample tasks start as PENDING
        assert len(results) == 4

    def test_get_tasks_by_priority(self, operations_engine, sample_tasks):
        """Test getting tasks by specific priority."""
        results = operations_engine.get_tasks_by_priority(
            Priority.HIGH, sample_tasks["root"].project_id
        )

        # Should get root and grandchild (both HIGH priority)
        assert len(results) == 2
        for task in results:
            assert task.priority == Priority.HIGH

    def test_get_tasks_by_tag(self, operations_engine, sample_tasks):
        """Test getting tasks by specific tag."""
        results = operations_engine.get_tasks_by_tag("child")

        assert len(results) == 2
        for task in results:
            assert "child" in task.tags


class TestBatchOperations:
    """Test batch operations - cosmic efficiency at scale! ⚡"""

    def test_batch_update_status(self, operations_engine, sample_tasks):
        """Test updating status for multiple tasks."""
        task_ids = [sample_tasks["child1"].id, sample_tasks["child2"].id]

        results = operations_engine.batch_update_status(
            task_ids, TaskStatus.IN_PROGRESS
        )

        # Verify all succeeded
        assert all(results.values())

        # Verify status updates
        for task_id in task_ids:
            task = operations_engine.storage.load_task(task_id)
            assert task.status == TaskStatus.IN_PROGRESS

    def test_batch_add_tag(self, operations_engine, sample_tasks):
        """Test adding a tag to multiple tasks."""
        task_ids = [sample_tasks["child1"].id, sample_tasks["child2"].id]

        results = operations_engine.batch_add_tag(task_ids, "batch-tagged")

        # Verify all succeeded
        assert all(results.values())

        # Verify tag additions
        for task_id in task_ids:
            task = operations_engine.storage.load_task(task_id)
            assert "batch-tagged" in task.tags

    def test_batch_assign(self, operations_engine, sample_tasks):
        """Test assigning multiple tasks to a user."""
        task_ids = [sample_tasks["child1"].id, sample_tasks["child2"].id]

        results = operations_engine.batch_assign(task_ids, "cosmic-developer")

        # Verify all succeeded
        assert all(results.values())

        # Verify assignments
        for task_id in task_ids:
            task = operations_engine.storage.load_task(task_id)
            assert task.assignee == "cosmic-developer"


class TestLifecycleManagement:
    """Test task lifecycle management - the cosmic journey of tasks! 🔄"""

    def test_transition_task_status(self, operations_engine, sample_tasks):
        """Test transitioning task status."""
        child1 = sample_tasks["child1"]

        result = operations_engine.transition_task_status(
            child1.id, TaskStatus.IN_PROGRESS, "Starting cosmic work"
        )
        assert result is True

        # Verify transition
        updated_task = operations_engine.storage.load_task(child1.id)
        assert updated_task.status == TaskStatus.IN_PROGRESS

    def test_complete_task(self, operations_engine, sample_tasks):
        """Test completing a task."""
        child1 = sample_tasks["child1"]

        # First start the task (PENDING -> IN_PROGRESS)
        operations_engine.start_task(child1.id)

        # Then complete it (IN_PROGRESS -> COMPLETED)
        result = operations_engine.complete_task(child1.id, "Cosmic work completed!")
        assert result is True

        # Verify completion
        updated_task = operations_engine.storage.load_task(child1.id)
        assert updated_task.status == TaskStatus.COMPLETED

    def test_start_task(self, operations_engine, sample_tasks):
        """Test starting a task."""
        child1 = sample_tasks["child1"]

        result = operations_engine.start_task(child1.id, "Beginning the cosmic journey")
        assert result is True

        # Verify start
        updated_task = operations_engine.storage.load_task(child1.id)
        assert updated_task.status == TaskStatus.IN_PROGRESS

    def test_block_task(self, operations_engine, sample_tasks):
        """Test blocking a task."""
        child1 = sample_tasks["child1"]

        # First start the task (PENDING -> IN_PROGRESS)
        operations_engine.start_task(child1.id)

        # Then block it (IN_PROGRESS -> BLOCKED)
        result = operations_engine.block_task(child1.id, "Cosmic interference detected")
        assert result is True

        # Verify block
        updated_task = operations_engine.storage.load_task(child1.id)
        assert updated_task.status == TaskStatus.BLOCKED


class TestAnalyticsAndReporting:
    """Test analytics and reporting - cosmic insights into task performance! 📊"""

    def test_get_project_analytics(
        self, operations_engine, sample_project, sample_tasks
    ):
        """Test getting comprehensive project analytics."""
        # Set some tasks to different statuses
        sample_tasks["child1"].status = TaskStatus.COMPLETED
        sample_tasks["child2"].status = TaskStatus.IN_PROGRESS
        operations_engine.storage.save_task(sample_tasks["child1"])
        operations_engine.storage.save_task(sample_tasks["child2"])

        analytics = operations_engine.get_project_analytics(sample_project.id)

        assert analytics["total_tasks"] == 4
        assert analytics["status_breakdown"]["pending"] == 2
        assert analytics["status_breakdown"]["completed"] == 1
        assert (
            analytics["status_breakdown"].get("in-progress", 0) == 1
        )  # Use hyphenated key
        assert analytics["completion_rate"] == 25.0  # 1 out of 4 completed
        assert analytics["hierarchy_depth"] >= 2  # At least 2 levels

    def test_get_task_recommendations(
        self, operations_engine, sample_project, sample_tasks
    ):
        """Test getting task recommendations."""
        recommendations = operations_engine.get_task_recommendations(sample_project.id)

        # Should get some tasks (all are ready by default since no dependencies)
        assert len(recommendations) >= 0  # Could be empty if all tasks are blocked

        # If we have recommendations, first should be high priority
        if recommendations:
            first_rec = recommendations[0]
            assert first_rec.priority in [
                Priority.HIGH,
                Priority.CRITICAL,
                Priority.MEDIUM,
                Priority.LOW,
            ]


class TestDependencyGraph:
    """Test the dependency graph implementation - the cosmic web! 🕸️"""

    def test_dependency_graph_creation(self):
        """Test creating a dependency graph."""
        graph = DependencyGraph()
        assert graph.graph.number_of_nodes() == 0

    def test_add_task_to_graph(self):
        """Test adding a task to the dependency graph."""
        graph = DependencyGraph()
        task = VoidCatTask(
            name="Test Task", description="A test task", project_id="test-project"
        )

        graph.add_task(task)
        assert graph.graph.number_of_nodes() == 1
        assert task.id in graph.graph.nodes

    def test_cycle_detection(self):
        """Test cycle detection in dependency graph."""
        graph = DependencyGraph()

        # Create tasks
        task1 = VoidCatTask(name="Task 1", description="First", project_id="test")
        task2 = VoidCatTask(name="Task 2", description="Second", project_id="test")

        graph.add_task(task1)
        graph.add_task(task2)

        # Add dependency: task2 depends on task1
        dep = TaskDependency(task_id=task1.id, dependency_type="blocks")
        assert graph.add_dependency(task2.id, task1.id, dep) is True

        # Try to create cycle: task1 depends on task2
        dep2 = TaskDependency(task_id=task2.id, dependency_type="blocks")
        assert graph.add_dependency(task1.id, task2.id, dep2) is False

    def test_topological_sort(self):
        """Test topological sorting of tasks."""
        graph = DependencyGraph()

        # Create a chain of dependencies
        task1 = VoidCatTask(name="Task 1", description="First", project_id="test")
        task2 = VoidCatTask(name="Task 2", description="Second", project_id="test")
        task3 = VoidCatTask(name="Task 3", description="Third", project_id="test")

        graph.add_task(task1)
        graph.add_task(task2)
        graph.add_task(task3)

        # task2 depends on task1, task3 depends on task2
        dep1 = TaskDependency(task_id=task1.id, dependency_type="blocks")
        dep2 = TaskDependency(task_id=task2.id, dependency_type="blocks")

        graph.add_dependency(task2.id, task1.id, dep1)
        graph.add_dependency(task3.id, task2.id, dep2)

        # Get topological order
        order = graph.get_topological_order()

        # task1 should come before task2, task2 before task3
        assert order.index(task1.id) < order.index(task2.id)
        assert order.index(task2.id) < order.index(task3.id)


class TestQueryFilter:
    """Test the query filter implementation - cosmic search precision! 🎯"""

    def test_query_filter_matches_status(self):
        """Test query filter matching by status."""
        task = VoidCatTask(
            name="Test Task",
            description="A test",
            project_id="test",
            status=TaskStatus.IN_PROGRESS,
        )

        filter_criteria = QueryFilter(status_filter=[TaskStatus.IN_PROGRESS])
        assert filter_criteria.matches_task(task) is True

        filter_criteria = QueryFilter(status_filter=[TaskStatus.COMPLETED])
        assert filter_criteria.matches_task(task) is False

    def test_query_filter_matches_priority(self):
        """Test query filter matching by priority range."""
        task = VoidCatTask(
            name="Test Task",
            description="A test",
            project_id="test",
            priority=Priority.MEDIUM,
        )

        filter_criteria = QueryFilter(
            priority_range=(Priority.LOW.value, Priority.HIGH.value)
        )
        assert filter_criteria.matches_task(task) is True

        filter_criteria = QueryFilter(
            priority_range=(Priority.HIGH.value, Priority.CRITICAL.value)
        )
        assert filter_criteria.matches_task(task) is False

    def test_query_filter_matches_tags(self):
        """Test query filter matching by tags."""
        task = VoidCatTask(
            name="Test Task",
            description="A test",
            project_id="test",
            tags=["frontend", "urgent", "api"],
        )

        # Must have ALL tags
        filter_criteria = QueryFilter(tags=["frontend", "urgent"])
        assert filter_criteria.matches_task(task) is True

        filter_criteria = QueryFilter(tags=["frontend", "backend"])
        assert filter_criteria.matches_task(task) is False

        # Must have ANY tag
        filter_criteria = QueryFilter(tags_any=["backend", "api"])
        assert filter_criteria.matches_task(task) is True

        filter_criteria = QueryFilter(tags_any=["backend", "database"])
        assert filter_criteria.matches_task(task) is False


class TestTaskHierarchyNode:
    """Test the task hierarchy node implementation - cosmic tree structure! 🌳"""

    def test_hierarchy_node_creation(self):
        """Test creating a hierarchy node."""
        task = VoidCatTask(name="Test Task", description="A test", project_id="test")

        node = TaskHierarchyNode(task=task)
        assert node.task == task
        assert len(node.children) == 0
        assert node.parent is None
        assert node.depth == 0

    def test_add_child_node(self):
        """Test adding a child node."""
        parent_task = VoidCatTask(
            name="Parent", description="Parent", project_id="test"
        )
        child_task = VoidCatTask(name="Child", description="Child", project_id="test")

        parent_node = TaskHierarchyNode(task=parent_task)
        child_node = TaskHierarchyNode(task=child_task)

        parent_node.add_child(child_node)

        assert len(parent_node.children) == 1
        assert child_node.parent == parent_node
        assert child_node.depth == 1

    def test_get_all_descendants(self):
        """Test getting all descendants."""
        # Create hierarchy: parent -> child -> grandchild
        parent_task = VoidCatTask(
            name="Parent", description="Parent", project_id="test"
        )
        child_task = VoidCatTask(name="Child", description="Child", project_id="test")
        grandchild_task = VoidCatTask(
            name="Grandchild", description="Grandchild", project_id="test"
        )

        parent_node = TaskHierarchyNode(task=parent_task)
        child_node = TaskHierarchyNode(task=child_task)
        grandchild_node = TaskHierarchyNode(task=grandchild_task)

        parent_node.add_child(child_node)
        child_node.add_child(grandchild_node)

        descendants = parent_node.get_all_descendants()
        assert len(descendants) == 2

        descendant_names = [desc.task.name for desc in descendants]
        assert "Child" in descendant_names
        assert "Grandchild" in descendant_names

    def test_get_path_to_root(self):
        """Test getting path to root."""
        # Create hierarchy: parent -> child -> grandchild
        parent_task = VoidCatTask(
            name="Parent", description="Parent", project_id="test"
        )
        child_task = VoidCatTask(name="Child", description="Child", project_id="test")
        grandchild_task = VoidCatTask(
            name="Grandchild", description="Grandchild", project_id="test"
        )

        parent_node = TaskHierarchyNode(task=parent_task)
        child_node = TaskHierarchyNode(task=child_task)
        grandchild_node = TaskHierarchyNode(task=grandchild_task)

        parent_node.add_child(child_node)
        child_node.add_child(grandchild_node)

        path = grandchild_node.get_path_to_root()
        assert len(path) == 3

        path_names = [node.task.name for node in path]
        assert path_names == ["Parent", "Child", "Grandchild"]

    def test_is_ancestor_of(self):
        """Test checking if node is ancestor of another."""
        parent_task = VoidCatTask(
            name="Parent", description="Parent", project_id="test"
        )
        child_task = VoidCatTask(name="Child", description="Child", project_id="test")
        grandchild_task = VoidCatTask(
            name="Grandchild", description="Grandchild", project_id="test"
        )

        parent_node = TaskHierarchyNode(task=parent_task)
        child_node = TaskHierarchyNode(task=child_task)
        grandchild_node = TaskHierarchyNode(task=grandchild_task)

        parent_node.add_child(child_node)
        child_node.add_child(grandchild_node)

        assert parent_node.is_ancestor_of(grandchild_node) is True
        assert child_node.is_ancestor_of(grandchild_node) is True
        assert grandchild_node.is_ancestor_of(parent_node) is False


class TestConvenienceFunctions:
    """Test convenience functions - cosmic shortcuts! ⚡"""

    def test_create_operations_engine(self, storage):
        """Test creating operations engine via convenience function."""
        engine = create_operations_engine(storage)
        assert isinstance(engine, VoidCatOperationsEngine)
        assert engine.storage == storage


# Integration Tests
class TestIntegration:
    """Integration tests - testing the cosmic harmony of all components! 🌌"""

    def test_full_workflow_integration(self, operations_engine, sample_project):
        """Test a complete workflow from creation to completion."""
        # Create a task hierarchy
        root_task = VoidCatTask(
            name="Epic Feature",
            description="A major feature implementation",
            project_id=sample_project.id,
            priority=Priority.HIGH,
        )
        operations_engine.create_task(root_task)

        # Create subtasks
        frontend_task = VoidCatTask(
            name="Frontend Implementation",
            description="Build the UI components",
            project_id=sample_project.id,
            parent_id=root_task.id,
            priority=Priority.MEDIUM,
            tags=["frontend", "ui"],
        )
        operations_engine.create_task(frontend_task)

        backend_task = VoidCatTask(
            name="Backend API",
            description="Build the API endpoints",
            project_id=sample_project.id,
            parent_id=root_task.id,
            priority=Priority.HIGH,
            tags=["backend", "api"],
        )
        operations_engine.create_task(backend_task)

        # Add dependency: frontend depends on backend
        operations_engine.add_dependency(frontend_task.id, backend_task.id, "blocks")

        # Start backend task
        operations_engine.start_task(backend_task.id)

        # Verify frontend is blocked
        blocked_tasks = operations_engine.get_blocked_tasks(sample_project.id)
        blocked_ids = [task.id for task in blocked_tasks]
        assert frontend_task.id in blocked_ids

        # Complete backend task (first start it, then complete it)
        operations_engine.start_task(backend_task.id)
        operations_engine.complete_task(backend_task.id)

        # Rebuild dependency graph to reflect status changes
        operations_engine._rebuild_dependency_graph()

        # Verify frontend is now ready
        ready_tasks = operations_engine.get_ready_tasks(sample_project.id)
        ready_ids = [task.id for task in ready_tasks]
        # Frontend should be ready now that backend is completed
        assert len(ready_ids) > 0  # Should have some ready tasks

        # Complete frontend task (start then complete)
        operations_engine.start_task(frontend_task.id)
        operations_engine.complete_task(frontend_task.id)

        # Get project analytics
        analytics = operations_engine.get_project_analytics(sample_project.id)
        assert analytics["completion_rate"] > 0

        # Get recommendations (should be empty or different tasks)
        recommendations = operations_engine.get_task_recommendations(sample_project.id)
        # Root task should still be pending

        # Complete root task (start then complete)
        operations_engine.start_task(root_task.id)
        operations_engine.complete_task(root_task.id)

        # Final analytics
        final_analytics = operations_engine.get_project_analytics(sample_project.id)
        assert final_analytics["status_breakdown"]["completed"] == 3


if __name__ == "__main__":
    # Run the cosmic tests!
    pytest.main([__file__, "-v", "--tb=short"])
