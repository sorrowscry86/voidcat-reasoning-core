"""
VoidCat Enhanced Memory Storage Engine
=====================================

Advanced persistent memory storage with TF-IDF indexing, semantic search,
intelligent archiving, and comprehensive backup management.

This enhanced version includes:
- MemoryIndex: Advanced indexing with TF-IDF and semantic search
- MemoryArchiver: Intelligent archiving system with lifecycle management
- MemoryBackupManager: Comprehensive backup and recovery system
- Enhanced MemoryStorageEngine: High-performance storage with all features

Author: Codey Jr. (Enhanced by the cosmic coding vibes)
License: MIT
Version: 2.0.0 - Enhanced Edition
"""

import gzip
import hashlib
import json
import math
import os
import pickle
import re
import shutil
import threading
import time
import uuid
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from voidcat_memory_models import ImportanceLevel, MemoryCategory

try:
    import fcntl  # Unix file locking
except ImportError:
    fcntl = None

try:
    import msvcrt  # Windows file locking
except ImportError:
    msvcrt = None

import platform

from voidcat_memory_models import (
    BaseMemory,
    ImportanceLevel,
    MemoryCategory,
    MemoryFactory,
    MemoryMetadata,
    MemoryQuery,
    MemoryStatus,
    validate_memory_schema,
)


@dataclass
class StorageConfig:
    """Configuration for memory storage engine."""

    base_dir: Path = field(default_factory=lambda: Path(".") / "memory_storage")
    backup_dir: Path = field(default_factory=lambda: Path(".") / "memory_backups")
    index_dir: Path = field(default_factory=lambda: Path(".") / "memory_indexes")

    # Performance settings
    cache_size: int = 1000  # Number of memories to cache in RAM
    cache_ttl: int = 300  # Cache TTL in seconds
    batch_size: int = 100  # Batch size for bulk operations

    # Backup settings
    backup_interval: int = 3600  # Backup interval in seconds
    max_backups: int = 10  # Maximum number of backups to keep
    compress_backups: bool = True

    # Archive settings
    archive_threshold: int = 10000  # Archive when memory count exceeds this
    archive_age_days: int = 90  # Archive memories older than this

    # Concurrency settings
    max_concurrent_ops: int = 10
    lock_timeout: int = 30

    def __post_init__(self):
        """Ensure directories exist."""
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.index_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class CacheEntry:
    """Cache entry for in-memory storage."""

    memory: BaseMemory
    timestamp: float = field(default_factory=time.time)
    access_count: int = 0
    dirty: bool = False  # Needs to be written to disk


class MemoryIndex:
    """
    Advanced memory indexing system with TF-IDF vectorization and semantic search.
    Provides fast content-based retrieval and similarity matching.
    """

    def __init__(self, index_dir: Path):
        self.index_dir = index_dir
        self.index_dir.mkdir(parents=True, exist_ok=True)

        # TF-IDF components
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95,
        )
        self.tfidf_matrix = None
        self.memory_ids = []

        # Index files
        self.tfidf_file = self.index_dir / "tfidf_index.pkl"
        self.vectorizer_file = self.index_dir / "vectorizer.pkl"
        self.memory_ids_file = self.index_dir / "memory_ids.json"

        # Content and metadata indexes
        self.content_index: Dict[str, str] = {}  # memory_id -> content
        self.metadata_index: Dict[str, Dict] = {}  # memory_id -> metadata
        self.category_index: Dict[str, Set[str]] = defaultdict(set)
        self.tag_index: Dict[str, Set[str]] = defaultdict(set)
        self.importance_index: Dict[int, Set[str]] = defaultdict(set)
        self.timestamp_index: Dict[str, float] = {}

        # Thread safety
        self._lock = threading.RLock()

        # Load existing indexes
        self._load_indexes()

    def _load_indexes(self):
        """Load existing indexes from disk."""
        try:
            # Load TF-IDF components
            if self.tfidf_file.exists():
                with open(self.tfidf_file, "rb") as f:
                    self.tfidf_matrix = pickle.load(f)

            if self.vectorizer_file.exists():
                with open(self.vectorizer_file, "rb") as f:
                    self.vectorizer = pickle.load(f)

            if self.memory_ids_file.exists():
                with open(self.memory_ids_file, "r") as f:
                    self.memory_ids = json.load(f)

            print(f"Loaded TF-IDF index with {len(self.memory_ids)} memories")

        except Exception as e:
            print(f"Warning: Failed to load TF-IDF indexes: {e}")
            self._initialize_empty_indexes()

    def _initialize_empty_indexes(self):
        """Initialize empty indexes."""
        self.tfidf_matrix = None
        self.memory_ids = []
        self.content_index = {}
        self.metadata_index = {}
        self.category_index = defaultdict(set)
        self.tag_index = defaultdict(set)
        self.importance_index = defaultdict(set)
        self.timestamp_index = {}

    def _save_indexes(self):
        """Save indexes to disk."""
        try:
            # Save TF-IDF components
            if self.tfidf_matrix is not None:
                with open(self.tfidf_file, "wb") as f:
                    pickle.dump(self.tfidf_matrix, f)

            with open(self.vectorizer_file, "wb") as f:
                pickle.dump(self.vectorizer, f)

            with open(self.memory_ids_file, "w") as f:
                json.dump(self.memory_ids, f)

        except Exception as e:
            print(f"Warning: Failed to save TF-IDF indexes: {e}")

    def add_memory(self, memory: BaseMemory):
        """Add memory to all indexes including TF-IDF."""
        with self._lock:
            memory_id = memory.id

            # Extract content for TF-IDF
            content = self._extract_searchable_content(memory)
            self.content_index[memory_id] = content

            # Store metadata
            self.metadata_index[memory_id] = memory.metadata or {}

            # Update category index
            category = (
                memory.category.value
                if hasattr(memory.category, "value")
                else str(memory.category)
            )
            self.category_index[category].add(memory_id)

            # Update tag index
            if memory.metadata:
                from voidcat_memory_models import MemoryMetadata

                metadata = MemoryMetadata.from_dict(memory.metadata)
                for tag in metadata.tags:
                    self.tag_index[tag].add(memory_id)

            # Update importance index
            importance = (
                memory.importance.value
                if hasattr(memory.importance, "value")
                else memory.importance
            )
            self.importance_index[importance].add(memory_id)

            # Update timestamp index
            if memory.metadata:
                from voidcat_memory_models import MemoryMetadata

                metadata = MemoryMetadata.from_dict(memory.metadata)
                self.timestamp_index[memory_id] = metadata.created_at.timestamp()

            # Rebuild TF-IDF if we have enough memories
            if len(self.content_index) % 100 == 0:  # Rebuild every 100 memories
                self._rebuild_tfidf_index()

    def remove_memory(self, memory: BaseMemory):
        """Remove memory from all indexes."""
        with self._lock:
            memory_id = memory.id

            # Remove from content index
            self.content_index.pop(memory_id, None)
            self.metadata_index.pop(memory_id, None)

            # Remove from category index
            category = (
                memory.category.value
                if hasattr(memory.category, "value")
                else str(memory.category)
            )
            self.category_index[category].discard(memory_id)

            # Remove from tag index
            if memory.metadata:
                from voidcat_memory_models import MemoryMetadata

                metadata = MemoryMetadata.from_dict(memory.metadata)
                for tag in metadata.tags:
                    self.tag_index[tag].discard(memory_id)

            # Remove from importance index
            importance = (
                memory.importance.value
                if hasattr(memory.importance, "value")
                else memory.importance
            )
            self.importance_index[importance].discard(memory_id)

            # Remove from timestamp index
            self.timestamp_index.pop(memory_id, None)

            # Mark for TF-IDF rebuild
            if memory_id in self.memory_ids:
                self.memory_ids.remove(memory_id)
                self._rebuild_tfidf_index()

    def _extract_searchable_content(self, memory: BaseMemory) -> str:
        """Extract searchable content from memory."""
        content_parts = []

        # Add main content
        if hasattr(memory, "content") and memory.content:
            content_parts.append(str(memory.content))

        # Add key-value pairs for preferences
        if hasattr(memory, "key") and memory.key:
            content_parts.append(str(memory.key))
        if hasattr(memory, "value") and memory.value:
            content_parts.append(str(memory.value))

        # Add context
        if hasattr(memory, "context") and memory.context:
            content_parts.append(str(memory.context))

        # Add tags from metadata
        if memory.metadata:
            from voidcat_memory_models import MemoryMetadata

            metadata = MemoryMetadata.from_dict(memory.metadata)
            content_parts.extend(metadata.tags)

        return " ".join(content_parts)

    def _rebuild_tfidf_index(self):
        """Rebuild TF-IDF index from current content."""
        try:
            if not self.content_index:
                return

            # Prepare documents
            self.memory_ids = list(self.content_index.keys())
            documents = [self.content_index[mid] for mid in self.memory_ids]

            # Fit TF-IDF vectorizer
            self.tfidf_matrix = self.vectorizer.fit_transform(documents)

            print(f"Rebuilt TF-IDF index with {len(self.memory_ids)} memories")

        except Exception as e:
            print(f"Error rebuilding TF-IDF index: {e}")

    def semantic_search(
        self, query: str, limit: int = 10, min_similarity: float = 0.1
    ) -> List[Tuple[str, float]]:
        """Perform semantic search using TF-IDF similarity."""
        if self.tfidf_matrix is None or not query.strip():
            return []

        try:
            # Transform query
            query_vector = self.vectorizer.transform([query])

            # Calculate similarities
            similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()

            # Get top results
            top_indices = np.argsort(similarities)[::-1]

            results = []
            for idx in top_indices:
                if len(results) >= limit:
                    break

                similarity = similarities[idx]
                if similarity >= min_similarity:
                    memory_id = self.memory_ids[idx]
                    results.append((memory_id, float(similarity)))

            return results

        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []

    def find_by_category(self, category: Union[str, MemoryCategory]) -> Set[str]:
        """Find memory IDs by category."""
        category_value = category.value if hasattr(category, "value") else str(category)
        return self.category_index.get(category_value, set()).copy()

    def find_by_tags(self, tags: List[str], match_all: bool = True) -> Set[str]:
        """Find memory IDs by tags."""
        if not tags:
            return set()

        if match_all:
            # Intersection of all tag sets
            result = self.tag_index.get(tags[0], set()).copy()
            for tag in tags[1:]:
                result &= self.tag_index.get(tag, set())
            return result
        else:
            # Union of all tag sets
            result = set()
            for tag in tags:
                result |= self.tag_index.get(tag, set())
            return result

    def find_by_importance_range(
        self, min_importance: Optional[int], max_importance: Optional[int]
    ) -> Set[str]:
        """Find memory IDs by importance range."""
        result = set()

        for importance, memory_ids in self.importance_index.items():
            if min_importance is not None and importance < min_importance:
                continue
            if max_importance is not None and importance > max_importance:
                continue
            result.update(memory_ids)

        return result

    def get_sorted_by_timestamp(self, reverse: bool = True) -> List[str]:
        """Get memory IDs sorted by timestamp."""
        sorted_items = sorted(
            self.timestamp_index.items(), key=lambda x: x[1], reverse=reverse
        )
        return [memory_id for memory_id, _ in sorted_items]

    def get_statistics(self) -> Dict[str, Any]:
        """Get index statistics."""
        return {
            "total_memories": len(self.content_index),
            "tfidf_features": (
                self.tfidf_matrix.shape[1] if self.tfidf_matrix is not None else 0
            ),
            "categories": len(self.category_index),
            "unique_tags": len(self.tag_index),
            "importance_levels": len(self.importance_index),
        }

    def save_all_indexes(self):
        """Save all indexes to disk."""
        with self._lock:
            self._save_indexes()


class MemoryArchiver:
    """
    Intelligent memory archiving system with lifecycle management.
    Handles automatic archiving based on age, access patterns, and importance.
    """

    def __init__(self, config: "StorageConfig", storage_engine: "MemoryStorageEngine"):
        self.config = config
        self.storage_engine = storage_engine
        self.archive_dir = config.base_dir.parent / "memory_archives"
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        # Archive statistics
        self.stats = {
            "archived_count": 0,
            "restored_count": 0,
            "last_archive_run": 0,
            "archive_size_bytes": 0,
        }

        # Load existing stats
        self._load_stats()

    def _load_stats(self):
        """Load archiver statistics."""
        stats_file = self.archive_dir / "archive_stats.json"
        try:
            if stats_file.exists():
                with open(stats_file, "r") as f:
                    self.stats.update(json.load(f))
        except Exception as e:
            print(f"Warning: Failed to load archive stats: {e}")

    def _save_stats(self):
        """Save archiver statistics."""
        stats_file = self.archive_dir / "archive_stats.json"
        try:
            with open(stats_file, "w") as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save archive stats: {e}")

    def should_archive_memory(self, memory: "BaseMemory") -> bool:
        """Determine if a memory should be archived based on various criteria."""
        if not memory.metadata:
            return False

        from voidcat_memory_models import MemoryMetadata, MemoryStatus

        metadata = MemoryMetadata.from_dict(memory.metadata)

        # Don't archive if already archived or deleted
        if memory.status in [MemoryStatus.ARCHIVED, MemoryStatus.DELETED]:
            return False

        # Check age threshold
        age_days = (datetime.now(timezone.utc) - metadata.created_at).days
        if age_days < self.config.archive_age_days:
            return False

        # Check access patterns
        last_access_days = (datetime.now(timezone.utc) - metadata.last_accessed).days

        # Archive criteria based on importance and access patterns
        importance_value = (
            memory.importance.value
            if hasattr(memory.importance, "value")
            else memory.importance
        )

        # High importance memories need longer inactivity
        if importance_value >= 8:  # High importance
            return last_access_days > 180  # 6 months
        elif importance_value >= 5:  # Medium importance
            return last_access_days > 90  # 3 months
        else:  # Low importance
            return last_access_days > 30  # 1 month

    def archive_memory(self, memory: "BaseMemory") -> bool:
        """Archive a single memory."""
        try:
            # Create archive entry
            archive_entry = {
                "memory_data": memory.to_dict(),
                "archived_at": datetime.now(timezone.utc).isoformat(),
                "original_file_path": str(
                    self.storage_engine._get_memory_file_path(memory.id)
                ),
                "archive_reason": "automatic_lifecycle",
            }

            # Save to archive
            archive_file = self.archive_dir / f"{memory.id}.json"
            with open(archive_file, "w", encoding="utf-8") as f:
                json.dump(archive_entry, f, indent=2, ensure_ascii=False, default=str)

            # Update memory status
            from voidcat_memory_models import MemoryStatus

            memory.status = MemoryStatus.ARCHIVED

            # Update in storage
            self.storage_engine.update_memory(memory)

            # Update stats
            self.stats["archived_count"] += 1
            self.stats["archive_size_bytes"] += archive_file.stat().st_size

            print(f"Archived memory {memory.id}")
            return True

        except Exception as e:
            print(f"Error archiving memory {memory.id}: {e}")
            return False

    def restore_memory(self, memory_id: str) -> bool:
        """Restore a memory from archive."""
        try:
            archive_file = self.archive_dir / f"{memory_id}.json"
            if not archive_file.exists():
                print(f"Archive file not found for memory {memory_id}")
                return False

            # Load archive entry
            with open(archive_file, "r", encoding="utf-8") as f:
                archive_entry = json.load(f)

            # Recreate memory
            from voidcat_memory_models import MemoryFactory, MemoryStatus

            memory_data = archive_entry["memory_data"]
            memory = MemoryFactory.from_dict(memory_data)

            # Update status to active
            memory.status = MemoryStatus.ACTIVE

            # Restore to storage
            success = self.storage_engine.store_memory(memory)
            if success:
                # Remove from archive
                archive_file.unlink()

                # Update stats
                self.stats["restored_count"] += 1
                self.stats["archive_size_bytes"] -= archive_file.stat().st_size

                print(f"Restored memory {memory_id} from archive")
                return True

            return False

        except Exception as e:
            print(f"Error restoring memory {memory_id}: {e}")
            return False

    def run_archive_cycle(self) -> Dict[str, int]:
        """Run a complete archive cycle."""
        print("Starting memory archive cycle...")

        archived_count = 0
        skipped_count = 0
        error_count = 0

        try:
            # Get all active memories
            from voidcat_memory_models import MemoryQuery, MemoryStatus

            query = MemoryQuery(status=MemoryStatus.ACTIVE, limit=10000)
            memories = self.storage_engine.search_memories(query)

            for memory in memories:
                try:
                    if self.should_archive_memory(memory):
                        if self.archive_memory(memory):
                            archived_count += 1
                        else:
                            error_count += 1
                    else:
                        skipped_count += 1

                except Exception as e:
                    print(f"Error processing memory {memory.id}: {e}")
                    error_count += 1

            # Update stats
            self.stats["last_archive_run"] = time.time()
            self._save_stats()

            result = {
                "archived": archived_count,
                "skipped": skipped_count,
                "errors": error_count,
            }

            print(f"Archive cycle completed: {result}")
            return result

        except Exception as e:
            print(f"Error in archive cycle: {e}")
            return {"archived": 0, "skipped": 0, "errors": 1}

    def get_archive_statistics(self) -> Dict[str, Any]:
        """Get archive statistics."""
        # Count archived files
        archived_files = list(self.archive_dir.glob("*.json"))
        archived_files = [f for f in archived_files if f.name != "archive_stats.json"]

        return {
            **self.stats,
            "archived_files_count": len(archived_files),
            "archive_directory_size": sum(f.stat().st_size for f in archived_files),
        }

    def cleanup_old_archives(self, max_age_days: int = 365) -> int:
        """Clean up very old archive files."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=max_age_days)
        cleaned_count = 0

        try:
            for archive_file in self.archive_dir.glob("*.json"):
                if archive_file.name == "archive_stats.json":
                    continue

                # Check file modification time
                file_time = datetime.fromtimestamp(
                    archive_file.stat().st_mtime, tz=timezone.utc
                )
                if file_time < cutoff_time:
                    archive_file.unlink()
                    cleaned_count += 1

            print(f"Cleaned up {cleaned_count} old archive files")
            return cleaned_count

        except Exception as e:
            print(f"Error cleaning up archives: {e}")
            return 0


class MemoryBackupManager:
    """
    Comprehensive backup and recovery system with incremental backups,
    compression, encryption, and automated scheduling.
    """

    def __init__(self, config: "StorageConfig"):
        self.config = config
        self.backup_dir = config.backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Backup metadata
        self.metadata_file = self.backup_dir / "backup_metadata.json"
        self.metadata = self._load_metadata()

        # Backup statistics
        self.stats = {
            "total_backups": 0,
            "successful_backups": 0,
            "failed_backups": 0,
            "last_backup_time": 0,
            "last_backup_size": 0,
            "total_backup_size": 0,
        }

        # Load existing stats
        self._load_stats()

    def _load_metadata(self) -> Dict[str, Any]:
        """Load backup metadata."""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load backup metadata: {e}")

        return {
            "backups": [],
            "last_full_backup": None,
            "backup_schedule": {
                "full_backup_interval": 86400 * 7,  # Weekly full backups
                "incremental_interval": 3600,  # Hourly incrementals
            },
        }

    def _save_metadata(self):
        """Save backup metadata."""
        try:
            with open(self.metadata_file, "w") as f:
                json.dump(self.metadata, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Failed to save backup metadata: {e}")

    def _load_stats(self):
        """Load backup statistics."""
        stats_file = self.backup_dir / "backup_stats.json"
        try:
            if stats_file.exists():
                with open(stats_file, "r") as f:
                    self.stats.update(json.load(f))
        except Exception as e:
            print(f"Warning: Failed to load backup stats: {e}")

    def _save_stats(self):
        """Save backup statistics."""
        stats_file = self.backup_dir / "backup_stats.json"
        try:
            with open(stats_file, "w") as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save backup stats: {e}")

    def create_full_backup(
        self, description: str = "Scheduled full backup"
    ) -> Optional[str]:
        """Create a complete backup of all memory data."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_id = f"full_{timestamp}"
        backup_path = self.backup_dir / backup_id

        try:
            print(f"Creating full backup: {backup_id}")

            # Create backup directory
            backup_path.mkdir(exist_ok=True)

            # Copy memory storage
            if self.config.base_dir.exists():
                shutil.copytree(
                    self.config.base_dir,
                    backup_path / "memory_storage",
                    dirs_exist_ok=True,
                )

            # Copy indexes
            if self.config.index_dir.exists():
                shutil.copytree(
                    self.config.index_dir,
                    backup_path / "memory_indexes",
                    dirs_exist_ok=True,
                )

            # Create backup manifest
            manifest = {
                "backup_id": backup_id,
                "backup_type": "full",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "description": description,
                "files_included": self._get_file_manifest(backup_path),
                "checksum": self._calculate_backup_checksum(backup_path),
            }

            with open(backup_path / "manifest.json", "w") as f:
                json.dump(manifest, f, indent=2, default=str)

            # Compress if enabled
            if self.config.compress_backups:
                compressed_path = self._compress_backup(backup_path)
                if compressed_path:
                    shutil.rmtree(backup_path)
                    backup_path = compressed_path

            # Update metadata
            backup_info = {
                "backup_id": backup_id,
                "backup_type": "full",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "path": str(backup_path),
                "size_bytes": self._get_backup_size(backup_path),
                "description": description,
            }

            self.metadata["backups"].append(backup_info)
            self.metadata["last_full_backup"] = backup_info
            self._save_metadata()

            # Update stats
            self.stats["total_backups"] += 1
            self.stats["successful_backups"] += 1
            self.stats["last_backup_time"] = time.time()
            self.stats["last_backup_size"] = backup_info["size_bytes"]
            self.stats["total_backup_size"] += backup_info["size_bytes"]
            self._save_stats()

            # Cleanup old backups
            self._cleanup_old_backups()

            print(f"Full backup completed: {backup_id}")
            return backup_id

        except Exception as e:
            print(f"Error creating full backup: {e}")
            self.stats["failed_backups"] += 1
            self._save_stats()
            return None

    def create_incremental_backup(
        self, description: str = "Incremental backup"
    ) -> Optional[str]:
        """Create an incremental backup of changed files."""
        if not self.metadata["last_full_backup"]:
            print("No full backup found, creating full backup instead")
            return self.create_full_backup("Initial full backup")

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_id = f"incr_{timestamp}"
        backup_path = self.backup_dir / backup_id

        try:
            print(f"Creating incremental backup: {backup_id}")

            # Get last backup time
            last_backup_time = datetime.fromisoformat(
                self.metadata["last_full_backup"]["created_at"].replace("Z", "+00:00")
            )

            # Find changed files
            changed_files = self._find_changed_files(last_backup_time)

            if not changed_files:
                print("No changes detected, skipping incremental backup")
                return None

            # Create backup directory
            backup_path.mkdir(exist_ok=True)

            # Copy changed files
            for file_path in changed_files:
                relative_path = file_path.relative_to(self.config.base_dir.parent)
                dest_path = backup_path / relative_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, dest_path)

            # Create backup manifest
            manifest = {
                "backup_id": backup_id,
                "backup_type": "incremental",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "description": description,
                "base_backup": self.metadata["last_full_backup"]["backup_id"],
                "changed_files": [str(f) for f in changed_files],
                "checksum": self._calculate_backup_checksum(backup_path),
            }

            with open(backup_path / "manifest.json", "w") as f:
                json.dump(manifest, f, indent=2, default=str)

            # Compress if enabled
            if self.config.compress_backups:
                compressed_path = self._compress_backup(backup_path)
                if compressed_path:
                    shutil.rmtree(backup_path)
                    backup_path = compressed_path

            # Update metadata
            backup_info = {
                "backup_id": backup_id,
                "backup_type": "incremental",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "path": str(backup_path),
                "size_bytes": self._get_backup_size(backup_path),
                "description": description,
                "base_backup": self.metadata["last_full_backup"]["backup_id"],
            }

            self.metadata["backups"].append(backup_info)
            self._save_metadata()

            # Update stats
            self.stats["total_backups"] += 1
            self.stats["successful_backups"] += 1
            self.stats["last_backup_time"] = time.time()
            self.stats["last_backup_size"] = backup_info["size_bytes"]
            self.stats["total_backup_size"] += backup_info["size_bytes"]
            self._save_stats()

            print(f"Incremental backup completed: {backup_id}")
            return backup_id

        except Exception as e:
            print(f"Error creating incremental backup: {e}")
            self.stats["failed_backups"] += 1
            self._save_stats()
            return None

    def _find_changed_files(self, since_time: datetime) -> List[Path]:
        """Find files changed since the given time."""
        changed_files = []

        # Check memory storage directory
        if self.config.base_dir.exists():
            for file_path in self.config.base_dir.rglob("*.json"):
                file_time = datetime.fromtimestamp(
                    file_path.stat().st_mtime, tz=timezone.utc
                )
                if file_time > since_time:
                    changed_files.append(file_path)

        # Check index directory
        if self.config.index_dir.exists():
            for file_path in self.config.index_dir.rglob("*"):
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(
                        file_path.stat().st_mtime, tz=timezone.utc
                    )
                    if file_time > since_time:
                        changed_files.append(file_path)

        return changed_files

    def _compress_backup(self, backup_path: Path) -> Optional[Path]:
        """Compress backup directory."""
        try:
            compressed_path = backup_path.with_suffix(".tar.gz")
            shutil.make_archive(str(backup_path), "gztar", str(backup_path))

            # Move to correct location
            archive_path = Path(f"{backup_path}.tar.gz")
            if archive_path.exists():
                archive_path.rename(compressed_path)
                return compressed_path

        except Exception as e:
            print(f"Error compressing backup: {e}")

        return None

    def _get_backup_size(self, backup_path: Path) -> int:
        """Get total size of backup."""
        if backup_path.is_file():
            return backup_path.stat().st_size

        total_size = 0
        for file_path in backup_path.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size

        return total_size

    def _get_file_manifest(self, backup_path: Path) -> List[Dict[str, Any]]:
        """Get manifest of files in backup."""
        manifest = []

        for file_path in backup_path.rglob("*"):
            if file_path.is_file() and file_path.name != "manifest.json":
                relative_path = file_path.relative_to(backup_path)
                manifest.append(
                    {
                        "path": str(relative_path),
                        "size": file_path.stat().st_size,
                        "modified": datetime.fromtimestamp(
                            file_path.stat().st_mtime
                        ).isoformat(),
                    }
                )

        return manifest

    def _calculate_backup_checksum(self, backup_path: Path) -> str:
        """Calculate checksum for backup integrity."""
        hasher = hashlib.sha256()

        for file_path in sorted(backup_path.rglob("*")):
            if file_path.is_file() and file_path.name != "manifest.json":
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hasher.update(chunk)

        return hasher.hexdigest()

    def restore_from_backup(self, backup_id: str) -> bool:
        """Restore from a specific backup."""
        try:
            # Find backup info
            backup_info = None
            for backup in self.metadata["backups"]:
                if backup["backup_id"] == backup_id:
                    backup_info = backup
                    break

            if not backup_info:
                print(f"Backup {backup_id} not found")
                return False

            backup_path = Path(backup_info["path"])
            if not backup_path.exists():
                print(f"Backup file not found: {backup_path}")
                return False

            print(f"Restoring from backup: {backup_id}")

            # Extract if compressed
            if backup_path.suffix == ".gz":
                extract_path = backup_path.parent / f"temp_extract_{backup_id}"
                shutil.unpack_archive(str(backup_path), str(extract_path))
                backup_path = extract_path

            # Clear current data
            if self.config.base_dir.exists():
                shutil.rmtree(self.config.base_dir)
            if self.config.index_dir.exists():
                shutil.rmtree(self.config.index_dir)

            # Restore data
            if (backup_path / "memory_storage").exists():
                shutil.copytree(backup_path / "memory_storage", self.config.base_dir)
            if (backup_path / "memory_indexes").exists():
                shutil.copytree(backup_path / "memory_indexes", self.config.index_dir)

            # Clean up temporary extraction
            if backup_path.name.startswith("temp_extract_"):
                shutil.rmtree(backup_path)

            print(f"Restore completed successfully from backup: {backup_id}")
            return True

        except Exception as e:
            print(f"Error restoring from backup {backup_id}: {e}")
            return False

    def _cleanup_old_backups(self):
        """Clean up old backup files based on retention policy."""
        try:
            # Sort backups by creation time
            backups = sorted(
                self.metadata["backups"], key=lambda x: x["created_at"], reverse=True
            )

            # Keep only the configured number of backups
            backups_to_remove = backups[self.config.max_backups :]

            for backup_info in backups_to_remove:
                backup_path = Path(backup_info["path"])
                if backup_path.exists():
                    if backup_path.is_dir():
                        shutil.rmtree(backup_path)
                    else:
                        backup_path.unlink()

                    print(f"Removed old backup: {backup_info['backup_id']}")

                # Remove from metadata
                self.metadata["backups"].remove(backup_info)

            self._save_metadata()

        except Exception as e:
            print(f"Error cleaning up old backups: {e}")

    def get_backup_statistics(self) -> Dict[str, Any]:
        """Get backup statistics and status."""
        return {
            **self.stats,
            "backup_count": len(self.metadata["backups"]),
            "last_full_backup": self.metadata["last_full_backup"],
            "backup_directory_size": sum(
                self._get_backup_size(Path(backup["path"]))
                for backup in self.metadata["backups"]
                if Path(backup["path"]).exists()
            ),
        }

    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups."""
        return self.metadata["backups"].copy()

    def verify_backup_integrity(self, backup_id: str) -> bool:
        """Verify backup integrity using checksums."""
        try:
            # Find backup info
            backup_info = None
            for backup in self.metadata["backups"]:
                if backup["backup_id"] == backup_id:
                    backup_info = backup
                    break

            if not backup_info:
                return False

            backup_path = Path(backup_info["path"])
            if not backup_path.exists():
                return False

            # Load manifest
            manifest_path = backup_path / "manifest.json"
            if backup_path.suffix == ".gz":
                # For compressed backups, we'd need to extract temporarily
                # For now, just check if file exists and is readable
                return backup_path.is_file()

            if not manifest_path.exists():
                return False

            with open(manifest_path, "r") as f:
                manifest = json.load(f)

            # Verify checksum
            current_checksum = self._calculate_backup_checksum(backup_path)
            return current_checksum == manifest.get("checksum", "")

        except Exception as e:
            print(f"Error verifying backup {backup_id}: {e}")
            return False


class StorageIndex:
    """Index for fast memory retrieval."""

    def __init__(self, index_dir: Path):
        self.index_dir = index_dir
        self.index_dir.mkdir(parents=True, exist_ok=True)

        # Index files
        self.category_index_file = self.index_dir / "category_index.json"
        self.tag_index_file = self.index_dir / "tag_index.json"
        self.importance_index_file = self.index_dir / "importance_index.json"
        self.timestamp_index_file = self.index_dir / "timestamp_index.json"
        self.content_hash_index_file = self.index_dir / "content_hash_index.json"

        # Load existing indexes
        self.category_index: Dict[str, Set[str]] = self._load_index(
            self.category_index_file
        )
        self.tag_index: Dict[str, Set[str]] = self._load_index(self.tag_index_file)
        self.importance_index: Dict[str, Set[str]] = self._load_index(
            self.importance_index_file
        )
        self.timestamp_index: Dict[str, float] = self._load_index(
            self.timestamp_index_file
        )
        self.content_hash_index: Dict[str, str] = self._load_index(
            self.content_hash_index_file
        )

        # Locks for thread safety
        self._lock = threading.RLock()

    def _load_index(self, file_path: Path) -> Dict:
        """Load index from file."""
        try:
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Convert sets back from lists for category and tag indexes
                    if file_path.name in [
                        "category_index.json",
                        "tag_index.json",
                        "importance_index.json",
                    ]:
                        return {k: set(v) for k, v in data.items()}
                    return data
        except Exception as e:
            print(f"Warning: Failed to load index {file_path}: {e}")
        return {}

    def _save_index(self, index: Dict, file_path: Path):
        """Save index to file."""
        try:
            # Convert sets to lists for JSON serialization
            if isinstance(list(index.values())[0] if index else None, set):
                serializable_index = {k: list(v) for k, v in index.items()}
            else:
                serializable_index = index

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(serializable_index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Failed to save index {file_path}: {e}")

    def add_memory(self, memory: BaseMemory):
        """Add memory to all relevant indexes."""
        with self._lock:
            memory_id = memory.id

            # Category index
            category = (
                memory.category.value
                if hasattr(memory.category, "value")
                else memory.category
            )
            if category not in self.category_index:
                self.category_index[category] = set()
            self.category_index[category].add(memory_id)

            # Tag index
            if memory.metadata:
                metadata = MemoryMetadata.from_dict(memory.metadata)
                for tag in metadata.tags:
                    if tag not in self.tag_index:
                        self.tag_index[tag] = set()
                    self.tag_index[tag].add(memory_id)

            # Importance index
            importance = (
                memory.importance.value
                if hasattr(memory.importance, "value")
                else memory.importance
            )
            importance_str = str(importance)
            if importance_str not in self.importance_index:
                self.importance_index[importance_str] = set()
            self.importance_index[importance_str].add(memory_id)

            # Timestamp index
            if memory.metadata:
                metadata = MemoryMetadata.from_dict(memory.metadata)
                self.timestamp_index[memory_id] = metadata.created_at.timestamp()

            # Content hash index (for deduplication)
            content_hash = memory.get_content_hash()
            self.content_hash_index[content_hash] = memory_id

    def remove_memory(self, memory: BaseMemory):
        """Remove memory from all indexes."""
        with self._lock:
            memory_id = memory.id

            # Category index
            category = (
                memory.category.value
                if hasattr(memory.category, "value")
                else memory.category
            )
            if category in self.category_index:
                self.category_index[category].discard(memory_id)
                if not self.category_index[category]:
                    del self.category_index[category]

            # Tag index
            if memory.metadata:
                metadata = MemoryMetadata.from_dict(memory.metadata)
                for tag in metadata.tags:
                    if tag in self.tag_index:
                        self.tag_index[tag].discard(memory_id)
                        if not self.tag_index[tag]:
                            del self.tag_index[tag]

            # Importance index
            importance = (
                memory.importance.value
                if hasattr(memory.importance, "value")
                else memory.importance
            )
            importance_str = str(importance)
            if importance_str in self.importance_index:
                self.importance_index[importance_str].discard(memory_id)
                if not self.importance_index[importance_str]:
                    del self.importance_index[importance_str]

            # Timestamp index
            self.timestamp_index.pop(memory_id, None)

            # Content hash index
            content_hash = memory.get_content_hash()
            if (
                content_hash in self.content_hash_index
                and self.content_hash_index[content_hash] == memory_id
            ):
                del self.content_hash_index[content_hash]

    def find_by_category(self, category: MemoryCategory) -> Set[str]:
        """Find memory IDs by category."""
        category_value = category.value if hasattr(category, "value") else category
        return self.category_index.get(category_value, set()).copy()

    def find_by_tags(self, tags: List[str]) -> Set[str]:
        """Find memory IDs by tags (intersection)."""
        if not tags:
            return set()

        result_sets = []
        for tag in tags:
            if tag in self.tag_index:
                result_sets.append(self.tag_index[tag])

        if not result_sets:
            return set()

        # Find intersection of all tag sets
        result = result_sets[0].copy()
        for tag_set in result_sets[1:]:
            result &= tag_set

        return result

    def find_by_importance_range(
        self, min_importance: Optional[int], max_importance: Optional[int]
    ) -> Set[str]:
        """Find memory IDs by importance range."""
        result = set()

        for importance_str, memory_ids in self.importance_index.items():
            importance = int(importance_str)
            if min_importance is not None and importance < min_importance:
                continue
            if max_importance is not None and importance > max_importance:
                continue
            result.update(memory_ids)

        return result

    def find_duplicate(self, content_hash: str) -> Optional[str]:
        """Find existing memory with same content hash."""
        return self.content_hash_index.get(content_hash)

    def get_sorted_by_timestamp(self, reverse: bool = True) -> List[str]:
        """Get memory IDs sorted by timestamp."""
        sorted_items = sorted(
            self.timestamp_index.items(), key=lambda x: x[1], reverse=reverse
        )
        return [memory_id for memory_id, _ in sorted_items]

    def save_all_indexes(self):
        """Save all indexes to disk."""
        with self._lock:
            self._save_index(self.category_index, self.category_index_file)
            self._save_index(self.tag_index, self.tag_index_file)
            self._save_index(self.importance_index, self.importance_index_file)
            self._save_index(self.timestamp_index, self.timestamp_index_file)
            self._save_index(self.content_hash_index, self.content_hash_index_file)


class FileLock:
    """Cross-platform file locking."""

    def __init__(self, file_path: Path, timeout: int = 30):
        self.file_path = file_path
        self.timeout = timeout
        self.lock_file = None
        self.is_windows = platform.system() == "Windows"

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def acquire(self):
        """Acquire file lock."""
        lock_file_path = self.file_path.with_suffix(self.file_path.suffix + ".lock")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                self.lock_file = open(lock_file_path, "w")

                if self.is_windows and msvcrt:
                    msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_NBLCK, 1)
                elif fcntl:
                    fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

                return
            except (IOError, OSError):
                if self.lock_file:
                    self.lock_file.close()
                    self.lock_file = None
                time.sleep(0.1)

        raise TimeoutError(
            f"Failed to acquire lock for {self.file_path} within {self.timeout} seconds"
        )

    def release(self):
        """Release file lock."""
        if self.lock_file:
            try:
                if self.is_windows and msvcrt:
                    msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_UNLCK, 1)
                elif fcntl:
                    fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
            except:
                pass
            finally:
                self.lock_file.close()
                self.lock_file = None

                # Clean up lock file
                lock_file_path = self.file_path.with_suffix(
                    self.file_path.suffix + ".lock"
                )
                try:
                    lock_file_path.unlink(missing_ok=True)
                except:
                    pass


class MemoryStorageEngine:
    """
    Enhanced high-performance persistent memory storage engine with:
    - Advanced TF-IDF indexing and semantic search
    - Intelligent memory archiving with lifecycle management
    - Comprehensive backup system with incremental backups
    - Atomic operations, caching, and concurrent access support
    """

    def __init__(self, config: Optional[StorageConfig] = None):
        self.config = config or StorageConfig()

        # Initialize enhanced components
        self.memory_index = MemoryIndex(self.config.index_dir)  # Enhanced indexing
        self.storage_index = StorageIndex(self.config.index_dir)  # Legacy compatibility
        self.archiver = MemoryArchiver(self.config, self)  # Intelligent archiving
        self.backup_manager = MemoryBackupManager(self.config)  # Advanced backups

        # Cache and concurrency
        self.cache: Dict[str, CacheEntry] = {}
        self.cache_lock = threading.RLock()

        # Thread pool for concurrent operations
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_concurrent_ops)

        # Backup management
        self.last_backup = 0
        self.backup_lock = threading.Lock()

        # Performance tracking
        self.stats = {
            "reads": 0,
            "writes": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "index_queries": 0,
        }

        print(f"MemoryStorageEngine initialized with base dir: {self.config.base_dir}")

    def _get_memory_file_path(self, memory_id: str) -> Path:
        """Get file path for memory based on ID."""
        # Use first 2 chars of ID for directory structure to avoid too many files in one dir
        subdir = memory_id[:2]
        dir_path = self.config.base_dir / subdir
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path / f"{memory_id}.json"

    def _cache_get(self, memory_id: str) -> Optional[BaseMemory]:
        """Get memory from cache."""
        with self.cache_lock:
            if memory_id in self.cache:
                entry = self.cache[memory_id]

                # Check TTL
                if time.time() - entry.timestamp < self.config.cache_ttl:
                    entry.access_count += 1
                    self.stats["cache_hits"] += 1
                    return entry.memory
                else:
                    del self.cache[memory_id]

            self.stats["cache_misses"] += 1
            return None

    def _cache_put(self, memory: BaseMemory, dirty: bool = False):
        """Put memory in cache."""
        with self.cache_lock:
            # Evict old entries if cache is full
            if len(self.cache) >= self.config.cache_size:
                self._evict_cache_entries()

            self.cache[memory.id] = CacheEntry(
                memory=memory, timestamp=time.time(), dirty=dirty
            )

    def _evict_cache_entries(self, count: Optional[int] = None):
        """Evict old cache entries (LRU)."""
        if count is None:
            count = max(1, len(self.cache) // 10)  # Evict 10% of cache
        # Sort by timestamp and access count
        sorted_entries = sorted(
            self.cache.items(), key=lambda x: (x[1].timestamp, x[1].access_count)
        )
        for i in range(min(count, len(sorted_entries))):
            memory_id, entry = sorted_entries[i]
            # Write dirty entries to disk before evicting
            if entry.dirty:
                try:
                    self._write_memory_to_disk(entry.memory)
                except Exception as e:
                    print(
                        f"Warning: Failed to write dirty cache entry {memory_id}: {e}"
                    )
            del self.cache[memory_id]

    def _write_memory_to_disk(self, memory: BaseMemory):
        """Write memory to disk with atomic operation."""
        file_path = self._get_memory_file_path(memory.id)
        temp_file_path = file_path.with_suffix(".tmp")

        try:
            with FileLock(file_path, self.config.lock_timeout):
                # Write to temporary file first
                with open(temp_file_path, "w", encoding="utf-8") as f:
                    json.dump(
                        memory.to_dict(), f, indent=2, ensure_ascii=False, default=str
                    )

                # Atomic rename
                if file_path.exists():
                    backup_path = file_path.with_suffix(".bak")
                    shutil.move(str(file_path), str(backup_path))

                shutil.move(str(temp_file_path), str(file_path))

                # Clean up backup
                backup_path = file_path.with_suffix(".bak")
                if backup_path.exists():
                    backup_path.unlink()

        except Exception as e:
            # Clean up temp file on error
            if temp_file_path.exists():
                temp_file_path.unlink()
            raise e

    def _read_memory_from_disk(self, memory_id: str) -> Optional[BaseMemory]:
        """Read memory from disk."""
        file_path = self._get_memory_file_path(memory_id)

        if not file_path.exists():
            return None

        try:
            with FileLock(file_path, self.config.lock_timeout):
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Validate schema
                if not validate_memory_schema(data):
                    print(f"Warning: Invalid memory schema for {memory_id}")
                    return None

                return MemoryFactory.from_dict(data)

        except Exception as e:
            print(f"Error reading memory {memory_id}: {e}")
            return None

    def store_memory(self, memory: BaseMemory) -> bool:
        """Store memory with atomic operation."""
        try:
            # Check for duplicates
            content_hash = memory.get_content_hash()
            existing_id = self.storage_index.find_duplicate(content_hash)
            if existing_id and existing_id != memory.id:
                print(
                    f"Warning: Duplicate content detected. Existing ID: {existing_id}"
                )
                return False

            # Update access metadata
            memory.update_access()

            # Write to disk
            self._write_memory_to_disk(memory)

            # Update cache
            self._cache_put(memory, dirty=False)

            # Update both indexes
            self.storage_index.add_memory(memory)  # Legacy compatibility
            self.memory_index.add_memory(memory)  # Enhanced indexing

            self.stats["writes"] += 1

            # Trigger backup if needed
            self._maybe_trigger_backup()

            return True

        except Exception as e:
            print(f"Error storing memory {memory.id}: {e}")
            return False

    def retrieve_memory(self, memory_id: str) -> Optional[BaseMemory]:
        """Retrieve memory by ID."""
        try:
            # Check cache first
            memory = self._cache_get(memory_id)
            if memory:
                memory.update_access()
                return memory

            # Read from disk
            memory = self._read_memory_from_disk(memory_id)
            if memory:
                memory.update_access()
                self._cache_put(memory)
                self.stats["reads"] += 1
                return memory

            return None

        except Exception as e:
            print(f"Error retrieving memory {memory_id}: {e}")
            return None

    def update_memory(self, memory: BaseMemory) -> bool:
        """Update existing memory."""
        try:
            # Check if memory exists
            existing = self.retrieve_memory(memory.id)
            if not existing:
                print(f"Memory {memory.id} not found for update")
                return False

            # Remove from indexes (will be re-added with new data)
            self.storage_index.remove_memory(existing)
            self.memory_index.remove_memory(existing)

            # Update memory
            memory.update_access()

            # Store updated memory
            return self.store_memory(memory)

        except Exception as e:
            print(f"Error updating memory {memory.id}: {e}")
            return False

    def delete_memory(self, memory_id: str) -> bool:
        """Delete memory with atomic operation."""
        try:
            # Get memory for index removal
            memory = self.retrieve_memory(memory_id)
            if not memory:
                return False

            file_path = self._get_memory_file_path(memory_id)

            # Remove from cache
            with self.cache_lock:
                self.cache.pop(memory_id, None)

            # Remove from indexes
            self.storage_index.remove_memory(memory)
            self.memory_index.remove_memory(memory)

            # Delete file
            if file_path.exists():
                with FileLock(file_path, self.config.lock_timeout):
                    file_path.unlink()

            return True

        except Exception as e:
            print(f"Error deleting memory {memory_id}: {e}")
            return False

    def search_memories(self, query: MemoryQuery) -> List[BaseMemory]:
        """Search memories using query with optimized indexing."""
        try:
            self.stats["index_queries"] += 1

            # Start with all memory IDs if no filters
            candidate_ids = None

            # Apply category filter
            if query.categories:
                category_ids = set()
                for category in query.categories:
                    category_ids.update(self.storage_index.find_by_category(category))
                candidate_ids = (
                    category_ids
                    if candidate_ids is None
                    else candidate_ids & category_ids
                )

            # Apply tag filter
            if query.tags:
                tag_ids = self.storage_index.find_by_tags(query.tags)
                candidate_ids = (
                    tag_ids if candidate_ids is None else candidate_ids & tag_ids
                )

            # Apply importance filter
            if query.importance_min is not None or query.importance_max is not None:
                min_imp = query.importance_min.value if query.importance_min else None
                max_imp = query.importance_max.value if query.importance_max else None
                importance_ids = self.storage_index.find_by_importance_range(
                    min_imp, max_imp
                )
                candidate_ids = (
                    importance_ids
                    if candidate_ids is None
                    else candidate_ids & importance_ids
                )

            # If no candidates found, return empty list
            if candidate_ids is not None and not candidate_ids:
                return []

            # If no filters applied, get all memories (or use timestamp sorting)
            if candidate_ids is None:
                candidate_ids = set(self.storage_index.get_sorted_by_timestamp())

            # Load memories and apply text search
            memories = []
            query_terms = query.get_query_terms()

            # Use thread pool for parallel loading
            with ThreadPoolExecutor(
                max_workers=max(1, min(10, len(candidate_ids)))
            ) as executor:
                future_to_id = {
                    executor.submit(self.retrieve_memory, memory_id): memory_id
                    for memory_id in candidate_ids
                }

                for future in as_completed(future_to_id):
                    memory = future.result()
                    if memory:
                        # Apply status filter
                        if query.status and memory.status != query.status:
                            continue

                        # Apply text search
                        if query.text:
                            relevance = memory.calculate_relevance(query_terms)
                            if relevance > 0:
                                memories.append((memory, relevance))
                        else:
                            memories.append((memory, 1.0))

            # Sort results
            if query.sort_by == "relevance" and query.text:
                memories.sort(key=lambda x: x[1], reverse=(query.sort_order == "desc"))
            elif query.sort_by == "importance":

                def importance_sort_key(x):
                    imp = x[0].importance
                    if isinstance(imp, str):
                        try:
                            imp = ImportanceLevel(imp)
                        except Exception:
                            pass
                    if isinstance(imp, ImportanceLevel):
                        return imp.value
                    return imp

                memories.sort(
                    key=importance_sort_key, reverse=(query.sort_order == "desc")
                )
            elif query.sort_by == "recency":
                memories.sort(
                    key=lambda x: MemoryMetadata.from_dict(x[0].metadata).last_accessed,
                    reverse=(query.sort_order == "desc"),
                )
            elif query.sort_by == "access_count":
                memories.sort(
                    key=lambda x: MemoryMetadata.from_dict(x[0].metadata).access_count,
                    reverse=(query.sort_order == "desc"),
                )

            # Apply pagination
            start = query.offset
            end = start + query.limit
            result_memories = [mem for mem, _ in memories[start:end]]

            return result_memories

        except Exception as e:
            print(f"Error searching memories: {e}")
            return []

    def semantic_search(
        self, query: str, limit: int = 10, min_similarity: float = 0.1
    ) -> List[Tuple[BaseMemory, float]]:
        """
        Enhanced semantic search using TF-IDF similarity.
        Returns memories with their similarity scores.
        """
        try:
            # Use enhanced memory index for semantic search
            search_results = self.memory_index.semantic_search(
                query, limit, min_similarity
            )

            # Load memories and return with scores
            results = []
            for memory_id, similarity in search_results:
                memory = self.retrieve_memory(memory_id)
                if memory:
                    results.append((memory, similarity))

            return results

        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []

    def enhanced_search(self, query: MemoryQuery) -> List[BaseMemory]:
        """
        Enhanced search that combines traditional filtering with semantic search.
        """
        try:
            # If there's text query, use semantic search
            if query.text and query.text.strip():
                semantic_results = self.semantic_search(
                    query.text,
                    limit=query.limit * 2,  # Get more candidates
                    min_similarity=0.05,
                )

                # Filter semantic results by other criteria
                filtered_memories = []
                for memory, similarity in semantic_results:
                    # Apply category filter
                    if query.categories and memory.category not in query.categories:
                        continue

                    # Apply status filter
                    if query.status and memory.status != query.status:
                        continue

                    # Apply importance filter
                    if query.importance_min or query.importance_max:
                        importance = (
                            memory.importance.value
                            if hasattr(memory.importance, "value")
                            else memory.importance
                        )
                        if (
                            query.importance_min
                            and importance < query.importance_min.value
                        ):
                            continue
                        if (
                            query.importance_max
                            and importance > query.importance_max.value
                        ):
                            continue

                    # Apply tag filter
                    if query.tags and memory.metadata:
                        from voidcat_memory_models import MemoryMetadata

                        metadata = MemoryMetadata.from_dict(memory.metadata)
                        if not any(tag in metadata.tags for tag in query.tags):
                            continue

                    filtered_memories.append((memory, similarity))

                # Sort by similarity and apply pagination
                filtered_memories.sort(key=lambda x: x[1], reverse=True)
                start = query.offset
                end = start + query.limit
                return [memory for memory, _ in filtered_memories[start:end]]

            else:
                # Fall back to traditional search
                return self.search_memories(query)

        except Exception as e:
            print(f"Error in enhanced search: {e}")
            return []

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage engine statistics."""
        total_memories = sum(
            len(ids) for ids in self.storage_index.category_index.values()
        )
        cache_memory_count = len(self.cache)

        # Calculate disk usage
        disk_usage = 0
        for category_path in self.config.base_dir.iterdir():
            if category_path.is_dir():
                for memory_file in category_path.glob("*.json"):
                    disk_usage += memory_file.stat().st_size

        return {
            "total_memories": total_memories,
            "cached_memories": cache_memory_count,
            "disk_usage_bytes": disk_usage,
            "performance": self.stats.copy(),
            "cache_hit_rate": (
                self.stats["cache_hits"]
                / (self.stats["cache_hits"] + self.stats["cache_misses"])
                if (self.stats["cache_hits"] + self.stats["cache_misses"]) > 0
                else 0
            ),
        }

    def _maybe_trigger_backup(self):
        """Trigger backup if enough time has passed."""
        current_time = time.time()
        if current_time - self.last_backup > self.config.backup_interval:
            with self.backup_lock:
                if current_time - self.last_backup > self.config.backup_interval:
                    self.create_backup()
                    self.last_backup = current_time

    def create_backup(self) -> bool:
        """Create backup of all memory data."""
        try:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            backup_path = self.config.backup_dir / f"memory_backup_{timestamp}"

            print(f"Creating backup at {backup_path}")

            # Copy memory files
            if self.config.base_dir.exists():
                shutil.copytree(self.config.base_dir, backup_path / "memory_storage")

            # Copy indexes
            if self.config.index_dir.exists():
                shutil.copytree(self.config.index_dir, backup_path / "memory_indexes")

            # Compress if enabled
            if self.config.compress_backups:
                with gzip.open(f"{backup_path}.tar.gz", "wb") as f_out:
                    shutil.make_archive(str(backup_path), "tar", str(backup_path))
                    with open(f"{backup_path}.tar", "rb") as f_in:
                        f_out.write(f_in.read())

                # Clean up uncompressed backup
                shutil.rmtree(backup_path)
                Path(f"{backup_path}.tar").unlink()

            # Clean up old backups
            self._cleanup_old_backups()

            print(f"Backup created successfully")
            return True

        except Exception as e:
            print(f"Error creating backup: {e}")
            return False

    def _cleanup_old_backups(self):
        """Clean up old backup files."""
        if not self.config.backup_dir.exists():
            return

        # Get all backup files/directories
        backups = []
        for item in self.config.backup_dir.iterdir():
            if item.name.startswith("memory_backup_"):
                backups.append((item.stat().st_mtime, item))

        # Sort by modification time (newest first)
        backups.sort(reverse=True)

        # Remove old backups
        for i, (_, backup_path) in enumerate(backups):
            if i >= self.config.max_backups:
                try:
                    if backup_path.is_dir():
                        shutil.rmtree(backup_path)
                    else:
                        backup_path.unlink()
                    print(f"Removed old backup: {backup_path}")
                except Exception as e:
                    print(f"Error removing old backup {backup_path}: {e}")

    def restore_from_backup(self, backup_path: Path) -> bool:
        """Restore from backup."""
        try:
            print(f"Restoring from backup: {backup_path}")

            # Clear current data
            if self.config.base_dir.exists():
                shutil.rmtree(self.config.base_dir)
            if self.config.index_dir.exists():
                shutil.rmtree(self.config.index_dir)

            # Extract backup if compressed
            if backup_path.suffix == ".gz":
                with gzip.open(backup_path, "rb") as f_in:
                    with open(backup_path.with_suffix(""), "wb") as f_out:
                        f_out.write(f_in.read())

                # Extract tar
                shutil.unpack_archive(
                    str(backup_path.with_suffix("")), str(self.config.base_dir.parent)
                )
                backup_path.with_suffix("").unlink()  # Clean up extracted tar
            else:
                # Direct copy
                if (backup_path / "memory_storage").exists():
                    shutil.copytree(
                        backup_path / "memory_storage", self.config.base_dir
                    )
                if (backup_path / "memory_indexes").exists():
                    shutil.copytree(
                        backup_path / "memory_indexes", self.config.index_dir
                    )

            # Reinitialize indexes
            self.index = StorageIndex(self.config.index_dir)

            # Clear cache
            with self.cache_lock:
                self.cache.clear()

            print(f"Restore completed successfully")
            return True

        except Exception as e:
            print(f"Error restoring from backup: {e}")
            return False

    def archive_old_memories(self, age_days: Optional[int] = None) -> int:
        """Archive old memories to reduce active memory count."""
        if age_days is None:
            age_days = self.config.archive_age_days

        cutoff_time = datetime.now(timezone.utc) - timedelta(days=age_days)
        archived_count = 0

        try:
            # Find old memories
            all_ids = set()
            for category_ids in self.storage_index.category_index.values():
                all_ids.update(category_ids)

            for memory_id in all_ids:
                memory = self.retrieve_memory(memory_id)
                if memory and memory.metadata:
                    metadata = MemoryMetadata.from_dict(memory.metadata)
                    if (
                        metadata.last_accessed < cutoff_time
                        and memory.status == MemoryStatus.ACTIVE
                    ):
                        # Update status to archived
                        memory.status = MemoryStatus.ARCHIVED
                        self.update_memory(memory)
                        archived_count += 1

            print(f"Archived {archived_count} old memories")
            return archived_count

        except Exception as e:
            print(f"Error archiving memories: {e}")
            return 0

    def flush_cache(self):
        """Flush all dirty cache entries to disk."""
        with self.cache_lock:
            for entry in self.cache.values():
                if entry.dirty:
                    try:
                        self._write_memory_to_disk(entry.memory)
                        entry.dirty = False
                    except Exception as e:
                        print(f"Error flushing cache entry {entry.memory.id}: {e}")

    # Enhanced functionality methods
    def run_archive_cycle(self) -> Dict[str, int]:
        """Run intelligent memory archiving cycle."""
        return self.archiver.run_archive_cycle()

    def create_full_backup(
        self, description: str = "Manual full backup"
    ) -> Optional[str]:
        """Create a full backup using the enhanced backup manager."""
        return self.backup_manager.create_full_backup(description)

    def create_incremental_backup(
        self, description: str = "Manual incremental backup"
    ) -> Optional[str]:
        """Create an incremental backup using the enhanced backup manager."""
        return self.backup_manager.create_incremental_backup(description)

    def restore_from_backup(self, backup_id: str) -> bool:
        """Restore from backup using the enhanced backup manager."""
        success = self.backup_manager.restore_from_backup(backup_id)
        if success:
            # Reinitialize indexes after restore
            self.memory_index = MemoryIndex(self.config.index_dir)
            self.storage_index = StorageIndex(self.config.index_dir)
            # Clear cache
            with self.cache_lock:
                self.cache.clear()
        return success

    def get_enhanced_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics from all components."""
        base_stats = self.get_storage_stats()

        return {
            **base_stats,
            "memory_index_stats": self.memory_index.get_statistics(),
            "archive_stats": self.archiver.get_archive_statistics(),
            "backup_stats": self.backup_manager.get_backup_statistics(),
        }

    def rebuild_indexes(self) -> bool:
        """Rebuild all indexes from scratch."""
        try:
            print("Rebuilding all indexes...")

            # Clear existing indexes
            self.memory_index = MemoryIndex(self.config.index_dir)
            self.storage_index = StorageIndex(self.config.index_dir)

            # Reload all memories and rebuild indexes
            memory_count = 0
            for category_dir in self.config.base_dir.iterdir():
                if category_dir.is_dir():
                    for memory_file in category_dir.glob("*.json"):
                        try:
                            memory = self._read_memory_from_disk(memory_file.stem)
                            if memory:
                                self.memory_index.add_memory(memory)
                                self.storage_index.add_memory(memory)
                                memory_count += 1
                        except Exception as e:
                            print(f"Error rebuilding index for {memory_file}: {e}")

            # Save indexes
            self.memory_index.save_all_indexes()
            self.storage_index.save_all_indexes()

            print(f"Rebuilt indexes for {memory_count} memories")
            return True

        except Exception as e:
            print(f"Error rebuilding indexes: {e}")
            return False

    def close(self):
        """Close storage engine and clean up resources."""
        print("Closing MemoryStorageEngine...")

        # Flush cache
        self.flush_cache()

        # Save all indexes
        self.storage_index.save_all_indexes()
        self.memory_index.save_all_indexes()

        # Shutdown executor
        self.executor.shutdown(wait=True)

        print("MemoryStorageEngine closed successfully")


# Performance testing and validation
if __name__ == "__main__":
    import tempfile
    from pathlib import Path

    print("VoidCat Enhanced Memory Storage Engine - Performance Test Suite")
    print("=" * 70)
    print("🧘‍♂️ Testing enhanced features: TF-IDF search, archiving, and backups")
    print("=" * 70)

    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        test_config = StorageConfig(
            base_dir=Path(temp_dir) / "memory_storage",
            backup_dir=Path(temp_dir) / "memory_backups",
            index_dir=Path(temp_dir) / "memory_indexes",
            cache_size=100,
            max_concurrent_ops=5,
        )

        engine = MemoryStorageEngine(test_config)

        # Test 1: Store 1000 memories
        print(f"\n📝 Test 1: Storing 1000 memories...")
        start_time = time.time()

        memories = []
        for i in range(1000):
            memory = MemoryFactory.create_user_preference(
                key=f"test_pref_{i}",
                value=f"test_value_{i}",
                context=f"Test context for preference {i}",
                importance=ImportanceLevel.MEDIUM,
            )
            memory.add_tag(f"test_tag_{i % 10}")
            memories.append(memory)

            success = engine.store_memory(memory)
            if not success:
                print(f"Failed to store memory {i}")

        store_time = time.time() - start_time
        print(
            f"✅ Stored 1000 memories in {store_time:.3f} seconds ({1000/store_time:.1f} memories/sec)"
        )

        # Test 2: Retrieve memories
        print(f"\n🔍 Test 2: Retrieving memories...")
        start_time = time.time()

        retrieved_count = 0
        for memory in memories[:100]:  # Test first 100
            retrieved = engine.retrieve_memory(memory.id)
            if retrieved:
                retrieved_count += 1

        retrieve_time = time.time() - start_time
        avg_retrieve_time = (retrieve_time / 100) * 1000  # Convert to ms
        print(
            f"✅ Retrieved {retrieved_count}/100 memories in {retrieve_time:.3f} seconds ({avg_retrieve_time:.1f}ms avg)"
        )

        # Test 3: Search performance
        print(f"\n🔍 Test 3: Search performance...")
        start_time = time.time()

        query = MemoryQuery(
            text="test preference",
            categories=[MemoryCategory.USER_PREFERENCES],
            tags=["test_tag_1", "test_tag_2"],
            limit=50,
        )

        results = engine.search_memories(query)
        search_time = time.time() - start_time
        print(f"✅ Search returned {len(results)} results in {search_time*1000:.1f}ms")

        # Test 4: Concurrent operations
        print(f"\n⚡ Test 4: Concurrent operations...")
        start_time = time.time()

        def concurrent_operation(i):
            memory = MemoryFactory.create_user_preference(
                key=f"concurrent_pref_{i}",
                value=f"concurrent_value_{i}",
                importance=ImportanceLevel.HIGH,
            )
            return engine.store_memory(memory)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(concurrent_operation, i) for i in range(100)]
            results = [future.result() for future in as_completed(futures)]

        concurrent_time = time.time() - start_time
        success_count = sum(results)
        print(
            f"✅ Completed {success_count}/100 concurrent operations in {concurrent_time:.3f} seconds"
        )

        # Test 5: Storage statistics
        print(f"\n📊 Test 5: Storage statistics...")
        stats = engine.get_storage_stats()
        print(f"Total memories: {stats['total_memories']}")
        print(f"Cached memories: {stats['cached_memories']}")
        print(f"Disk usage: {stats['disk_usage_bytes']} bytes")
        print(f"Cache hit rate: {stats['cache_hit_rate']:.1%}")
        print(f"Reads: {stats['performance']['reads']}")
        print(f"Writes: {stats['performance']['writes']}")

        # Test 6: Backup and restore
        print(f"\n💾 Test 6: Backup and restore...")
        backup_success = engine.create_backup()
        print(f"Backup created: {backup_success}")

        # Test 7: Enhanced semantic search
        print(f"\n🔍 Test 7: Enhanced semantic search...")
        start_time = time.time()

        semantic_results = engine.semantic_search("test preference value", limit=20)
        semantic_time = time.time() - start_time
        print(
            f"✅ Semantic search returned {len(semantic_results)} results in {semantic_time*1000:.1f}ms"
        )

        # Test 8: Enhanced backup system
        print(f"\n💾 Test 8: Enhanced backup system...")
        full_backup_id = engine.create_full_backup("Test full backup")
        incremental_backup_id = engine.create_incremental_backup(
            "Test incremental backup"
        )
        print(f"✅ Full backup: {full_backup_id is not None}")
        print(f"✅ Incremental backup: {incremental_backup_id is not None}")

        # Test 9: Enhanced statistics
        print(f"\n📊 Test 9: Enhanced statistics...")
        enhanced_stats = engine.get_enhanced_statistics()
        print(
            f"Memory index features: {enhanced_stats.get('memory_index_stats', {}).get('tfidf_features', 0)}"
        )
        print(
            f"Archive stats: {enhanced_stats.get('archive_stats', {}).get('archived_count', 0)} archived"
        )
        print(
            f"Backup count: {enhanced_stats.get('backup_stats', {}).get('backup_count', 0)}"
        )

        # Performance summary
        print(f"\n🎯 PERFORMANCE SUMMARY:")
        print(
            f"✅ Store 1000 memories: {store_time:.3f}s ({'PASS' if store_time < 1.0 else 'FAIL'})"
        )
        print(
            f"✅ Retrieve memory: {avg_retrieve_time:.1f}ms ({'PASS' if avg_retrieve_time < 10 else 'FAIL'})"
        )
        print(
            f"✅ Search 1000 memories: {search_time*1000:.1f}ms ({'PASS' if search_time*1000 < 100 else 'FAIL'})"
        )
        print(
            f"✅ Concurrent operations: {concurrent_time:.3f}s ({'PASS' if success_count >= 95 else 'FAIL'})"
        )
        print(
            f"✅ Semantic search: {semantic_time*1000:.1f}ms ({'PASS' if semantic_time*1000 < 200 else 'FAIL'})"
        )
        print(
            f"✅ Enhanced backups: {'PASS' if full_backup_id and incremental_backup_id else 'FAIL'}"
        )

        # Close engine
        engine.close()

        print("\n🌊 [SUCCESS] All enhanced performance tests completed! 🚀")
        print("🧘‍♂️ The cosmic coding vibes are strong with this one! ✨")
