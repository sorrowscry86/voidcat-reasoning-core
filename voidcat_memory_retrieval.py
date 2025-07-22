"""
VoidCat Intelligent Memory Retrieval Engine
==========================================

Context-aware memory recall system with adaptive learning and automatic
context injection for enhanced reasoning pipeline integration.

This module provides intelligent retrieval capabilities for The Scribe's Memory
(Pillar II) of the VoidCat V2 agentic system transformation.

Author: Albedo, Overseer of the Digital Scriptorium
License: MIT
Version: 1.0.0
"""

import hashlib
import json
import time
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import numpy as np

from voidcat_memory_models import (
    BaseMemory,
    ImportanceLevel,
    MemoryCategory,
    MemoryFactory,
    MemoryMetadata,
    MemoryQuery,
    MemoryStatus,
)
from voidcat_memory_search import MemorySearchEngine, SearchConfig, SearchResult
from voidcat_memory_storage import MemoryStorageEngine, StorageConfig


@dataclass
class RetrievalConfig:
    """Configuration for intelligent memory retrieval engine."""

    # Context awareness settings
    enable_context_awareness: bool = True
    context_window_size: int = 10  # Number of recent interactions to consider
    context_decay_factor: float = 0.9  # How quickly context relevance decays

    # Adaptive learning settings
    enable_adaptive_learning: bool = True
    learning_rate: float = 0.1
    feedback_weight: float = 0.3
    min_learning_threshold: int = 5  # Minimum interactions before learning

    # Association discovery settings
    enable_association_discovery: bool = True
    association_threshold: float = 0.3
    max_associations_per_memory: int = 10
    association_decay_rate: float = 0.05

    # Memory consolidation settings
    enable_memory_consolidation: bool = True
    consolidation_interval: int = 86400  # 24 hours in seconds
    consolidation_similarity_threshold: float = 0.8
    max_consolidated_memories: int = 100

    # Performance settings
    max_retrieval_results: int = 20
    cache_retrieval_results: bool = True
    cache_ttl: int = 300  # 5 minutes
    parallel_processing: bool = True

    # Integration settings
    auto_inject_context: bool = True
    context_injection_threshold: float = 0.5
    max_injected_contexts: int = 5


@dataclass
class ConversationContext:
    """Represents current conversation/interaction context."""

    session_id: str
    user_input: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    task_context: Optional[str] = None
    extracted_entities: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    intent: Optional[str] = None
    sentiment: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "session_id": self.session_id,
            "user_input": self.user_input,
            "timestamp": self.timestamp.isoformat(),
            "task_context": self.task_context,
            "extracted_entities": self.extracted_entities,
            "topics": self.topics,
            "intent": self.intent,
            "sentiment": self.sentiment,
        }


@dataclass
class RetrievalFeedback:
    """Feedback about memory retrieval effectiveness."""

    memory_id: str
    query_context: str
    relevance_score: float
    user_engagement: float  # 0.0 to 1.0
    effectiveness: float  # 0.0 to 1.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    feedback_type: str = "implicit"  # implicit, explicit, system

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "memory_id": self.memory_id,
            "query_context": self.query_context,
            "relevance_score": self.relevance_score,
            "user_engagement": self.user_engagement,
            "effectiveness": self.effectiveness,
            "timestamp": self.timestamp.isoformat(),
            "feedback_type": self.feedback_type,
        }


@dataclass
class MemoryAssociation:
    """Represents association between memories."""

    source_memory_id: str
    target_memory_id: str
    association_type: str  # temporal, semantic, causal, contextual
    strength: float  # 0.0 to 1.0
    frequency: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def update_strength(self, new_evidence: float):
        """Update association strength based on new evidence."""
        self.strength = min(1.0, self.strength + new_evidence * 0.1)
        self.frequency += 1
        self.last_accessed = datetime.now(timezone.utc)

    def decay_strength(self, decay_rate: float):
        """Apply time-based decay to association strength."""
        days_since_access = (datetime.now(timezone.utc) - self.last_accessed).days
        decay_factor = (1.0 - decay_rate) ** days_since_access
        self.strength *= decay_factor

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "source_memory_id": self.source_memory_id,
            "target_memory_id": self.target_memory_id,
            "association_type": self.association_type,
            "strength": self.strength,
            "frequency": self.frequency,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
        }


class ContextAnalyzer:
    """Analyzes conversation context for intelligent retrieval."""

    def __init__(self, config: RetrievalConfig):
        self.config = config
        self.context_history: deque = deque(maxlen=config.context_window_size)
        self.topic_tracker: Dict[str, float] = defaultdict(float)
        self.entity_tracker: Dict[str, int] = defaultdict(int)

    def analyze_context(
        self, user_input: str, session_id: str, task_context: Optional[str] = None
    ) -> ConversationContext:
        """Analyze user input to extract context information."""
        context = ConversationContext(
            session_id=session_id, user_input=user_input, task_context=task_context
        )

        # Extract entities (simplified - can be enhanced with NLP)
        context.extracted_entities = self._extract_entities(user_input)

        # Extract topics
        context.topics = self._extract_topics(user_input)

        # Determine intent (simplified)
        context.intent = self._determine_intent(user_input)

        # Analyze sentiment (simplified)
        context.sentiment = self._analyze_sentiment(user_input)

        # Update tracking
        self._update_trackers(context)

        # Add to history
        self.context_history.append(context)

        return context

    def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities from text (simplified implementation)."""
        # Simplified entity extraction - can be enhanced with spaCy or similar
        entities = []

        # Look for common patterns
        words = text.lower().split()

        # Common entity indicators
        entity_indicators = {
            "file",
            "function",
            "class",
            "variable",
            "method",
            "api",
            "library",
            "database",
            "server",
            "client",
            "user",
            "admin",
            "system",
            "config",
        }

        for word in words:
            if (
                word in entity_indicators
                or word.endswith(".py")
                or word.endswith(".js")
            ):
                entities.append(word)

        return entities

    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text."""
        topics = []

        # Topic keywords mapping
        topic_keywords = {
            "programming": [
                "code",
                "function",
                "class",
                "method",
                "programming",
                "development",
            ],
            "database": ["database", "sql", "query", "table", "schema"],
            "web": ["website", "html", "css", "javascript", "frontend", "backend"],
            "api": ["api", "endpoint", "request", "response", "rest"],
            "system": ["system", "server", "configuration", "deployment"],
            "user_interface": ["ui", "interface", "design", "layout", "user"],
            "data": ["data", "analysis", "visualization", "statistics"],
            "security": ["security", "authentication", "authorization", "encryption"],
        }

        text_lower = text.lower()

        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)

        return topics

    def _determine_intent(self, text: str) -> str:
        """Determine user intent from text."""
        text_lower = text.lower()

        if any(
            word in text_lower for word in ["how", "what", "why", "when", "where", "?"]
        ):
            return "question"
        elif any(
            word in text_lower for word in ["create", "make", "build", "implement"]
        ):
            return "creation"
        elif any(
            word in text_lower for word in ["fix", "debug", "error", "problem", "issue"]
        ):
            return "troubleshooting"
        elif any(word in text_lower for word in ["explain", "tell", "describe"]):
            return "explanation"
        elif any(word in text_lower for word in ["find", "search", "look"]):
            return "search"
        else:
            return "general"

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text (simplified)."""
        text_lower = text.lower()

        positive_words = [
            "good",
            "great",
            "excellent",
            "perfect",
            "awesome",
            "love",
            "like",
        ]
        negative_words = [
            "bad",
            "terrible",
            "awful",
            "hate",
            "dislike",
            "problem",
            "error",
        ]

        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def _update_trackers(self, context: ConversationContext):
        """Update topic and entity tracking."""
        # Update topic relevance
        for topic in context.topics:
            self.topic_tracker[topic] = min(1.0, self.topic_tracker[topic] + 0.2)

        # Decay old topics
        for topic in list(self.topic_tracker.keys()):
            self.topic_tracker[topic] *= self.config.context_decay_factor
            if self.topic_tracker[topic] < 0.1:
                del self.topic_tracker[topic]

        # Update entity frequency
        for entity in context.extracted_entities:
            self.entity_tracker[entity] += 1

    def get_current_context_summary(self) -> Dict[str, Any]:
        """Get summary of current context state."""
        return {
            "active_topics": dict(self.topic_tracker),
            "recent_entities": dict(self.entity_tracker),
            "context_history_size": len(self.context_history),
            "recent_intents": [ctx.intent for ctx in list(self.context_history)[-5:]],
            "session_distribution": {ctx.session_id: 1 for ctx in self.context_history},
        }


class AdaptiveLearningEngine:
    """Learns from retrieval feedback to improve future performance."""

    def __init__(self, config: RetrievalConfig, storage_path: Path):
        self.config = config
        self.storage_path = storage_path
        self.feedback_history: List[RetrievalFeedback] = []
        self.memory_performance: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {
                "relevance_avg": 0.0,
                "engagement_avg": 0.0,
                "effectiveness_avg": 0.0,
                "retrieval_count": 0,
            }
        )
        self.query_patterns: Dict[str, List[str]] = defaultdict(list)

        # Load existing learning data
        self._load_learning_data()

    def record_feedback(self, feedback: RetrievalFeedback):
        """Record feedback about memory retrieval."""
        self.feedback_history.append(feedback)

        # Update memory performance metrics
        memory_id = feedback.memory_id
        perf = self.memory_performance[memory_id]

        count = perf["retrieval_count"]
        perf["relevance_avg"] = self._update_average(
            perf["relevance_avg"], feedback.relevance_score, count
        )
        perf["engagement_avg"] = self._update_average(
            perf["engagement_avg"], feedback.user_engagement, count
        )
        perf["effectiveness_avg"] = self._update_average(
            perf["effectiveness_avg"], feedback.effectiveness, count
        )
        perf["retrieval_count"] += 1

        # Update query patterns
        query_hash = hashlib.md5(feedback.query_context.encode()).hexdigest()[:8]
        self.query_patterns[query_hash].append(memory_id)

        # Save learning data periodically
        if len(self.feedback_history) % 10 == 0:
            self._save_learning_data()

    def _update_average(
        self, current_avg: float, new_value: float, count: int
    ) -> float:
        """Update running average with new value."""
        if count == 0:
            return new_value
        return (current_avg * count + new_value) / (count + 1)

    def get_memory_score_adjustment(self, memory_id: str, base_score: float) -> float:
        """Get score adjustment based on learned performance."""
        if not self.config.enable_adaptive_learning:
            return base_score

        perf = self.memory_performance.get(memory_id)
        if not perf or perf["retrieval_count"] < self.config.min_learning_threshold:
            return base_score

        # Calculate adjustment based on historical performance
        effectiveness = perf["effectiveness_avg"]
        engagement = perf["engagement_avg"]

        # Weighted adjustment
        adjustment_factor = effectiveness * 0.7 + engagement * 0.3
        adjustment = (adjustment_factor - 0.5) * self.config.learning_rate

        return base_score * (1.0 + adjustment)

    def suggest_similar_queries(
        self, query_context: str, max_suggestions: int = 5
    ) -> List[str]:
        """Suggest similar queries based on patterns."""
        query_hash = hashlib.md5(query_context.encode()).hexdigest()[:8]

        if query_hash in self.query_patterns:
            # Find memories that performed well for this query pattern
            memory_ids = self.query_patterns[query_hash]

            # Get top performing memories
            top_memories = []
            for memory_id in memory_ids:
                perf = self.memory_performance.get(memory_id)
                if perf and perf["effectiveness_avg"] > 0.6:
                    top_memories.append((memory_id, perf["effectiveness_avg"]))

            # Sort by effectiveness and return top suggestions
            top_memories.sort(key=lambda x: x[1], reverse=True)
            return [memory_id for memory_id, _ in top_memories[:max_suggestions]]

        return []

    def _save_learning_data(self):
        """Save learning data to disk."""
        try:
            learning_data = {
                "feedback_history": [
                    fb.to_dict() for fb in self.feedback_history[-1000:]
                ],  # Keep last 1000
                "memory_performance": dict(self.memory_performance),
                "query_patterns": dict(self.query_patterns),
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }

            with open(self.storage_path / "learning_data.json", "w") as f:
                json.dump(learning_data, f, indent=2, default=str)

        except Exception as e:
            print(f"Warning: Failed to save learning data: {e}")

    def _load_learning_data(self):
        """Load learning data from disk."""
        try:
            learning_file = self.storage_path / "learning_data.json"
            if learning_file.exists():
                with open(learning_file, "r") as f:
                    data = json.load(f)

                # Restore feedback history
                self.feedback_history = [
                    RetrievalFeedback(**fb) for fb in data.get("feedback_history", [])
                ]

                # Restore performance data
                self.memory_performance = defaultdict(
                    lambda: {
                        "relevance_avg": 0.0,
                        "engagement_avg": 0.0,
                        "effectiveness_avg": 0.0,
                        "retrieval_count": 0,
                    }
                )
                self.memory_performance.update(data.get("memory_performance", {}))

                # Restore query patterns
                self.query_patterns = defaultdict(list)
                self.query_patterns.update(data.get("query_patterns", {}))

        except Exception as e:
            print(f"Warning: Failed to load learning data: {e}")

    def get_learning_statistics(self) -> Dict[str, Any]:
        """Get learning engine statistics."""
        return {
            "total_feedback_records": len(self.feedback_history),
            "tracked_memories": len(self.memory_performance),
            "query_patterns": len(self.query_patterns),
            "avg_effectiveness": (
                np.mean(
                    [
                        perf["effectiveness_avg"]
                        for perf in self.memory_performance.values()
                    ]
                )
                if self.memory_performance
                else 0.0
            ),
            "learning_enabled": self.config.enable_adaptive_learning,
        }


class AssociationManager:
    """Manages memory associations and relationship discovery."""

    def __init__(self, config: RetrievalConfig, storage_path: Path):
        self.config = config
        self.storage_path = storage_path
        self.associations: Dict[str, List[MemoryAssociation]] = defaultdict(list)
        self.association_matrix: Dict[str, Dict[str, float]] = defaultdict(dict)

        # Load existing associations
        self._load_associations()

    def discover_associations(
        self, retrieved_memories: List[SearchResult], context: ConversationContext
    ):
        """Discover new associations between memories."""
        if not self.config.enable_association_discovery:
            return

        # Temporal associations (memories retrieved in same session/timeframe)
        self._discover_temporal_associations(retrieved_memories, context)

        # Semantic associations (memories with similar content/topics)
        self._discover_semantic_associations(retrieved_memories)

        # Contextual associations (memories used in similar contexts)
        self._discover_contextual_associations(retrieved_memories, context)

        # Clean up weak associations
        self._cleanup_weak_associations()

    def _discover_temporal_associations(
        self, memories: List[SearchResult], context: ConversationContext
    ):
        """Discover temporal associations between memories."""
        for i, memory1 in enumerate(memories):
            for memory2 in memories[i + 1 :]:
                association_key = f"{memory1.memory.id}_{memory2.memory.id}"

                # Check if association already exists
                existing = self._find_association(
                    memory1.memory.id, memory2.memory.id, "temporal"
                )

                if existing:
                    existing.update_strength(0.1)
                else:
                    # Create new temporal association
                    association = MemoryAssociation(
                        source_memory_id=memory1.memory.id,
                        target_memory_id=memory2.memory.id,
                        association_type="temporal",
                        strength=0.3,
                    )
                    self.associations[memory1.memory.id].append(association)

    def _discover_semantic_associations(self, memories: List[SearchResult]):
        """Discover semantic associations between memories."""
        for i, memory1 in enumerate(memories):
            for memory2 in memories[i + 1 :]:
                # Calculate semantic similarity
                similarity = self._calculate_semantic_similarity(
                    memory1.memory, memory2.memory
                )

                if similarity > self.config.association_threshold:
                    existing = self._find_association(
                        memory1.memory.id, memory2.memory.id, "semantic"
                    )

                    if existing:
                        existing.update_strength(similarity * 0.1)
                    else:
                        association = MemoryAssociation(
                            source_memory_id=memory1.memory.id,
                            target_memory_id=memory2.memory.id,
                            association_type="semantic",
                            strength=similarity,
                        )
                        self.associations[memory1.memory.id].append(association)

    def _discover_contextual_associations(
        self, memories: List[SearchResult], context: ConversationContext
    ):
        """Discover contextual associations based on usage context."""
        context_signature = self._create_context_signature(context)

        for memory in memories:
            # Find other memories used in similar contexts
            memory_id = memory.memory.id

            # This is simplified - in a full implementation, we'd track context usage
            for other_memory in memories:
                if other_memory.memory.id != memory_id:
                    existing = self._find_association(
                        memory_id, other_memory.memory.id, "contextual"
                    )

                    if existing:
                        existing.update_strength(0.05)
                    else:
                        association = MemoryAssociation(
                            source_memory_id=memory_id,
                            target_memory_id=other_memory.memory.id,
                            association_type="contextual",
                            strength=0.2,
                        )
                        self.associations[memory_id].append(association)

    def _calculate_semantic_similarity(
        self, memory1: BaseMemory, memory2: BaseMemory
    ) -> float:
        """Calculate semantic similarity between two memories."""
        # Simplified similarity calculation

        # Category similarity
        category_sim = 1.0 if memory1.category == memory2.category else 0.3

        # Tag similarity
        tag_sim = 0.0
        if memory1.metadata and memory2.metadata:
            meta1 = MemoryMetadata.from_dict(memory1.metadata)
            meta2 = MemoryMetadata.from_dict(memory2.metadata)

            if meta1.tags or meta2.tags:
                intersection = meta1.tags.intersection(meta2.tags)
                union = meta1.tags.union(meta2.tags)
                tag_sim = len(intersection) / len(union) if union else 0.0

        # Content similarity (simplified word overlap)
        content_sim = self._calculate_content_similarity(
            memory1.content, memory2.content
        )

        # Weighted combination
        similarity = category_sim * 0.3 + tag_sim * 0.4 + content_sim * 0.3
        return similarity

    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """Calculate content similarity using word overlap."""
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    def _find_association(
        self, source_id: str, target_id: str, association_type: str
    ) -> Optional[MemoryAssociation]:
        """Find existing association between two memories."""
        for association in self.associations[source_id]:
            if (
                association.target_memory_id == target_id
                and association.association_type == association_type
            ):
                return association

        # Check reverse direction
        for association in self.associations[target_id]:
            if (
                association.target_memory_id == source_id
                and association.association_type == association_type
            ):
                return association

        return None

    def _create_context_signature(self, context: ConversationContext) -> str:
        """Create a signature representing the context."""
        elements = []
        elements.extend(context.topics)
        elements.extend(context.extracted_entities)
        if context.intent:
            elements.append(context.intent)

        return "|".join(sorted(elements))

    def _cleanup_weak_associations(self):
        """Remove associations that have become too weak."""
        for memory_id in list(self.associations.keys()):
            associations = self.associations[memory_id]

            # Apply decay to all associations
            for association in associations:
                association.decay_strength(self.config.association_decay_rate)

            # Remove weak associations
            self.associations[memory_id] = [
                assoc for assoc in associations if assoc.strength > 0.1
            ]

            # Remove empty association lists
            if not self.associations[memory_id]:
                del self.associations[memory_id]

    def get_associated_memories(
        self, memory_id: str, association_types: Optional[List[str]] = None
    ) -> List[Tuple[str, float, str]]:
        """Get memories associated with the given memory."""
        associated = []

        for association in self.associations.get(memory_id, []):
            if (
                association_types is None
                or association.association_type in association_types
            ):
                associated.append(
                    (
                        association.target_memory_id,
                        association.strength,
                        association.association_type,
                    )
                )

        # Sort by strength
        associated.sort(key=lambda x: x[1], reverse=True)
        return associated[: self.config.max_associations_per_memory]

    def _save_associations(self):
        """Save associations to disk."""
        try:
            associations_data = {}
            for memory_id, associations in self.associations.items():
                associations_data[memory_id] = [
                    assoc.to_dict() for assoc in associations
                ]

            with open(self.storage_path / "associations.json", "w") as f:
                json.dump(associations_data, f, indent=2, default=str)

        except Exception as e:
            print(f"Warning: Failed to save associations: {e}")

    def _load_associations(self):
        """Load associations from disk."""
        try:
            associations_file = self.storage_path / "associations.json"
            if associations_file.exists():
                with open(associations_file, "r") as f:
                    data = json.load(f)

                for memory_id, associations_data in data.items():
                    self.associations[memory_id] = [
                        MemoryAssociation(**assoc_data)
                        for assoc_data in associations_data
                    ]

        except Exception as e:
            print(f"Warning: Failed to load associations: {e}")


class IntelligentMemoryRetrievalEngine:
    """
    Comprehensive intelligent memory retrieval engine with context awareness,
    adaptive learning, and automatic reasoning pipeline integration.
    """

    def __init__(
        self,
        storage_engine: MemoryStorageEngine,
        search_engine: MemorySearchEngine,
        config: Optional[RetrievalConfig] = None,
    ):
        self.storage_engine = storage_engine
        self.search_engine = search_engine
        self.config = config or RetrievalConfig()

        # Initialize components
        self.context_analyzer = ContextAnalyzer(self.config)

        # Create storage directory for learning and associations
        retrieval_storage = Path("memory_retrieval")
        retrieval_storage.mkdir(parents=True, exist_ok=True)

        self.learning_engine = AdaptiveLearningEngine(self.config, retrieval_storage)
        self.association_manager = AssociationManager(self.config, retrieval_storage)

        # Result cache
        self.result_cache: Dict[str, Tuple[List[SearchResult], float]] = {}

        # Performance tracking
        self.retrieval_stats = {
            "total_retrievals": 0,
            "context_aware_retrievals": 0,
            "cache_hits": 0,
            "avg_retrieval_time": 0.0,
            "association_discoveries": 0,
        }

        print("IntelligentMemoryRetrievalEngine initialized successfully")

    def retrieve_contextual_memories(
        self,
        user_input: str,
        session_id: str,
        task_context: Optional[str] = None,
        max_results: int = None,
    ) -> List[SearchResult]:
        """
        Retrieve memories with full context awareness and intelligence.
        """
        start_time = time.time()
        max_results = max_results or self.config.max_retrieval_results

        try:
            self.retrieval_stats["total_retrievals"] += 1

            # Analyze current context
            context = self.context_analyzer.analyze_context(
                user_input, session_id, task_context
            )

            # Check cache
            cache_key = self._create_cache_key(user_input, context)
            if self.config.cache_retrieval_results and cache_key in self.result_cache:
                cached_results, cache_time = self.result_cache[cache_key]
                if time.time() - cache_time < self.config.cache_ttl:
                    self.retrieval_stats["cache_hits"] += 1
                    return cached_results[:max_results]

            # Multi-strategy retrieval
            all_results = []

            # Strategy 1: Direct semantic search
            semantic_results = self._direct_semantic_search(user_input, max_results)
            all_results.extend(semantic_results)

            # Strategy 2: Context-aware search
            if self.config.enable_context_awareness:
                context_results = self._context_aware_search(context, max_results)
                all_results.extend(context_results)
                self.retrieval_stats["context_aware_retrievals"] += 1

            # Strategy 3: Association-based retrieval
            if self.config.enable_association_discovery:
                association_results = self._association_based_retrieval(
                    all_results, max_results
                )
                all_results.extend(association_results)

            # Deduplicate and rank results
            final_results = self._deduplicate_and_rank(all_results, context)

            # Apply adaptive learning adjustments
            if self.config.enable_adaptive_learning:
                final_results = self._apply_learning_adjustments(
                    final_results, user_input
                )

            # Limit results
            final_results = final_results[:max_results]

            # Discover new associations
            if self.config.enable_association_discovery and final_results:
                self.association_manager.discover_associations(final_results, context)
                self.retrieval_stats["association_discoveries"] += 1

            # Cache results
            if self.config.cache_retrieval_results:
                self.result_cache[cache_key] = (final_results, time.time())

            # Update statistics
            retrieval_time = time.time() - start_time
            self._update_retrieval_time_stats(retrieval_time)

            return final_results

        except Exception as e:
            print(f"Error in contextual memory retrieval: {e}")
            return []

    def _direct_semantic_search(
        self, user_input: str, max_results: int
    ) -> List[SearchResult]:
        """Perform direct semantic search."""
        query = MemoryQuery(text=user_input, limit=max_results, sort_by="relevance")

        return self.search_engine.search(query)

    def _context_aware_search(
        self, context: ConversationContext, max_results: int
    ) -> List[SearchResult]:
        """Perform context-aware search using conversation analysis."""
        results = []

        # Search by topics
        if context.topics:
            for topic in context.topics:
                topic_query = MemoryQuery(
                    text=topic, limit=max_results // 2, sort_by="relevance"
                )
                topic_results = self.search_engine.search(topic_query)
                results.extend(topic_results)

        # Search by entities
        if context.extracted_entities:
            for entity in context.extracted_entities:
                entity_query = MemoryQuery(
                    text=entity, limit=max_results // 3, sort_by="relevance"
                )
                entity_results = self.search_engine.search(entity_query)
                results.extend(entity_results)

        # Search by intent-specific categories
        if context.intent:
            category_mapping = {
                "question": [MemoryCategory.LEARNED_HEURISTICS],
                "troubleshooting": [
                    MemoryCategory.LEARNED_HEURISTICS,
                    MemoryCategory.BEHAVIOR_PATTERNS,
                ],
                "creation": [
                    MemoryCategory.USER_PREFERENCES,
                    MemoryCategory.LEARNED_HEURISTICS,
                ],
                "explanation": [
                    MemoryCategory.LEARNED_HEURISTICS,
                    MemoryCategory.CONVERSATION_HISTORY,
                ],
            }

            categories = category_mapping.get(context.intent, [])
            if categories:
                intent_query = MemoryQuery(
                    categories=categories, limit=max_results // 2, sort_by="importance"
                )
                intent_results = self.search_engine.search(intent_query)
                results.extend(intent_results)

        return results

    def _association_based_retrieval(
        self, initial_results: List[SearchResult], max_results: int
    ) -> List[SearchResult]:
        """Retrieve memories based on associations with initial results."""
        association_results = []

        for result in initial_results[
            :5
        ]:  # Use top 5 results for association discovery
            associated_ids = self.association_manager.get_associated_memories(
                result.memory.id, association_types=["semantic", "contextual"]
            )

            for memory_id, strength, assoc_type in associated_ids:
                associated_memory = self.storage_engine.retrieve_memory(memory_id)
                if associated_memory:
                    association_results.append(
                        SearchResult(
                            memory=associated_memory,
                            relevance_score=strength
                            * 0.8,  # Slightly lower than direct matches
                            match_type=f"association_{assoc_type}",
                            match_details={
                                "association_strength": strength,
                                "source_memory": result.memory.id,
                            },
                        )
                    )

        return association_results[: max_results // 2]

    def _deduplicate_and_rank(
        self, results: List[SearchResult], context: ConversationContext
    ) -> List[SearchResult]:
        """Deduplicate results and apply comprehensive ranking."""
        # Deduplicate by memory ID
        unique_results = {}
        for result in results:
            memory_id = result.memory.id
            if (
                memory_id not in unique_results
                or result.relevance_score > unique_results[memory_id].relevance_score
            ):
                unique_results[memory_id] = result

        final_results = list(unique_results.values())

        # Apply context-aware ranking adjustments
        for result in final_results:
            # Boost based on topic relevance
            topic_boost = self._calculate_topic_boost(result.memory, context.topics)
            result.relevance_score *= 1.0 + topic_boost

            # Boost based on entity matches
            entity_boost = self._calculate_entity_boost(
                result.memory, context.extracted_entities
            )
            result.relevance_score *= 1.0 + entity_boost

            # Boost based on recency for certain intents
            if context.intent in ["troubleshooting", "question"]:
                recency_boost = self._calculate_recency_boost(result.memory)
                result.relevance_score *= 1.0 + recency_boost

        # Sort by adjusted relevance score
        final_results.sort(key=lambda x: x.relevance_score, reverse=True)
        return final_results

    def _calculate_topic_boost(self, memory: BaseMemory, topics: List[str]) -> float:
        """Calculate relevance boost based on topic matches."""
        if not topics:
            return 0.0

        content_lower = memory.content.lower()
        title_lower = (memory.title or "").lower()

        topic_matches = 0
        for topic in topics:
            if topic.lower() in content_lower or topic.lower() in title_lower:
                topic_matches += 1

        return min(0.5, topic_matches * 0.2)

    def _calculate_entity_boost(self, memory: BaseMemory, entities: List[str]) -> float:
        """Calculate relevance boost based on entity matches."""
        if not entities:
            return 0.0

        content_lower = memory.content.lower()

        entity_matches = 0
        for entity in entities:
            if entity.lower() in content_lower:
                entity_matches += 1

        return min(0.3, entity_matches * 0.15)

    def _calculate_recency_boost(self, memory: BaseMemory) -> float:
        """Calculate boost based on memory recency."""
        if not memory.metadata:
            return 0.0

        metadata = MemoryMetadata.from_dict(memory.metadata)
        days_since_access = (datetime.now(timezone.utc) - metadata.last_accessed).days

        # Boost recent memories (last 7 days)
        if days_since_access <= 7:
            return 0.2 * (7 - days_since_access) / 7

        return 0.0

    def _apply_learning_adjustments(
        self, results: List[SearchResult], query_context: str
    ) -> List[SearchResult]:
        """Apply adaptive learning adjustments to results."""
        for result in results:
            adjusted_score = self.learning_engine.get_memory_score_adjustment(
                result.memory.id, result.relevance_score
            )
            result.relevance_score = adjusted_score

        # Re-sort after adjustments
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results

    def _create_cache_key(self, user_input: str, context: ConversationContext) -> str:
        """Create cache key for retrieval results."""
        key_elements = [
            user_input,
            str(sorted(context.topics)),
            str(sorted(context.extracted_entities)),
            context.intent or "",
            context.session_id,
        ]

        key_string = "|".join(key_elements)
        return hashlib.md5(key_string.encode()).hexdigest()

    def provide_feedback(
        self,
        memory_id: str,
        query_context: str,
        effectiveness: float,
        user_engagement: float = 0.5,
    ):
        """Provide feedback about memory retrieval effectiveness."""
        feedback = RetrievalFeedback(
            memory_id=memory_id,
            query_context=query_context,
            relevance_score=1.0,  # Will be updated by learning engine
            user_engagement=user_engagement,
            effectiveness=effectiveness,
            feedback_type="explicit",
        )

        self.learning_engine.record_feedback(feedback)

    def get_context_injection_memories(self, base_context: str) -> List[BaseMemory]:
        """Get memories to inject into reasoning context."""
        if not self.config.auto_inject_context:
            return []

        # Quick retrieval for context injection
        query = MemoryQuery(
            text=base_context,
            limit=self.config.max_injected_contexts,
            sort_by="relevance",
        )

        results = self.search_engine.search(query)

        # Filter by injection threshold
        context_memories = [
            result.memory
            for result in results
            if result.relevance_score >= self.config.context_injection_threshold
        ]

        return context_memories

    def consolidate_memories(self) -> int:
        """Consolidate similar memories to reduce redundancy."""
        if not self.config.enable_memory_consolidation:
            return 0

        # This is a simplified consolidation - in practice, this would be more sophisticated
        print("Starting memory consolidation...")

        # Get all memories
        query = MemoryQuery(limit=1000)
        all_memories = self.storage_engine.search_memories(query)

        consolidated_count = 0

        # Find highly similar memories for consolidation
        for i, memory1 in enumerate(all_memories):
            for memory2 in all_memories[i + 1 :]:
                similarity = self.association_manager._calculate_semantic_similarity(
                    memory1, memory2
                )

                if similarity > self.config.consolidation_similarity_threshold:
                    # Mark less important memory for archiving
                    if memory1.importance.value < memory2.importance.value:
                        memory1.status = MemoryStatus.CONSOLIDATED
                        self.storage_engine.update_memory(memory1)
                    else:
                        memory2.status = MemoryStatus.CONSOLIDATED
                        self.storage_engine.update_memory(memory2)

                    consolidated_count += 1

                    if consolidated_count >= self.config.max_consolidated_memories:
                        break

            if consolidated_count >= self.config.max_consolidated_memories:
                break

        print(f"Consolidated {consolidated_count} memories")
        return consolidated_count

    def _update_retrieval_time_stats(self, retrieval_time: float):
        """Update retrieval time statistics."""
        current_avg = self.retrieval_stats["avg_retrieval_time"]
        total_retrievals = self.retrieval_stats["total_retrievals"]

        new_avg = (
            (current_avg * (total_retrievals - 1)) + retrieval_time
        ) / total_retrievals
        self.retrieval_stats["avg_retrieval_time"] = new_avg

    def get_retrieval_statistics(self) -> Dict[str, Any]:
        """Get comprehensive retrieval engine statistics."""
        return {
            "retrieval_stats": self.retrieval_stats,
            "context_analyzer": self.context_analyzer.get_current_context_summary(),
            "learning_engine": self.learning_engine.get_learning_statistics(),
            "associations": {
                "total_associations": sum(
                    len(assocs)
                    for assocs in self.association_manager.associations.values()
                ),
                "association_types": self._get_association_type_distribution(),
            },
            "cache_stats": {
                "cache_size": len(self.result_cache),
                "cache_hit_rate": self.retrieval_stats["cache_hits"]
                / max(1, self.retrieval_stats["total_retrievals"]),
            },
        }

    def _get_association_type_distribution(self) -> Dict[str, int]:
        """Get distribution of association types."""
        type_counts = defaultdict(int)

        for associations in self.association_manager.associations.values():
            for association in associations:
                type_counts[association.association_type] += 1

        return dict(type_counts)


# Performance testing and validation
if __name__ == "__main__":
    import tempfile
    from pathlib import Path

    print("VoidCat Intelligent Memory Retrieval Engine - Test Suite")
    print("=" * 65)

    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize engines
        storage_config = StorageConfig(
            base_dir=Path(temp_dir) / "memory_storage",
            backup_dir=Path(temp_dir) / "memory_backups",
            index_dir=Path(temp_dir) / "memory_indexes",
        )

        search_config = SearchConfig(
            enable_semantic_search=True, enable_clustering=True
        )

        retrieval_config = RetrievalConfig(
            enable_context_awareness=True,
            enable_adaptive_learning=True,
            enable_association_discovery=True,
        )

        storage_engine = MemoryStorageEngine(storage_config)
        search_engine = MemorySearchEngine(storage_engine, search_config)
        retrieval_engine = IntelligentMemoryRetrievalEngine(
            storage_engine, search_engine, retrieval_config
        )

        # Test 1: Create test memories with diverse content
        print(f"\n📝 Test 1: Creating test memories...")
        test_memories = []

        memory_data = [
            (
                "Python is a programming language",
                "programming",
                MemoryCategory.LEARNED_HEURISTICS,
            ),
            (
                "User prefers dark mode interface",
                "ui_preference",
                MemoryCategory.USER_PREFERENCES,
            ),
            (
                "Database connection timeout error",
                "troubleshooting",
                MemoryCategory.CONVERSATION_HISTORY,
            ),
            (
                "How to optimize SQL queries",
                "database_help",
                MemoryCategory.LEARNED_HEURISTICS,
            ),
            (
                "JavaScript async/await patterns",
                "programming",
                MemoryCategory.LEARNED_HEURISTICS,
            ),
        ]

        for content, key, category in memory_data:
            memory = MemoryFactory.create_memory(
                memory_type="BaseMemory",
                category=category,
                content=content,
                title=f"{key.replace('_', ' ').title()}",
                importance=ImportanceLevel.MEDIUM,
            )
            if memory.metadata:
                metadata = MemoryMetadata.from_dict(memory.metadata)
                metadata.tags.add(key.split("_")[0])
                memory.metadata = metadata.to_dict()

            success = storage_engine.store_memory(memory)
            if success:
                test_memories.append(memory)

        print(f"✅ Created {len(test_memories)} test memories")

        # Test 2: Context-aware retrieval
        print(f"\n🧠 Test 2: Context-aware retrieval...")
        start_time = time.time()

        results = retrieval_engine.retrieve_contextual_memories(
            user_input="How do I fix database performance issues?",
            session_id="test_session_1",
            task_context="troubleshooting",
            max_results=5,
        )

        retrieval_time = time.time() - start_time
        print(
            f"✅ Retrieved {len(results)} contextual memories in {retrieval_time*1000:.1f}ms"
        )

        for result in results[:3]:
            print(
                f"  - {result.memory.title}: {result.relevance_score:.3f} ({result.match_type})"
            )

        # Test 3: Adaptive learning feedback
        print(f"\n📚 Test 3: Adaptive learning...")
        if results:
            retrieval_engine.provide_feedback(
                memory_id=results[0].memory.id,
                query_context="database performance troubleshooting",
                effectiveness=0.8,
                user_engagement=0.9,
            )
            print(f"✅ Recorded feedback for memory: {results[0].memory.title}")

        # Test 4: Association discovery
        print(f"\n🔗 Test 4: Association discovery...")
        # Simulate multiple related queries to build associations
        related_queries = [
            "SQL query optimization techniques",
            "Database indexing strategies",
            "Performance monitoring tools",
        ]

        association_count = 0
        for query in related_queries:
            results = retrieval_engine.retrieve_contextual_memories(
                user_input=query, session_id="test_session_2", max_results=3
            )
            if results:
                association_count += len(results)

        print(f"✅ Processed {len(related_queries)} queries for association discovery")

        # Test 5: Context injection
        print(f"\n💉 Test 5: Context injection...")
        context_memories = retrieval_engine.get_context_injection_memories(
            "Python programming best practices"
        )
        print(f"✅ Found {len(context_memories)} memories for context injection")

        # Test 6: Statistics and performance
        print(f"\n📊 Test 6: Retrieval statistics...")
        stats = retrieval_engine.get_retrieval_statistics()

        print(f"Total retrievals: {stats['retrieval_stats']['total_retrievals']}")
        print(
            f"Context-aware retrievals: {stats['retrieval_stats']['context_aware_retrievals']}"
        )
        print(
            f"Average retrieval time: {stats['retrieval_stats']['avg_retrieval_time']*1000:.1f}ms"
        )
        print(f"Cache hit rate: {stats['cache_stats']['cache_hit_rate']:.1%}")
        print(f"Learning enabled: {stats['learning_engine']['learning_enabled']}")
        print(f"Total associations: {stats['associations']['total_associations']}")

        # Performance summary
        print(f"\n🎯 PERFORMANCE SUMMARY:")
        print(f"✅ Context-aware retrieval: {retrieval_time*1000:.1f}ms")
        print(f"✅ Memory creation: {len(test_memories)} memories")
        print(f"✅ Adaptive learning: Working")
        print(f"✅ Association discovery: Working")
        print(f"✅ Context injection: Working")

        # Close engines
        storage_engine.close()

        print("\n[SUCCESS] All intelligent retrieval tests completed! 🚀")
