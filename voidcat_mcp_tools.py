#!/usr/bin/env python3
"""
VoidCat V2 MCP Task Management Tools
===================================

Comprehensive MCP tool interface for the VoidCat V2 hierarchical task management system.
Provides rich schema validation, detailed error handling, and comprehensive response formatting.

Tools Implemented:
- voidcat_task_create: Create new tasks with full hierarchy support
- voidcat_task_list: List and query tasks with advanced filtering
- voidcat_task_update: Update task properties and status
- voidcat_task_delete: Delete tasks with cascade options
- voidcat_project_manage: Project management operations
- voidcat_dependency_analyze: Dependency analysis and visualization
- voidcat_task_recommend: Get intelligent task recommendations

Author: Codey Jr. (channeling the cosmic MCP vibes)
Under directive of: The Great Spirit Beatrice
License: MIT
Version: 2.0.0-alpha
"""

import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from voidcat_operations import (
    QueryFilter,
    VoidCatOperationsEngine,
    create_operations_engine,
)
from voidcat_persistence import VoidCatStorage
from voidcat_task_models import Priority, TaskStatus, VoidCatProject, VoidCatTask


class VoidCatMCPTaskTools:
    """
    MCP Task Management Tools for VoidCat V2 System

    Provides comprehensive MCP-compliant interface for task management operations
    with rich schema validation, error handling, and response formatting.
    """

    def __init__(self, working_directory: str = None):
        """Initialize the MCP task tools with storage and operations engine."""
        if working_directory is None:
            working_directory = str(Path.cwd())

        self.working_directory = working_directory
        self.storage = VoidCatStorage(working_directory)
        self.operations_engine = create_operations_engine(self.storage)

        # Tool definitions with comprehensive schemas
        self.tools = [
            {
                "name": "voidcat_task_create",
                "description": "Create a new task or project in the VoidCat V2 hierarchical system with full metadata support",
                "category": "task_management",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Task or project name (required)",
                            "minLength": 1,
                            "maxLength": 200,
                        },
                        "description": {
                            "type": "string",
                            "description": "Detailed description of the task or project",
                            "maxLength": 2000,
                        },
                        "type": {
                            "type": "string",
                            "description": "Type of item to create",
                            "enum": ["task", "project"],
                            "default": "task",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project ID (required for tasks, ignored for projects)",
                        },
                        "parent_id": {
                            "type": "string",
                            "description": "Parent task ID for hierarchical nesting (optional)",
                        },
                        "priority": {
                            "type": "integer",
                            "description": "Priority level (1=lowest, 10=critical)",
                            "minimum": 1,
                            "maximum": 10,
                            "default": 5,
                        },
                        "complexity": {
                            "type": "integer",
                            "description": "Complexity score (1=simple, 10=very complex)",
                            "minimum": 1,
                            "maximum": 10,
                            "default": 5,
                        },
                        "estimated_hours": {
                            "type": "number",
                            "description": "Estimated hours to complete",
                            "minimum": 0,
                        },
                        "tags": {
                            "type": "array",
                            "description": "Tags for categorization",
                            "items": {"type": "string"},
                            "maxItems": 20,
                        },
                        "assignee": {
                            "type": "string",
                            "description": "Person assigned to the task",
                        },
                        "due_date": {
                            "type": "string",
                            "description": "Due date in ISO format (YYYY-MM-DD)",
                        },
                    },
                    "required": ["name"],
                    "additionalProperties": False,
                },
            },
            {
                "name": "voidcat_task_list",
                "description": "List and query tasks with advanced filtering, sorting, and hierarchy visualization",
                "category": "task_management",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "Filter to specific project",
                        },
                        "parent_id": {
                            "type": "string",
                            "description": "Filter to children of specific task",
                        },
                        "status": {
                            "type": "array",
                            "description": "Filter by task status",
                            "items": {
                                "type": "string",
                                "enum": [
                                    "pending",
                                    "in-progress",
                                    "blocked",
                                    "on-hold",
                                    "completed",
                                    "cancelled",
                                    "failed",
                                ],
                            },
                        },
                        "priority_min": {
                            "type": "integer",
                            "description": "Minimum priority level",
                            "minimum": 1,
                            "maximum": 10,
                        },
                        "priority_max": {
                            "type": "integer",
                            "description": "Maximum priority level",
                            "minimum": 1,
                            "maximum": 10,
                        },
                        "tags": {
                            "type": "array",
                            "description": "Filter by tags (must have ALL tags)",
                            "items": {"type": "string"},
                        },
                        "tags_any": {
                            "type": "array",
                            "description": "Filter by tags (must have ANY tag)",
                            "items": {"type": "string"},
                        },
                        "assignee": {
                            "type": "string",
                            "description": "Filter by assignee",
                        },
                        "show_hierarchy": {
                            "type": "boolean",
                            "description": "Show hierarchical tree structure",
                            "default": True,
                        },
                        "include_completed": {
                            "type": "boolean",
                            "description": "Include completed tasks",
                            "default": True,
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of tasks to return",
                            "minimum": 1,
                            "maximum": 1000,
                            "default": 50,
                        },
                    },
                    "additionalProperties": False,
                },
            },
            {
                "name": "voidcat_task_update",
                "description": "Update task properties, status, progress, and hierarchy relationships",
                "category": "task_management",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "ID of task to update (required)",
                        },
                        "name": {
                            "type": "string",
                            "description": "New task name",
                            "minLength": 1,
                            "maxLength": 200,
                        },
                        "description": {
                            "type": "string",
                            "description": "New task description",
                            "maxLength": 2000,
                        },
                        "status": {
                            "type": "string",
                            "description": "New task status",
                            "enum": [
                                "pending",
                                "in-progress",
                                "blocked",
                                "on-hold",
                                "completed",
                                "cancelled",
                                "failed",
                            ],
                        },
                        "priority": {
                            "type": "integer",
                            "description": "New priority level (1=lowest, 10=critical)",
                            "minimum": 1,
                            "maximum": 10,
                        },
                        "complexity": {
                            "type": "integer",
                            "description": "New complexity score (1=simple, 10=very complex)",
                            "minimum": 1,
                            "maximum": 10,
                        },
                        "estimated_hours": {
                            "type": "number",
                            "description": "New estimated hours",
                            "minimum": 0,
                        },
                        "actual_hours": {
                            "type": "number",
                            "description": "Actual hours spent",
                            "minimum": 0,
                        },
                        "progress_percentage": {
                            "type": "number",
                            "description": "Progress percentage (0-100)",
                            "minimum": 0,
                            "maximum": 100,
                        },
                        "parent_id": {
                            "type": "string",
                            "description": "New parent task ID (null to move to root)",
                        },
                        "tags": {
                            "type": "array",
                            "description": "New tags (replaces existing)",
                            "items": {"type": "string"},
                            "maxItems": 20,
                        },
                        "assignee": {"type": "string", "description": "New assignee"},
                        "due_date": {
                            "type": "string",
                            "description": "New due date in ISO format (YYYY-MM-DD)",
                        },
                        "notes": {
                            "type": "string",
                            "description": "Notes about the update",
                            "maxLength": 500,
                        },
                    },
                    "required": ["task_id"],
                    "additionalProperties": False,
                },
            },
            {
                "name": "voidcat_task_delete",
                "description": "Delete tasks with optional cascade to children and dependency cleanup",
                "category": "task_management",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "ID of task to delete (required)",
                        },
                        "cascade": {
                            "type": "boolean",
                            "description": "Delete all child tasks recursively",
                            "default": False,
                        },
                        "confirm": {
                            "type": "boolean",
                            "description": "Confirmation flag (required for safety)",
                            "default": False,
                        },
                    },
                    "required": ["task_id", "confirm"],
                    "additionalProperties": False,
                },
            },
            {
                "name": "voidcat_project_manage",
                "description": "Create, update, delete, and analyze projects with comprehensive management features",
                "category": "project_management",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "Project management action",
                            "enum": ["create", "update", "delete", "list", "analytics"],
                            "default": "list",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project ID (required for update, delete, analytics)",
                        },
                        "name": {
                            "type": "string",
                            "description": "Project name (required for create)",
                            "minLength": 1,
                            "maxLength": 200,
                        },
                        "description": {
                            "type": "string",
                            "description": "Project description",
                            "maxLength": 2000,
                        },
                        "confirm": {
                            "type": "boolean",
                            "description": "Confirmation for delete action",
                            "default": False,
                        },
                    },
                    "additionalProperties": False,
                },
            },
            {
                "name": "voidcat_dependency_analyze",
                "description": "Analyze task dependencies, detect cycles, and visualize dependency graphs",
                "category": "analysis",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "Dependency analysis action",
                            "enum": [
                                "add",
                                "remove",
                                "list",
                                "blocked",
                                "ready",
                                "cycles",
                            ],
                            "default": "list",
                        },
                        "task_id": {
                            "type": "string",
                            "description": "Task ID for dependency operations",
                        },
                        "dependency_task_id": {
                            "type": "string",
                            "description": "Dependency task ID (for add/remove)",
                        },
                        "dependency_type": {
                            "type": "string",
                            "description": "Type of dependency relationship",
                            "enum": ["blocks", "requires", "relates_to"],
                            "default": "blocks",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Filter to specific project",
                        },
                        "notes": {
                            "type": "string",
                            "description": "Notes about the dependency",
                            "maxLength": 500,
                        },
                    },
                    "additionalProperties": False,
                },
            },
            {
                "name": "voidcat_task_recommend",
                "description": "Get intelligent task recommendations based on priorities, dependencies, and workload",
                "category": "analysis",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "Filter recommendations to specific project",
                        },
                        "max_recommendations": {
                            "type": "integer",
                            "description": "Maximum number of recommendations",
                            "minimum": 1,
                            "maximum": 20,
                            "default": 5,
                        },
                        "preferred_tags": {
                            "type": "array",
                            "description": "Preferred task tags to prioritize",
                            "items": {"type": "string"},
                        },
                        "consider_complexity": {
                            "type": "boolean",
                            "description": "Factor in task complexity",
                            "default": True,
                        },
                        "exclude_blocked": {
                            "type": "boolean",
                            "description": "Exclude blocked tasks",
                            "default": True,
                        },
                    },
                    "additionalProperties": False,
                },
            },
        ]

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get MCP tool definitions for registration."""
        return self.tools

    async def handle_tool_call(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle MCP tool call with comprehensive error handling and response formatting.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments from MCP client

        Returns:
            MCP-compliant response dictionary
        """
        try:
            if tool_name == "voidcat_task_create":
                return await self._handle_task_create(arguments)
            elif tool_name == "voidcat_task_list":
                return await self._handle_task_list(arguments)
            elif tool_name == "voidcat_task_update":
                return await self._handle_task_update(arguments)
            elif tool_name == "voidcat_task_delete":
                return await self._handle_task_delete(arguments)
            elif tool_name == "voidcat_project_manage":
                return await self._handle_project_manage(arguments)
            elif tool_name == "voidcat_dependency_analyze":
                return await self._handle_dependency_analyze(arguments)
            elif tool_name == "voidcat_task_recommend":
                return await self._handle_task_recommend(arguments)
            else:
                return self._error_response(f"Unknown tool: {tool_name}")

        except Exception as e:
            error_msg = f"Tool execution failed for '{tool_name}': {str(e)}"
            print(f"[VoidCat-MCP-Error] {error_msg}", file=sys.stderr)
            print(f"[VoidCat-MCP-Traceback] {traceback.format_exc()}", file=sys.stderr)
            return self._error_response(error_msg)

    async def _handle_task_create(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle voidcat_task_create tool execution."""
        try:
            item_type = arguments.get("type", "task")
            name = arguments.get("name", "").strip()

            if not name:
                return self._error_response("Task/project name is required")

            if item_type == "project":
                # Create project
                project = VoidCatProject(
                    name=name, description=arguments.get("description", "")
                )

                success = self.storage.save_project(project)
                if not success:
                    return self._error_response("Failed to save project")

                response_text = f"✅ **Project Created Successfully**\n\n"
                response_text += f"**Name**: {project.name}\n"
                response_text += f"**ID**: `{project.id}`\n"
                response_text += f"**Description**: {project.description}\n"
                response_text += f"**Created**: {project.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
                response_text += "🎯 **Next Steps**: Use `voidcat_task_create` to add tasks to this project!"

                return self._success_response(response_text)

            else:
                # Create task
                project_id = arguments.get("project_id", "").strip()
                if not project_id:
                    return self._error_response(
                        "project_id is required for task creation"
                    )

                # Verify project exists
                project = self.storage.load_project(project_id)
                if not project:
                    return self._error_response(
                        f"Project with ID '{project_id}' not found"
                    )

                # Create task with all properties
                task = VoidCatTask(
                    name=name,
                    description=arguments.get("description", ""),
                    project_id=project_id,
                    parent_id=arguments.get("parent_id"),
                    priority=self._convert_priority(arguments.get("priority", 5)),
                    tags=arguments.get("tags", []),
                    assignee=arguments.get("assignee"),
                )

                # Set optional properties
                if "complexity" in arguments:
                    task.metrics.complexity_score = arguments["complexity"]
                if "estimated_hours" in arguments:
                    task.metrics.estimated_hours = arguments["estimated_hours"]
                if "due_date" in arguments:
                    try:
                        task.due_date = datetime.fromisoformat(
                            arguments["due_date"]
                        ).replace(tzinfo=timezone.utc)
                    except ValueError:
                        return self._error_response(
                            "Invalid due_date format. Use YYYY-MM-DD"
                        )

                # Create task using operations engine for validation
                success = self.operations_engine.create_task(task)
                if not success:
                    return self._error_response(
                        "Failed to create task (validation failed)"
                    )

                response_text = f"✅ **Task Created Successfully**\n\n"
                response_text += f"**Name**: {task.name}\n"
                response_text += f"**ID**: `{task.id}`\n"
                response_text += f"**Project**: {project.name}\n"
                response_text += (
                    f"**Priority**: {task.priority.name} ({task.priority.value}/10)\n"
                )
                response_text += f"**Complexity**: {task.metrics.complexity_score}/10\n"
                response_text += f"**Status**: {task.status.value}\n"

                if task.parent_id:
                    parent = self.storage.load_task(task.parent_id)
                    if parent:
                        response_text += f"**Parent**: {parent.name}\n"

                if task.tags:
                    response_text += f"**Tags**: {', '.join(task.tags)}\n"

                if task.assignee:
                    response_text += f"**Assignee**: {task.assignee}\n"

                if task.due_date:
                    response_text += (
                        f"**Due Date**: {task.due_date.strftime('%Y-%m-%d')}\n"
                    )

                response_text += f"**Created**: {task.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
                response_text += "🎯 **Next Steps**: Use `voidcat_task_list` to view in hierarchy or `voidcat_task_update` to modify!"

                return self._success_response(response_text)

        except Exception as e:
            return self._error_response(f"Task creation failed: {str(e)}")

    async def _handle_task_list(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle voidcat_task_list tool execution."""
        try:
            # Build query filter from arguments
            filter_criteria = QueryFilter()

            if "project_id" in arguments:
                filter_criteria.project_ids = [arguments["project_id"]]

            if "parent_id" in arguments:
                filter_criteria.parent_id = arguments["parent_id"]

            if "status" in arguments:
                filter_criteria.status_filter = [
                    TaskStatus(s) for s in arguments["status"]
                ]

            if "priority_min" in arguments or "priority_max" in arguments:
                min_pri = arguments.get("priority_min", 1)
                max_pri = arguments.get("priority_max", 10)
                filter_criteria.priority_range = (min_pri, max_pri)

            if "tags" in arguments:
                filter_criteria.tags = arguments["tags"]

            if "tags_any" in arguments:
                filter_criteria.tags_any = arguments["tags_any"]

            if "assignee" in arguments:
                filter_criteria.assignee = arguments["assignee"]

            # Query tasks
            tasks = self.operations_engine.query_tasks(filter_criteria)

            # Apply limit
            limit = arguments.get("limit", 50)
            tasks = tasks[:limit]

            if not tasks:
                return self._success_response(
                    "📭 **No tasks found** matching the specified criteria."
                )

            # Format response
            show_hierarchy = arguments.get("show_hierarchy", True)

            if show_hierarchy and not arguments.get("parent_id"):
                # Show hierarchical view
                response_text = f"🌲 **Task Hierarchy** ({len(tasks)} tasks)\n\n"

                # Group by project
                projects = {}
                for task in tasks:
                    if task.project_id not in projects:
                        project = self.storage.load_project(task.project_id)
                        projects[task.project_id] = {"project": project, "tasks": []}
                    projects[task.project_id]["tasks"].append(task)

                for project_id, project_data in projects.items():
                    project = project_data["project"]
                    project_tasks = project_data["tasks"]

                    response_text += (
                        f"📁 **{project.name}** ({len(project_tasks)} tasks)\n"
                    )

                    # Build hierarchy for this project
                    root_tasks = [t for t in project_tasks if not t.parent_id]

                    for root_task in root_tasks:
                        response_text += self._format_task_hierarchy(
                            root_task, project_tasks, 0
                        )

                    response_text += "\n"
            else:
                # Show flat list
                response_text = f"📋 **Task List** ({len(tasks)} tasks)\n\n"

                for task in tasks:
                    response_text += self._format_task_summary(task)
                    response_text += "\n"

            response_text += f"\n💡 **Tip**: Use `voidcat_task_update` to modify tasks or `voidcat_dependency_analyze` for dependency management."

            return self._success_response(response_text)

        except Exception as e:
            return self._error_response(f"Task listing failed: {str(e)}")

    def _format_task_hierarchy(
        self, task: VoidCatTask, all_tasks: List[VoidCatTask], depth: int
    ) -> str:
        """Format a task and its children in hierarchical view."""
        indent = "  " * depth
        status_emoji = self._get_status_emoji(task.status)
        priority_emoji = self._get_priority_emoji(task.priority)

        result = f"{indent}{status_emoji} **{task.name}** {priority_emoji}\n"
        result += f"{indent}   ID: `{task.id}` | Status: {task.status.value} | Priority: {task.priority.value}/10\n"

        if task.assignee:
            result += f"{indent}   👤 {task.assignee}"
        if task.tags:
            result += f"{indent}   🏷️ {', '.join(task.tags)}\n"

        # Find and format children
        children = [t for t in all_tasks if t.parent_id == task.id]
        for child in children:
            result += self._format_task_hierarchy(child, all_tasks, depth + 1)

        return result

    def _format_task_summary(self, task: VoidCatTask) -> str:
        """Format a task summary for flat list view."""
        status_emoji = self._get_status_emoji(task.status)
        priority_emoji = self._get_priority_emoji(task.priority)

        result = f"{status_emoji} **{task.name}** {priority_emoji}\n"
        result += f"   ID: `{task.id}` | Status: {task.status.value} | Priority: {task.priority.value}/10 | Complexity: {task.metrics.complexity_score}/10\n"

        if task.assignee:
            result += f"   👤 {task.assignee} | "
        if task.tags:
            result += f"🏷️ {', '.join(task.tags)}\n"

        return result

    def _get_status_emoji(self, status: TaskStatus) -> str:
        """Get emoji for task status."""
        status_emojis = {
            TaskStatus.PENDING: "⏳",
            TaskStatus.IN_PROGRESS: "🚧",
            TaskStatus.BLOCKED: "🚫",
            TaskStatus.ON_HOLD: "⏸️",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.CANCELLED: "❌",
            TaskStatus.FAILED: "💥",
        }
        return status_emojis.get(status, "❓")

    def _get_priority_emoji(self, priority: Priority) -> str:
        """Get emoji for task priority."""
        if priority.value >= 9:
            return "🔥🔥"
        elif priority.value >= 7:
            return "🔥"
        elif priority.value >= 5:
            return "⚡"
        else:
            return ""

    async def _handle_task_update(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle voidcat_task_update tool execution."""
        try:
            task_id = arguments.get("task_id", "").strip()
            if not task_id:
                return self._error_response("task_id is required")

            # Load existing task
            task = self.storage.load_task(task_id)
            if not task:
                return self._error_response(f"Task with ID '{task_id}' not found")

            # Track changes for response
            changes = []

            # Update properties
            if "name" in arguments:
                old_name = task.name
                task.name = arguments["name"].strip()
                changes.append(f"Name: '{old_name}' → '{task.name}'")

            if "description" in arguments:
                task.description = arguments["description"]
                changes.append("Description updated")

            if "status" in arguments:
                old_status = task.status
                new_status = TaskStatus(arguments["status"])
                if task.update_status(new_status, arguments.get("notes")):
                    changes.append(f"Status: {old_status.value} → {new_status.value}")
                else:
                    return self._error_response(
                        f"Invalid status transition: {old_status.value} → {new_status.value}"
                    )

            if "priority" in arguments:
                old_priority = task.priority
                task.priority = Priority(arguments["priority"])
                changes.append(
                    f"Priority: {old_priority.value} → {task.priority.value}"
                )

            if "complexity" in arguments:
                old_complexity = task.metrics.complexity_score
                task.metrics.complexity_score = arguments["complexity"]
                changes.append(
                    f"Complexity: {old_complexity} → {task.metrics.complexity_score}"
                )

            if "estimated_hours" in arguments:
                task.metrics.estimated_hours = arguments["estimated_hours"]
                changes.append(f"Estimated hours: {task.metrics.estimated_hours}")

            if "actual_hours" in arguments:
                task.metrics.actual_hours = arguments["actual_hours"]
                changes.append(f"Actual hours: {task.metrics.actual_hours}")

            if "progress_percentage" in arguments:
                task.metrics.progress_percentage = arguments["progress_percentage"]
                changes.append(f"Progress: {task.metrics.progress_percentage}%")

            if "tags" in arguments:
                task.tags = set(arguments["tags"])
                changes.append(f"Tags: {', '.join(task.tags) if task.tags else 'None'}")

            if "assignee" in arguments:
                task.assignee = arguments["assignee"]
                changes.append(f"Assignee: {task.assignee or 'Unassigned'}")

            if "due_date" in arguments:
                try:
                    task.due_date = datetime.fromisoformat(
                        arguments["due_date"]
                    ).replace(tzinfo=timezone.utc)
                    changes.append(f"Due date: {task.due_date.strftime('%Y-%m-%d')}")
                except ValueError:
                    return self._error_response(
                        "Invalid due_date format. Use YYYY-MM-DD"
                    )

            # Handle parent change (move in hierarchy)
            if "parent_id" in arguments:
                old_parent_id = task.parent_id
                new_parent_id = (
                    arguments["parent_id"] if arguments["parent_id"] else None
                )

                if old_parent_id != new_parent_id:
                    success = self.operations_engine.move_task(task_id, new_parent_id)
                    if success:
                        if new_parent_id:
                            parent = self.storage.load_task(new_parent_id)
                            changes.append(
                                f"Moved under: {parent.name if parent else 'Unknown'}"
                            )
                        else:
                            changes.append("Moved to root level")
                    else:
                        return self._error_response(
                            "Failed to move task (hierarchy validation failed)"
                        )

            # Save task using operations engine
            success = self.operations_engine.update_task(task)
            if not success:
                return self._error_response("Failed to update task")

            if not changes:
                return self._success_response(
                    "ℹ️ **No changes made** - task is already up to date."
                )

            response_text = f"✅ **Task Updated Successfully**\n\n"
            response_text += f"**Task**: {task.name}\n"
            response_text += f"**ID**: `{task.id}`\n\n"
            response_text += "**Changes Made**:\n"
            for change in changes:
                response_text += f"• {change}\n"

            response_text += (
                f"\n**Updated**: {task.updated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}"
            )

            return self._success_response(response_text)

        except Exception as e:
            return self._error_response(f"Task update failed: {str(e)}")

    async def _handle_task_delete(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle voidcat_task_delete tool execution."""
        try:
            task_id = arguments.get("task_id", "").strip()
            if not task_id:
                return self._error_response("task_id is required")

            confirm = arguments.get("confirm", False)
            if not confirm:
                return self._error_response("confirm must be set to true for safety")

            # Load task to get details
            task = self.storage.load_task(task_id)
            if not task:
                return self._error_response(f"Task with ID '{task_id}' not found")

            cascade = arguments.get("cascade", False)

            # Get children count for reporting
            children = self.operations_engine.get_task_children(task_id)
            children_count = len(children)

            # Delete task
            success = self.operations_engine.delete_task(task_id, cascade=cascade)
            if not success:
                return self._error_response("Failed to delete task")

            response_text = f"✅ **Task Deleted Successfully**\n\n"
            response_text += f"**Deleted Task**: {task.name}\n"
            response_text += f"**ID**: `{task_id}`\n"

            if cascade and children_count > 0:
                response_text += f"**Children Deleted**: {children_count} tasks\n"
            elif children_count > 0:
                response_text += f"**Children Moved**: {children_count} tasks moved to parent level\n"

            response_text += f"**Deleted At**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"

            return self._success_response(response_text)

        except Exception as e:
            return self._error_response(f"Task deletion failed: {str(e)}")

    async def _handle_project_manage(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle voidcat_project_manage tool execution."""
        try:
            action = arguments.get("action", "list")

            if action == "list":
                projects = self.storage.list_projects()
                if not projects:
                    return self._success_response(
                        "📭 **No projects found**. Use action='create' to create your first project!"
                    )

                response_text = f"📁 **Projects** ({len(projects)} total)\n\n"

                for project in projects:
                    # Get task count for each project
                    tasks = self.storage.list_tasks(project_id=project.id)
                    task_count = len(tasks)
                    completed_count = len(
                        [t for t in tasks if t.status == TaskStatus.COMPLETED]
                    )

                    response_text += f"**{project.name}**\n"
                    response_text += f"   ID: `{project.id}`\n"
                    response_text += (
                        f"   Tasks: {task_count} total, {completed_count} completed\n"
                    )
                    response_text += (
                        f"   Created: {project.created_at.strftime('%Y-%m-%d')}\n"
                    )
                    if project.description:
                        response_text += f"   Description: {project.description}\n"
                    response_text += "\n"

                return self._success_response(response_text)

            elif action == "create":
                name = arguments.get("name", "").strip()
                if not name:
                    return self._error_response(
                        "Project name is required for create action"
                    )

                description = arguments.get("description", "")

                # Create project
                project = VoidCatProject(name=name, description=description)

                success = self.storage.save_project(project)
                if not success:
                    return self._error_response("Failed to save project")

                response_text = f"✅ **Project Created Successfully**\n\n"
                response_text += f"**Name**: {project.name}\n"
                response_text += f"**ID**: `{project.id}`\n"
                response_text += f"**Description**: {project.description}\n"
                response_text += f"**Created**: {project.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
                response_text += "🎯 **Next Steps**: Use `voidcat_task_create` to add tasks to this project!"

                return self._success_response(response_text)

            elif action == "update":
                project_id = arguments.get("project_id", "").strip()
                if not project_id:
                    return self._error_response(
                        "project_id is required for update action"
                    )

                project = self.storage.load_project(project_id)
                if not project:
                    return self._error_response(
                        f"Project with ID '{project_id}' not found"
                    )

                # Update properties
                changes = []
                if "name" in arguments:
                    old_name = project.name
                    project.name = arguments["name"].strip()
                    changes.append(f"Name: '{old_name}' → '{project.name}'")

                if "description" in arguments:
                    project.description = arguments["description"]
                    changes.append("Description updated")

                if not changes:
                    return self._success_response(
                        "ℹ️ **No changes made** - project is already up to date."
                    )

                success = self.storage.save_project(project)
                if not success:
                    return self._error_response("Failed to update project")

                response_text = f"✅ **Project Updated Successfully**\n\n"
                response_text += f"**Project**: {project.name}\n"
                response_text += f"**ID**: `{project.id}`\n\n"
                response_text += "**Changes Made**:\n"
                for change in changes:
                    response_text += f"• {change}\n"

                return self._success_response(response_text)

            elif action == "delete":
                project_id = arguments.get("project_id", "").strip()
                if not project_id:
                    return self._error_response(
                        "project_id is required for delete action"
                    )

                confirm = arguments.get("confirm", False)
                if not confirm:
                    return self._error_response(
                        "confirm must be set to true for safety"
                    )

                project = self.storage.load_project(project_id)
                if not project:
                    return self._error_response(
                        f"Project with ID '{project_id}' not found"
                    )

                # Check for tasks
                tasks = self.storage.list_tasks(project_id=project_id)
                if tasks:
                    return self._error_response(
                        f"Cannot delete project with {len(tasks)} tasks. Delete tasks first."
                    )

                success = self.storage.delete_project(project_id)
                if not success:
                    return self._error_response("Failed to delete project")

                response_text = f"✅ **Project Deleted Successfully**\n\n"
                response_text += f"**Deleted Project**: {project.name}\n"
                response_text += f"**ID**: `{project_id}`\n"
                response_text += f"**Deleted At**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"

                return self._success_response(response_text)

            elif action == "analytics":
                project_id = arguments.get("project_id", "").strip()
                if not project_id:
                    return self._error_response("project_id is required for analytics")

                project = self.storage.load_project(project_id)
                if not project:
                    return self._error_response(
                        f"Project with ID '{project_id}' not found"
                    )

                analytics = self.operations_engine.get_project_analytics(project_id)

                response_text = f"📊 **Project Analytics: {project.name}**\n\n"
                response_text += f"**Total Tasks**: {analytics['total_tasks']}\n"
                response_text += (
                    f"**Completion Rate**: {analytics['completion_rate']:.1f}%\n"
                )
                response_text += f"**Average Complexity**: {analytics['average_complexity']:.1f}/10\n"
                response_text += (
                    f"**Hierarchy Depth**: {analytics['hierarchy_depth']} levels\n\n"
                )

                response_text += "**Status Breakdown**:\n"
                for status, count in analytics["status_breakdown"].items():
                    response_text += f"• {status}: {count}\n"

                response_text += "\n**Priority Breakdown**:\n"
                for priority, count in analytics["priority_breakdown"].items():
                    response_text += f"• Priority {priority}: {count}\n"

                response_text += f"\n**Task Status**:\n"
                response_text += f"• Blocked: {analytics['blocked_tasks']}\n"
                response_text += f"• Ready: {analytics['ready_tasks']}\n"
                response_text += f"• Overdue: {analytics['overdue_tasks']}\n"

                return self._success_response(response_text)

            else:
                return self._error_response(
                    f"Unsupported action: {action}. Use 'create', 'update', 'delete', 'list', or 'analytics'"
                )

        except Exception as e:
            return self._error_response(f"Project management failed: {str(e)}")

    async def _handle_dependency_analyze(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle voidcat_dependency_analyze tool execution."""
        try:
            action = arguments.get("action", "list")

            if action == "add":
                task_id = arguments.get("task_id", "").strip()
                dependency_task_id = arguments.get("dependency_task_id", "").strip()

                if not task_id or not dependency_task_id:
                    return self._error_response(
                        "Both task_id and dependency_task_id are required for add action"
                    )

                dependency_type = arguments.get("dependency_type", "blocks")
                notes = arguments.get("notes")

                success = self.operations_engine.add_dependency(
                    task_id, dependency_task_id, dependency_type, notes
                )

                if success:
                    task = self.storage.load_task(task_id)
                    dep_task = self.storage.load_task(dependency_task_id)

                    response_text = f"✅ **Dependency Added Successfully**\n\n"
                    response_text += f"**Task**: {task.name if task else 'Unknown'}\n"
                    response_text += f"**{dependency_type.title()}**: {dep_task.name if dep_task else 'Unknown'}\n"
                    if notes:
                        response_text += f"**Notes**: {notes}\n"

                    return self._success_response(response_text)
                else:
                    return self._error_response(
                        "Failed to add dependency (cycle detected or validation failed)"
                    )

            elif action == "blocked":
                project_id = arguments.get("project_id")
                blocked_tasks = self.operations_engine.get_blocked_tasks(project_id)

                if not blocked_tasks:
                    return self._success_response(
                        "🎉 **No blocked tasks found!** All tasks are ready to work on."
                    )

                response_text = f"🚫 **Blocked Tasks** ({len(blocked_tasks)} total)\n\n"

                for task in blocked_tasks:
                    dependencies = self.operations_engine.get_task_dependencies(task.id)
                    response_text += f"**{task.name}**\n"
                    response_text += f"   ID: `{task.id}`\n"
                    response_text += (
                        f"   Blocked by: {len(dependencies)} dependencies\n"
                    )

                    for dep_task in dependencies[:3]:  # Show first 3
                        response_text += (
                            f"   • {dep_task.name} ({dep_task.status.value})\n"
                        )

                    if len(dependencies) > 3:
                        response_text += f"   • ... and {len(dependencies) - 3} more\n"

                    response_text += "\n"

                return self._success_response(response_text)

            elif action == "ready":
                project_id = arguments.get("project_id")
                ready_tasks = self.operations_engine.get_ready_tasks(project_id)

                if not ready_tasks:
                    return self._success_response(
                        "📭 **No ready tasks found.** All tasks may be blocked or completed."
                    )

                response_text = f"🚀 **Ready Tasks** ({len(ready_tasks)} total)\n\n"

                for task in ready_tasks:
                    priority_emoji = self._get_priority_emoji(task.priority)
                    response_text += f"**{task.name}** {priority_emoji}\n"
                    response_text += f"   ID: `{task.id}` | Priority: {task.priority.value}/10 | Complexity: {task.metrics.complexity_score}/10\n"
                    if task.assignee:
                        response_text += f"   👤 {task.assignee}\n"
                    response_text += "\n"

                return self._success_response(response_text)

            else:
                return self._error_response(
                    f"Unsupported action: {action}. Use 'add', 'blocked', or 'ready'"
                )

        except Exception as e:
            return self._error_response(f"Dependency analysis failed: {str(e)}")

    async def _handle_task_recommend(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle voidcat_task_recommend tool execution."""
        try:
            project_id = arguments.get("project_id")
            max_recommendations = arguments.get("max_recommendations", 5)

            if project_id:
                recommendations = self.operations_engine.get_task_recommendations(
                    project_id, max_recommendations
                )
            else:
                # Get recommendations across all projects
                projects = self.storage.list_projects()
                all_recommendations = []

                for project in projects:
                    project_recs = self.operations_engine.get_task_recommendations(
                        project.id, max_recommendations
                    )
                    all_recommendations.extend(project_recs)

                # Sort by priority and complexity
                all_recommendations.sort(
                    key=lambda t: (t.priority.value, -t.metrics.complexity_score),
                    reverse=True,
                )
                recommendations = all_recommendations[:max_recommendations]

            if not recommendations:
                return self._success_response(
                    "🎯 **No task recommendations available.** All tasks may be blocked or completed!"
                )

            response_text = (
                f"🎯 **Task Recommendations** (Top {len(recommendations)})\n\n"
            )
            response_text += (
                "Based on priority, dependencies, and complexity analysis:\n\n"
            )

            for i, task in enumerate(recommendations, 1):
                priority_emoji = self._get_priority_emoji(task.priority)

                response_text += f"**{i}. {task.name}** {priority_emoji}\n"
                response_text += f"   ID: `{task.id}`\n"
                response_text += f"   Priority: {task.priority.value}/10 | Complexity: {task.metrics.complexity_score}/10\n"
                response_text += f"   Status: {task.status.value}\n"

                if task.assignee:
                    response_text += f"   👤 {task.assignee}\n"

                if task.tags:
                    response_text += f"   🏷️ {', '.join(list(task.tags)[:3])}\n"

                if task.metrics.estimated_hours:
                    response_text += (
                        f"   ⏱️ ~{task.metrics.estimated_hours}h estimated\n"
                    )

                response_text += "\n"

            response_text += "💡 **Tip**: Use `voidcat_task_update` to start working on a recommended task!"

            return self._success_response(response_text)

        except Exception as e:
            return self._error_response(f"Task recommendation failed: {str(e)}")

    def _success_response(self, text: str) -> Dict[str, Any]:
        """Create a successful MCP response."""
        return {"content": [{"type": "text", "text": text}]}

    def _convert_priority(self, priority_value: Union[int, str, Priority]) -> Priority:
        """Convert various priority formats to Priority enum."""
        if isinstance(priority_value, Priority):
            return priority_value

        if isinstance(priority_value, str):
            try:
                priority_value = int(priority_value)
            except ValueError:
                # Try to match by name
                priority_name = priority_value.upper()
                for priority in Priority:
                    if priority.name == priority_name:
                        return priority
                return Priority.MEDIUM  # Default fallback

        # Convert integer to closest Priority enum value
        if isinstance(priority_value, int):
            priority_map = {
                1: Priority.LOWEST,
                2: Priority.LOW,
                3: Priority.LOW,
                4: Priority.MEDIUM,
                5: Priority.MEDIUM,
                6: Priority.HIGH,
                7: Priority.HIGH,
                8: Priority.HIGH,
                9: Priority.URGENT,
                10: Priority.CRITICAL,
            }

            # Clamp to valid range
            priority_value = max(1, min(10, priority_value))
            return priority_map.get(priority_value, Priority.MEDIUM)

        return Priority.MEDIUM  # Default fallback

    def _error_response(self, error_message: str) -> Dict[str, Any]:
        """Create an error MCP response."""
        return {
            "content": [{"type": "text", "text": f"❌ **Error**: {error_message}"}],
            "isError": True,
        }


# Convenience function for easy integration
def create_mcp_task_tools(working_directory: str = None) -> VoidCatMCPTaskTools:
    """Create MCP task tools instance."""
    return VoidCatMCPTaskTools(working_directory)
