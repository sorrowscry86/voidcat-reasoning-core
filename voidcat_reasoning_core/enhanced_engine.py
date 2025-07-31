#!/usr/bin/env python3
"""
VoidCat Reasoning Core Engine - Enhanced Version
Reliable MCP server compatible engine with advanced RAG functionality
Integrates Sequential Thinking and Context7 for enhanced reasoning capabilities
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
import numpy as np
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from context7_integration import Context7Engine, ContextRequest

# Import our advanced reasoning modules
from sequential_thinking import SequentialThinkingEngine


def debug_print(message: str) -> None:
    """Print debug messages to stderr for MCP compatibility."""
    print(f"[VoidCat] {message}", file=sys.stderr, flush=True)


class VoidCatEnhancedEngine:
    """
    Enhanced, reliable RAG-enabled reasoning engine for VoidCat system.
    Designed for MCP server compatibility and production stability.
    """

    def __init__(self, knowledge_dir: str = "knowledge_source"):
        """Initialize VoidCat Enhanced Engine with knowledge loading."""
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

        # Ensure knowledge_dir is absolute
        if not os.path.isabs(knowledge_dir):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            knowledge_dir = os.path.join(script_dir, knowledge_dir)

        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.deepseek_url = "https://api.deepseek.com/v1/chat/completions"

        if not self.openai_api_key and not self.deepseek_api_key:
            debug_print(
                "Warning: No API keys found. Set " "OPENAI_API_KEY or DEEPSEEK_API_KEY"
            )

        self.documents: List[str] = []
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words="english",
            lowercase=True,
            ngram_range=(1, 2),
        )
        self.doc_vectors = None
        self.total_queries_processed = 0
        self.last_query_timestamp = None

        # Initialize advanced reasoning engines
        debug_print("Initializing advanced reasoning engines...")
        self.sequential_engine = SequentialThinkingEngine()
        self.context7_engine = Context7Engine()
        debug_print("✅ Advanced engines initialized")

        self._load_documents(knowledge_dir)

    def _load_documents(self, knowledge_dir: str) -> None:
        """Load all markdown documents from knowledge base directory."""
        debug_print("Loading knowledge base...")

        if not os.path.isdir(knowledge_dir):
            debug_print(f"Warning: Knowledge directory '{knowledge_dir}' not found")
            return

        markdown_files = [f for f in os.listdir(knowledge_dir) if f.endswith(".md")]

        if not markdown_files:
            debug_print(f"Warning: No .md files found in '{knowledge_dir}'")
            return

        for filename in markdown_files:
            filepath = os.path.join(knowledge_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        self.documents.append(content)
                        debug_print(f"✓ Loaded: {filename}")
            except Exception as e:
                debug_print(f"✗ Failed to load {filename}: {str(e)}")

        if self.documents:
            try:
                self.doc_vectors = self.vectorizer.fit_transform(self.documents)
                debug_print(
                    f"✓ Vectorized {len(self.documents)} documents "
                    f"with {self.doc_vectors.shape[1]} features"
                )
            except Exception as e:
                debug_print(f"Error during vectorization: {str(e)}")
                self.doc_vectors = None

    def _retrieve_context(self, query: str, top_k: int = 1) -> str:
        """Retrieve most relevant document chunks for a query."""
        if self.doc_vectors is None or not self.documents:
            return "No knowledge base loaded."

        try:
            query_vector = self.vectorizer.transform([query])
            cosine_similarities = cosine_similarity(
                query_vector, self.doc_vectors
            ).flatten()

            effective_k = min(top_k, len(self.documents))

            if effective_k >= len(self.documents):
                relevant_doc_indices = cosine_similarities.argsort()[::-1]
            else:
                relevant_doc_indices = np.argpartition(
                    cosine_similarities, -effective_k
                )[-effective_k:]
                relevant_doc_indices = relevant_doc_indices[
                    np.argsort(cosine_similarities[relevant_doc_indices])
                ][::-1]

            return "\n---DOCUMENT SEPARATOR---\n".join(
                [self.documents[i] for i in relevant_doc_indices]
            )

        except Exception as e:
            return f"Error during context retrieval: {str(e)}"

    async def query(
        self,
        user_query: str,
        model: str = "gpt-4o-mini",
        top_k: int = 2,
        session_id: str = None,
    ) -> str:
        """Process user query with RAG-enhanced reasoning."""
        # Determine which API to use
        if model.startswith("deepseek") and self.deepseek_api_key:
            api_key = self.deepseek_api_key
            api_url = self.deepseek_url
        elif self.openai_api_key:
            api_key = self.openai_api_key
            api_url = self.api_url
            if model.startswith("deepseek"):
                model = "gpt-4o-mini"  # Fallback to OpenAI model
        else:
            return "Error: No valid API key configured"

        # Retrieve context
        debug_print("Retrieving context...")
        context = self._retrieve_context(user_query, top_k=top_k)

        # Build enhanced prompt
        enhanced_prompt = f"""You are an intelligent reasoning assistant with access to a knowledge base.
Please analyze the provided context and answer the user's query with precision.

CONTEXT:
{context}

USER QUERY: {user_query}

Please provide a detailed, well-reasoned response based on the context."""

        # Call API
        debug_print(f"Calling {model} API...")
        response = await self._call_api(enhanced_prompt, model, api_key, api_url)

        # Update metrics
        self.total_queries_processed += 1
        self.last_query_timestamp = datetime.now().isoformat()

        return response

    async def _call_api(
        self, prompt: str, model: str, api_key: str, api_url: str
    ) -> str:
        """Make API call with error handling."""
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
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(api_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()

                if "choices" not in data or not data["choices"]:
                    return "Error: Unexpected API response format"

                return data["choices"][0]["message"]["content"]

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid API key"
            elif e.response.status_code == 429:
                return "Error: API rate limit exceeded"
            else:
                return f"Error: HTTP {e.response.status_code}"
        except httpx.TimeoutException:
            return "Error: Request timeout"
        except Exception as e:
            return f"Error: {str(e)}"

    async def enhanced_query_with_sequential_thinking(
        self, user_query: str, model: str = "gpt-4o-mini", max_thoughts: int = 5
    ) -> Dict[str, Any]:
        """
        Process query using Sequential Thinking for complex reasoning.
        Returns detailed reasoning path along with final answer.
        """
        debug_print(f"Processing query with Sequential Thinking: {user_query}")

        # First get basic RAG context
        context = self._retrieve_context(user_query, top_k=3)

        # Use Sequential Thinking with RAG context
        result = await self.sequential_engine.process_query(
            user_query, context=context, max_thoughts=max_thoughts
        )

        self.total_queries_processed += 1
        self.last_query_timestamp = datetime.now().isoformat()

        return result

    async def enhanced_query_with_context7(
        self, user_query: str, model: str = "gpt-4o-mini", max_sources: int = 3
    ) -> Dict[str, Any]:
        """
        Process query using Context7 for enhanced context analysis.
        Returns context analysis along with reasoning.
        """
        debug_print(f"Processing query with Context7: {user_query}")

        # Create Context7 request
        context_request = ContextRequest(
            id=f"enhanced_query_{self.total_queries_processed}",
            query=user_query,
            max_sources=max_sources,
            min_relevance=0.2,
        )

        # Get enhanced context
        context_response = await self.context7_engine.retrieve_context(context_request)

        # Combine with basic RAG query
        basic_result = await self.query(user_query, model=model)

        self.total_queries_processed += 1
        self.last_query_timestamp = datetime.now().isoformat()

        return {
            "query": user_query,
            "basic_answer": basic_result,
            "context7_analysis": context_response,
            "enhanced_sources": len(context_response.sources),
            "processing_metadata": context_response.processing_metadata,
        }

    async def ultimate_enhanced_query(
        self,
        user_query: str,
        model: str = "gpt-4o-mini",
        max_thoughts: int = 3,
        max_sources: int = 3,
        reasoning_mode: str = "adaptive",
    ) -> Dict[str, Any]:
        """
        Ultimate reasoning pipeline combining all three approaches:
        Basic RAG + Sequential Thinking + Context7

        Args:
            user_query: The user's question
            model: OpenAI model to use
            max_thoughts: Max thoughts for sequential reasoning
            max_sources: Max sources for Context7
            reasoning_mode: "adaptive", "comprehensive", or "fast"
        """
        debug_print(f"Ultimate Enhanced Query: {user_query}")
        debug_print(f"Reasoning mode: {reasoning_mode}")

        results = {
            "query": user_query,
            "reasoning_mode": reasoning_mode,
            "timestamp": datetime.now().isoformat(),
        }

        # OPTIMIZED: Implement parallel processing for all reasoning modes
        if reasoning_mode == "fast":
            # Just basic RAG with light Context7 (parallel)
            context_req = ContextRequest(
                id=f"fast_{self.total_queries_processed}",
                query=user_query,
                max_sources=1,
                min_relevance=0.3,
            )

            # Run both operations in parallel
            basic_rag_task = self.query(user_query, model=model)
            context7_task = self.context7_engine.retrieve_context(context_req)

            # Gather results
            rag_result, context7_result = await asyncio.gather(
                basic_rag_task, context7_task
            )
            results["basic_rag"] = rag_result
            results["context7"] = context7_result.to_dict()
            results["approach"] = "parallel_fast"

        elif reasoning_mode == "comprehensive":
            # Use all three approaches with full power (parallel)
            # Start all three operations concurrently
            basic_rag_task = self.query(user_query, model=model)
            sequential_task = self.enhanced_query_with_sequential_thinking(
                user_query, model=model, max_thoughts=max_thoughts
            )
            context7_task = self.enhanced_query_with_context7(
                user_query, model=model, max_sources=max_sources
            )

            # Gather results from all concurrent tasks
            parallel_results = await asyncio.gather(
                basic_rag_task, sequential_task, context7_task
            )
            results["basic_rag"] = parallel_results[0]
            results["sequential_thinking"] = parallel_results[1]
            results["context7"] = parallel_results[2]
            results["approach"] = "parallel_comprehensive"

        else:  # adaptive mode
            # Assess complexity and choose appropriate approach
            complexity = self.sequential_engine.assess_complexity(user_query)

            if complexity.value == "simple":
                results["approach"] = "basic_rag"
                results["basic_rag"] = await self.query(user_query, model=model)
            elif complexity.value == "medium":
                results["approach"] = "rag_plus_context7"
                # Run both operations in parallel
                basic_rag_task = self.query(user_query, model=model)
                context7_task = self.enhanced_query_with_context7(
                    user_query, model=model, max_sources=max_sources
                )

                # Gather results
                parallel_results = await asyncio.gather(basic_rag_task, context7_task)
                results["basic_rag"] = parallel_results[0]
                results["context7"] = parallel_results[1]
            else:  # complex
                results["approach"] = "full_parallel_pipeline"
                # Run all three operations in parallel for complex queries
                basic_rag_task = self.query(user_query, model=model)
                sequential_task = self.enhanced_query_with_sequential_thinking(
                    user_query, model=model, max_thoughts=max_thoughts
                )
                context7_task = self.enhanced_query_with_context7(
                    user_query, model=model, max_sources=max_sources
                )

                # Gather all results at once
                parallel_results = await asyncio.gather(
                    basic_rag_task, sequential_task, context7_task
                )
                results["basic_rag"] = parallel_results[0]
                results["sequential_thinking"] = parallel_results[1]
                results["context7"] = parallel_results[2]

        self.total_queries_processed += 1
        self.last_query_timestamp = datetime.now().isoformat()

        return results

    def get_diagnostics(self) -> dict:
        """Return diagnostic information."""
        return {
            "documents_loaded": len(self.documents),
            "total_queries_processed": self.total_queries_processed,
            "last_query_timestamp": self.last_query_timestamp,
            "vectorizer_features": (
                self.doc_vectors.shape[1] if self.doc_vectors is not None else 0
            ),
            "api_configured": bool(self.openai_api_key or self.deepseek_api_key),
        }


if __name__ == "__main__":

    async def test():
        engine = VoidCatEnhancedEngine()
        result = await engine.query("What is VoidCat?")
        print(result)

    asyncio.run(test())
