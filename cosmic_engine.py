#!/usr/bin/env python3
"""
VoidCat Cosmic Engine - Lightweight wrapper around MultiProviderClient
A zen-like engine that flows without heavy dependencies! 🧘‍♂️

This engine provides the same interface as the original VoidCatEngine
but uses our cosmic MultiProviderClient for API calls without sklearn dependencies.
"""

import asyncio
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from multi_provider_client import MultiProviderClient


def debug_print(message: str) -> None:
    """Print debug messages with cosmic vibes."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")


class VoidCatCosmicEngine:
    """
    Lightweight VoidCat engine powered by cosmic MultiProviderClient.
    
    This engine provides the same interface as VoidCatEngine but without
    heavy dependencies like sklearn. Perfect for API gateway integration! 🌊
    """
    
    def __init__(self, knowledge_dir: str = "knowledge_source"):
        """Initialize the cosmic engine with zen-like simplicity."""
        load_dotenv()
        
        debug_print("🧘‍♂️ Initializing VoidCat Cosmic Engine...")
        
        # Initialize our cosmic multi-provider client
        self.multi_provider_client = MultiProviderClient()
        debug_print("✨ Cosmic MultiProvider Client initialized")
        
        # Simple knowledge base (without vectorization for now)
        self.knowledge_dir = knowledge_dir
        self.documents = []
        self._load_simple_knowledge_base()
        
        # Basic metrics
        self.total_queries_processed = 0
        self.last_query_timestamp = None
        
        debug_print("🎉 VoidCat Cosmic Engine ready for cosmic queries!")
    
    def _load_simple_knowledge_base(self):
        """Load knowledge base documents without vectorization."""
        if not os.path.isdir(self.knowledge_dir):
            debug_print(f"⚠️ Knowledge directory '{self.knowledge_dir}' not found")
            return
        
        try:
            markdown_files = [f for f in os.listdir(self.knowledge_dir) if f.endswith(".md")]
            
            for filename in markdown_files:
                # Secure path handling to prevent path traversal attacks
                safe_filename = os.path.basename(filename)  # Remove any path components
                filepath = os.path.join(self.knowledge_dir, safe_filename)
                filepath = os.path.abspath(filepath)  # Get absolute path
                
                # Ensure the file is within the knowledge directory
                if not filepath.startswith(os.path.abspath(self.knowledge_dir)):
                    debug_print(f"⚠️ Skipping file outside knowledge directory: {filename}")
                    continue
                    
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:
                            self.documents.append({
                                "filename": filename,
                                "content": content
                            })
                            debug_print(f"✓ Loaded: {filename}")
                except Exception as e:
                    debug_print(f"✗ Failed to load {filename}: {str(e)}")
            
            debug_print(f"📚 Loaded {len(self.documents)} knowledge documents")
            
        except Exception as e:
            debug_print(f"Error loading knowledge base: {e}")
    
    def _get_simple_context(self, query: str, max_docs: int = 2) -> str:
        """Get simple context by keyword matching (no vectorization needed)."""
        if not self.documents:
            return "No knowledge base available."
        
        query_lower = query.lower()
        relevant_docs = []
        
        # Simple keyword matching
        for doc in self.documents:
            content_lower = doc["content"].lower()
            # Count keyword matches
            matches = sum(1 for word in query_lower.split() if word in content_lower)
            if matches > 0:
                relevant_docs.append((doc, matches))
        
        # Sort by relevance and take top documents
        relevant_docs.sort(key=lambda x: x[1], reverse=True)
        selected_docs = relevant_docs[:max_docs]
        
        if not selected_docs:
            return "No relevant knowledge found."
        
        context_parts = []
        for doc, matches in selected_docs:
            context_parts.append(f"--- {doc['filename']} ---\n{doc['content']}")
        
        return "\n\n".join(context_parts)
    
    async def query(
        self,
        user_query: str,
        model: str = "gpt-4o-mini",
        top_k: int = 2,
        session_id: Optional[str] = None,
    ) -> str:
        """Process user query with cosmic RAG-enhanced reasoning."""
        debug_print(f"🌊 Processing cosmic query: {user_query[:50]}...")
        
        # Get simple context
        context = self._get_simple_context(user_query, max_docs=top_k)
        
        # Build enhanced prompt
        enhanced_prompt = f"""You are an intelligent reasoning assistant with access to a knowledge base.
Please analyze the provided context and answer the user's query with precision and cosmic wisdom.

CONTEXT:
{context}

USER QUERY: {user_query}

Please provide a detailed, well-reasoned response based on the context. If the context doesn't contain relevant information, provide a helpful general response."""
        
        try:
            # Use our cosmic client
            messages = [{"role": "user", "content": enhanced_prompt}]
            
            response = await self.multi_provider_client.chat_completion(
                messages=messages,
                model=model,
                max_tokens=2000,
                temperature=0.7
            )
            
            # Extract response content
            if "choices" in response and len(response["choices"]) > 0:
                content = response["choices"][0]["message"]["content"]
                
                # Update metrics
                self.total_queries_processed += 1
                self.last_query_timestamp = datetime.now().isoformat()
                
                debug_print("✨ Cosmic query processed successfully!")
                return content
            else:
                debug_print(f"⚠️ Unexpected response format: {response}")
                return f"Response received but format unexpected: {str(response)}"
                
        except Exception as e:
            debug_print(f"💫 Cosmic query failed: {str(e)}")
            return f"I apologize, but I encountered an error processing your query: {str(e)}"
    
    def get_status(self) -> Dict[str, Any]:
        """Get engine status with cosmic metrics."""
        try:
            provider_status = self.multi_provider_client.get_provider_status()
            
            return {
                "engine_type": "VoidCat Cosmic Engine",
                "status": "operational",
                "total_queries_processed": self.total_queries_processed,
                "last_query_timestamp": self.last_query_timestamp,
                "knowledge_documents": len(self.documents),
                "providers": provider_status,
                "cosmic_vibes": "flowing smoothly ✨"
            }
        except Exception as e:
            return {
                "engine_type": "VoidCat Cosmic Engine",
                "status": "error",
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        try:
            # Check provider health
            provider_health = await self.multi_provider_client.health_check()
            
            # Test a simple query
            test_response = await self.query(
                "Health check test - please respond with 'OK'",
                model="gpt-4o-mini"
            )
            
            query_test_passed = "OK" in test_response or "ok" in test_response.lower()
            
            return {
                "engine_status": "healthy",
                "providers": provider_health,
                "query_test": "passed" if query_test_passed else "failed",
                "knowledge_base": len(self.documents) > 0,
                "cosmic_energy": "flowing strong 🌊"
            }
            
        except Exception as e:
            return {
                "engine_status": "unhealthy",
                "error": str(e),
                "cosmic_energy": "blocked 😵"
            }
    
    def get_provider_metrics(self) -> Dict[str, Any]:
        """Get detailed provider metrics."""
        try:
            return self.multi_provider_client.get_provider_status()
        except Exception as e:
            return {"error": str(e)}


# Compatibility alias for existing code
VoidCatEngine = VoidCatCosmicEngine


async def test_cosmic_engine():
    """Test the cosmic engine functionality."""
    print("🧘‍♂️ Testing VoidCat Cosmic Engine")
    print("=" * 40)
    
    engine = VoidCatCosmicEngine()
    
    # Test query
    response = await engine.query("What is the meaning of life?")
    print(f"Response: {response[:100]}...")
    
    # Test status
    status = engine.get_status()
    print(f"Status: {status['status']}")
    
    # Test health check
    health = await engine.health_check()
    print(f"Health: {health['engine_status']}")


if __name__ == "__main__":
    asyncio.run(test_cosmic_engine())