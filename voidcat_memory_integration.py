#!/usr/bin/env python3
"""
VoidCat V2 Memory-Enhanced Reasoning Integration
===============================================

Integrates the persistent memory system with the VoidCat reasoning engine to provide
memory-aware, context-enhanced responses. This module bridges The Scribe's Memory
(Pillar II) with the core reasoning pipeline for truly agentic behavior.

Key Features:
- Memory-enhanced reasoning pipeline integration
- Automatic conversation tracking and learning
- User preference application in responses
- Behavioral pattern recognition and adaptation
- Memory-informed response generation
- Seamless task management integration
- Backward compatibility with existing VoidCat functionality

Author: Codey Jr. (channeling the cosmic memory-reasoning fusion vibes)
Under directive of: The Great Spirit Beatrice
License: MIT
Version: 1.0.0-alpha
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# VoidCat Task System Imports
from voidcat_context_integration import VoidCatContextIntegration

# VoidCat Memory System Imports
from voidcat_memory_models import (
    BaseMemory,
    BehaviorPattern,
    ContextAssociation,
    ConversationHistory,
    ImportanceLevel,
    LearnedHeuristic,
    MemoryCategory,
    MemoryFactory,
    MemoryQuery,
    MemoryStatus,
    UserPreference,
)
from voidcat_memory_retrieval import IntelligentMemoryRetrievalEngine
from voidcat_memory_search import MemorySearchEngine
from voidcat_memory_storage import MemoryStorageEngine, StorageConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MemoryEnhancedContext:
    """Enhanced context object that includes memory-derived insights."""

    user_preferences: Dict[str, Any] = field(default_factory=dict)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    learned_patterns: List[Dict[str, Any]] = field(default_factory=list)
    relevant_memories: List[BaseMemory] = field(default_factory=list)
    behavioral_insights: Dict[str, Any] = field(default_factory=dict)
    task_context: Dict[str, Any] = field(default_factory=dict)
    memory_confidence: float = 0.0


@dataclass
class ConversationContext:
    """Context for tracking ongoing conversations."""

    session_id: str
    user_id: str
    start_time: datetime
    last_interaction: datetime
    interaction_count: int = 0
    topics: List[str] = field(default_factory=list)
    sentiment_trend: List[str] = field(default_factory=list)
    preferences_learned: Dict[str, Any] = field(default_factory=dict)


class VoidCatMemoryIntegration:
    """
    Memory-Enhanced Reasoning Integration for VoidCat V2.

    This class provides the bridge between the persistent memory system and the
    reasoning engine, enabling memory-aware responses and continuous learning
    from user interactions.
    """

    def __init__(self, working_directory: str = None, user_id: str = "default"):
        """
        Initialize the memory integration system.

        Args:
            working_directory: Directory for data storage
            user_id: Default user identifier
        """
        self.working_directory = working_directory or str(Path.cwd())
        self.user_id = user_id

        # Initialize memory components
        self.storage_config = StorageConfig(
            base_dir=Path(self.working_directory) / "memory_storage",
            backup_dir=Path(self.working_directory) / "memory_backups",
            index_dir=Path(self.working_directory) / "memory_indexes",
            backup_interval=24 * 3600,  # Convert hours to seconds
            archive_age_days=365,
        )

        self.storage_engine = MemoryStorageEngine(self.storage_config)
        self.search_engine = MemorySearchEngine(self.storage_engine)
        self.retrieval_engine = IntelligentMemoryRetrievalEngine(
            self.storage_engine, self.search_engine
        )

        # Initialize task context integration
        self.context_integration = VoidCatContextIntegration(working_directory)

        # Active conversation tracking
        self.active_conversations: Dict[str, ConversationContext] = {}

        # Memory enhancement cache
        self._enhancement_cache = {}
        self._cache_ttl = 300  # 5 minutes

        logger.info("VoidCat Memory Integration initialized successfully")

    async def enhance_query_with_memory(
        self, query: str, session_id: str = None, include_task_context: bool = True
    ) -> Tuple[str, MemoryEnhancedContext]:
        """
        Enhance a user query with memory-derived context and insights.

        Args:
            query: Original user query
            session_id: Session identifier for conversation tracking
            include_task_context: Whether to include task management context

        Returns:
            Tuple of (enhanced_query, memory_context)
        """
        session_id = session_id or f"session_{datetime.now().timestamp()}"

        # Track conversation
        await self._track_conversation(query, session_id)

        # Retrieve relevant memories
        memory_context = await self._build_memory_context(query, session_id)

        # Include task context if requested
        if include_task_context:
            task_context = self.context_integration.get_active_context(self.user_id)
            memory_context.task_context = task_context

        # Enhance query with memory insights
        enhanced_query = await self._enhance_query_text(query, memory_context)

        return enhanced_query, memory_context

    async def process_response_for_learning(
        self,
        original_query: str,
        response: str,
        memory_context: MemoryEnhancedContext,
        session_id: str,
        user_feedback: Optional[str] = None,
    ) -> None:
        """
        Process the AI response to extract learning opportunities and update memory.

        Args:
            original_query: The original user query
            response: The AI-generated response
            memory_context: The memory context used for generation
            session_id: Session identifier
            user_feedback: Optional user feedback on the response
        """
        try:
            # Learn user preferences from interaction
            await self._learn_user_preferences(
                original_query, response, user_feedback, session_id
            )

            # Identify behavioral patterns
            await self._identify_behavioral_patterns(
                original_query, response, memory_context, session_id
            )

            # Store conversation history
            await self._store_conversation_history(
                original_query, response, session_id, user_feedback
            )

            # Update context associations
            await self._update_context_associations(
                original_query, response, memory_context
            )

            logger.info(f"Processed response for learning in session {session_id}")

        except Exception as e:
            logger.error(f"Error processing response for learning: {e}")

    async def get_user_preferences(self, category: str = None) -> Dict[str, Any]:
        """
        Retrieve current user preferences, optionally filtered by category.

        Args:
            category: Optional category filter

        Returns:
            Dictionary of user preferences
        """
        query = MemoryQuery(
            categories=[MemoryCategory.USER_PREFERENCES],
            user_id=self.user_id,
            status=MemoryStatus.ACTIVE,
        )

        if category:
            query.tags = [category]

        preferences = await self.storage_engine.search_memories(query)

        result = {}
        for pref_memory in preferences:
            if isinstance(pref_memory, UserPreference):
                result[pref_memory.preference_key] = pref_memory.preference_value

        return result

    async def apply_user_preferences_to_response(
        self, response: str, preferences: Dict[str, Any]
    ) -> str:
        """
        Apply user preferences to modify response style and content.

        Args:
            response: Original response text
            preferences: User preferences dictionary

        Returns:
            Modified response text
        """
        if not preferences:
            return response

        # Apply communication style preferences
        if "communication_style" in preferences:
            style = preferences["communication_style"]
            if style == "concise":
                # TODO: Implement response shortening logic
                pass
            elif style == "detailed":
                # TODO: Implement response expansion logic
                pass

        # Apply technical level preferences
        if "technical_level" in preferences:
            level = preferences["technical_level"]
            # TODO: Implement technical level adjustment
            pass

        # Apply format preferences
        if "response_format" in preferences:
            format_pref = preferences["response_format"]
            # TODO: Implement format adjustment
            pass

        return response

    async def _track_conversation(self, query: str, session_id: str) -> None:
        """Track ongoing conversation for context building."""
        now = datetime.now(timezone.utc)

        if session_id not in self.active_conversations:
            self.active_conversations[session_id] = ConversationContext(
                session_id=session_id,
                user_id=self.user_id,
                start_time=now,
                last_interaction=now,
            )

        conversation = self.active_conversations[session_id]
        conversation.last_interaction = now
        conversation.interaction_count += 1

        # Extract topics from query (simple keyword extraction)
        # TODO: Implement more sophisticated topic extraction
        words = query.lower().split()
        potential_topics = [word for word in words if len(word) > 4]
        conversation.topics.extend(potential_topics[:3])  # Limit to avoid noise

    async def _build_memory_context(
        self, query: str, session_id: str
    ) -> MemoryEnhancedContext:
        """Build comprehensive memory context for query enhancement."""
        context = MemoryEnhancedContext()

        try:
            # Get user preferences
            context.user_preferences = await self.get_user_preferences()

            # Get relevant conversation history
            context.conversation_history = (
                await self._get_relevant_conversation_history(query, session_id)
            )

            # Get learned behavioral patterns
            context.learned_patterns = await self._get_learned_patterns(query)

            # Get relevant memories using intelligent retrieval
            context.relevant_memories = (
                await self.retrieval_engine.retrieve_contextual_memories(
                    query, max_results=5
                )
            )

            # Generate behavioral insights
            context.behavioral_insights = await self._generate_behavioral_insights(
                query, context
            )

            # Calculate overall memory confidence
            context.memory_confidence = self._calculate_memory_confidence(context)

        except Exception as e:
            logger.error(f"Error building memory context: {e}")

        return context

    async def _enhance_query_text(
        self, query: str, memory_context: MemoryEnhancedContext
    ) -> str:
        """Enhance query text with memory-derived context."""
        enhancements = []

        # Add user preference context
        if memory_context.user_preferences:
            pref_context = "User preferences: " + ", ".join(
                [f"{k}={v}" for k, v in memory_context.user_preferences.items()]
            )
            enhancements.append(pref_context)

        # Add relevant conversation context
        if memory_context.conversation_history:
            recent_topics = set()
            for conv in memory_context.conversation_history[
                -3:
            ]:  # Last 3 conversations
                recent_topics.update(conv.get("topics", []))

            if recent_topics:
                topic_context = (
                    f"Recent conversation topics: {', '.join(recent_topics)}"
                )
                enhancements.append(topic_context)

        # Add behavioral insights
        if memory_context.behavioral_insights:
            behavior_context = "User behavior patterns: " + ", ".join(
                [
                    f"{k}={v}"
                    for k, v in memory_context.behavioral_insights.items()
                    if isinstance(v, (str, int, float))
                ]
            )
            enhancements.append(behavior_context)

        # Add task context if available
        if memory_context.task_context and memory_context.task_context.get(
            "active_projects"
        ):
            active_projects = memory_context.task_context["active_projects"]
            if active_projects:
                project_names = [
                    p["name"] for p in active_projects[:2]
                ]  # Top 2 projects
                task_context = f"Active projects: {', '.join(project_names)}"
                enhancements.append(task_context)

        # Combine original query with enhancements
        if enhancements:
            enhanced_query = f"{query}\n\nContext: {' | '.join(enhancements)}"
        else:
            enhanced_query = query

        return enhanced_query

    async def _learn_user_preferences(
        self, query: str, response: str, feedback: Optional[str], session_id: str
    ) -> None:
        """Learn and update user preferences from interactions."""
        try:
            # Analyze query patterns for preferences
            preferences_to_update = {}

            # Detect communication style preference
            if len(query.split()) < 10:
                preferences_to_update["query_style"] = "concise"
            elif len(query.split()) > 30:
                preferences_to_update["query_style"] = "detailed"

            # Detect technical level from query complexity
            technical_keywords = [
                "api",
                "function",
                "class",
                "method",
                "algorithm",
                "database",
            ]
            if any(keyword in query.lower() for keyword in technical_keywords):
                preferences_to_update["technical_level"] = "advanced"

            # Process user feedback if provided
            if feedback:
                if "too long" in feedback.lower() or "verbose" in feedback.lower():
                    preferences_to_update["communication_style"] = "concise"
                elif (
                    "more detail" in feedback.lower()
                    or "explain more" in feedback.lower()
                ):
                    preferences_to_update["communication_style"] = "detailed"

            # Store learned preferences
            for key, value in preferences_to_update.items():
                preference = UserPreference(
                    preference_key=key,
                    preference_value=value,
                    user_id=self.user_id,
                    confidence_score=0.7,  # Medium confidence from single interaction
                    last_updated=datetime.now(timezone.utc),
                    usage_count=1,
                )

                await self.storage_engine.store_memory(preference)

        except Exception as e:
            logger.error(f"Error learning user preferences: {e}")

    async def _identify_behavioral_patterns(
        self,
        query: str,
        response: str,
        memory_context: MemoryEnhancedContext,
        session_id: str,
    ) -> None:
        """Identify and store behavioral patterns from user interactions."""
        try:
            # Analyze query timing patterns
            conversation = self.active_conversations.get(session_id)
            if conversation and conversation.interaction_count > 1:
                time_since_last = (
                    conversation.last_interaction - conversation.start_time
                ).total_seconds()

                if time_since_last < 60:  # Quick succession
                    pattern = BehaviorPattern(
                        pattern_type="interaction_frequency",
                        pattern_data={
                            "type": "rapid_fire",
                            "interval": time_since_last,
                        },
                        user_id=self.user_id,
                        confidence_score=0.6,
                        occurrences=1,
                    )
                    await self.storage_engine.store_memory(pattern)

            # Analyze query complexity patterns
            query_length = len(query.split())
            if query_length > 50:
                pattern = BehaviorPattern(
                    pattern_type="query_complexity",
                    pattern_data={
                        "type": "detailed_queries",
                        "avg_length": query_length,
                    },
                    user_id=self.user_id,
                    confidence_score=0.5,
                    occurrences=1,
                )
                await self.storage_engine.store_memory(pattern)

        except Exception as e:
            logger.error(f"Error identifying behavioral patterns: {e}")

    async def _store_conversation_history(
        self, query: str, response: str, session_id: str, feedback: Optional[str] = None
    ) -> None:
        """Store conversation history for future context."""
        try:
            conversation = ConversationHistory(
                session_id=session_id,
                user_query=query,
                ai_response=response,
                user_feedback=feedback,
                user_id=self.user_id,
                interaction_timestamp=datetime.now(timezone.utc),
                response_quality_score=(
                    0.8 if not feedback or "good" in feedback.lower() else 0.5
                ),
            )

            await self.storage_engine.store_memory(conversation)

        except Exception as e:
            logger.error(f"Error storing conversation history: {e}")

    async def _update_context_associations(
        self, query: str, response: str, memory_context: MemoryEnhancedContext
    ) -> None:
        """Update context associations based on successful interactions."""
        try:
            # Create associations between query topics and successful responses
            if memory_context.task_context and memory_context.task_context.get(
                "active_projects"
            ):
                for project in memory_context.task_context["active_projects"]:
                    association = ContextAssociation(
                        primary_context=query[:100],  # First 100 chars of query
                        associated_context=project["name"],
                        association_strength=0.6,
                        user_id=self.user_id,
                        context_type="project_query",
                    )
                    await self.storage_engine.store_memory(association)

        except Exception as e:
            logger.error(f"Error updating context associations: {e}")

    async def _get_relevant_conversation_history(
        self, query: str, session_id: str, max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Get relevant conversation history for context."""
        try:
            search_query = MemoryQuery(
                categories=[MemoryCategory.CONVERSATION_HISTORY],
                user_id=self.user_id,
                status=MemoryStatus.ACTIVE,
                limit=max_results,
            )

            conversations = await self.storage_engine.search_memories(search_query)

            result = []
            for conv in conversations:
                if isinstance(conv, ConversationHistory):
                    result.append(
                        {
                            "session_id": conv.session_id,
                            "query": conv.user_query,
                            "response": conv.ai_response,
                            "timestamp": conv.interaction_timestamp.isoformat(),
                            "topics": getattr(conv, "topics", []),
                        }
                    )

            return result

        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []

    async def _get_learned_patterns(self, query: str) -> List[Dict[str, Any]]:
        """Get learned behavioral patterns relevant to the query."""
        try:
            search_query = MemoryQuery(
                categories=[MemoryCategory.BEHAVIOR_PATTERNS],
                user_id=self.user_id,
                status=MemoryStatus.ACTIVE,
                limit=10,
            )

            patterns = await self.storage_engine.search_memories(search_query)

            result = []
            for pattern in patterns:
                if isinstance(pattern, BehaviorPattern):
                    result.append(
                        {
                            "type": pattern.pattern_type,
                            "data": pattern.pattern_data,
                            "confidence": pattern.confidence_score,
                            "occurrences": pattern.occurrences,
                        }
                    )

            return result

        except Exception as e:
            logger.error(f"Error getting learned patterns: {e}")
            return []

    async def _generate_behavioral_insights(
        self, query: str, context: MemoryEnhancedContext
    ) -> Dict[str, Any]:
        """Generate behavioral insights from memory context."""
        insights = {}

        try:
            # Analyze communication patterns
            if context.learned_patterns:
                query_patterns = [
                    p
                    for p in context.learned_patterns
                    if p["type"] == "query_complexity"
                ]
                if query_patterns:
                    avg_complexity = sum(
                        p["data"].get("avg_length", 0) for p in query_patterns
                    ) / len(query_patterns)
                    insights["preferred_query_complexity"] = (
                        "high" if avg_complexity > 30 else "medium"
                    )

            # Analyze interaction frequency
            frequency_patterns = [
                p
                for p in context.learned_patterns
                if p["type"] == "interaction_frequency"
            ]
            if frequency_patterns:
                insights["interaction_style"] = (
                    "rapid" if len(frequency_patterns) > 3 else "measured"
                )

            # Analyze preference consistency
            if context.user_preferences:
                insights["preference_count"] = len(context.user_preferences)
                insights["has_established_preferences"] = (
                    len(context.user_preferences) > 3
                )

        except Exception as e:
            logger.error(f"Error generating behavioral insights: {e}")

        return insights

    def _calculate_memory_confidence(self, context: MemoryEnhancedContext) -> float:
        """Calculate overall confidence in memory-derived context."""
        confidence_factors = []

        # User preferences confidence
        if context.user_preferences:
            confidence_factors.append(min(len(context.user_preferences) * 0.2, 1.0))

        # Conversation history confidence
        if context.conversation_history:
            confidence_factors.append(
                min(len(context.conversation_history) * 0.15, 1.0)
            )

        # Learned patterns confidence
        if context.learned_patterns:
            avg_pattern_confidence = sum(
                p.get("confidence", 0) for p in context.learned_patterns
            ) / len(context.learned_patterns)
            confidence_factors.append(avg_pattern_confidence)

        # Relevant memories confidence
        if context.relevant_memories:
            confidence_factors.append(min(len(context.relevant_memories) * 0.1, 1.0))

        return (
            sum(confidence_factors) / len(confidence_factors)
            if confidence_factors
            else 0.0
        )


def create_memory_integration(
    working_directory: str = None, user_id: str = "default"
) -> VoidCatMemoryIntegration:
    """
    Factory function to create a VoidCat Memory Integration instance.

    Args:
        working_directory: Directory for data storage
        user_id: User identifier

    Returns:
        Configured VoidCatMemoryIntegration instance
    """
    return VoidCatMemoryIntegration(working_directory, user_id)


# Example usage and testing
if __name__ == "__main__":

    async def test_memory_integration():
        """Test the memory integration functionality."""
        integration = create_memory_integration()

        # Test query enhancement
        test_query = "How do I implement a REST API in Python?"
        enhanced_query, context = await integration.enhance_query_with_memory(
            test_query
        )

        print(f"Original Query: {test_query}")
        print(f"Enhanced Query: {enhanced_query}")
        print(f"Memory Confidence: {context.memory_confidence}")

        # Test response processing
        test_response = (
            "You can implement a REST API in Python using FastAPI or Flask..."
        )
        await integration.process_response_for_learning(
            test_query, test_response, context, "test_session"
        )

        print("Memory integration test completed successfully!")

    # Run the test
    asyncio.run(test_memory_integration())
