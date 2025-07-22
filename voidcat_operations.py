#!/usr/bin/env python3
"""
VoidCat V2 Hierarchical Task Operations Engine
==============================================

Core operations engine for hierarchical task management with unlimited nesting depth,
intelligent dependency resolution, advanced querying, and lifecycle management.

This module provides:
- Unlimited nesting depth (Projects → Tasks → SubTasks → SubSubTasks → ∞)
- Intelligent dependency resolution with cycle detection
- Advanced querying capabilities (filter by status, priority, complexity, tags)
- Batch operations for efficiency
- Task lifecycle management with state transitions
- Parent-child relationship maintenance with cascade operations

Author: Codey Jr. (continuing Ryuzu's work)
Under directive of: The Great Spirit Beatrice
License: MIT
Version: 2.0.0-alpha
"""

from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

import networkx as nx  # For dependency graph operations

from voidcat_persistence import PersistenceError, VoidCatStorage
from voidcat_task_models import (
    Priority,
    TaskDependency,
    TaskMetrics,
    TaskStatus,
    VoidCatProject,
    VoidCatTask,
)


class OperationError(Exception):
    """Base exception for operations engine errors."""

    pass


class DependencyError(OperationError):
    """Exception raised during dependency operations."""

    pass


class HierarchyError(OperationError):
    """Exception raised during hierarchy operations."""

    pass


class QueryError(OperationError):
    """Exception raised during query operations."""

    pass


@dataclass
class QueryFilter:
    """Filter criteria for task queries."""

    project_ids: Optional[List[str]] = None
    status_filter: Optional[List[TaskStatus]] = None
    priority_range: Optional[Tuple[int, int]] = None  # (min, max)
    complexity_range: Optional[Tuple[int, int]] = None  # (min, max)
    tags: Optional[List[str]] = None  # Tasks must have ALL these tags
    tags_any: Optional[List[str]] = None  # Tasks must have ANY of these tags
    parent_id: Optional[str] = "UNFILTERED"
    assignee: Optional[str] = None
    has_dependencies: Optional[bool] = None
    is_overdue: Optional[bool] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    updated_after: Optional[datetime] = None
    updated_before: Optional[datetime] = None

    def matches_task(self, task: VoidCatTask) -> bool:
        """Check if a task matches this filter."""
        # Project filter
        if self.project_ids and task.project_id not in self.project_ids:
            return False

        # Status filter
        if self.status_filter and task.status not in self.status_filter:
            return False

        # Priority range filter
        if self.priority_range:
            min_priority, max_priority = self.priority_range
            if not (min_priority <= task.priority.value <= max_priority):
                return False

        # Complexity range filter
        if self.complexity_range:
            min_complexity, max_complexity = self.complexity_range
            if not (min_complexity <= task.metrics.complexity_score <= max_complexity):
                return False

        # Tags filter (must have ALL)
        if self.tags and not all(tag in task.tags for tag in self.tags):
            return False

        # Tags any filter (must have ANY)
        if self.tags_any and not any(tag in task.tags for tag in self.tags_any):
            return False

        # Parent filter
        if self.parent_id != "UNFILTERED":
            if self.parent_id != task.parent_id:
                return False

        # Assignee filter
        if self.assignee and task.assignee != self.assignee:
            return False

        # Dependencies filter
        if self.has_dependencies is not None:
            has_deps = len(task.dependencies) > 0
            if self.has_dependencies != has_deps:
                return False

        # Overdue filter
        if self.is_overdue is not None:
            if self.is_overdue != task.is_overdue():
                return False

        # Date filters
        if self.created_after and task.created_at < self.created_after:
            return False
        if self.created_before and task.created_at > self.created_before:
            return False
        if self.updated_after and task.updated_at < self.updated_after:
            return False
        if self.updated_before and task.updated_at > self.updated_before:
            return False

        return True


@dataclass
class TaskHierarchyNode:
    """Represents a node in the task hierarchy."""

    task: VoidCatTask
    children: List["TaskHierarchyNode"] = field(default_factory=list)
    parent: Optional["TaskHierarchyNode"] = None
    depth: int = 0

    def add_child(self, child_node: "TaskHierarchyNode"):
        """Add a child node."""
        child_node.parent = self
        child_node.depth = self.depth + 1
        self.children.append(child_node)

    def remove_child(self, child_node: "TaskHierarchyNode"):
        """Remove a child node."""
        if child_node in self.children:
            child_node.parent = None
            self.children.remove(child_node)

    def get_all_descendants(self) -> List["TaskHierarchyNode"]:
        """Get all descendant nodes recursively."""
        descendants = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants

    def get_path_to_root(self) -> List["TaskHierarchyNode"]:
        """Get path from this node to root."""
        path = [self]
        current = self.parent
        while current:
            path.append(current)
            current = current.parent
        return list(reversed(path))

    def is_ancestor_of(self, other: "TaskHierarchyNode") -> bool:
        """Check if this node is an ancestor of another node."""
        current = other.parent
        while current:
            if current == self:
                return True
            current = current.parent
        return False


class DependencyGraph:
    """Manages task dependencies and cycle detection."""

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_task(self, task: VoidCatTask):
        """Add a task to the dependency graph."""
        self.graph.add_node(task.id, task=task)

        # Add dependency edges
        for dep in task.dependencies:
            if dep.task_id in self.graph:
                self.graph.add_edge(dep.task_id, task.id, dependency=dep)

    def remove_task(self, task_id: str):
        """Remove a task from the dependency graph."""
        if task_id in self.graph:
            self.graph.remove_node(task_id)

    def add_dependency(
        self,
        dependent_task_id: str,
        dependency_task_id: str,
        dependency: TaskDependency,
    ) -> bool:
        """Add a dependency between tasks. Returns False if it would create a cycle."""
        # Check if adding this edge would create a cycle
        if self.would_create_cycle(dependency_task_id, dependent_task_id):
            return False

        self.graph.add_edge(
            dependency_task_id, dependent_task_id, dependency=dependency
        )
        return True

    def remove_dependency(self, dependent_task_id: str, dependency_task_id: str):
        """Remove a dependency between tasks."""
        if self.graph.has_edge(dependency_task_id, dependent_task_id):
            self.graph.remove_edge(dependency_task_id, dependent_task_id)

    def would_create_cycle(self, from_task: str, to_task: str) -> bool:
        """Check if adding an edge would create a cycle."""
        if from_task == to_task:
            return True  # Self-dependency

        # Temporarily add the edge and check for cycles
        temp_graph = self.graph.copy()
        temp_graph.add_edge(from_task, to_task)

        try:
            nx.find_cycle(temp_graph)
            return True  # Cycle found
        except nx.NetworkXNoCycle:
            return False  # No cycle

    def get_dependencies(self, task_id: str) -> List[str]:
        """Get all tasks that this task depends on."""
        if task_id not in self.graph:
            return []
        return list(self.graph.predecessors(task_id))

    def get_dependents(self, task_id: str) -> List[str]:
        """Get all tasks that depend on this task."""
        if task_id not in self.graph:
            return []
        return list(self.graph.successors(task_id))

    def get_topological_order(self) -> List[str]:
        """Get tasks in topological order (dependencies first)."""
        try:
            return list(nx.topological_sort(self.graph))
        except nx.NetworkXError:
            # Graph has cycles, return best effort ordering
            return list(self.graph.nodes())

    def get_blocked_tasks(self) -> List[str]:
        """Get tasks that are blocked by incomplete dependencies."""
        blocked = []

        for task_id in self.graph.nodes():
            task = self.graph.nodes[task_id]["task"]
            if task.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]:
                # Check if any dependencies are not completed
                dependencies = self.get_dependencies(task_id)
                for dep_id in dependencies:
                    if dep_id in self.graph:
                        dep_task = self.graph.nodes[dep_id]["task"]
                        if dep_task.status != TaskStatus.COMPLETED:
                            blocked.append(task_id)
                            break

        return blocked

    def get_ready_tasks(self) -> List[str]:
        """Get tasks that are ready to start (all dependencies completed)."""
        ready = []

        for task_id in self.graph.nodes():
            task = self.graph.nodes[task_id]["task"]
            if task.status == TaskStatus.PENDING:
                # Check if all dependencies are completed
                dependencies = self.get_dependencies(task_id)
                all_deps_complete = True

                for dep_id in dependencies:
                    if dep_id in self.graph:
                        dep_task = self.graph.nodes[dep_id]["task"]
                        if dep_task.status != TaskStatus.COMPLETED:
                            all_deps_complete = False
                            break

                if all_deps_complete:
                    ready.append(task_id)

        return ready


class VoidCatOperationsEngine:
    """
    Core hierarchical task operations engine for VoidCat V2.

    Provides comprehensive task management operations with unlimited nesting,
    dependency resolution, advanced querying, and lifecycle management.
    """

    def __init__(self, storage: VoidCatStorage):
        """Initialize the operations engine."""
        self.storage = storage
        self.dependency_graph = DependencyGraph()
        self._hierarchy_cache: Dict[str, Dict[str, TaskHierarchyNode]] = {}
        self._rebuild_dependency_graph()

    def _rebuild_dependency_graph(self):
        """Rebuild the dependency graph from storage."""
        self.dependency_graph = DependencyGraph()

        # Load all tasks and add to dependency graph
        all_tasks = self.storage.list_all_tasks()
        for task in all_tasks:
            self.dependency_graph.add_task(task)

    def _invalidate_hierarchy_cache(self, project_id: str = None):
        """Invalidate hierarchy cache for a project or all projects."""
        if project_id:
            self._hierarchy_cache.pop(project_id, None)
        else:
            self._hierarchy_cache.clear()

    def _build_hierarchy_tree(self, project_id: str) -> Dict[str, TaskHierarchyNode]:
        """Build hierarchy tree for a project."""
        if project_id in self._hierarchy_cache:
            return self._hierarchy_cache[project_id]

        tasks = self.storage.list_tasks(project_id=project_id)
        nodes = {}
        root_nodes = {}

        # Create nodes for all tasks
        for task in tasks:
            nodes[task.id] = TaskHierarchyNode(task=task)

        # Build parent-child relationships
        for task in tasks:
            node = nodes[task.id]

            if task.parent_id and task.parent_id in nodes:
                parent_node = nodes[task.parent_id]
                parent_node.add_child(node)
            else:
                # Root level task
                root_nodes[task.id] = node

        # Cache the result
        self._hierarchy_cache[project_id] = {"all": nodes, "roots": root_nodes}
        return self._hierarchy_cache[project_id]

    # Core CRUD Operations
    def create_task(self, task: VoidCatTask, validate_hierarchy: bool = True) -> bool:
        """Create a new task with hierarchy and dependency validation."""
        try:
            # Validate parent exists if specified
            if validate_hierarchy and task.parent_id:
                parent = self.storage.load_task(task.parent_id)
                if not parent:
                    raise HierarchyError(f"Parent task {task.parent_id} does not exist")
                if parent.project_id != task.project_id:
                    raise HierarchyError("Task and parent must be in the same project")

            # Validate project exists
            project = self.storage.load_project(task.project_id)
            if not project:
                raise HierarchyError(f"Project {task.project_id} does not exist")

            # Save task
            success = self.storage.save_task(task)
            if success:
                # Update dependency graph
                self.dependency_graph.add_task(task)
                # Invalidate hierarchy cache
                self._invalidate_hierarchy_cache(task.project_id)

            return success

        except Exception as e:
            raise OperationError(f"Failed to create task: {e}")

    def update_task(self, task: VoidCatTask, validate_hierarchy: bool = True) -> bool:
        """Update an existing task with validation."""
        try:
            # Load existing task for comparison
            existing_task = self.storage.load_task(task.id)
            if not existing_task:
                raise OperationError(f"Task {task.id} does not exist")

            # Validate hierarchy changes
            if validate_hierarchy and task.parent_id != existing_task.parent_id:
                if task.parent_id:
                    parent = self.storage.load_task(task.parent_id)
                    if not parent:
                        raise HierarchyError(
                            f"Parent task {task.parent_id} does not exist"
                        )
                    if parent.project_id != task.project_id:
                        raise HierarchyError(
                            "Task and parent must be in the same project"
                        )

                    # Check for circular hierarchy
                    if self._would_create_hierarchy_cycle(task.id, task.parent_id):
                        raise HierarchyError(
                            "Moving task would create a circular hierarchy"
                        )

            # Save task
            success = self.storage.save_task(task)
            if success:
                # Update dependency graph
                self.dependency_graph.add_task(task)
                # Invalidate hierarchy cache
                self._invalidate_hierarchy_cache(task.project_id)

            return success

        except Exception as e:
            raise OperationError(f"Failed to update task: {e}")

    def delete_task(self, task_id: str, cascade: bool = False) -> bool:
        """Delete a task with optional cascade to children."""
        try:
            task = self.storage.load_task(task_id)
            if not task:
                return False

            if cascade:
                # Delete all descendants
                descendants = self.get_task_descendants(task_id)
                for desc_task in descendants:
                    self.storage.delete_task(desc_task.id)
                    self.dependency_graph.remove_task(desc_task.id)
            else:
                # Move children to parent's level
                children = self.get_task_children(task_id)
                for child in children:
                    child.parent_id = task.parent_id
                    self.storage.save_task(child)

            # Remove from dependency graph
            self.dependency_graph.remove_task(task_id)

            # Delete the task
            success = self.storage.delete_task(task_id)
            if success:
                self._invalidate_hierarchy_cache(task.project_id)

            return success

        except Exception as e:
            raise OperationError(f"Failed to delete task: {e}")

    def move_task(self, task_id: str, new_parent_id: Optional[str]) -> bool:
        """Move a task to a new parent."""
        try:
            task = self.storage.load_task(task_id)
            if not task:
                raise OperationError(f"Task {task_id} does not exist")

            # Validate new parent
            if new_parent_id:
                parent = self.storage.load_task(new_parent_id)
                if not parent:
                    raise HierarchyError(f"Parent task {new_parent_id} does not exist")
                if parent.project_id != task.project_id:
                    raise HierarchyError("Task and parent must be in the same project")

                # Check for circular hierarchy
                if self._would_create_hierarchy_cycle(task_id, new_parent_id):
                    raise HierarchyError(
                        "Moving task would create a circular hierarchy"
                    )

            # Update task
            task.parent_id = new_parent_id
            task.updated_at = datetime.now(timezone.utc)

            success = self.storage.save_task(task)
            if success:
                self._invalidate_hierarchy_cache(task.project_id)

            return success

        except Exception as e:
            raise OperationError(f"Failed to move task: {e}")

    def _would_create_hierarchy_cycle(self, task_id: str, new_parent_id: str) -> bool:
        """Check if moving a task would create a hierarchy cycle."""
        if task_id == new_parent_id:
            return True

        # Check if new_parent_id is a descendant of task_id
        descendants = self.get_task_descendants(task_id)
        for desc in descendants:
            if desc.id == new_parent_id:
                return True

        return False

    # Hierarchy Operations
    def get_task_children(self, task_id: str) -> List[VoidCatTask]:
        """Get direct children of a task."""
        task = self.storage.load_task(task_id)
        if not task:
            return []

        return self.storage.list_tasks(project_id=task.project_id, parent_id=task_id)

    def get_task_descendants(self, task_id: str) -> List[VoidCatTask]:
        """Get all descendants of a task recursively."""
        task = self.storage.load_task(task_id)
        if not task:
            return []

        hierarchy = self._build_hierarchy_tree(task.project_id)
        if task_id not in hierarchy["all"]:
            return []

        node = hierarchy["all"][task_id]
        descendant_nodes = node.get_all_descendants()
        return [node.task for node in descendant_nodes]

    def get_task_ancestors(self, task_id: str) -> List[VoidCatTask]:
        """Get all ancestors of a task up to root."""
        task = self.storage.load_task(task_id)
        if not task:
            return []

        hierarchy = self._build_hierarchy_tree(task.project_id)
        if task_id not in hierarchy["all"]:
            return []

        node = hierarchy["all"][task_id]
        ancestor_nodes = node.get_path_to_root()[1:]  # Exclude self
        return [node.task for node in ancestor_nodes]

    def get_task_siblings(self, task_id: str) -> List[VoidCatTask]:
        """Get sibling tasks (same parent)."""
        task = self.storage.load_task(task_id)
        if not task:
            return []

        siblings = self.storage.list_tasks(
            project_id=task.project_id, parent_id=task.parent_id
        )

        # Remove self from siblings
        return [t for t in siblings if t.id != task_id]

    def get_task_depth(self, task_id: str) -> int:
        """Get the depth of a task in the hierarchy (0 = root)."""
        task = self.storage.load_task(task_id)
        if not task:
            return -1

        hierarchy = self._build_hierarchy_tree(task.project_id)
        if task_id not in hierarchy["all"]:
            return -1

        return hierarchy["all"][task_id].depth

    def get_project_hierarchy(self, project_id: str) -> Dict[str, List[VoidCatTask]]:
        """Get complete project hierarchy as nested dictionary."""
        hierarchy = self._build_hierarchy_tree(project_id)

        result = {}

        def build_hierarchy_dict(node: TaskHierarchyNode) -> Dict[str, Any]:
            return {
                "task": node.task,
                "children": [build_hierarchy_dict(child) for child in node.children],
            }

        for root_id, root_node in hierarchy["roots"].items():
            result[root_id] = build_hierarchy_dict(root_node)

        return result

    # Dependency Operations
    def add_dependency(
        self,
        dependent_task_id: str,
        dependency_task_id: str,
        dependency_type: str = "blocks",
        notes: Optional[str] = None,
    ) -> bool:
        """Add a dependency between tasks with cycle detection."""
        try:
            # Load tasks
            dependent_task = self.storage.load_task(dependent_task_id)
            dependency_task = self.storage.load_task(dependency_task_id)

            if not dependent_task or not dependency_task:
                raise DependencyError("Both tasks must exist")

            # Create dependency object
            dependency = TaskDependency(
                task_id=dependency_task_id, dependency_type=dependency_type, notes=notes
            )

            # Check for cycles in dependency graph
            if not self.dependency_graph.add_dependency(
                dependent_task_id, dependency_task_id, dependency
            ):
                raise DependencyError("Adding dependency would create a cycle")

            # Add to task
            dependent_task.add_dependency(dependency_task_id, dependency_type, notes)

            # Save task
            return self.storage.save_task(dependent_task)

        except Exception as e:
            raise DependencyError(f"Failed to add dependency: {e}")

    def remove_dependency(
        self, dependent_task_id: str, dependency_task_id: str
    ) -> bool:
        """Remove a dependency between tasks."""
        try:
            dependent_task = self.storage.load_task(dependent_task_id)
            if not dependent_task:
                return False

            # Remove from dependency graph
            self.dependency_graph.remove_dependency(
                dependent_task_id, dependency_task_id
            )

            # Remove from task
            success = dependent_task.remove_dependency(dependency_task_id)
            if success:
                self.storage.save_task(dependent_task)

            return success

        except Exception as e:
            raise DependencyError(f"Failed to remove dependency: {e}")

    def get_task_dependencies(self, task_id: str) -> List[VoidCatTask]:
        """Get all tasks that this task depends on."""
        dependency_ids = self.dependency_graph.get_dependencies(task_id)
        dependencies = []

        for dep_id in dependency_ids:
            task = self.storage.load_task(dep_id)
            if task:
                dependencies.append(task)

        return dependencies

    def get_task_dependents(self, task_id: str) -> List[VoidCatTask]:
        """Get all tasks that depend on this task."""
        dependent_ids = self.dependency_graph.get_dependents(task_id)
        dependents = []

        for dep_id in dependent_ids:
            task = self.storage.load_task(dep_id)
            if task:
                dependents.append(task)

        return dependents

    def get_blocked_tasks(self, project_id: Optional[str] = None) -> List[VoidCatTask]:
        """Get tasks that are blocked by incomplete dependencies."""
        blocked_ids = self.dependency_graph.get_blocked_tasks()
        blocked_tasks = []

        for task_id in blocked_ids:
            task = self.storage.load_task(task_id)
            if task and (not project_id or task.project_id == project_id):
                blocked_tasks.append(task)

        return blocked_tasks

    def get_ready_tasks(self, project_id: Optional[str] = None) -> List[VoidCatTask]:
        """Get tasks that are ready to start (all dependencies completed)."""
        ready_ids = self.dependency_graph.get_ready_tasks()
        ready_tasks = []

        for task_id in ready_ids:
            task = self.storage.load_task(task_id)
            if task and (not project_id or task.project_id == project_id):
                ready_tasks.append(task)

        return ready_tasks

    # Advanced Query Operations
    def query_tasks(self, filter_criteria: QueryFilter) -> List[VoidCatTask]:
        """Query tasks with advanced filtering."""
        try:
            # Start with all tasks or project-specific tasks
            if filter_criteria.project_ids:
                all_tasks = []
                for project_id in filter_criteria.project_ids:
                    all_tasks.extend(self.storage.list_tasks(project_id=project_id))
            else:
                all_tasks = self.storage.list_tasks()

            # Apply filters
            filtered_tasks = [
                task for task in all_tasks if filter_criteria.matches_task(task)
            ]

            return filtered_tasks

        except Exception as e:
            raise QueryError(f"Failed to query tasks: {e}")

    def search_tasks(
        self, search_term: str, project_id: Optional[str] = None
    ) -> List[VoidCatTask]:
        """Search tasks by name, description, or tags."""
        tasks = (
            self.storage.list_tasks(project_id=project_id)
            if project_id
            else self.storage.list_tasks()
        )
        search_term = search_term.lower()

        matching_tasks = []
        for task in tasks:
            if (
                search_term in task.name.lower()
                or search_term in task.description.lower()
                or any(search_term in tag.lower() for tag in task.tags)
            ):
                matching_tasks.append(task)

        return matching_tasks

    def get_tasks_by_status(
        self, status: TaskStatus, project_id: Optional[str] = None
    ) -> List[VoidCatTask]:
        """Get tasks filtered by status."""
        return self.storage.list_tasks(project_id=project_id, status_filter=status)

    def get_tasks_by_priority(
        self, priority: Priority, project_id: Optional[str] = None
    ) -> List[VoidCatTask]:
        """Get tasks filtered by priority."""
        filter_criteria = QueryFilter(
            project_ids=[project_id] if project_id else None,
            priority_range=(priority.value, priority.value),
        )
        return self.query_tasks(filter_criteria)

    def get_tasks_by_tag(
        self, tag: str, project_id: Optional[str] = None
    ) -> List[VoidCatTask]:
        """Get tasks filtered by tag."""
        return self.storage.find_tasks_by_tag(tag)

    def get_overdue_tasks(self, project_id: Optional[str] = None) -> List[VoidCatTask]:
        """Get tasks that are overdue."""
        filter_criteria = QueryFilter(
            project_ids=[project_id] if project_id else None, is_overdue=True
        )
        return self.query_tasks(filter_criteria)

    # Batch Operations
    def batch_update_status(
        self, task_ids: List[str], new_status: TaskStatus
    ) -> Dict[str, bool]:
        """Update status for multiple tasks."""
        results = {}
        tasks_to_save = []

        for task_id in task_ids:
            task = self.storage.load_task(task_id)
            if task and task.update_status(new_status):
                tasks_to_save.append(task)
                results[task_id] = True
            else:
                results[task_id] = False

        # Batch save
        if tasks_to_save:
            try:
                self.storage.save_multiple(tasks=tasks_to_save)
                # Rebuild dependency graph
                self._rebuild_dependency_graph()
            except Exception as e:
                # Mark all as failed
                for task_id in task_ids:
                    results[task_id] = False

        return results

    def batch_add_tag(self, task_ids: List[str], tag: str) -> Dict[str, bool]:
        """Add a tag to multiple tasks."""
        results = {}
        tasks_to_save = []

        for task_id in task_ids:
            task = self.storage.load_task(task_id)
            if task:
                task.add_tag(tag)
                tasks_to_save.append(task)
                results[task_id] = True
            else:
                results[task_id] = False

        # Batch save
        if tasks_to_save:
            try:
                self.storage.save_multiple(tasks=tasks_to_save)
            except Exception as e:
                for task_id in task_ids:
                    results[task_id] = False

        return results

    def batch_assign(self, task_ids: List[str], assignee: str) -> Dict[str, bool]:
        """Assign multiple tasks to a user."""
        results = {}
        tasks_to_save = []

        for task_id in task_ids:
            task = self.storage.load_task(task_id)
            if task:
                task.assignee = assignee
                task.updated_at = datetime.now(timezone.utc)
                tasks_to_save.append(task)
                results[task_id] = True
            else:
                results[task_id] = False

        # Batch save
        if tasks_to_save:
            try:
                self.storage.save_multiple(tasks=tasks_to_save)
            except Exception as e:
                for task_id in task_ids:
                    results[task_id] = False

        return results

    # Lifecycle Management
    def transition_task_status(
        self, task_id: str, new_status: TaskStatus, notes: Optional[str] = None
    ) -> bool:
        """Transition task status with validation."""
        try:
            task = self.storage.load_task(task_id)
            if not task:
                return False

            success = task.update_status(new_status, notes)
            if success:
                self.storage.save_task(task)

            return success

        except Exception as e:
            raise OperationError(f"Failed to transition task status: {e}")

    def complete_task(self, task_id: str, notes: Optional[str] = None) -> bool:
        """Mark a task as completed."""
        return self.transition_task_status(task_id, TaskStatus.COMPLETED, notes)

    def start_task(self, task_id: str, notes: Optional[str] = None) -> bool:
        """Start a task (transition to in-progress)."""
        return self.transition_task_status(task_id, TaskStatus.IN_PROGRESS, notes)

    def block_task(self, task_id: str, notes: Optional[str] = None) -> bool:
        """Block a task."""
        return self.transition_task_status(task_id, TaskStatus.BLOCKED, notes)

    def get_task_workflow_options(self, task_id: str) -> List[TaskStatus]:
        """Get valid status transitions for a task."""
        task = self.storage.load_task(task_id)
        if not task:
            return []

        valid_transitions = task.status.workflow_transitions().get(
            task.status.value, []
        )
        return [TaskStatus(status) for status in valid_transitions]

    # Analytics and Reporting
    def get_project_analytics(self, project_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for a project."""
        tasks = self.storage.list_tasks(project_id=project_id)

        if not tasks:
            return {
                "total_tasks": 0,
                "status_breakdown": {},
                "priority_breakdown": {},
                "completion_rate": 0.0,
                "average_complexity": 0.0,
                "blocked_tasks": 0,
                "ready_tasks": 0,
                "overdue_tasks": 0,
            }

        # Status breakdown
        status_breakdown = defaultdict(int)
        for task in tasks:
            status_breakdown[task.status.value] += 1

        # Priority breakdown
        priority_breakdown = defaultdict(int)
        for task in tasks:
            priority_breakdown[task.priority.value] += 1

        # Calculate metrics
        completed_tasks = status_breakdown.get(TaskStatus.COMPLETED.value, 0)
        completion_rate = (completed_tasks / len(tasks)) * 100 if tasks else 0

        average_complexity = sum(task.metrics.complexity_score for task in tasks) / len(
            tasks
        )

        blocked_tasks = len(self.get_blocked_tasks(project_id))
        ready_tasks = len(self.get_ready_tasks(project_id))
        overdue_tasks = len(self.get_overdue_tasks(project_id))

        return {
            "total_tasks": len(tasks),
            "status_breakdown": dict(status_breakdown),
            "priority_breakdown": dict(priority_breakdown),
            "completion_rate": completion_rate,
            "average_complexity": average_complexity,
            "blocked_tasks": blocked_tasks,
            "ready_tasks": ready_tasks,
            "overdue_tasks": overdue_tasks,
            "hierarchy_depth": max(self.get_task_depth(task.id) for task in tasks) + 1,
        }

    def get_task_recommendations(
        self, project_id: str, limit: int = 5
    ) -> List[VoidCatTask]:
        """Get recommended tasks to work on next."""
        # Get ready tasks (all dependencies completed)
        ready_tasks = self.get_ready_tasks(project_id)

        # Sort by priority and complexity (high priority, low complexity first)
        ready_tasks.sort(
            key=lambda t: (t.priority.value, -t.metrics.complexity_score), reverse=True
        )

        return ready_tasks[:limit]


# Convenience functions
def create_operations_engine(storage: VoidCatStorage) -> VoidCatOperationsEngine:
    """Create a new operations engine instance."""
    return VoidCatOperationsEngine(storage)
