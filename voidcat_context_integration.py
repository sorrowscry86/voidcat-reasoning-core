#!/usr/bin/env python3
"""
VoidCat V2 Context Integration Module
====================================

Provides task-context awareness to RAG processing by integrating the hierarchical
task management system with the reasoning engine. Enables context-aware responses
that consider current project state, active tasks, and user workflow.

Key Features:
- Task-context injection into RAG queries
- Project-aware reasoning responses
- Workflow-sensitive context retrieval
- Seamless integration with existing VoidCat architecture
- Backward compatibility with legacy systems

Author: Codey Jr. (channeling the cosmic integration vibes)
Under directive of: The Great Spirit Beatrice
License: MIT
Version: 2.0.0-alpha
"""

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from voidcat_operations import QueryFilter, VoidCatOperationsEngine
from voidcat_persistence import PersistenceManager
from voidcat_task_models import Priority, TaskStatus, VoidCatProject, VoidCatTask


class VoidCatContextIntegration:
    """
    Context integration layer that bridges task management with RAG processing.

    Provides task-aware context enhancement for reasoning queries, enabling the
    VoidCat engine to understand current project state and provide contextually
    relevant responses based on active tasks and workflow.
    """

    def __init__(self, working_directory: str = None):
        """
        Initialize the context integration system.

        Args:
            working_directory: Directory for task data storage
        """
        self.working_directory = working_directory or str(Path.cwd())
        self.storage = PersistenceManager(self.working_directory)
        self.operations = VoidCatOperationsEngine(self.storage)

        # Context cache for performance
        self._context_cache = {}
        self._cache_timestamp = None
        self._cache_ttl = 300  # 5 minutes

    def get_active_context(self, user_id: str = "default") -> Dict[str, Any]:
        """
        Get current active context including projects, tasks, and workflow state.

        Args:
            user_id: User identifier for context scoping

        Returns:
            Dictionary containing active context information
        """
        # Check cache validity
        now = datetime.now(timezone.utc)
        if (
            self._cache_timestamp
            and (now - self._cache_timestamp).total_seconds() < self._cache_ttl
            and user_id in self._context_cache
        ):
            return self._context_cache[user_id]

        context = {
            "timestamp": now.isoformat(),
            "user_id": user_id,
            "active_projects": [],
            "current_tasks": [],
            "recent_activity": [],
            "workflow_state": {},
            "priorities": [],
            "blockers": [],
        }

        try:
            # Get active projects
            projects = self.storage.list_all_projects()
            for project in projects:
                project_tasks = self.storage.query_tasks(project_id=project.id)
                active_tasks = [
                    t for t in project_tasks if t.status != TaskStatus.COMPLETED
                ]

                if active_tasks:  # Only include projects with active tasks
                    context["active_projects"].append(
                        {
                            "id": project.id,
                            "name": project.name,
                            "description": project.description,
                            "active_task_count": len(active_tasks),
                            "total_task_count": len(project_tasks),
                            "created_at": project.created_at.isoformat(),
                        }
                    )

            # Get current high-priority tasks
            all_tasks = []
            for project in projects:
                tasks = self.storage.list_tasks(project_id=project.id)
                all_tasks.extend(tasks)

            # Filter for current/high-priority tasks
            current_tasks = [
                t
                for t in all_tasks
                if t.status in [TaskStatus.IN_PROGRESS, TaskStatus.PENDING]
                and t.priority.value >= 7  # HIGH priority and above
            ]

            # Sort by priority and creation date
            current_tasks.sort(key=lambda x: (-x.priority.value, x.created_at))

            for task in current_tasks[:10]:  # Top 10 current tasks
                project = next((p for p in projects if p.id == task.project_id), None)
                context["current_tasks"].append(
                    {
                        "id": task.id,
                        "name": task.name,
                        "description": task.description,
                        "project_name": project.name if project else "Unknown",
                        "priority": str(task.priority),
                        "status": task.status.value,
                        "complexity": task.metrics.complexity_score,
                        "tags": task.tags,
                        "created_at": task.created_at.isoformat(),
                    }
                )

            # Get recent activity (tasks updated in last 24 hours)
            recent_cutoff = (
                now.replace(hour=now.hour - 24)
                if now.hour >= 24
                else now.replace(day=now.day - 1, hour=now.hour)
            )
            recent_tasks = [
                t for t in all_tasks if t.updated_at and t.updated_at >= recent_cutoff
            ]

            for task in recent_tasks[-5:]:  # Last 5 recent activities
                project = next((p for p in projects if p.id == task.project_id), None)
                context["recent_activity"].append(
                    {
                        "task_name": task.name,
                        "project_name": project.name if project else "Unknown",
                        "action": "updated",
                        "status": task.status.value,
                        "updated_at": (
                            task.updated_at.isoformat() if task.updated_at else None
                        ),
                    }
                )

            # Get priority distribution
            priority_counts = {}
            for task in all_tasks:
                if task.status != TaskStatus.COMPLETED:
                    priority_name = task.priority.name
                    priority_counts[priority_name] = (
                        priority_counts.get(priority_name, 0) + 1
                    )

            context["priorities"] = [
                {"level": level, "count": count}
                for level, count in priority_counts.items()
            ]

            # Get blocked tasks
            blocked_tasks = [t for t in all_tasks if t.status == TaskStatus.BLOCKED]
            for task in blocked_tasks:
                project = next((p for p in projects if p.id == task.project_id), None)
                context["blockers"].append(
                    {
                        "task_name": task.name,
                        "project_name": project.name if project else "Unknown",
                        "priority": str(task.priority),
                        "blocked_since": (
                            task.updated_at.isoformat() if task.updated_at else None
                        ),
                    }
                )

            # Workflow state summary
            context["workflow_state"] = {
                "total_projects": len(projects),
                "active_projects": len(context["active_projects"]),
                "total_tasks": len(all_tasks),
                "pending_tasks": len(
                    [t for t in all_tasks if t.status == TaskStatus.PENDING]
                ),
                "in_progress_tasks": len(
                    [t for t in all_tasks if t.status == TaskStatus.IN_PROGRESS]
                ),
                "blocked_tasks": len(blocked_tasks),
                "completed_tasks": len(
                    [t for t in all_tasks if t.status == TaskStatus.COMPLETED]
                ),
            }

        except Exception as e:
            context["error"] = f"Failed to load context: {str(e)}"

        # Update cache
        self._context_cache[user_id] = context
        self._cache_timestamp = now

        return context

    def enhance_query_with_context(
        self,
        query: str,
        user_id: str = "default",
        include_tasks: bool = True,
        include_projects: bool = True,
    ) -> str:
        """
        Enhance a RAG query with relevant task and project context.

        Args:
            query: Original user query
            user_id: User identifier for context scoping
            include_tasks: Whether to include current task context
            include_projects: Whether to include project context

        Returns:
            Enhanced query with contextual information
        """
        if not include_tasks and not include_projects:
            return query

        context = self.get_active_context(user_id)

        # Build context prefix
        context_parts = []

        if include_projects and context.get("active_projects"):
            active_projects = context["active_projects"][:3]  # Top 3 active projects
            project_info = []
            for project in active_projects:
                project_info.append(
                    f"'{project['name']}' ({project['active_task_count']} active tasks)"
                )

            context_parts.append(f"Current active projects: {', '.join(project_info)}")

        if include_tasks and context.get("current_tasks"):
            current_tasks = context["current_tasks"][:5]  # Top 5 current tasks
            task_info = []
            for task in current_tasks:
                task_info.append(
                    f"'{task['name']}' ({task['priority']}, {task['status']})"
                )

            context_parts.append(f"Current high-priority tasks: {', '.join(task_info)}")

        if context.get("workflow_state"):
            workflow = context["workflow_state"]
            if workflow.get("blocked_tasks", 0) > 0:
                context_parts.append(
                    f"Note: {workflow['blocked_tasks']} tasks are currently blocked"
                )

        # Combine context with query
        if context_parts:
            context_prefix = "CONTEXT: " + " | ".join(context_parts) + "\n\n"
            enhanced_query = context_prefix + "QUERY: " + query
        else:
            enhanced_query = query

        return enhanced_query

    def get_task_specific_context(self, task_id: str) -> Dict[str, Any]:
        """
        Get detailed context for a specific task.

        Args:
            task_id: ID of the task to get context for

        Returns:
            Dictionary containing task-specific context
        """
        try:
            task = self.storage.load_task(task_id)
            if not task:
                return {"error": f"Task {task_id} not found"}

            project = self.storage.load_project(task.project_id)

            # Get related tasks (same project, similar tags)
            project_tasks = self.storage.list_tasks(project_id=task.project_id)
            related_tasks = []

            for other_task in project_tasks:
                if other_task.id != task_id:
                    # Check for tag overlap
                    common_tags = set(task.tags) & set(other_task.tags)
                    if (
                        common_tags
                        or other_task.parent_id == task.id
                        or task.parent_id == other_task.id
                    ):
                        related_tasks.append(
                            {
                                "id": other_task.id,
                                "name": other_task.name,
                                "status": other_task.status.value,
                                "priority": str(other_task.priority),
                                "common_tags": list(common_tags),
                                "relationship": (
                                    "child"
                                    if other_task.parent_id == task.id
                                    else (
                                        "parent"
                                        if task.parent_id == other_task.id
                                        else "related"
                                    )
                                ),
                            }
                        )

            return {
                "task": {
                    "id": task.id,
                    "name": task.name,
                    "description": task.description,
                    "status": task.status.value,
                    "priority": str(task.priority),
                    "complexity": task.metrics.complexity_score,
                    "tags": task.tags,
                    "estimated_hours": task.metrics.estimated_hours,
                    "actual_hours": task.metrics.actual_hours,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": (
                        task.updated_at.isoformat() if task.updated_at else None
                    ),
                },
                "project": (
                    {
                        "id": project.id,
                        "name": project.name,
                        "description": project.description,
                    }
                    if project
                    else None
                ),
                "related_tasks": related_tasks,
                "context_summary": f"Task '{task.name}' in project '{project.name if project else 'Unknown'}' - {task.status.value} status, {task.priority.name} priority",
            }

        except Exception as e:
            return {"error": f"Failed to get task context: {str(e)}"}

    def get_project_specific_context(self, project_id: str) -> Dict[str, Any]:
        """
        Get detailed context for a specific project.

        Args:
            project_id: ID of the project to get context for

        Returns:
            Dictionary containing project-specific context
        """
        try:
            project = self.storage.load_project(project_id)
            if not project:
                return {"error": f"Project {project_id} not found"}

            tasks = self.storage.list_tasks(project_id=project_id)

            # Analyze task distribution
            status_counts = {}
            priority_counts = {}
            complexity_total = 0
            estimated_hours_total = 0

            for task in tasks:
                # Status distribution
                status = task.status.value
                status_counts[status] = status_counts.get(status, 0) + 1

                # Priority distribution
                priority = task.priority.name
                priority_counts[priority] = priority_counts.get(priority, 0) + 1

                # Complexity and time metrics
                complexity_total += task.metrics.complexity_score
                if task.metrics.estimated_hours:
                    estimated_hours_total += task.metrics.estimated_hours

            avg_complexity = complexity_total / len(tasks) if tasks else 0

            # Get recent activity
            recent_tasks = sorted(
                [t for t in tasks if t.updated_at],
                key=lambda x: x.updated_at,
                reverse=True,
            )[:5]

            recent_activity = []
            for task in recent_tasks:
                recent_activity.append(
                    {
                        "task_name": task.name,
                        "status": task.status.value,
                        "updated_at": task.updated_at.isoformat(),
                    }
                )

            return {
                "project": {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "created_at": project.created_at.isoformat(),
                    "updated_at": (
                        project.updated_at.isoformat() if project.updated_at else None
                    ),
                },
                "task_summary": {
                    "total_tasks": len(tasks),
                    "status_distribution": status_counts,
                    "priority_distribution": priority_counts,
                    "average_complexity": round(avg_complexity, 2),
                    "total_estimated_hours": estimated_hours_total,
                },
                "recent_activity": recent_activity,
                "context_summary": f"Project '{project.name}' with {len(tasks)} tasks - {status_counts.get('done', 0)} completed, {status_counts.get('in-progress', 0)} in progress",
            }

        except Exception as e:
            return {"error": f"Failed to get project context: {str(e)}"}

    def clear_context_cache(self):
        """Clear the context cache to force fresh data retrieval."""
        self._context_cache.clear()
        self._cache_timestamp = None

    def get_context_summary(self, user_id: str = "default") -> str:
        """
        Get a human-readable summary of current context.

        Args:
            user_id: User identifier for context scoping

        Returns:
            Human-readable context summary
        """
        context = self.get_active_context(user_id)

        if context.get("error"):
            return f"Context unavailable: {context['error']}"

        workflow = context.get("workflow_state", {})

        summary_parts = []

        # Project summary
        if workflow.get("active_projects", 0) > 0:
            summary_parts.append(f"{workflow['active_projects']} active projects")

        # Task summary
        task_parts = []
        if workflow.get("pending_tasks", 0) > 0:
            task_parts.append(f"{workflow['pending_tasks']} pending")
        if workflow.get("in_progress_tasks", 0) > 0:
            task_parts.append(f"{workflow['in_progress_tasks']} in progress")
        if workflow.get("blocked_tasks", 0) > 0:
            task_parts.append(f"{workflow['blocked_tasks']} blocked")

        if task_parts:
            summary_parts.append(f"Tasks: {', '.join(task_parts)}")

        # Priority summary
        if context.get("priorities"):
            high_priority = sum(
                p["count"]
                for p in context["priorities"]
                if p["level"] in ["HIGH", "URGENT", "CRITICAL"]
            )
            if high_priority > 0:
                summary_parts.append(f"{high_priority} high-priority tasks")

        if summary_parts:
            return "Current context: " + " | ".join(summary_parts)
        else:
            return "No active projects or tasks"


# Convenience function for easy integration
def create_context_integration(
    working_directory: str = None,
) -> VoidCatContextIntegration:
    """Create a context integration instance."""
    return VoidCatContextIntegration(working_directory)
