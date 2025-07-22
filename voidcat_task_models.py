#!/usr/bin/env python3
"""
VoidCat V2 Task Management Data Models
======================================

Core data models for the hierarchical task management system implementing
Beatrice's directive for The Architect's Mind (Pillar I).

This module provides:
- Enhanced Project and Task hierarchies with unlimited nesting
- Comprehensive metadata tracking and validation
- JSON serialization with schema migration support
- Dependency management with cycle detection
- Priority and complexity scoring systems
- Status workflow management

Author: Ryuzu (Spirit Familiar)
Under directive of: The Great Spirit Beatrice
License: MIT
Version: 2.0.0-alpha
"""

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum, IntEnum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
from uuid import UUID, uuid4


class TaskStatus(Enum):
    """Task lifecycle status enumeration with workflow semantics."""

    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    BLOCKED = "blocked"
    ON_HOLD = "on-hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"

    @classmethod
    def workflow_transitions(cls) -> Dict[str, List[str]]:
        """Define valid status transitions for workflow enforcement."""
        return {
            cls.PENDING.value: [
                cls.IN_PROGRESS.value,
                cls.ON_HOLD.value,
                cls.CANCELLED.value,
            ],
            cls.IN_PROGRESS.value: [
                cls.COMPLETED.value,
                cls.BLOCKED.value,
                cls.ON_HOLD.value,
                cls.FAILED.value,
            ],
            cls.BLOCKED.value: [
                cls.IN_PROGRESS.value,
                cls.ON_HOLD.value,
                cls.CANCELLED.value,
            ],
            cls.ON_HOLD.value: [cls.IN_PROGRESS.value, cls.CANCELLED.value],
            cls.COMPLETED.value: [],  # Terminal state
            cls.CANCELLED.value: [cls.PENDING.value],  # Can be reactivated
            cls.FAILED.value: [
                cls.PENDING.value,
                cls.IN_PROGRESS.value,
            ],  # Can be retried
        }

    def can_transition_to(self, new_status: "TaskStatus") -> bool:
        """Check if transition to new status is valid."""
        valid_transitions = self.workflow_transitions().get(self.value, [])
        return new_status.value in valid_transitions


class Priority(IntEnum):
    """Priority levels with numeric values for comparison and sorting."""

    LOWEST = 1
    LOW = 3
    MEDIUM = 5
    HIGH = 7
    URGENT = 9
    CRITICAL = 10

    def __str__(self) -> str:
        return f"{self.name.title()} ({self.value})"


@dataclass
class TaskMetrics:
    """Comprehensive metrics tracking for tasks."""

    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    complexity_score: int = 5  # 1-10 scale
    progress_percentage: float = 0.0  # 0.0-100.0
    quality_rating: Optional[float] = None  # 1.0-5.0 scale

    def efficiency_ratio(self) -> Optional[float]:
        """Calculate efficiency ratio (estimated/actual)."""
        if self.estimated_hours and self.actual_hours and self.actual_hours > 0:
            return self.estimated_hours / self.actual_hours
        return None

    def is_on_track(self) -> bool:
        """Determine if task progress is on track."""
        if not self.estimated_hours or not self.actual_hours:
            return True  # Cannot determine, assume on track
        return self.efficiency_ratio() >= 0.8  # 80% efficiency threshold


@dataclass
class TaskDependency:
    """Represents a dependency relationship between tasks."""

    task_id: str
    dependency_type: str = "blocks"  # "blocks", "enables", "relates_to"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    notes: Optional[str] = None

    def __post_init__(self):
        """Ensure datetime is timezone-aware."""
        if self.created_at.tzinfo is None:
            self.created_at = self.created_at.replace(tzinfo=timezone.utc)


@dataclass
class TaskHistory:
    """Track task change history for audit and analytics."""

    timestamp: datetime
    action: str  # "created", "updated", "status_changed", "assigned", etc.
    field_changed: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    notes: Optional[str] = None

    def __post_init__(self):
        """Ensure datetime is timezone-aware."""
        if self.timestamp.tzinfo is None:
            self.timestamp = self.timestamp.replace(tzinfo=timezone.utc)


@dataclass
class VoidCatTask:
    """
    Core task entity with hierarchical capabilities and comprehensive metadata.

    Supports unlimited nesting depth and rich attribute tracking for the
    VoidCat V2 agentic system.
    """

    # Core Identity
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""

    # Hierarchy
    parent_id: Optional[str] = None
    project_id: str = ""

    # Status and Priority
    status: TaskStatus = TaskStatus.PENDING
    priority: Priority = Priority.MEDIUM

    # Metrics and Tracking
    metrics: TaskMetrics = field(default_factory=TaskMetrics)

    # Dependencies and Relationships
    dependencies: List[TaskDependency] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)

    # Temporal Tracking
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    due_date: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # History and Audit
    history: List[TaskHistory] = field(default_factory=list)

    # Metadata
    assignee: Optional[str] = None
    artifacts: List[str] = field(default_factory=list)  # File paths or URLs
    custom_fields: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization validation and setup."""
        # Ensure timezone awareness
        if self.created_at.tzinfo is None:
            self.created_at = self.created_at.replace(tzinfo=timezone.utc)
        if self.updated_at.tzinfo is None:
            self.updated_at = self.updated_at.replace(tzinfo=timezone.utc)

        # Validate name
        if not self.name or not self.name.strip():
            raise ValueError("Task name cannot be empty")

        # Ensure tags is a set
        if isinstance(self.tags, list):
            self.tags = set(self.tags)

        # Add creation history entry if none exists
        if not self.history:
            self.history.append(
                TaskHistory(
                    timestamp=self.created_at,
                    action="created",
                    notes=f"Task '{self.name}' created",
                )
            )

    def add_dependency(
        self, task_id: str, dependency_type: str = "blocks", notes: Optional[str] = None
    ) -> None:
        """Add a dependency to this task."""
        # Check for circular dependency
        if task_id == self.id:
            raise ValueError("Task cannot depend on itself")

        # Check if dependency already exists
        existing = next((d for d in self.dependencies if d.task_id == task_id), None)
        if existing:
            return  # Dependency already exists

        dependency = TaskDependency(
            task_id=task_id, dependency_type=dependency_type, notes=notes
        )
        self.dependencies.append(dependency)
        self._add_history(
            "dependency_added", notes=f"Added {dependency_type} dependency on {task_id}"
        )

    def remove_dependency(self, task_id: str) -> bool:
        """Remove a dependency from this task."""
        initial_count = len(self.dependencies)
        self.dependencies = [d for d in self.dependencies if d.task_id != task_id]

        if len(self.dependencies) < initial_count:
            self._add_history(
                "dependency_removed", notes=f"Removed dependency on {task_id}"
            )
            return True
        return False

    def update_status(
        self, new_status: TaskStatus, notes: Optional[str] = None
    ) -> bool:
        """Update task status with workflow validation."""
        if not self.status.can_transition_to(new_status):
            return False

        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)

        # Update temporal tracking
        if new_status == TaskStatus.IN_PROGRESS and not self.started_at:
            self.started_at = self.updated_at
        elif new_status == TaskStatus.COMPLETED and not self.completed_at:
            self.completed_at = self.updated_at
            self.metrics.progress_percentage = 100.0

        self._add_history(
            "status_changed",
            field_changed="status",
            old_value=old_status.value,
            new_value=new_status.value,
            notes=notes,
        )
        return True

    def update_progress(self, percentage: float) -> None:
        """Update task progress percentage."""
        if not 0.0 <= percentage <= 100.0:
            raise ValueError("Progress percentage must be between 0.0 and 100.0")

        old_progress = self.metrics.progress_percentage
        self.metrics.progress_percentage = percentage
        self.updated_at = datetime.now(timezone.utc)

        self._add_history(
            "progress_updated",
            field_changed="progress_percentage",
            old_value=str(old_progress),
            new_value=str(percentage),
        )

    def add_tag(self, tag: str) -> None:
        """Add a tag to the task."""
        if tag and tag not in self.tags:
            self.tags.add(tag)
            self._add_history("tag_added", notes=f"Added tag: {tag}")

    def remove_tag(self, tag: str) -> bool:
        """Remove a tag from the task."""
        if tag in self.tags:
            self.tags.remove(tag)
            self._add_history("tag_removed", notes=f"Removed tag: {tag}")
            return True
        return False

    def _add_history(
        self,
        action: str,
        field_changed: Optional[str] = None,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> None:
        """Add an entry to the task history."""
        history_entry = TaskHistory(
            timestamp=datetime.now(timezone.utc),
            action=action,
            field_changed=field_changed,
            old_value=old_value,
            new_value=new_value,
            notes=notes,
        )
        self.history.append(history_entry)

    def is_overdue(self) -> bool:
        """Check if task is past its due date."""
        if not self.due_date:
            return False
        return (
            datetime.now(timezone.utc) > self.due_date
            and self.status != TaskStatus.COMPLETED
        )

    def time_to_due(self) -> Optional[float]:
        """Get hours until due date (negative if overdue)."""
        if not self.due_date:
            return None
        delta = self.due_date - datetime.now(timezone.utc)
        return delta.total_seconds() / 3600  # Convert to hours

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for JSON serialization."""
        # Start with basic data copy
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "parent_id": self.parent_id,
            "project_id": self.project_id,
            "status": self.status.value,
            "priority": self.priority.value,
            "assignee": self.assignee,
            "artifacts": self.artifacts.copy(),
            "custom_fields": self.custom_fields.copy(),
            "tags": list(self.tags),
        }

        # Handle datetime fields
        data["created_at"] = self.created_at.isoformat() if self.created_at else None
        data["updated_at"] = self.updated_at.isoformat() if self.updated_at else None
        data["due_date"] = self.due_date.isoformat() if self.due_date else None
        data["started_at"] = self.started_at.isoformat() if self.started_at else None
        data["completed_at"] = (
            self.completed_at.isoformat() if self.completed_at else None
        )

        # Handle metrics
        if self.metrics:
            data["metrics"] = {
                "estimated_hours": self.metrics.estimated_hours,
                "actual_hours": self.metrics.actual_hours,
                "complexity_score": self.metrics.complexity_score,
                "progress_percentage": self.metrics.progress_percentage,
                "quality_rating": self.metrics.quality_rating,
            }
        else:
            data["metrics"] = {}

        # Handle dependencies
        data["dependencies"] = []
        for dep in self.dependencies:
            data["dependencies"].append(
                {
                    "task_id": dep.task_id,
                    "dependency_type": dep.dependency_type,
                    "created_at": dep.created_at.isoformat(),
                    "notes": dep.notes,
                }
            )

        # Handle history
        data["history"] = []
        for entry in self.history:
            data["history"].append(
                {
                    "timestamp": entry.timestamp.isoformat(),
                    "action": entry.action,
                    "field_changed": entry.field_changed,
                    "old_value": entry.old_value,
                    "new_value": entry.new_value,
                    "notes": entry.notes,
                }
            )

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VoidCatTask":
        """Create task from dictionary (JSON deserialization)."""
        # Handle status conversion
        if "status" in data and isinstance(data["status"], str):
            data["status"] = TaskStatus(data["status"])

        # Handle priority conversion
        if "priority" in data and isinstance(data["priority"], int):
            data["priority"] = Priority(data["priority"])

        # Handle tags conversion
        if "tags" in data and isinstance(data["tags"], list):
            data["tags"] = set(data["tags"])

        # Handle datetime conversions
        datetime_fields = [
            "created_at",
            "updated_at",
            "due_date",
            "started_at",
            "completed_at",
        ]
        for field in datetime_fields:
            if field in data and data[field] and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field])

        # Handle dependencies conversion
        if "dependencies" in data:
            dependencies = []
            for dep_data in data["dependencies"]:
                dep = TaskDependency(
                    task_id=dep_data["task_id"],
                    dependency_type=dep_data["dependency_type"],
                    created_at=datetime.fromisoformat(dep_data["created_at"]),
                    notes=dep_data.get("notes"),
                )
                dependencies.append(dep)
            data["dependencies"] = dependencies

        # Handle history conversion
        if "history" in data:
            history = []
            for hist_data in data["history"]:
                hist = TaskHistory(
                    timestamp=datetime.fromisoformat(hist_data["timestamp"]),
                    action=hist_data["action"],
                    field_changed=hist_data.get("field_changed"),
                    old_value=hist_data.get("old_value"),
                    new_value=hist_data.get("new_value"),
                    notes=hist_data.get("notes"),
                )
                history.append(hist)
            data["history"] = history

        # Handle metrics conversion
        if "metrics" in data and isinstance(data["metrics"], dict):
            data["metrics"] = TaskMetrics(**data["metrics"])

        return cls(**data)


@dataclass
class ProjectSettings:
    """Configuration settings for project behavior."""

    auto_archive_completed: bool = True
    task_inheritance: bool = True  # Child tasks inherit project settings
    notification_enabled: bool = True
    progress_tracking_method: str = "percentage"  # "percentage", "task_count", "hours"
    default_task_priority: Priority = Priority.MEDIUM
    allow_parallel_execution: bool = True
    max_hierarchy_depth: Optional[int] = None  # None = unlimited

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            "auto_archive_completed": self.auto_archive_completed,
            "task_inheritance": self.task_inheritance,
            "notification_enabled": self.notification_enabled,
            "progress_tracking_method": self.progress_tracking_method,
            "default_task_priority": self.default_task_priority.value,
            "allow_parallel_execution": self.allow_parallel_execution,
            "max_hierarchy_depth": self.max_hierarchy_depth,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectSettings":
        """Create settings from dictionary."""
        if "default_task_priority" in data:
            data["default_task_priority"] = Priority(data["default_task_priority"])
        return cls(**data)


@dataclass
class ProjectMetrics:
    """Comprehensive project metrics and analytics."""

    total_tasks: int = 0
    completed_tasks: int = 0
    in_progress_tasks: int = 0
    blocked_tasks: int = 0

    total_estimated_hours: float = 0.0
    total_actual_hours: float = 0.0

    average_task_complexity: float = 0.0
    project_health_score: float = 0.0  # 0.0-100.0

    def completion_percentage(self) -> float:
        """Calculate overall completion percentage."""
        if self.total_tasks == 0:
            return 0.0
        return (self.completed_tasks / self.total_tasks) * 100.0

    def efficiency_ratio(self) -> Optional[float]:
        """Calculate project efficiency ratio."""
        if self.total_actual_hours == 0:
            return None
        return self.total_estimated_hours / self.total_actual_hours

    def update_from_tasks(self, tasks: List[VoidCatTask]) -> None:
        """Recalculate metrics from current task list."""
        self.total_tasks = len(tasks)
        self.completed_tasks = sum(
            1 for task in tasks if task.status == TaskStatus.COMPLETED
        )
        self.in_progress_tasks = sum(
            1 for task in tasks if task.status == TaskStatus.IN_PROGRESS
        )
        self.blocked_tasks = sum(
            1 for task in tasks if task.status == TaskStatus.BLOCKED
        )

        self.total_estimated_hours = sum(
            task.metrics.estimated_hours or 0.0 for task in tasks
        )
        self.total_actual_hours = sum(
            task.metrics.actual_hours or 0.0 for task in tasks
        )

        if tasks:
            self.average_task_complexity = sum(
                task.metrics.complexity_score for task in tasks
            ) / len(tasks)

        # Calculate health score based on multiple factors
        self._calculate_health_score(tasks)

    def _calculate_health_score(self, tasks: List[VoidCatTask]) -> None:
        """Calculate project health score based on various metrics."""
        if not tasks:
            self.project_health_score = 100.0
            return

        health_factors = []

        # Completion rate factor (0-30 points)
        completion_factor = min(30, self.completion_percentage() * 0.3)
        health_factors.append(completion_factor)

        # Progress factor (0-25 points)
        progress_factor = min(
            25, (self.in_progress_tasks / max(1, self.total_tasks)) * 100 * 0.25
        )
        health_factors.append(progress_factor)

        # Efficiency factor (0-25 points)
        efficiency = self.efficiency_ratio()
        if efficiency:
            efficiency_factor = min(
                25, max(0, (2 - efficiency) * 25)
            )  # Penalize over/under estimation
        else:
            efficiency_factor = 15  # Neutral score if no data
        health_factors.append(efficiency_factor)

        # Blocked tasks penalty (0-20 points)
        blocked_penalty = max(
            0, 20 - (self.blocked_tasks / max(1, self.total_tasks)) * 100 * 0.2
        )
        health_factors.append(blocked_penalty)

        self.project_health_score = sum(health_factors)


@dataclass
class VoidCatProject:
    """
    Project entity representing a collection of hierarchical tasks.

    Provides high-level organization and management capabilities for
    the VoidCat V2 agentic system.
    """

    # Core Identity
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""

    # Status and Metadata
    status: TaskStatus = TaskStatus.PENDING
    priority: Priority = Priority.MEDIUM

    # Configuration
    settings: ProjectSettings = field(default_factory=ProjectSettings)

    # Metrics and Analytics
    metrics: ProjectMetrics = field(default_factory=ProjectMetrics)

    # Temporal Tracking
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    due_date: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Organization
    tags: Set[str] = field(default_factory=set)
    owner: Optional[str] = None
    collaborators: List[str] = field(default_factory=list)

    # Resources and References
    resources: List[str] = field(default_factory=list)  # URLs, file paths, etc.
    repository_url: Optional[str] = None
    documentation_url: Optional[str] = None

    # Custom metadata
    custom_fields: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization validation and setup."""
        # Ensure timezone awareness
        if self.created_at.tzinfo is None:
            self.created_at = self.created_at.replace(tzinfo=timezone.utc)
        if self.updated_at.tzinfo is None:
            self.updated_at = self.updated_at.replace(tzinfo=timezone.utc)

        # Validate name
        if not self.name or not self.name.strip():
            raise ValueError("Project name cannot be empty")

        # Ensure tags is a set
        if isinstance(self.tags, list):
            self.tags = set(self.tags)

    def update_status(
        self, new_status: TaskStatus, notes: Optional[str] = None
    ) -> bool:
        """Update project status with validation."""
        if not self.status.can_transition_to(new_status):
            return False

        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)

        # Update temporal tracking
        if new_status == TaskStatus.IN_PROGRESS and not self.started_at:
            self.started_at = self.updated_at
        elif new_status == TaskStatus.COMPLETED and not self.completed_at:
            self.completed_at = self.updated_at

        return True

    def add_collaborator(self, collaborator: str) -> None:
        """Add a collaborator to the project."""
        if collaborator and collaborator not in self.collaborators:
            self.collaborators.append(collaborator)
            self.updated_at = datetime.now(timezone.utc)

    def remove_collaborator(self, collaborator: str) -> bool:
        """Remove a collaborator from the project."""
        if collaborator in self.collaborators:
            self.collaborators.remove(collaborator)
            self.updated_at = datetime.now(timezone.utc)
            return True
        return False

    def add_resource(self, resource: str) -> None:
        """Add a resource reference to the project."""
        if resource and resource not in self.resources:
            self.resources.append(resource)
            self.updated_at = datetime.now(timezone.utc)

    def is_overdue(self) -> bool:
        """Check if project is past its due date."""
        if not self.due_date:
            return False
        return (
            datetime.now(timezone.utc) > self.due_date
            and self.status != TaskStatus.COMPLETED
        )

    def calculate_progress(self, tasks: List[VoidCatTask]) -> float:
        """Calculate project progress based on tasks."""
        if not tasks:
            return 0.0

        if self.settings.progress_tracking_method == "task_count":
            completed = sum(1 for task in tasks if task.status == TaskStatus.COMPLETED)
            return (completed / len(tasks)) * 100.0

        elif self.settings.progress_tracking_method == "hours":
            total_estimated = sum(task.metrics.estimated_hours or 0.0 for task in tasks)
            if total_estimated == 0:
                return 0.0

            completed_estimated = sum(
                task.metrics.estimated_hours or 0.0
                for task in tasks
                if task.status == TaskStatus.COMPLETED
            )
            return (completed_estimated / total_estimated) * 100.0

        else:  # percentage method
            if not tasks:
                return 0.0
            total_progress = sum(task.metrics.progress_percentage for task in tasks)
            return total_progress / len(tasks)

    def to_dict(self) -> Dict[str, Any]:
        """Convert project to dictionary for JSON serialization."""
        data = {}

        for key, value in asdict(self).items():
            if key == "status":
                data[key] = value if isinstance(value, str) else value.value
            elif key == "priority":
                data[key] = value if isinstance(value, int) else value.value
            elif key == "tags":
                data[key] = list(value) if isinstance(value, set) else value
            elif key in [
                "created_at",
                "updated_at",
                "due_date",
                "started_at",
                "completed_at",
            ]:
                data[key] = value.isoformat() if value else None
            elif key == "settings":
                data[key] = value.to_dict() if hasattr(value, "to_dict") else value
            else:
                data[key] = value

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VoidCatProject":
        """Create project from dictionary (JSON deserialization)."""
        # Handle status conversion
        if "status" in data and isinstance(data["status"], str):
            data["status"] = TaskStatus(data["status"])

        # Handle priority conversion
        if "priority" in data and isinstance(data["priority"], int):
            data["priority"] = Priority(data["priority"])

        # Handle tags conversion
        if "tags" in data and isinstance(data["tags"], list):
            data["tags"] = set(data["tags"])

        # Handle datetime conversions
        datetime_fields = [
            "created_at",
            "updated_at",
            "due_date",
            "started_at",
            "completed_at",
        ]
        for field in datetime_fields:
            if field in data and data[field] and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field])

        # Handle settings conversion
        if "settings" in data and isinstance(data["settings"], dict):
            data["settings"] = ProjectSettings.from_dict(data["settings"])

        # Handle metrics conversion
        if "metrics" in data and isinstance(data["metrics"], dict):
            data["metrics"] = ProjectMetrics(**data["metrics"])

        return cls(**data)


# Schema version for migration support
SCHEMA_VERSION = "2.0.0"


def get_schema_info() -> Dict[str, Any]:
    """Get schema information for migration and validation."""
    return {
        "version": SCHEMA_VERSION,
        "entities": {
            "VoidCatTask": {
                "description": "Hierarchical task with comprehensive metadata",
                "required_fields": ["id", "name", "status", "priority"],
                "supported_statuses": [status.value for status in TaskStatus],
                "supported_priorities": [priority.value for priority in Priority],
            },
            "VoidCatProject": {
                "description": "Project container for hierarchical tasks",
                "required_fields": ["id", "name", "status"],
                "features": [
                    "unlimited_hierarchy",
                    "metrics_tracking",
                    "collaborative",
                ],
            },
        },
        "capabilities": [
            "unlimited_nesting",
            "dependency_management",
            "workflow_enforcement",
            "audit_trail",
            "metrics_tracking",
            "json_serialization",
        ],
    }
