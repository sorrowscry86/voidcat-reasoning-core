#!/usr/bin/env python3
"""
VoidCat Reasoning Core Engine - Enhanced Version
Reliable MCP server compatible engine with advanced RAG functionality
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import List

import httpx
import numpy as np
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


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
