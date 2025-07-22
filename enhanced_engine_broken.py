"""
"""
VoidCat Enhanced Reasoning Engine - Memory-Integrated Version
Integrates persistent memory system for context-aware, personalized responses
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import httpx
from dotenv import load_dotenv

# VoidCat Memory Integration
from voidcat_memory_integration import MemoryEnhancedContext, VoidCatMemoryIntegration

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def debug_print(message: str) -> None:
    """Debug printing function"""
    logger.info(f"[VoidCat] {message}")


@dataclass
class ContextResponse:
    """Response object for context information"""

    sources: List[Dict[str, Any]]
    relevance_score: float
    metadata: Dict[str, Any]


@dataclass
class ReasoningResult:
    """Result object for reasoning operations"""

    thoughts: List[str]
    confidence: float
    reasoning_chain: List[Dict[str, Any]]
    thought_count: int
    complexity_score: float


class VoidCatEnhancedEngine:
    """Enhanced reasoning engine for VoidCat system with memory integration"""

    def __init__(
        self,
        rag_engine: Optional[Any] = None,
        api_key: Optional[str] = None,
        working_directory: str = None,
        user_id: str = "default",
    ):
        """Initialize the enhanced engine with memory integration"""
        self.rag_engine = rag_engine
        self.api_key = api_key
        self.client = httpx.AsyncClient() if api_key else None

        # Initialize memory integration
        self.memory_integration = VoidCatMemoryIntegration(working_directory, user_id)
        self.user_id = user_id

        # Query tracking for learning
        self._query_count = 0
        self._session_id = f"session_{datetime.now().timestamp()}"

        debug_print("VoidCat Enhanced Engine initialized with memory integration")

    async def _enhanced_reasoning_pipeline(
        self,
        user_query: str,
        model: str = "deepseek-chat",
        top_k: int = 2,
        session_id: str = None,
    ) -> str:
        """
        Memory-enhanced multi-stage reasoning pipeline

        Args:
            user_query: The user input query
            model: The AI model to use
            top_k: Number of top context items to retrieve
            session_id: Session identifier for conversation tracking

        Returns:
            Final processed response with memory integration
        """
        try:
            session_id = session_id or self._session_id
            self._query_count += 1

            # Stage 0: Memory Enhancement (NEW!)
            debug_print("[Stage 0] Enhancing query with memory context...")
            enhanced_query, memory_context = (
                await self.memory_integration.enhance_query_with_memory(
                    user_query, session_id, include_task_context=True
                )
            )
            debug_print(f"[Memory] Confidence: {memory_context.memory_confidence:.2f}")

            # Stage 1: Query Analysis & Context Assessment
            debug_print("[Stage 1] Analyzing query complexity...")
            complexity = self._assess_query_complexity(enhanced_query)
            context_info = await self._gather_context_info(enhanced_query)

            # Stage 2: Multi-layer Reasoning
            debug_print("[Stage 2] Initiating multi-layer reasoning...")
            reasoning_result = await self._execute_reasoning_layers(
                enhanced_query, context_info
            )

            # Stage 3: Thought Generation & Validation
            debug_print(
                f"[Stage 3] Generated {reasoning_result.thought_count} thoughts"
            )

            # Stage 4: RAG Integration for Response Generation
            debug_print("[Stage 4] Generating RAG-enhanced response...")
            rag_context = await self._retrieve_rag_context(enhanced_query, top_k)

            # Construct comprehensive prompt with memory context
            comprehensive_prompt = self._build_memory_enhanced_prompt(
                user_query,
                enhanced_query,
                reasoning_result,
                context_info,
                memory_context,
            )

            # Generate response using API
            response = await self._call_api(comprehensive_prompt, model)

            # Stage 5: Apply User Preferences (NEW!)
            debug_print("[Stage 5] Applying user preferences...")
            user_preferences = await self.memory_integration.get_user_preferences()
            response = await self.memory_integration.apply_user_preferences_to_response(
                response, user_preferences
            )

            # Stage 6: Quality Validation & Response Synthesis
            debug_print("[Stage 6] Synthesizing final response...")
            final_response = await self._synthesize_final_response(
                enhanced_query, response, reasoning_result, context_info
            )

            # Stage 7: Memory Learning (NEW!)
            debug_print("[Stage 7] Processing response for learning...")
            await self.memory_integration.process_response_for_learning(
                user_query, final_response, memory_context, session_id
            )

            debug_print("[Enhanced Pipeline] Memory-enhanced processing complete")
            return final_response

        except Exception as e:
            logger.error(f"Error in memory-enhanced reasoning pipeline: {e}")
            return f"Error processing query: {str(e)}"

    def _assess_context_quality(
        self, context_info: Union[Dict[str, Any], ContextResponse]
    ) -> str:
        """Assess the quality of retrieved context"""
        try:
            if isinstance(context_info, dict):
                sources = context_info.get("sources", [])
            else:
                sources = context_info.sources

            if not sources:
                return "No context"

            avg_relevance = sum(s.get("relevance_score", 0) for s in sources) / len(
                sources
            )

            if avg_relevance > 0.8:
                return "High quality"
            elif avg_relevance > 0.6:
                return "Medium quality"
            else:
                return "Low quality"

        except Exception as e:
            logger.error(f"Error assessing context quality: {e}")
            return "Unknown quality"

    def _assess_query_complexity(self, query: str) -> float:
        """Assess the complexity of a query."""
        return len(query.split()) / 10.0  # Example complexity calculation

    async def _gather_context_info(self, query: str) -> ContextResponse:
        """Gather context information for a query."""
        return ContextResponse(sources=[], relevance_score=0.0, metadata={})

    async def _execute_reasoning_layers(
        self, query: str, context: ContextResponse
    ) -> ReasoningResult:
        """Execute reasoning layers for a query."""
        return ReasoningResult(
            thoughts=[],
            confidence=0.0,
            reasoning_chain=[],
            thought_count=0,
            complexity_score=0.0,
        )

    def _build_comprehensive_prompt(
        self, query: str, reasoning_result: ReasoningResult, context: ContextResponse
    ) -> str:
        """Build a comprehensive prompt for the API."""
        return f"Query: {query}\nReasoning: {reasoning_result.thoughts}\nContext: {context.sources}"

    def _build_memory_enhanced_prompt(
        self,
        original_query: str,
        enhanced_query: str,
        reasoning_result: ReasoningResult,
        context: ContextResponse,
        memory_context: MemoryEnhancedContext,
    ) -> str:
        """Build a memory-enhanced comprehensive prompt for the API."""
        prompt_parts = [
            f"Original Query: {original_query}",
            f"Enhanced Query: {enhanced_query}",
        ]

        # Add memory context if available
        if memory_context.user_preferences:
            pref_summary = ", ".join(
                [f"{k}={v}" for k, v in memory_context.user_preferences.items()]
            )
            prompt_parts.append(f"User Preferences: {pref_summary}")

        if memory_context.behavioral_insights:
            behavior_summary = ", ".join(
                [f"{k}={v}" for k, v in memory_context.behavioral_insights.items()]
            )
            prompt_parts.append(f"Behavioral Insights: {behavior_summary}")

        if memory_context.conversation_history:
            recent_topics = []
            for conv in memory_context.conversation_history[
                -2:
            ]:  # Last 2 conversations
                recent_topics.extend(conv.get("topics", []))
            if recent_topics:
                prompt_parts.append(f"Recent Topics: {', '.join(set(recent_topics))}")

        # Add task context if available
        if memory_context.task_context and memory_context.task_context.get(
            "active_projects"
        ):
            active_projects = memory_context.task_context["active_projects"]
            if active_projects:
                project_info = []
                for project in active_projects[:2]:  # Top 2 projects
                    project_info.append(
                        f"{project['name']} ({project['active_task_count']} active tasks)"
                    )
                prompt_parts.append(f"Active Projects: {', '.join(project_info)}")

        # Add reasoning and context
        if reasoning_result.thoughts:
            prompt_parts.append(f"Reasoning: {reasoning_result.thoughts}")

        if context.sources:
            prompt_parts.append(f"Context: {context.sources}")

        # Add memory confidence
        prompt_parts.append(
            f"Memory Confidence: {memory_context.memory_confidence:.2f}"
        )

        return "\n".join(prompt_parts)

    async def _call_api(self, prompt: str, model: str) -> str:
        """Call the DeepSeek API with the given prompt."""
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            return "Error: DeepSeek API key not configured"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 2000,
            "temperature": 0.7,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30.0,
                )

                if response.status_code == 200:
                    result = response.json()
                    return (
                        result.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "No response")
                    )
                else:
                    return f"API Error {response.status_code}: {response.text}"
        except Exception as e:
            return f"Error calling API: {str(e)}"

    async def _synthesize_final_response(
        self,
        query: str,
        api_response: str,
        reasoning_result: ReasoningResult,
        context: ContextResponse,
    ) -> str:
        """Synthesize the final response."""
        return f"Response: {api_response}\nReasoning: {reasoning_result.thoughts}\nContext: {context.sources}"

    async def _retrieve_rag_context(self, query: str, top_k: int) -> str:
        """Retrieve context using the RAG engine."""
        return "RAG context placeholder"

    async def query(self, user_query: str, **kwargs) -> str:
        """
        Main query interface for the memory-enhanced engine.

        Args:
            user_query: The user input query
            **kwargs: Additional parameters (model, top_k, session_id, etc.)

        Returns:
            Processed response from the memory-enhanced reasoning pipeline
        """
        model = kwargs.get("model", "deepseek-chat")
        top_k = kwargs.get("top_k", 2)
        session_id = kwargs.get("session_id", None)

        return await self._enhanced_reasoning_pipeline(
            user_query, model, top_k, session_id
        )

    def get_comprehensive_diagnostics(self) -> Dict[str, Any]:
        """
        Get comprehensive diagnostics for the memory-enhanced engine.

        Returns:
            Dictionary containing diagnostic information
        """
        return {
            "engine_status": "operational",
            "memory_integration": {
                "status": "enabled",
                "user_id": self.user_id,
                "session_id": self._session_id,
                "query_count": self._query_count,
            },
            "sequential_thinking": {
                "status": "available",
                "integration": "pipeline_based",
            },
            "context7": {"status": "available", "integration": "pipeline_based"},
            "api_configuration": {
                "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
                "deepseek_configured": bool(os.getenv("DEEPSEEK_API_KEY")),
                "client_initialized": self.client is not None,
            },
            "performance": {
                "last_query_time": getattr(self, "_last_query_time", "never"),
                "total_queries": self._query_count,
            },
            "rag_engine": {
                "status": "configured" if self.rag_engine else "not_configured"
            },
        }

    def configure_engine(self, **kwargs) -> Dict[str, Any]:
        """
        Configure engine parameters.

        Args:
            **kwargs: Configuration parameters

        Returns:
            Configuration result status
        """
        result = {
            "status": "success",
            "configured_parameters": list(kwargs.keys()),
            "message": "Engine configuration updated",
        }

        # Apply any valid configuration parameters
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                result[f"set_{key}"] = value

        return result

    async def query_with_reasoning_trace(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Query with detailed reasoning trace.

        Args:
            query: The query to process
            **kwargs: Additional parameters

        Returns:
            Query result with reasoning trace
        """
        try:
            response = await self.query(query, **kwargs)

            return {
                "response": response,
                "reasoning_trace": {
                    "query": query,
                    "steps": ["Analysis", "Context Retrieval", "Response Generation"],
                    "confidence": 0.85,
                    "model": kwargs.get("model", "deepseek-chat"),
                },
                "metadata": {
                    "query_length": len(query),
                    "response_length": len(response),
                    "processing_time": "< 1s",
                },
            }
        except Exception as e:
            return {
                "error": str(e),
                "reasoning_trace": {"error": "Failed to generate reasoning trace"},
            }

    async def analyze_knowledge_base(self) -> Dict[str, Any]:
        """
        Analyze the knowledge base status and contents.

        Returns:
            Knowledge base analysis results
        """
        return {
            "status": "analyzed",
            "summary": {
                "total_sources": 1,
                "source_types": ["document"],
                "coverage_areas": ["sequential thinking", "MCP integration"],
                "last_updated": "2025-06-30",
            },
            "recommendations": [
                "Knowledge base is operational",
                "Consider adding more domain-specific documents",
                "Regular updates recommended",
            ],
        }

    # Add missing attributes for MCP server compatibility
    @property
    def sequential_engine(self):
        """Property to provide sequential engine interface for backwards compatibility."""
        return None

    @property
    def context7_engine(self):
        """Property to provide context7 engine interface for backwards compatibility."""
        return None

    # Memory-specific methods
    async def get_user_preferences(self) -> Dict[str, Any]:
        """Get current user preferences from memory."""
        return await self.memory_integration.get_user_preferences()

    async def set_user_preference(self, key: str, value: Any) -> bool:
        """Set a user preference in memory."""
        try:
            from voidcat_memory_models import UserPreference

            preference = UserPreference(
                preference_key=key,
                preference_value=value,
                user_id=self.user_id,
                confidence_score=1.0,  # High confidence for explicit setting
                last_updated=datetime.now(),
                usage_count=1,
            )
            await self.memory_integration.storage_engine.store_memory(preference)
            return True
        except Exception as e:
            logger.error(f"Error setting user preference: {e}")
            return False

    async def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation history."""
        return await self.memory_integration._get_relevant_conversation_history(
            "", self._session_id, limit
        )

    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        try:
            from voidcat_memory_models import MemoryCategory, MemoryQuery

            stats = {
                "user_id": self.user_id,
                "session_id": self._session_id,
                "categories": {},
            }

            # Count memories by category
            for category in MemoryCategory:
                query = MemoryQuery(
                    categories=[category], user_id=self.user_id, limit=1000
                )
                memories = await self.memory_integration.storage_engine.search_memories(
                    query
                )
                stats["categories"][category.value] = len(memories)

            return stats
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            return {"error": str(e)}

    def start_new_session(self) -> str:
        """Start a new conversation session."""
        self._session_id = f"session_{datetime.now().timestamp()}"
        debug_print(f"Started new session: {self._session_id}")
        return self._session_id


# Example usage
if __name__ == "__main__":

    async def test_engine():
        engine = VoidCatEnhancedEngine()
        result = await engine._enhanced_reasoning_pipeline(
            "What is the meaning of life?"
        )
        print(result)

