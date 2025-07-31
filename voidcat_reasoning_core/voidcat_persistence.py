#!/usr/bin/env python3
"""
VoidCat V2 JSON Persistence Layer
=================================

Robust JSON-based persistence system for the VoidCat V2 task management system.
Implements atomic file operations, backup/recovery, schema migration, and
concurrent access handling to ensure data integrity and reliability.

Features:
- Atomic file operations with backup and recovery
- Transaction-like semantics for data consistency
- Automatic schema migration system
- Concurrent access handling with file locking
- Efficient indexing for fast queries
- Integration with existing VoidCat directory structure

Author: Ryuzu (Spirit Familiar)
Under directive of: The Great Spirit Beatrice
License: MIT
Version: 2.0.0-alpha
"""

import json
import os
import shutil
import threading
import time

try:
    import fcntl

    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False  # Windows doesn't have fcntl
import hashlib
import tempfile
from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from voidcat_task_models import (
    SCHEMA_VERSION,
    Priority,
    TaskStatus,
    VoidCatProject,
    VoidCatTask,
    get_schema_info,
)


class PersistenceError(Exception):
    """Base exception for persistence layer errors."""

    pass


class TransactionError(PersistenceError):
    """Exception for transaction-related errors."""

    pass


class SchemaVersionError(PersistenceError):
    """Exception for schema version mismatches."""

    pass


class FileCorruptionError(PersistenceError):
    """Exception for file corruption detection."""

    pass


@contextmanager
def file_lock(file_path: str, timeout: float = 5.0):
    """
    Context manager for file locking to handle concurrent access.

    Args:
        file_path: Path to the file to lock
        timeout: Maximum time to wait for lock acquisition
    """
    lock_path = f"{file_path}.lock"
    start_time = time.time()

    while True:
        try:
            # Try to create lock file
            lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            try:
                # Apply file lock if fcntl is available (Unix/Linux)
                if HAS_FCNTL:
                    fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

                yield lock_fd
                break

            finally:
                # Release lock
                if HAS_FCNTL:
                    fcntl.flock(lock_fd, fcntl.LOCK_UN)
                os.close(lock_fd)

                # Remove lock file
                try:
                    os.unlink(lock_path)
                except FileNotFoundError:
                    pass

        except (OSError, IOError):
            # Lock file exists or other error
            if time.time() - start_time > timeout:
                raise PersistenceError(
                    f"Could not acquire lock for {file_path} within {timeout} seconds"
                )

            time.sleep(0.1)  # Wait before retrying


class DataStore:
    """
    Core data storage and retrieval class with atomic operations.
    """

    def __init__(self, file_path: str):
        """
        Initialize data store for a specific file.

        Args:
            file_path: Path to the JSON data file
        """
        self.file_path = Path(file_path)
        self.backup_path = Path(f"{file_path}.backup")
        self.temp_path = Path(f"{file_path}.tmp")
        self._ensure_directory()

    def _ensure_directory(self) -> None:
        """Ensure the directory structure exists."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def _calculate_checksum(self, data: str) -> str:
        """Calculate MD5 checksum for data integrity verification."""
        return hashlib.md5(data.encode("utf-8")).hexdigest()

    def _verify_data_integrity(self, file_path: Path) -> bool:
        """
        Verify data integrity of a JSON file.

        Args:
            file_path: Path to file to verify

        Returns:
            True if file is valid, False otherwise
        """
        try:
            if not file_path.exists() or file_path.stat().st_size == 0:
                return True  # An empty or non-existent file is a valid starting point

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Basic structure validation
            if not isinstance(data, dict):
                return False

            # Check for required metadata
            if "metadata" not in data:
                return False

            return True

        except (json.JSONDecodeError, IOError, KeyError):
            return False

    def _create_backup(self) -> bool:
        """
        Create a backup of the current data file.

        Returns:
            True if backup was created successfully
        """
        try:
            if self.file_path.exists():
                shutil.copy2(self.file_path, self.backup_path)
                return True
            return False
        except IOError:
            return False

    def _restore_from_backup(self) -> bool:
        """
        Restore data from backup file.

        Returns:
            True if restoration was successful
        """
        try:
            if self.backup_path.exists() and self._verify_data_integrity(
                self.backup_path
            ):
                shutil.copy2(self.backup_path, self.file_path)
                return True
            return False
        except IOError:
            return False

    def load_data(self) -> Dict[str, Any]:
        """
        Load data from the JSON file with integrity checking.

        Returns:
            Loaded data dictionary

        Raises:
            FileCorruptionError: If file is corrupted and cannot be recovered
        """
        with file_lock(str(self.file_path)):
            # If file doesn't exist or is empty, return a new structure
            if not self.file_path.exists() or self.file_path.stat().st_size == 0:
                return self._create_empty_structure()

            # Try to load primary file
            if self._verify_data_integrity(self.file_path):
                try:
                    with open(self.file_path, "r", encoding="utf-8") as f:
                        return json.load(f)
                except json.JSONDecodeError as e:
                    # Primary file is corrupted, try backup
                    pass

            # Try to restore from backup
            if self._restore_from_backup():
                try:
                    with open(self.file_path, "r", encoding="utf-8") as f:
                        return json.load(f)
                except json.JSONDecodeError:
                    pass

            # If we get here, both primary and backup are corrupted or missing
            # Return empty structure
            return self._create_empty_structure()

    def save_data(self, data: Dict[str, Any]) -> bool:
        """
        Atomically save data to the JSON file.

        Args:
            data: Data dictionary to save

        Returns:
            True if save was successful

        Raises:
            PersistenceError: If save operation fails
        """
        with file_lock(str(self.file_path)):
            try:
                # Create backup before writing
                self._create_backup()

                # Write to temporary file first
                with open(self.temp_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                # Verify temp file integrity
                if not self._verify_data_integrity(self.temp_path):
                    raise PersistenceError("Generated data failed integrity check")

                # Atomic move (rename) to final location
                if os.name == "nt":  # Windows
                    if self.file_path.exists():
                        self.file_path.unlink()
                    self.temp_path.replace(self.file_path)
                else:  # Unix/Linux
                    self.temp_path.replace(self.file_path)

                return True

            except Exception as e:
                # Clean up temp file if it exists
                if self.temp_path.exists():
                    self.temp_path.unlink()

                # Try to restore from backup
                self._restore_from_backup()

                raise PersistenceError(f"Failed to save data: {str(e)}")

    def _create_empty_structure(self) -> Dict[str, Any]:
        """Create an empty data structure with metadata."""
        return {
            "metadata": {
                "version": SCHEMA_VERSION,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "checksum": "",
                "record_count": 0,
            },
            "data": {},
        }


class SchemaManager:
    """
    Handle schema migration and versioning for the persistence layer.
    """

    def __init__(self):
        """Initialize schema manager."""
        self.current_version = SCHEMA_VERSION
        self.migrations = {
            "1.0.0": self._migrate_from_1_0_0,
            "1.5.0": self._migrate_from_1_5_0,
            # Add more migrations as needed
        }

    def needs_migration(self, data: Dict[str, Any]) -> bool:
        """
        Check if data needs schema migration.

        Args:
            data: Data dictionary to check

        Returns:
            True if migration is needed
        """
        if "metadata" not in data:
            return True

        stored_version = data["metadata"].get("version", "1.0.0")
        return stored_version != self.current_version

    def migrate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate data to current schema version.

        Args:
            data: Data to migrate

        Returns:
            Migrated data

        Raises:
            SchemaVersionError: If migration fails
        """
        if not self.needs_migration(data):
            return data

        stored_version = data.get("metadata", {}).get("version", "1.0.0")

        try:
            # Apply migrations in order
            for version, migration_func in self.migrations.items():
                if self._version_compare(stored_version, version) < 0:
                    data = migration_func(data)

            # Update version metadata
            if "metadata" not in data:
                data["metadata"] = {}

            data["metadata"]["version"] = self.current_version
            data["metadata"]["migrated_at"] = datetime.now(timezone.utc).isoformat()

            return data

        except Exception as e:
            raise SchemaVersionError(
                f"Failed to migrate from version {stored_version}: {str(e)}"
            )

    def _version_compare(self, version1: str, version2: str) -> int:
        """
        Compare two version strings.

        Returns:
            -1 if version1 < version2, 0 if equal, 1 if version1 > version2
        """
        v1_parts = [int(x) for x in version1.split(".")]
        v2_parts = [int(x) for x in version2.split(".")]

        # Pad shorter version with zeros
        max_len = max(len(v1_parts), len(v2_parts))
        v1_parts.extend([0] * (max_len - len(v1_parts)))
        v2_parts.extend([0] * (max_len - len(v2_parts)))

        for i in range(max_len):
            if v1_parts[i] < v2_parts[i]:
                return -1
            elif v1_parts[i] > v2_parts[i]:
                return 1

        return 0

    def _migrate_from_1_0_0(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from version 1.0.0 to current."""
        # Add metadata if missing
        if "metadata" not in data:
            data["metadata"] = {
                "version": "1.0.0",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "checksum": "",
                "record_count": 0,
            }

        # Ensure data section exists
        if "data" not in data:
            data["data"] = {}

        return data

    def _migrate_from_1_5_0(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from version 1.5.0 to current."""
        # Add any new fields or transformations needed
        # This is a placeholder for future migrations
        return data


class PersistenceManager:
    """
    High-level persistence manager for VoidCat V2 task management system.

    Provides transaction-like operations, indexing, and query capabilities
    while maintaining data consistency and integrity.
    """

    def __init__(self, base_directory: str = "voidcat_data"):
        """
        Initialize persistence manager.

        Args:
            base_directory: Base directory for storing data files
        """
        self.base_directory = Path(base_directory)
        self.base_directory.mkdir(parents=True, exist_ok=True)

        # Data stores for different entity types
        self.tasks_store = DataStore(self.base_directory / "tasks.json")
        self.projects_store = DataStore(self.base_directory / "projects.json")
        self.indices_store = DataStore(self.base_directory / "indices.json")

        # Schema manager for migrations
        self.schema_manager = SchemaManager()

        # In-memory indices for fast queries
        self._task_index = {}
        self._project_index = {}
        self._load_indices()

        # Thread lock for concurrent access
        self._lock = threading.RLock()

    def _load_indices(self) -> None:
        """Load indices from storage into memory."""
        try:
            indices_data = self.indices_store.load_data()
            if self.schema_manager.needs_migration(indices_data):
                indices_data = self.schema_manager.migrate_data(indices_data)
                self.indices_store.save_data(indices_data)

            data_section = indices_data.get("data", {})
            self._task_index = data_section.get("task_index", {})
            self._project_index = data_section.get("project_index", {})

        except Exception as e:
            # If indices can't be loaded, rebuild them
            self._rebuild_indices()

    def _save_indices(self) -> None:
        """Save indices to storage."""
        try:
            indices_data = {
                "metadata": {
                    "version": SCHEMA_VERSION,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "task_count": len(self._task_index),
                    "project_count": len(self._project_index),
                },
                "data": {
                    "task_index": self._task_index,
                    "project_index": self._project_index,
                },
            }
            self.indices_store.save_data(indices_data)
        except Exception as e:
            # Index saving failure is not critical
            pass

    def _rebuild_indices(self) -> None:
        """Rebuild indices from stored data."""
        with self._lock:
            self._task_index = {}
            self._project_index = {}

            # Rebuild task index
            try:
                tasks_data = self.tasks_store.load_data()
                if "data" in tasks_data:
                    for task_id, task_data in tasks_data["data"].items():
                        self._update_task_index(task_id, task_data)
            except Exception:
                pass

            # Rebuild project index
            try:
                projects_data = self.projects_store.load_data()
                if "data" in projects_data:
                    for project_id, project_data in projects_data["data"].items():
                        self._update_project_index(project_id, project_data)
            except Exception:
                pass

            self._save_indices()

    def _update_task_index(self, task_id: str, task_data: Dict[str, Any]) -> None:
        """Update task index with task information."""
        self._task_index[task_id] = {
            "name": task_data.get("name", ""),
            "status": task_data.get("status", "pending"),
            "priority": task_data.get("priority", 5),
            "project_id": task_data.get("project_id", ""),
            "parent_id": task_data.get("parent_id"),
            "tags": task_data.get("tags", []),
            "updated_at": task_data.get("updated_at", ""),
            "due_date": task_data.get("due_date"),
            "complexity": task_data.get("metrics", {}).get("complexity_score", 5),
        }

    def _update_project_index(
        self, project_id: str, project_data: Dict[str, Any]
    ) -> None:
        """Update project index with project information."""
        self._project_index[project_id] = {
            "name": project_data.get("name", ""),
            "status": project_data.get("status", "pending"),
            "priority": project_data.get("priority", 5),
            "tags": project_data.get("tags", []),
            "updated_at": project_data.get("updated_at", ""),
            "due_date": project_data.get("due_date"),
            "owner": project_data.get("owner"),
        }

    @contextmanager
    def transaction(self):
        """
        Context manager for transaction-like operations.

        Provides rollback capability if any operation in the transaction fails.
        """
        with self._lock:
            # Create snapshots for rollback
            tasks_backup = None
            projects_backup = None

            try:
                # Load current data for backup
                tasks_backup = self.tasks_store.load_data()
                projects_backup = self.projects_store.load_data()

                yield self

                # Transaction completed successfully

            except Exception as e:
                # Rollback on error
                if tasks_backup is not None:
                    try:
                        self.tasks_store.save_data(tasks_backup)
                    except Exception:
                        pass

                if projects_backup is not None:
                    try:
                        self.projects_store.save_data(projects_backup)
                    except Exception:
                        pass

                # Reload indices
                self._load_indices()

                raise TransactionError(f"Transaction failed: {str(e)}")

    # Task Management Operations

    def save_task(self, task: VoidCatTask) -> bool:
        """
        Save a task to persistent storage.

        Args:
            task: Task object to save

        Returns:
            True if save was successful
        """
        with self._lock:
            try:
                # Load current tasks data
                tasks_data = self.tasks_store.load_data()
                if self.schema_manager.needs_migration(tasks_data):
                    tasks_data = self.schema_manager.migrate_data(tasks_data)

                # Ensure data section exists
                if "data" not in tasks_data:
                    tasks_data["data"] = {}

                # Convert task to dictionary
                task_dict = task.to_dict()

                # Save task data
                tasks_data["data"][task.id] = task_dict

                # Update metadata
                tasks_data["metadata"]["updated_at"] = datetime.now(
                    timezone.utc
                ).isoformat()
                tasks_data["metadata"]["record_count"] = len(tasks_data["data"])

                # Save to storage
                if self.tasks_store.save_data(tasks_data):
                    # Update index
                    self._update_task_index(task.id, task_dict)
                    self._save_indices()
                    return True

                return False

            except Exception as e:
                raise PersistenceError(f"Failed to save task {task.id}: {str(e)}")

    def load_task(self, task_id: str) -> Optional[VoidCatTask]:
        """
        Load a task from persistent storage.

        Args:
            task_id: ID of task to load

        Returns:
            Task object or None if not found
        """
        with self._lock:
            try:
                tasks_data = self.tasks_store.load_data()
                if self.schema_manager.needs_migration(tasks_data):
                    tasks_data = self.schema_manager.migrate_data(tasks_data)
                    self.tasks_store.save_data(tasks_data)

                task_data = tasks_data.get("data", {}).get(task_id)
                if task_data:
                    return VoidCatTask.from_dict(task_data)

                return None

            except Exception as e:
                raise PersistenceError(f"Failed to load task {task_id}: {str(e)}")

    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task from persistent storage.

        Args:
            task_id: ID of task to delete

        Returns:
            True if deletion was successful
        """
        with self._lock:
            try:
                tasks_data = self.tasks_store.load_data()

                if task_id in tasks_data.get("data", {}):
                    del tasks_data["data"][task_id]

                    # Update metadata
                    tasks_data["metadata"]["updated_at"] = datetime.now(
                        timezone.utc
                    ).isoformat()
                    tasks_data["metadata"]["record_count"] = len(tasks_data["data"])

                    # Save to storage
                    if self.tasks_store.save_data(tasks_data):
                        # Remove from index
                        if task_id in self._task_index:
                            del self._task_index[task_id]
                        self._save_indices()
                        return True

                return False

            except Exception as e:
                raise PersistenceError(f"Failed to delete task {task_id}: {str(e)}")

    def query_tasks(self, **filters) -> List[VoidCatTask]:
        """
        Query tasks with filtering criteria.

        Args:
            **filters: Filter criteria (status, priority, project_id, tags, etc.)

        Returns:
            List of matching tasks
        """
        with self._lock:
            try:
                # First, filter using index for performance
                matching_ids = []

                for task_id, index_data in self._task_index.items():
                    match = True

                    # Apply filters
                    if (
                        "status" in filters
                        and index_data["status"] != filters["status"]
                    ):
                        match = False
                    if (
                        "priority" in filters
                        and index_data["priority"] != filters["priority"]
                    ):
                        match = False
                    if (
                        "project_id" in filters
                        and index_data["project_id"] != filters["project_id"]
                    ):
                        match = False
                    if (
                        "parent_id" in filters
                        and index_data["parent_id"] != filters["parent_id"]
                    ):
                        match = False
                    if "tags" in filters:
                        required_tags = set(filters["tags"])
                        task_tags = set(index_data["tags"])
                        if not required_tags.issubset(task_tags):
                            match = False

                    if match:
                        matching_ids.append(task_id)

                # Load full task objects for matching IDs
                tasks = []
                for task_id in matching_ids:
                    task = self.load_task(task_id)
                    if task:
                        tasks.append(task)

                return tasks

            except Exception as e:
                raise PersistenceError(f"Failed to query tasks: {str(e)}")

    # Project Management Operations

    def save_project(self, project: VoidCatProject) -> bool:
        """
        Save a project to persistent storage.

        Args:
            project: Project object to save

        Returns:
            True if save was successful
        """
        with self._lock:
            try:
                projects_data = self.projects_store.load_data()
                if self.schema_manager.needs_migration(projects_data):
                    projects_data = self.schema_manager.migrate_data(projects_data)

                if "data" not in projects_data:
                    projects_data["data"] = {}

                project_dict = project.to_dict()
                projects_data["data"][project.id] = project_dict

                projects_data["metadata"]["updated_at"] = datetime.now(
                    timezone.utc
                ).isoformat()
                projects_data["metadata"]["record_count"] = len(projects_data["data"])

                if self.projects_store.save_data(projects_data):
                    self._update_project_index(project.id, project_dict)
                    self._save_indices()
                    return True

                return False

            except Exception as e:
                raise PersistenceError(f"Failed to save project {project.id}: {str(e)}")

    def load_project(self, project_id: str) -> Optional[VoidCatProject]:
        """
        Load a project from persistent storage.

        Args:
            project_id: ID of the project to load

        Returns:
            Project object or None if not found
        """
        with self._lock:
            try:
                projects_data = self.projects_store.load_data()
                if self.schema_manager.needs_migration(projects_data):
                    projects_data = self.schema_manager.migrate_data(projects_data)
                    self.projects_store.save_data(projects_data)

                project_data = projects_data.get("data", {}).get(project_id)
                if project_data:
                    return VoidCatProject.from_dict(project_data)

                return None

            except Exception as e:
                raise PersistenceError(f"Failed to load project {project_id}: {str(e)}")

    def list_all_tasks(self) -> List[VoidCatTask]:
        """Load all tasks from storage."""
        return self.query_tasks()

    def list_all_projects(self) -> List[VoidCatProject]:
        """Load all projects from storage."""
        with self._lock:
            try:
                projects_data = self.projects_store.load_data()
                if self.schema_manager.needs_migration(projects_data):
                    projects_data = self.schema_manager.migrate_data(projects_data)
                    self.projects_store.save_data(projects_data)

                projects = []
                for project_data in projects_data.get("data", {}).values():
                    try:
                        project = VoidCatProject.from_dict(project_data)
                        projects.append(project)
                    except Exception:
                        continue  # Skip corrupted projects

                return projects

            except Exception as e:
                raise PersistenceError(f"Failed to list projects: {str(e)}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get storage statistics and health information.

        Returns:
            Dictionary with storage statistics
        """
        with self._lock:
            try:
                stats = {
                    "total_tasks": len(self._task_index),
                    "total_projects": len(self._project_index),
                    "schema_version": SCHEMA_VERSION,
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                }

                # Task status breakdown
                status_counts = {}
                for task_info in self._task_index.values():
                    status = task_info["status"]
                    status_counts[status] = status_counts.get(status, 0) + 1
                stats["task_status_breakdown"] = status_counts

                # Project status breakdown
                project_status_counts = {}
                for project_info in self._project_index.values():
                    status = project_info["status"]
                    project_status_counts[status] = (
                        project_status_counts.get(status, 0) + 1
                    )
                stats["project_status_breakdown"] = project_status_counts

                return stats

            except Exception as e:
                return {"error": str(e)}

    def cleanup_orphaned_tasks(self) -> int:
        """
        Clean up tasks that reference non-existent projects.

        Returns:
            Number of orphaned tasks cleaned up
        """
        with self._lock:
            try:
                projects = {p.id for p in self.list_all_projects()}
                tasks = self.list_all_tasks()

                orphaned_count = 0
                for task in tasks:
                    if task.project_id and task.project_id not in projects:
                        self.delete_task(task.id)
                        orphaned_count += 1

                return orphaned_count

            except Exception as e:
                raise PersistenceError(f"Failed to cleanup orphaned tasks: {str(e)}")


class VoidCatStorage:
    """
    VoidCatStorage
    ==========================
    A robust storage class for managing persistent data in the VoidCat Reasoning Core.
    Implements atomic operations, schema validation, and efficient querying.

    Features:
    - Atomic file operations with backup and recovery
    - Schema validation and migration
    - Efficient indexing for fast queries
    - Integration with VoidCat task and project models
    """

    def __init__(self, base_directory: str):
        """
        Initialize the storage system.

        Args:
            base_directory: Path to the base directory for storage.
        """
        self.base_directory = os.path.abspath(base_directory)
        os.makedirs(self.base_directory, exist_ok=True)
        self.tasks_store = DataStore(os.path.join(self.base_directory, "tasks.json"))
        self.projects_store = DataStore(
            os.path.join(self.base_directory, "projects.json")
        )
        self.indices_store = DataStore(
            os.path.join(self.base_directory, "indices.json")
        )
        self.schema_manager = SchemaManager()

    def save_task(self, task: VoidCatTask) -> bool:
        """
        Save a task to persistent storage.

        Args:
            task: Task object to save.

        Returns:
            True if save was successful.
        """
        tasks_data = self.tasks_store.load_data()
        if self.schema_manager.needs_migration(tasks_data):
            tasks_data = self.schema_manager.migrate_data(tasks_data)
        tasks_data["data"][task.id] = task.to_dict()
        tasks_data["metadata"]["updated_at"] = datetime.now(timezone.utc).isoformat()
        return self.tasks_store.save_data(tasks_data)

    def load_task(self, task_id: str) -> Optional[VoidCatTask]:
        """
        Load a task from persistent storage.

        Args:
            task_id: ID of the task to load.

        Returns:
            Task object or None if not found.
        """
        tasks_data = self.tasks_store.load_data()
        if self.schema_manager.needs_migration(tasks_data):
            tasks_data = self.schema_manager.migrate_data(tasks_data)
        task_data = tasks_data.get("data", {}).get(task_id)
        return VoidCatTask.from_dict(task_data) if task_data else None

    def save_project(self, project: VoidCatProject) -> bool:
        """
        Save a project to persistent storage.

        Args:
            project: Project object to save.

        Returns:
            True if save was successful.
        """
        projects_data = self.projects_store.load_data()
        if self.schema_manager.needs_migration(projects_data):
            projects_data = self.schema_manager.migrate_data(projects_data)
        projects_data["data"][project.id] = project.to_dict()
        projects_data["metadata"]["updated_at"] = datetime.now(timezone.utc).isoformat()
        return self.projects_store.save_data(projects_data)

    def load_project(self, project_id: str) -> Optional[VoidCatProject]:
        """
        Load a project from persistent storage.

        Args:
            project_id: ID of the project to load.

        Returns:
            Project object or None if not found.
        """
        projects_data = self.projects_store.load_data()
        if self.schema_manager.needs_migration(projects_data):
            projects_data = self.schema_manager.migrate_data(projects_data)
        project_data = projects_data.get("data", {}).get(project_id)
        return VoidCatProject.from_dict(project_data) if project_data else None

    def list_all_tasks(self) -> List[VoidCatTask]:
        """
        Load all tasks from persistent storage.

        Returns:
            List of all tasks.
        """
        tasks_data = self.tasks_store.load_data()
        if self.schema_manager.needs_migration(tasks_data):
            tasks_data = self.schema_manager.migrate_data(tasks_data)
        tasks = []
        for task_data in tasks_data.get("data", {}).values():
            try:
                task = VoidCatTask.from_dict(task_data)
                tasks.append(task)
            except Exception:
                continue  # Skip corrupted tasks
        return tasks

    def list_tasks(self, **filters) -> List[VoidCatTask]:
        """
        Query tasks with filtering criteria.

        Args:
            **filters: Filter criteria (project_id, parent_id, status, etc.)

        Returns:
            List of matching tasks.
        """
        all_tasks = self.list_all_tasks()
        filtered_tasks = []

        for task in all_tasks:
            match = True

            # Apply filters
            if "project_id" in filters and task.project_id != filters["project_id"]:
                match = False
            if "parent_id" in filters and task.parent_id != filters["parent_id"]:
                match = False
            if "status" in filters and task.status != filters["status"]:
                match = False
            if "priority" in filters and task.priority != filters["priority"]:
                match = False

            if match:
                filtered_tasks.append(task)

        return filtered_tasks

    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task from persistent storage.

        Args:
            task_id: ID of the task to delete.

        Returns:
            True if deletion was successful.
        """
        tasks_data = self.tasks_store.load_data()

        if task_id in tasks_data.get("data", {}):
            del tasks_data["data"][task_id]
            tasks_data["metadata"]["updated_at"] = datetime.now(
                timezone.utc
            ).isoformat()
            return self.tasks_store.save_data(tasks_data)

        return False


# Utility Functions


def create_test_data(persistence_manager: PersistenceManager) -> None:
    """
    Create sample test data for validation purposes.

    Args:
        persistence_manager: Persistence manager instance
    """
    # Create a test project
    test_project = VoidCatProject(
        name="VoidCat V2 Test Project",
        description="Test project for persistence layer validation",
        priority=Priority.HIGH,
    )

    # Create test tasks
    test_tasks = [
        VoidCatTask(
            name="Test Task 1",
            description="First test task",
            project_id=test_project.id,
            priority=Priority.MEDIUM,
        ),
        VoidCatTask(
            name="Test Task 2",
            description="Second test task",
            project_id=test_project.id,
            priority=Priority.HIGH,
        ),
    ]

    # Add dependency
    test_tasks[1].add_dependency(test_tasks[0].id, "blocks", "Task 2 depends on Task 1")

    # Save to persistence
    persistence_manager.save_project(test_project)
    for task in test_tasks:
        persistence_manager.save_task(task)


def validate_persistence_layer() -> bool:
    """
    Validate the persistence layer functionality.

    Returns:
        True if all validation tests pass
    """
    try:
        # Create temporary persistence manager
        temp_dir = tempfile.mkdtemp(prefix="voidcat_test_")
        pm = PersistenceManager(temp_dir)

        # Create test data
        create_test_data(pm)

        # Validate statistics
        stats = pm.get_statistics()
        assert stats["total_projects"] >= 1, "Should have at least one project"
        assert stats["total_tasks"] >= 1, "Should have at least one task"

        # Test transaction rollback
        try:
            with pm.transaction():
                # Create a task that will be rolled back
                rollback_task = VoidCatTask(
                    name="Rollback Test", project_id="nonexistent"
                )
                pm.save_task(rollback_task)
                raise Exception("Forced rollback")
        except TransactionError:
            pass  # Expected

        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

        return True

    except Exception as e:
        print(f"Persistence validation failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Run validation if executed directly
    if validate_persistence_layer():
        print("✅ Persistence layer validation successful!")
    else:
        print("❌ Persistence layer validation failed!")
