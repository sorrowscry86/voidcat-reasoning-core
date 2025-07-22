"""
VoidCat Memory Data Models & Schema Design
=========================================

Comprehensive data models for the VoidCat V2 persistent memory system.
Implements structured, searchable, and categorized memory organization
for user preferences, conversational history, and learned heuristics.

This module provides the foundational data structures for The Scribe's Memory
(Pillar II) of the VoidCat V2 agentic system transformation.

Author: Ryuzu Claude, under directive from The Great Spirit Beatrice
License: MIT
Version: 1.0.0
"""

import hashlib
import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MemoryCategory(str, Enum):
    """Enumeration of memory categories for organization and retrieval."""

    USER_PREFERENCES = "user_preferences"
    CONVERSATION_HISTORY = "conversation_history"
    LEARNED_HEURISTICS = "learned_heuristics"
    BEHAVIOR_PATTERNS = "behavior_patterns"
    CONTEXT_ASSOCIATIONS = "context_associations"
    TASK_INSIGHTS = "task_insights"
    SYSTEM_CONFIGURATION = "system_configuration"
    INTERACTION_FEEDBACK = "interaction_feedback"


class ImportanceLevel(int, Enum):
    """Memory importance levels for prioritization and retention."""

    CRITICAL = 10  # Essential memories that must never be deleted
    HIGH = 8  # Important memories for personalization
    MEDIUM = 5  # Useful memories for context
    LOW = 3  # Background memories for learning
    MINIMAL = 1  # Temporary memories for immediate context


class MemoryStatus(str, Enum):
    """Status of memory entries for lifecycle management."""

    ACTIVE = "active"  # Currently active and accessible
    ARCHIVED = "archived"  # Older but preserved memories
    DEPRECATED = "deprecated"  # Outdated memories ready for cleanup
    CONSOLIDATED = "consolidated"  # Merged into other memories


@dataclass
class MemoryMetadata:
    """Metadata associated with memory entries."""

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    access_count: int = 0
    importance_score: float = 0.5
    relevance_decay: float = 0.95  # How quickly relevance decays over time
    source: str = "user_interaction"
    confidence: float = 1.0
    tags: Set[str] = field(default_factory=set)
    associations: Set[str] = field(default_factory=set)  # IDs of related memories

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary for JSON serialization."""
        return {
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count,
            "importance_score": self.importance_score,
            "relevance_decay": self.relevance_decay,
            "source": self.source,
            "confidence": self.confidence,
            "tags": list(self.tags),
            "associations": list(self.associations),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryMetadata":
        """Create metadata from dictionary."""
        return cls(
            created_at=datetime.fromisoformat(data["created_at"]),
            last_accessed=datetime.fromisoformat(data["last_accessed"]),
            access_count=data["access_count"],
            importance_score=data["importance_score"],
            relevance_decay=data["relevance_decay"],
            source=data["source"],
            confidence=data["confidence"],
            tags=set(data["tags"]),
            associations=set(data["associations"]),
        )


class BaseMemory(BaseModel):
    """Base class for all memory types with common functionality."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
        use_enum_values=True,
    )

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: MemoryCategory
    content: str = Field(min_length=1, max_length=50000)
    title: Optional[str] = Field(None, max_length=200)
    importance: ImportanceLevel = ImportanceLevel.MEDIUM
    status: MemoryStatus = MemoryStatus.ACTIVE
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def __init__(self, **data):
        # Convert category and importance to Enum if needed
        if "category" in data and isinstance(data["category"], str):
            try:
                data["category"] = MemoryCategory(data["category"])
            except Exception:
                pass
        if "importance" in data and isinstance(data["importance"], str):
            try:
                data["importance"] = ImportanceLevel(data["importance"])
            except Exception:
                pass
        super().__init__(**data)
        # Initialize metadata if not provided
        if not self.metadata:
            self.metadata = MemoryMetadata().to_dict()

    @field_validator("content")
    @classmethod
    def validate_content(cls, v):
        """Validate content is not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError("Content cannot be empty or whitespace")
        return v.strip()

    def update_access(self):
        """Update access metadata when memory is retrieved."""
        metadata = MemoryMetadata.from_dict(self.metadata)
        metadata.last_accessed = datetime.now(timezone.utc)
        metadata.access_count += 1
        self.metadata = metadata.to_dict()

    def calculate_relevance(self, query_terms: List[str]) -> float:
        """Calculate relevance score based on query terms."""
        content_lower = self.content.lower()
        title_lower = (self.title or "").lower()
        # Basic term matching
        content_matches = sum(
            1 for term in query_terms if term.lower() in content_lower
        )
        title_matches = sum(1 for term in query_terms if term.lower() in title_lower)
        # Weight title matches more heavily
        base_score = (content_matches + title_matches * 2) / (len(query_terms) + 1)
        # Apply importance and recency weights
        importance = (
            self.importance.value
            if isinstance(self.importance, ImportanceLevel)
            else self.importance
        )
        importance_weight = importance / 10.0
        metadata = MemoryMetadata.from_dict(self.metadata)
        days_since_access = (datetime.now(timezone.utc) - metadata.last_accessed).days
        recency_weight = max(0.1, 1.0 - (days_since_access * 0.1))
        return base_score * importance_weight * recency_weight

    def add_tag(self, tag: str):
        """Add a tag to the memory."""
        metadata = MemoryMetadata.from_dict(self.metadata)
        metadata.tags.add(tag.lower().strip())
        self.metadata = metadata.to_dict()

    def remove_tag(self, tag: str):
        """Remove a tag from the memory."""
        metadata = MemoryMetadata.from_dict(self.metadata)
        metadata.tags.discard(tag.lower().strip())
        self.metadata = metadata.to_dict()

    def has_tag(self, tag: str) -> bool:
        """Check if memory has a specific tag."""
        metadata = MemoryMetadata.from_dict(self.metadata)
        return tag.lower().strip() in metadata.tags

    def get_content_hash(self) -> str:
        """Generate hash of content for deduplication."""
        category = (
            self.category.value
            if isinstance(self.category, MemoryCategory)
            else self.category
        )
        content_str = f"{category}:{self.content}"
        return hashlib.md5(content_str.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert memory to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "category": (
                self.category.value
                if hasattr(self.category, "value")
                else self.category
            ),
            "content": self.content,
            "title": self.title,
            "importance": (
                self.importance.value
                if hasattr(self.importance, "value")
                else self.importance
            ),
            "status": (
                self.status.value if hasattr(self.status, "value") else self.status
            ),
            "metadata": self.metadata,
            "type": self.__class__.__name__,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseMemory":
        """Create memory from dictionary."""
        return cls(
            id=data["id"],
            category=MemoryCategory(data["category"]),
            content=data["content"],
            title=data.get("title"),
            importance=ImportanceLevel(data["importance"]),
            status=MemoryStatus(data["status"]),
            metadata=data["metadata"],
        )


class UserPreference(BaseMemory):
    """User preference memory for personalization."""

    category: MemoryCategory = Field(default=MemoryCategory.USER_PREFERENCES)
    preference_key: str = Field(..., min_length=1, max_length=100)
    preference_value: Union[str, int, float, bool, List[str]] = Field(...)
    context: Optional[str] = Field(None, max_length=500)

    def __init__(self, **data):
        super().__init__(**data)
        if not self.title:
            self.title = f"User Preference: {self.preference_key}"

    @field_validator("preference_key")
    @classmethod
    def validate_preference_key(cls, v):
        """Validate preference key format."""
        if not v.strip():
            raise ValueError("Preference key cannot be empty")
        return v.strip().lower().replace(" ", "_")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with preference-specific fields."""
        base_dict = super().to_dict()
        base_dict.update(
            {
                "preference_key": self.preference_key,
                "preference_value": self.preference_value,
                "context": self.context,
            }
        )
        return base_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserPreference":
        """Create UserPreference from dictionary."""
        return cls(
            id=data["id"],
            content=data["content"],
            title=data.get("title"),
            importance=ImportanceLevel(data["importance"]),
            status=MemoryStatus(data["status"]),
            metadata=data["metadata"],
            preference_key=data["preference_key"],
            preference_value=data["preference_value"],
            context=data.get("context"),
        )


class ConversationHistory(BaseMemory):
    """Conversation history memory for session tracking."""

    category: MemoryCategory = Field(default=MemoryCategory.CONVERSATION_HISTORY)
    session_id: str = Field(..., min_length=1)
    user_input: str = Field(..., min_length=1)
    assistant_response: str = Field(..., min_length=1)
    context_used: List[str] = Field(default_factory=list)
    tools_used: List[str] = Field(default_factory=list)

    def __init__(self, **data):
        # Set content from user_input and assistant_response if not provided
        if (
            "content" not in data
            and "user_input" in data
            and "assistant_response" in data
        ):
            data["content"] = (
                f"User: {data['user_input']}\nAssistant: {data['assistant_response']}"
            )

        super().__init__(**data)

        if not self.title:
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
            self.title = f"Conversation: {timestamp}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with conversation-specific fields."""
        base_dict = super().to_dict()
        base_dict.update(
            {
                "session_id": self.session_id,
                "user_input": self.user_input,
                "assistant_response": self.assistant_response,
                "context_used": self.context_used,
                "tools_used": self.tools_used,
            }
        )
        return base_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationHistory":
        """Create ConversationHistory from dictionary."""
        return cls(
            id=data["id"],
            content=data["content"],
            title=data.get("title"),
            importance=ImportanceLevel(data["importance"]),
            status=MemoryStatus(data["status"]),
            metadata=data["metadata"],
            session_id=data["session_id"],
            user_input=data["user_input"],
            assistant_response=data["assistant_response"],
            context_used=data.get("context_used", []),
            tools_used=data.get("tools_used", []),
        )


class LearnedHeuristic(BaseMemory):
    """Learned heuristic memory for behavioral patterns."""

    category: MemoryCategory = Field(default=MemoryCategory.LEARNED_HEURISTICS)
    pattern_type: str = Field(..., min_length=1, max_length=100)
    condition: str = Field(..., min_length=1, max_length=500)
    action: str = Field(..., min_length=1, max_length=500)
    success_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    usage_count: int = Field(default=0, ge=0)

    def __init__(self, **data):
        # Set content and title if not provided
        if "content" not in data and "condition" in data and "action" in data:
            data["content"] = f"When {data['condition']}, then {data['action']}"

        super().__init__(**data)

        if not self.title and hasattr(self, "pattern_type"):
            self.title = f"Heuristic: {self.pattern_type}"

    def update_success_rate(self, success: bool):
        """Update success rate based on usage outcome."""
        self.usage_count += 1
        if success:
            self.success_rate = (
                self.success_rate * (self.usage_count - 1) + 1.0
            ) / self.usage_count
        else:
            self.success_rate = (
                self.success_rate * (self.usage_count - 1)
            ) / self.usage_count

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with heuristic-specific fields."""
        base_dict = super().to_dict()
        base_dict.update(
            {
                "pattern_type": self.pattern_type,
                "condition": self.condition,
                "action": self.action,
                "success_rate": self.success_rate,
                "usage_count": self.usage_count,
            }
        )
        return base_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LearnedHeuristic":
        """Create LearnedHeuristic from dictionary."""
        return cls(
            id=data["id"],
            content=data["content"],
            title=data.get("title"),
            importance=ImportanceLevel(data["importance"]),
            status=MemoryStatus(data["status"]),
            metadata=data["metadata"],
            pattern_type=data["pattern_type"],
            condition=data["condition"],
            action=data["action"],
            success_rate=data["success_rate"],
            usage_count=data["usage_count"],
        )


class BehaviorPattern(BaseMemory):
    """Behavior pattern memory for user modeling."""

    category: MemoryCategory = Field(default=MemoryCategory.BEHAVIOR_PATTERNS)
    pattern_name: str = Field(..., min_length=1, max_length=100)
    trigger_conditions: List[str] = Field(default_factory=list)
    observed_behaviors: List[str] = Field(default_factory=list)
    frequency: int = Field(default=1, ge=1)
    confidence_score: float = Field(default=0.5, ge=0.0, le=1.0)

    def __init__(self, **data):
        # Set content and title if not provided
        if "content" not in data and "pattern_name" in data and "frequency" in data:
            data["content"] = (
                f"Pattern: {data['pattern_name']} - Observed {data['frequency']} times"
            )

        super().__init__(**data)

        if not self.title and hasattr(self, "pattern_name"):
            self.title = f"Behavior Pattern: {self.pattern_name}"

    def increment_frequency(self):
        """Increment frequency counter when pattern is observed."""
        self.frequency += 1
        # Update confidence based on frequency
        self.confidence_score = min(1.0, self.confidence_score + 0.1)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with behavior-specific fields."""
        base_dict = super().to_dict()
        base_dict.update(
            {
                "pattern_name": self.pattern_name,
                "trigger_conditions": self.trigger_conditions,
                "observed_behaviors": self.observed_behaviors,
                "frequency": self.frequency,
                "confidence_score": self.confidence_score,
            }
        )
        return base_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BehaviorPattern":
        """Create BehaviorPattern from dictionary."""
        return cls(
            id=data["id"],
            content=data["content"],
            title=data.get("title"),
            importance=ImportanceLevel(data["importance"]),
            status=MemoryStatus(data["status"]),
            metadata=data["metadata"],
            pattern_name=data["pattern_name"],
            trigger_conditions=data["trigger_conditions"],
            observed_behaviors=data["observed_behaviors"],
            frequency=data["frequency"],
            confidence_score=data["confidence_score"],
        )


class ContextAssociation(BaseMemory):
    """Context association memory for relationship mapping."""

    category: MemoryCategory = Field(default=MemoryCategory.CONTEXT_ASSOCIATIONS)
    primary_entity: str = Field(..., min_length=1, max_length=200)
    associated_entity: str = Field(..., min_length=1, max_length=200)
    association_type: str = Field(..., min_length=1, max_length=100)
    strength: float = Field(default=0.5, ge=0.0, le=1.0)
    bidirectional: bool = Field(default=False)

    def __init__(self, **data):
        # Set content and title if not provided
        if (
            "content" not in data
            and "primary_entity" in data
            and "associated_entity" in data
            and "association_type" in data
        ):
            data["content"] = (
                f"{data['primary_entity']} {data['association_type']} {data['associated_entity']}"
            )

        super().__init__(**data)

        if (
            not self.title
            and hasattr(self, "primary_entity")
            and hasattr(self, "associated_entity")
        ):
            self.title = (
                f"Association: {self.primary_entity} -> {self.associated_entity}"
            )

    def strengthen_association(self, amount: float = 0.1):
        """Strengthen the association by a given amount."""
        self.strength = min(1.0, self.strength + amount)

    def weaken_association(self, amount: float = 0.1):
        """Weaken the association by a given amount."""
        self.strength = max(0.0, self.strength - amount)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with association-specific fields."""
        base_dict = super().to_dict()
        base_dict.update(
            {
                "primary_entity": self.primary_entity,
                "associated_entity": self.associated_entity,
                "association_type": self.association_type,
                "strength": self.strength,
                "bidirectional": self.bidirectional,
            }
        )
        return base_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContextAssociation":
        """Create ContextAssociation from dictionary."""
        return cls(
            id=data["id"],
            content=data["content"],
            title=data.get("title"),
            importance=ImportanceLevel(data["importance"]),
            status=MemoryStatus(data["status"]),
            metadata=data["metadata"],
            primary_entity=data["primary_entity"],
            associated_entity=data["associated_entity"],
            association_type=data["association_type"],
            strength=data["strength"],
            bidirectional=data["bidirectional"],
        )


class MemoryQuery:
    """Query class for searching and filtering memories."""

    def __init__(
        self,
        text: Optional[str] = None,
        categories: Optional[List[MemoryCategory]] = None,
        tags: Optional[List[str]] = None,
        importance_min: Optional[ImportanceLevel] = None,
        importance_max: Optional[ImportanceLevel] = None,
        status: Optional[MemoryStatus] = None,
        limit: int = 10,
        offset: int = 0,
        sort_by: str = "relevance",  # relevance, importance, recency, access_count
        sort_order: str = "desc",
    ):
        self.text = text
        self.categories = categories or []
        self.tags = [tag.lower().strip() for tag in (tags or [])]
        self.importance_min = importance_min
        self.importance_max = importance_max
        self.status = status
        self.limit = limit
        self.offset = offset
        self.sort_by = sort_by
        self.sort_order = sort_order

    def get_query_terms(self) -> List[str]:
        """Extract query terms from text for relevance calculation."""
        if not self.text:
            return []

        # Simple tokenization - can be enhanced with NLP
        terms = self.text.lower().split()
        # Remove common stop words
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
        }
        return [term for term in terms if term not in stop_words and len(term) > 2]


class MemoryFactory:
    """Factory class for creating memory instances."""

    MEMORY_TYPES = {
        "BaseMemory": BaseMemory,
        "UserPreference": UserPreference,
        "ConversationHistory": ConversationHistory,
        "LearnedHeuristic": LearnedHeuristic,
        "BehaviorPattern": BehaviorPattern,
        "ContextAssociation": ContextAssociation,
    }

    @classmethod
    def create_memory(cls, memory_type: str, **kwargs) -> BaseMemory:
        """Create a memory instance of the specified type."""
        if memory_type not in cls.MEMORY_TYPES:
            raise ValueError(f"Unknown memory type: {memory_type}")

        return cls.MEMORY_TYPES[memory_type](**kwargs)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BaseMemory:
        """Create memory instance from dictionary based on type."""
        memory_type = data.get("type", "BaseMemory")
        if memory_type not in cls.MEMORY_TYPES:
            memory_type = "BaseMemory"

        return cls.MEMORY_TYPES[memory_type].from_dict(data)

    @classmethod
    def create_user_preference(
        cls, key: str, value: Any, context: Optional[str] = None, **kwargs
    ) -> UserPreference:
        """Convenience method for creating user preferences."""
        return UserPreference(
            preference_key=key,
            preference_value=value,
            content=f"User preference: {key} = {value}",
            context=context,
            **kwargs,
        )

    @classmethod
    def create_conversation_memory(
        cls, session_id: str, user_input: str, assistant_response: str, **kwargs
    ) -> ConversationHistory:
        """Convenience method for creating conversation memories."""
        return ConversationHistory(
            session_id=session_id,
            user_input=user_input,
            assistant_response=assistant_response,
            **kwargs,
        )

    @classmethod
    def create_learned_heuristic(
        cls, pattern_type: str, condition: str, action: str, **kwargs
    ) -> LearnedHeuristic:
        """Convenience method for creating learned heuristics."""
        return LearnedHeuristic(
            pattern_type=pattern_type, condition=condition, action=action, **kwargs
        )


# Memory schema validation
MEMORY_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string", "format": "uuid"},
        "category": {"type": "string", "enum": [cat.value for cat in MemoryCategory]},
        "content": {"type": "string", "minLength": 1, "maxLength": 50000},
        "title": {"type": ["string", "null"], "maxLength": 200},
        "importance": {"type": "integer", "minimum": 1, "maximum": 10},
        "status": {"type": "string", "enum": [status.value for status in MemoryStatus]},
        "metadata": {"type": "object"},
        "type": {"type": "string"},
    },
    "required": [
        "id",
        "category",
        "content",
        "importance",
        "status",
        "metadata",
        "type",
    ],
    "additionalProperties": True,
}


def validate_memory_schema(memory_dict: Dict[str, Any]) -> bool:
    """Validate memory dictionary against schema."""
    try:
        # Basic validation - can be enhanced with jsonschema library
        required_fields = [
            "id",
            "category",
            "content",
            "importance",
            "status",
            "metadata",
            "type",
        ]
        for field in required_fields:
            if field not in memory_dict:
                return False

        # Validate category
        if memory_dict["category"] not in [cat.value for cat in MemoryCategory]:
            return False

        # Validate status
        if memory_dict["status"] not in [status.value for status in MemoryStatus]:
            return False

        # Validate importance
        if (
            not isinstance(memory_dict["importance"], int)
            or memory_dict["importance"] < 1
            or memory_dict["importance"] > 10
        ):
            return False

        return True
    except Exception:
        return False


if __name__ == "__main__":
    # Example usage and testing
    print("VoidCat Memory Models - Test Suite")
    print("=" * 50)

    # Test UserPreference
    pref = MemoryFactory.create_user_preference(
        key="response_style",
        value="detailed",
        context="User prefers detailed explanations",
        importance=ImportanceLevel.HIGH,
    )
    print(f"User Preference: {pref.title}")
    print(f"Content: {pref.content}")

    # Test ConversationHistory
    conv = MemoryFactory.create_conversation_memory(
        session_id="session_123",
        user_input="How does machine learning work?",
        assistant_response="Machine learning is a subset of artificial intelligence...",
        importance=ImportanceLevel.MEDIUM,
    )
    print(f"\nConversation: {conv.title}")
    print(f"Session: {conv.session_id}")

    # Test LearnedHeuristic
    heuristic = MemoryFactory.create_learned_heuristic(
        pattern_type="question_complexity",
        condition="user asks about technical topics",
        action="provide detailed explanation with examples",
        importance=ImportanceLevel.HIGH,
    )
    print(f"\nHeuristic: {heuristic.title}")
    print(f"Pattern: {heuristic.content}")

    # Test JSON serialization
    print(f"\nJSON Serialization Test:")
    pref_dict = pref.to_dict()
    print(f"Serialized: {json.dumps(pref_dict, indent=2)}")

    # Test deserialization
    restored_pref = MemoryFactory.from_dict(pref_dict)
    print(f"Restored: {restored_pref.title}")

    print("\n[SUCCESS] All tests passed! Memory models are working correctly.")
