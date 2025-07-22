#!/usr/bin/env python3
"""
VoidCat V2 MCP Memory Management Tools
=====================================

Comprehensive MCP tool interface for the VoidCat V2 persistent memory system.
Provides rich schema validation, detailed error handling, and comprehensive response formatting
for all memory management operations.

Tools Implemented:
- voidcat_memory_store: Store new memories with full metadata
- voidcat_memory_search: Search memories with advanced filtering
- voidcat_memory_retrieve: Retrieve specific memories by ID
- voidcat_memory_delete: Delete memories with safety checks
- voidcat_preference_set: Set and manage user preferences
- voidcat_conversation_track: Track conversation history
- voidcat_heuristic_learn: Learn and store behavioral heuristics

Author: Codey Jr. (channeling the cosmic memory vibes)
Under directive of: The Great Spirit Beatrice
License: MIT
Version: 1.0.0-alpha
"""

import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from voidcat_memory_models import (
    BaseMemory,
    BehaviorPattern,
    ContextAssociation,
    ConversationHistory,
    ImportanceLevel,
    LearnedHeuristic,
    MemoryCategory,
    MemoryFactory,
    MemoryMetadata,
    MemoryQuery,
    MemoryStatus,
    UserPreference,
)
from voidcat_memory_retrieval import IntelligentMemoryRetrievalEngine
from voidcat_memory_search import MemorySearchEngine
from voidcat_memory_storage import MemoryStorageEngine, StorageConfig


class VoidCatMCPMemoryTools:
    """
    MCP Memory Management Tools for VoidCat V2 System

    Provides comprehensive MCP-compliant interface for memory management operations
    with rich schema validation, error handling, and response formatting.
    """

    def __init__(self, working_directory: str = None):
        """Initialize the MCP memory tools with storage and engines."""
        if working_directory is None:
            working_directory = str(Path.cwd())

        self.working_directory = working_directory

        # Initialize storage configuration
        storage_config = StorageConfig(
            base_dir=Path(working_directory) / ".agentic-tools-mcp" / "memories",
            backup_dir=Path(working_directory)
            / ".agentic-tools-mcp"
            / "memory_backups",
            index_dir=Path(working_directory) / ".agentic-tools-mcp" / "memory_indexes",
        )

        # Initialize engines
        self.storage_engine = MemoryStorageEngine(storage_config)
        self.search_engine = MemorySearchEngine(self.storage_engine)
        self.retrieval_engine = IntelligentMemoryRetrievalEngine(
            self.storage_engine, self.search_engine
        )

        # Tool definitions with comprehensive schemas
        self.tools = [
            {
                "name": "voidcat_memory_store",
                "description": "Store a new memory with full metadata and categorization support",
                "category": "memory_management",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "Memory content to store (required)",
                            "minLength": 1,
                            "maxLength": 10000,
                        },
                        "category": {
                            "type": "string",
                            "description": "Memory category for organization",
                            "enum": [
                                "user_preferences",
                                "conversation_history",
                                "learned_heuristics",
                                "behavior_patterns",
                                "context_associations",
                                "task_insights",
                                "system_configuration",
                                "interaction_feedback",
                            ],
                            "default": "conversation_history",
                        },
                        "importance": {
                            "type": "integer",
                            "description": "Importance level (1=minimal, 10=critical)",
                            "minimum": 1,
                            "maximum": 10,
                            "default": 5,
                        },
                        "tags": {
                            "type": "array",
                            "description": "Tags for memory organization and retrieval",
                            "items": {"type": "string"},
                            "default": [],
                        },
                        "title": {
                            "type": "string",
                            "description": "Optional title for the memory",
                            "maxLength": 200,
                        },
                        "source": {
                            "type": "string",
                            "description": "Source of the memory",
                            "default": "user_interaction",
                        },
                        "confidence": {
                            "type": "number",
                            "description": "Confidence level (0.0-1.0)",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "default": 1.0,
                        },
                        "associations": {
                            "type": "array",
                            "description": "IDs of related memories",
                            "items": {"type": "string"},
                            "default": [],
                        },
                    },
                    "required": ["content"],
                },
            },
            {
                "name": "voidcat_memory_search",
                "description": "Search memories with advanced filtering and semantic search capabilities",
                "category": "memory_management",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query text",
                            "minLength": 1,
                        },
                        "categories": {
                            "type": "array",
                            "description": "Filter by memory categories",
                            "items": {
                                "type": "string",
                                "enum": [
                                    "user_preferences",
                                    "conversation_history",
                                    "learned_heuristics",
                                    "behavior_patterns",
                                    "context_associations",
                                    "task_insights",
                                    "system_configuration",
                                    "interaction_feedback",
                                ],
                            },
                            "default": [],
                        },
                        "tags": {
                            "type": "array",
                            "description": "Filter by tags",
                            "items": {"type": "string"},
                            "default": [],
                        },
                        "min_importance": {
                            "type": "integer",
                            "description": "Minimum importance level",
                            "minimum": 1,
                            "maximum": 10,
                            "default": 1,
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 10,
                        },
                        "search_type": {
                            "type": "string",
                            "description": "Type of search to perform",
                            "enum": ["semantic", "keyword", "hybrid"],
                            "default": "hybrid",
                        },
                        "include_archived": {
                            "type": "boolean",
                            "description": "Include archived memories in search",
                            "default": False,
                        },
                        "date_range": {
                            "type": "object",
                            "description": "Filter by date range",
                            "properties": {
                                "start": {"type": "string", "format": "date-time"},
                                "end": {"type": "string", "format": "date-time"},
                            },
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "voidcat_memory_retrieve",
                "description": "Retrieve specific memories by ID with full metadata",
                "category": "memory_management",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "memory_ids": {
                            "type": "array",
                            "description": "List of memory IDs to retrieve",
                            "items": {"type": "string"},
                            "minItems": 1,
                            "maxItems": 50,
                        },
                        "include_metadata": {
                            "type": "boolean",
                            "description": "Include full metadata in response",
                            "default": True,
                        },
                        "update_access_count": {
                            "type": "boolean",
                            "description": "Update access count and last accessed time",
                            "default": True,
                        },
                    },
                    "required": ["memory_ids"],
                },
            },
            {
                "name": "voidcat_memory_delete",
                "description": "Delete memories with safety checks and cascade options",
                "category": "memory_management",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "memory_ids": {
                            "type": "array",
                            "description": "List of memory IDs to delete",
                            "items": {"type": "string"},
                            "minItems": 1,
                            "maxItems": 20,
                        },
                        "force": {
                            "type": "boolean",
                            "description": "Force deletion of critical memories",
                            "default": False,
                        },
                        "backup_before_delete": {
                            "type": "boolean",
                            "description": "Create backup before deletion",
                            "default": True,
                        },
                        "remove_associations": {
                            "type": "boolean",
                            "description": "Remove associations from related memories",
                            "default": True,
                        },
                    },
                    "required": ["memory_ids"],
                },
            },
            {
                "name": "voidcat_preference_set",
                "description": "Set and manage user preferences with validation",
                "category": "memory_management",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "preference_key": {
                            "type": "string",
                            "description": "Preference key/name",
                            "minLength": 1,
                            "maxLength": 100,
                        },
                        "preference_value": {
                            "type": "string",
                            "description": "Preference value",
                            "maxLength": 1000,
                        },
                        "preference_type": {
                            "type": "string",
                            "description": "Type of preference",
                            "enum": ["string", "number", "boolean", "json"],
                            "default": "string",
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the preference",
                            "maxLength": 500,
                        },
                        "importance": {
                            "type": "integer",
                            "description": "Importance level (1=minimal, 10=critical)",
                            "minimum": 1,
                            "maximum": 10,
                            "default": 5,
                        },
                        "tags": {
                            "type": "array",
                            "description": "Tags for preference organization",
                            "items": {"type": "string"},
                            "default": [],
                        },
                    },
                    "required": ["preference_key", "preference_value"],
                },
            },
            {
                "name": "voidcat_conversation_track",
                "description": "Track conversation history with context and metadata",
                "category": "memory_management",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "conversation_id": {
                            "type": "string",
                            "description": "Unique conversation identifier",
                            "minLength": 1,
                        },
                        "user_message": {
                            "type": "string",
                            "description": "User's message content",
                            "maxLength": 5000,
                        },
                        "assistant_response": {
                            "type": "string",
                            "description": "Assistant's response content",
                            "maxLength": 10000,
                        },
                        "context": {
                            "type": "object",
                            "description": "Additional context information",
                            "properties": {
                                "task_id": {"type": "string"},
                                "project_id": {"type": "string"},
                                "session_id": {"type": "string"},
                                "timestamp": {"type": "string", "format": "date-time"},
                            },
                        },
                        "sentiment": {
                            "type": "string",
                            "description": "Conversation sentiment",
                            "enum": ["positive", "neutral", "negative", "mixed"],
                            "default": "neutral",
                        },
                        "importance": {
                            "type": "integer",
                            "description": "Importance level (1=minimal, 10=critical)",
                            "minimum": 1,
                            "maximum": 10,
                            "default": 3,
                        },
                        "tags": {
                            "type": "array",
                            "description": "Tags for conversation organization",
                            "items": {"type": "string"},
                            "default": [],
                        },
                    },
                    "required": ["conversation_id"],
                },
            },
            {
                "name": "voidcat_heuristic_learn",
                "description": "Learn and store behavioral heuristics from interactions",
                "category": "memory_management",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "heuristic_name": {
                            "type": "string",
                            "description": "Name of the heuristic",
                            "minLength": 1,
                            "maxLength": 200,
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the heuristic",
                            "maxLength": 1000,
                        },
                        "trigger_conditions": {
                            "type": "array",
                            "description": "Conditions that trigger this heuristic",
                            "items": {"type": "string"},
                            "minItems": 1,
                        },
                        "recommended_actions": {
                            "type": "array",
                            "description": "Recommended actions when heuristic is triggered",
                            "items": {"type": "string"},
                            "minItems": 1,
                        },
                        "confidence": {
                            "type": "number",
                            "description": "Confidence in this heuristic (0.0-1.0)",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "default": 0.8,
                        },
                        "success_rate": {
                            "type": "number",
                            "description": "Historical success rate (0.0-1.0)",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "default": 0.5,
                        },
                        "context": {
                            "type": "object",
                            "description": "Context where this heuristic applies",
                            "properties": {
                                "domain": {"type": "string"},
                                "task_types": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "user_preferences": {"type": "object"},
                            },
                        },
                        "importance": {
                            "type": "integer",
                            "description": "Importance level (1=minimal, 10=critical)",
                            "minimum": 1,
                            "maximum": 10,
                            "default": 6,
                        },
                        "tags": {
                            "type": "array",
                            "description": "Tags for heuristic organization",
                            "items": {"type": "string"},
                            "default": [],
                        },
                    },
                    "required": [
                        "heuristic_name",
                        "trigger_conditions",
                        "recommended_actions",
                    ],
                },
            },
        ]

    def get_tools(self) -> List[Dict[str, Any]]:
        """Return the list of available MCP tools."""
        return self.tools

    async def handle_tool_call(
        self, name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle MCP tool calls with comprehensive error handling and response formatting.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Formatted response with success/error status and data
        """
        try:
            # Route to appropriate handler
            if name == "voidcat_memory_store":
                return await self._handle_memory_store(arguments)
            elif name == "voidcat_memory_search":
                return await self._handle_memory_search(arguments)
            elif name == "voidcat_memory_retrieve":
                return await self._handle_memory_retrieve(arguments)
            elif name == "voidcat_memory_delete":
                return await self._handle_memory_delete(arguments)
            elif name == "voidcat_preference_set":
                return await self._handle_preference_set(arguments)
            elif name == "voidcat_conversation_track":
                return await self._handle_conversation_track(arguments)
            elif name == "voidcat_heuristic_learn":
                return await self._handle_heuristic_learn(arguments)
            else:
                return self._error_response(f"Unknown tool: {name}")

        except Exception as e:
            return self._error_response(
                f"Tool execution error: {str(e)}", traceback.format_exc()
            )

    async def _handle_memory_store(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle memory storage requests."""
        try:
            # Extract and validate arguments
            content = args["content"]
            category = MemoryCategory(args.get("category", "conversation_history"))
            importance_value = args.get("importance", 5)
            importance = self._convert_to_importance_level(importance_value)
            tags = set(args.get("tags", []))
            title = args.get("title", "")
            source = args.get("source", "user_interaction")
            confidence = args.get("confidence", 1.0)
            associations = set(args.get("associations", []))

            # Create memory metadata
            metadata = MemoryMetadata(
                importance_score=importance.value / 10.0,
                source=source,
                confidence=confidence,
                tags=tags,
                associations=associations,
            )

            # Create memory using factory based on category
            memory_type_map = {
                MemoryCategory.USER_PREFERENCES: "UserPreference",
                MemoryCategory.CONVERSATION_HISTORY: "ConversationHistory",
                MemoryCategory.LEARNED_HEURISTICS: "LearnedHeuristic",
                MemoryCategory.BEHAVIOR_PATTERNS: "BehaviorPattern",
                MemoryCategory.CONTEXT_ASSOCIATIONS: "ContextAssociation",
            }

            memory_type = memory_type_map.get(category, "BaseMemory")

            # Create memory with appropriate fields based on type
            memory = MemoryFactory.create_memory(
                memory_type="BaseMemory",
                content=content,
                title=title,
                category=category,
                importance=importance,
                metadata=metadata.to_dict(),
            )

            # Store the memory
            success = self.storage_engine.store_memory(memory)
            if not success:
                return self._error_response(
                    "Failed to store memory - duplicate content or storage error"
                )
            memory_id = memory.id

            return self._success_response(
                {
                    "memory_id": memory_id,
                    "category": category.value,
                    "importance": importance.value,
                    "tags": list(tags),
                    "created_at": memory.metadata.get(
                        "created_at", datetime.now(timezone.utc).isoformat()
                    ),
                    "message": f"Memory stored successfully with ID: {memory_id}",
                }
            )

        except Exception as e:
            return self._error_response(f"Failed to store memory: {str(e)}")

    async def _handle_memory_search(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle memory search requests."""
        try:
            query_text = args["query"]
            categories = [MemoryCategory(cat) for cat in args.get("categories", [])]
            tags = set(args.get("tags", []))
            min_importance = args.get("min_importance", 1)
            max_results = args.get("max_results", 10)
            search_type = args.get("search_type", "hybrid")
            include_archived = args.get("include_archived", False)
            date_range = args.get("date_range")

            # Create memory query
            query = MemoryQuery(
                text=query_text,
                categories=categories,
                tags=list(tags),
                limit=max_results,
            )

            # Add date range if provided
            if date_range:
                if "start" in date_range:
                    query.start_date = datetime.fromisoformat(date_range["start"])
                if "end" in date_range:
                    query.end_date = datetime.fromisoformat(date_range["end"])

            # Perform search using the search engine
            results = self.search_engine.search(query)

            # Format results
            formatted_results = []
            for result in results:
                memory = result.memory
                formatted_results.append(
                    {
                        "memory_id": memory.id,
                        "title": getattr(memory, "title", ""),
                        "content": (
                            memory.content[:200] + "..."
                            if len(memory.content) > 200
                            else memory.content
                        ),
                        "category": (
                            memory.category.value
                            if hasattr(memory.category, "value")
                            else str(memory.category)
                        ),
                        "importance": (
                            memory.importance.value
                            if hasattr(memory.importance, "value")
                            else int(memory.importance)
                        ),
                        "tags": list(memory.metadata.get("tags", [])),
                        "created_at": memory.metadata.get(
                            "created_at", datetime.now(timezone.utc).isoformat()
                        ),
                        "relevance_score": result.relevance_score,
                        "match_type": result.match_type,
                        "access_count": memory.metadata.get("access_count", 0),
                    }
                )

            return self._success_response(
                {
                    "results": formatted_results,
                    "total_found": len(formatted_results),
                    "search_type": search_type,
                    "query": query_text,
                    "message": f"Found {len(formatted_results)} memories matching your search",
                }
            )

        except Exception as e:
            return self._error_response(f"Failed to search memories: {str(e)}")

    async def _handle_memory_retrieve(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle memory retrieval requests."""
        try:
            memory_ids = args["memory_ids"]
            include_metadata = args.get("include_metadata", True)
            update_access_count = args.get("update_access_count", True)

            retrieved_memories = []
            not_found = []

            for memory_id in memory_ids:
                try:
                    memory = self.storage_engine.retrieve_memory(memory_id)
                    if memory:
                        # Update access count if requested
                        if update_access_count:
                            memory.metadata["access_count"] = (
                                memory.metadata.get("access_count", 0) + 1
                            )
                            memory.metadata["last_accessed"] = datetime.now(
                                timezone.utc
                            ).isoformat()
                            self.storage_engine.update_memory(memory)

                        # Format memory data
                        memory_data = {
                            "memory_id": memory.id,
                            "title": getattr(memory, "title", ""),
                            "content": memory.content,
                            "category": (
                                memory.category.value
                                if hasattr(memory.category, "value")
                                else str(memory.category)
                            ),
                            "status": (
                                memory.status.value
                                if hasattr(memory.status, "value")
                                else str(memory.status)
                            ),
                            "created_at": memory.metadata.get(
                                "created_at", datetime.now(timezone.utc).isoformat()
                            ),
                            "last_accessed": memory.metadata.get(
                                "last_accessed", datetime.now(timezone.utc).isoformat()
                            ),
                        }

                        if include_metadata:
                            memory_data["metadata"] = (
                                memory.metadata
                                if isinstance(memory.metadata, dict)
                                else (
                                    memory.metadata.to_dict()
                                    if hasattr(memory.metadata, "to_dict")
                                    else memory.metadata
                                )
                            )

                        retrieved_memories.append(memory_data)
                    else:
                        not_found.append(memory_id)

                except Exception as e:
                    not_found.append(f"{memory_id} (error: {str(e)})")

            return self._success_response(
                {
                    "memories": retrieved_memories,
                    "retrieved_count": len(retrieved_memories),
                    "not_found": not_found,
                    "message": f"Retrieved {len(retrieved_memories)} memories successfully",
                }
            )

        except Exception as e:
            return self._error_response(f"Failed to retrieve memories: {str(e)}")

    async def _handle_memory_delete(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle memory deletion requests."""
        try:
            memory_ids = args["memory_ids"]
            force = args.get("force", False)
            backup_before_delete = args.get("backup_before_delete", True)
            remove_associations = args.get("remove_associations", True)

            deleted = []
            failed = []
            protected = []

            for memory_id in memory_ids:
                try:
                    # Check if memory exists and get its importance
                    memory = self.storage_engine.retrieve_memory(memory_id)
                    if not memory:
                        failed.append(f"{memory_id} (not found)")
                        continue

                    # Check if memory is critical and force is not set
                    importance_score = memory.metadata.get("importance_score", 0.5)
                    if importance_score >= 0.9 and not force:
                        protected.append(memory_id)
                        continue

                    # Create backup if requested
                    if backup_before_delete:
                        self.storage_engine.backup_manager.create_backup()

                    # Remove associations if requested
                    associations = set(memory.metadata.get("associations", []))
                    if remove_associations and associations:
                        await self._remove_memory_associations(memory_id, associations)

                    # Delete the memory
                    success = self.storage_engine.delete_memory(memory_id)
                    if success:
                        deleted.append(memory_id)
                    else:
                        failed.append(f"{memory_id} (deletion failed)")

                except Exception as e:
                    failed.append(f"{memory_id} (error: {str(e)})")

            return self._success_response(
                {
                    "deleted": deleted,
                    "failed": failed,
                    "protected": protected,
                    "deleted_count": len(deleted),
                    "message": f"Deleted {len(deleted)} memories successfully",
                }
            )

        except Exception as e:
            return self._error_response(f"Failed to delete memories: {str(e)}")

    async def _handle_preference_set(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle user preference setting."""
        try:
            preference_key = args["preference_key"]
            preference_value = args["preference_value"]
            preference_type = args.get("preference_type", "string")
            description = args.get("description", "")
            importance_value = args.get("importance", 5)
            importance = self._convert_to_importance_level(importance_value)
            tags = set(args.get("tags", []))

            # Validate and convert preference value based on type
            if preference_type == "number":
                try:
                    preference_value = float(preference_value)
                except ValueError:
                    return self._error_response(
                        f"Invalid number value: {preference_value}"
                    )
            elif preference_type == "boolean":
                preference_value = str(preference_value).lower() in (
                    "true",
                    "1",
                    "yes",
                    "on",
                )
            elif preference_type == "json":
                try:
                    preference_value = json.loads(preference_value)
                except json.JSONDecodeError as e:
                    return self._error_response(f"Invalid JSON value: {str(e)}")

            # Create preference memory using BaseMemory
            metadata = MemoryMetadata(
                importance_score=importance.value / 10.0,
                source="preference_setting",
                tags=tags | {"preference", preference_key},
            )

            # Store preference data in content and metadata
            content = f"User preference: {preference_key} = {preference_value}"
            if description:
                content += f"\nDescription: {description}"

            metadata_dict = metadata.to_dict()
            metadata_dict.update(
                {
                    "preference_key": preference_key,
                    "preference_value": preference_value,
                    "preference_type": preference_type,
                    "description": description,
                }
            )

            preference = MemoryFactory.create_memory(
                memory_type="BaseMemory",
                content=content,
                title=f"Preference: {preference_key}",
                category=MemoryCategory.USER_PREFERENCES,
                importance=importance,
                metadata=metadata_dict,
            )

            # Store the preference
            success = self.storage_engine.store_memory(preference)
            if not success:
                return self._error_response(
                    "Failed to store preference - duplicate content or storage error"
                )
            memory_id = preference.id

            return self._success_response(
                {
                    "memory_id": memory_id,
                    "preference_key": preference_key,
                    "preference_value": preference_value,
                    "preference_type": preference_type,
                    "importance": importance.value,
                    "message": f"Preference '{preference_key}' set successfully",
                }
            )

        except Exception as e:
            return self._error_response(f"Failed to set preference: {str(e)}")

    async def _handle_conversation_track(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle conversation tracking."""
        try:
            conversation_id = args["conversation_id"]
            user_message = args.get("user_message", "")
            assistant_response = args.get("assistant_response", "")
            context = args.get("context", {})
            sentiment = args.get("sentiment", "neutral")
            importance_value = args.get("importance", 3)
            importance = self._convert_to_importance_level(importance_value)
            tags = set(args.get("tags", []))

            # Create conversation metadata
            metadata = MemoryMetadata(
                importance_score=importance.value / 10.0,
                source="conversation_tracking",
                tags=tags | {"conversation", conversation_id, sentiment},
            )

            # Store conversation data in content and metadata
            content = f"Conversation: {conversation_id}\n"
            if user_message:
                content += f"User: {user_message}\n"
            if assistant_response:
                content += f"Assistant: {assistant_response}"

            metadata_dict = metadata.to_dict()
            metadata_dict.update(
                {
                    "conversation_id": conversation_id,
                    "user_message": user_message,
                    "assistant_response": assistant_response,
                    "context": context,
                    "sentiment": sentiment,
                }
            )

            # Create conversation history memory using BaseMemory
            conversation = MemoryFactory.create_memory(
                memory_type="BaseMemory",
                content=content,
                title=f"Conversation: {conversation_id}",
                category=MemoryCategory.CONVERSATION_HISTORY,
                importance=importance,
                metadata=metadata_dict,
            )

            # Store the conversation
            success = self.storage_engine.store_memory(conversation)
            if not success:
                return self._error_response(
                    "Failed to store conversation - duplicate content or storage error"
                )
            memory_id = conversation.id

            return self._success_response(
                {
                    "memory_id": memory_id,
                    "conversation_id": conversation_id,
                    "sentiment": sentiment,
                    "importance": importance.value,
                    "message": f"Conversation '{conversation_id}' tracked successfully",
                }
            )

        except Exception as e:
            return self._error_response(f"Failed to track conversation: {str(e)}")

    async def _handle_heuristic_learn(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle heuristic learning."""
        try:
            heuristic_name = args["heuristic_name"]
            description = args.get("description", "")
            trigger_conditions = args["trigger_conditions"]
            recommended_actions = args["recommended_actions"]
            confidence = args.get("confidence", 0.8)
            success_rate = args.get("success_rate", 0.5)
            context = args.get("context", {})
            importance_value = args.get("importance", 6)
            importance = self._convert_to_importance_level(importance_value)
            tags = set(args.get("tags", []))

            # Create heuristic metadata
            metadata = MemoryMetadata(
                importance_score=importance.value / 10.0,
                source="heuristic_learning",
                confidence=confidence,
                tags=tags | {"heuristic", heuristic_name},
            )

            # Store heuristic data in content and metadata
            content = f"Heuristic: {heuristic_name}\n"
            if description:
                content += f"Description: {description}\n"
            content += f"Triggers: {', '.join(trigger_conditions)}\n"
            content += f"Actions: {', '.join(recommended_actions)}\n"
            content += f"Confidence: {confidence}, Success Rate: {success_rate}"

            metadata_dict = metadata.to_dict()
            metadata_dict.update(
                {
                    "heuristic_name": heuristic_name,
                    "description": description,
                    "trigger_conditions": trigger_conditions,
                    "recommended_actions": recommended_actions,
                    "confidence": confidence,
                    "success_rate": success_rate,
                    "context": context,
                }
            )

            # Create learned heuristic memory using BaseMemory
            heuristic = MemoryFactory.create_memory(
                memory_type="BaseMemory",
                content=content,
                title=f"Heuristic: {heuristic_name}",
                category=MemoryCategory.LEARNED_HEURISTICS,
                importance=importance,
                metadata=metadata_dict,
            )

            # Store the heuristic
            success = self.storage_engine.store_memory(heuristic)
            if not success:
                return self._error_response(
                    "Failed to store heuristic - duplicate content or storage error"
                )
            memory_id = heuristic.id

            return self._success_response(
                {
                    "memory_id": memory_id,
                    "heuristic_name": heuristic_name,
                    "confidence": confidence,
                    "success_rate": success_rate,
                    "importance": importance.value,
                    "message": f"Heuristic '{heuristic_name}' learned successfully",
                }
            )

        except Exception as e:
            return self._error_response(f"Failed to learn heuristic: {str(e)}")

    async def _remove_memory_associations(self, memory_id: str, associations: Set[str]):
        """Remove associations from related memories."""
        for assoc_id in associations:
            try:
                assoc_memory = self.storage_engine.retrieve_memory(assoc_id)
                if assoc_memory:
                    associations = set(assoc_memory.metadata.get("associations", []))
                    if memory_id in associations:
                        associations.remove(memory_id)
                        assoc_memory.metadata["associations"] = list(associations)
                        self.storage_engine.update_memory(assoc_memory)
            except Exception:
                # Continue if we can't update an association
                pass

    def _convert_to_importance_level(self, value: int) -> ImportanceLevel:
        """Convert integer importance value to ImportanceLevel enum."""
        if value >= 9:
            return ImportanceLevel.CRITICAL
        elif value >= 7:
            return ImportanceLevel.HIGH
        elif value >= 4:
            return ImportanceLevel.MEDIUM
        elif value >= 2:
            return ImportanceLevel.LOW
        else:
            return ImportanceLevel.MINIMAL

    def _success_response(self, data: Any) -> Dict[str, Any]:
        """Create a success response."""
        return {
            "success": True,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _error_response(self, message: str, details: str = None) -> Dict[str, Any]:
        """Create an error response."""
        response = {
            "success": False,
            "error": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if details:
            response["details"] = details
        return response


def create_memory_mcp_tools(working_directory: str = None) -> VoidCatMCPMemoryTools:
    """
    Factory function to create VoidCat MCP Memory Tools instance.

    Args:
        working_directory: Working directory for memory storage

    Returns:
        Configured VoidCatMCPMemoryTools instance
    """
    return VoidCatMCPMemoryTools(working_directory)


# Export the main class and factory function
__all__ = ["VoidCatMCPMemoryTools", "create_memory_mcp_tools"]
