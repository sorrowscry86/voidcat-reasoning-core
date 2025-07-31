#!/usr/bin/env python3
# cspell:words vectorizer
"""
VoidCat Reasoning Core Engine
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import List

import httpx
import numpy as np
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="[VoidCat] %(levelname)s: %(message)s",
    stream=sys.stderr,
)


class VoidCatEngine:
    """
    Clean, reliable RAG-enabled reasoning engine for VoidCat system.
    Designed for MCP server compatibility and production stability.
    """

    def __init__(self, knowledge_dir: str = "knowledge_source"):
        """Initialize the VoidCat Engine with knowledge base loading."""
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
            logging.warning("No API keys found. Set OPENAI_API_KEY or DEEPSEEK_API_KEY")

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
        logging.debug("Loading knowledge base...")

        if not os.path.isdir(knowledge_dir):
            logging.warning(
                "Warning: Knowledge directory '%s' not found", knowledge_dir
            )
            return

        markdown_files = [f for f in os.listdir(knowledge_dir) if f.endswith(".md")]

        if not markdown_files:
            logging.warning("No .md files found in '%s'", knowledge_dir)
            return

        for filename in markdown_files:
            filepath = os.path.join(knowledge_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        self.documents.append(content)
                        logging.debug("✓ Loaded: %s", filename)
            except Exception as e:
                logging.error("Failed to load %s: %s", filename, e)

        if self.documents:
            try:
                self.doc_vectors = self.vectorizer.fit_transform(self.documents)
                log_msg = "✓ Vectorized %d documents with %d features"
                logging.debug(
                    log_msg,
                    len(self.documents),
                    self.doc_vectors.shape[1],
                )
            except Exception as e:
                logging.error("Vectorization error: %s", e)
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
                sorted_indices = np.argsort(cosine_similarities[relevant_doc_indices])
                relevant_doc_indices = relevant_doc_indices[sorted_indices]
                relevant_doc_indices = relevant_doc_indices[::-1]

            return "\n---DOCUMENT SEPARATOR---\n".join(
                [self.documents[i] for i in relevant_doc_indices]
            )

        except Exception as e:
            logging.error("Context retrieval error: %s", e)
            return f"Error during context retrieval: {str(e)}"

    async def query(self, user_query: str, model: str = "gpt-4o-mini") -> str:
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
        logging.debug("Retrieving context...")
        context = self._retrieve_context(user_query)

        # Build enhanced prompt
        enhanced_prompt = f"""You are an intelligent reasoning assistant.
Please analyze the provided context and answer the user's query.

CONTEXT:
{context}

USER QUERY: {user_query}

Provide a detailed, well-reasoned response based on the context."""

        # Call API
        logging.debug(f"Calling {model} API...")
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
                    logging.error("Unexpected API response format")
                    return "Error: Unexpected API response format"

                return data["choices"][0]["message"]["content"]

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                logging.error("Invalid API key")
                return "Error: Invalid API key"
            elif e.response.status_code == 429:
                logging.error("API rate limit exceeded")
                return "Error: API rate limit exceeded"
            else:
                logging.error(f"HTTP {e.response.status_code}: {e.response.text}")
                return f"Error: HTTP {e.response.status_code}"
        except httpx.TimeoutException:
            logging.error("Request timeout")
            return "Error: Request timeout"
        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")
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


# Compatibility aliases for enhanced engine
VoidCatEnhancedEngine = VoidCatEngine


if __name__ == "__main__":

    async def test():
        engine = VoidCatEngine()
        result = await engine.query("What is VoidCat?")
        print(result)

    asyncio.run(test())
