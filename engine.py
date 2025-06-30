# engine.py
"""
VoidCat Reasoning Core Engine

This module implements the core RAG (Retrieval Augmented Generation) engine
for the VoidCat Reasoning Core system. It provides intelligent document
processing, vectorization, and context-aware query processing.

Key Features:
- TF-IDF based document vectorization
- Cosine similarity for context retrieval
- OpenAI API integration for reasoning
- Async query processing
- Comprehensive error handling

Author: VoidCat Reasoning Core Team
License: MIT
"""

import os
import sys
import httpx
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Optional


def debug_print(message: str) -> None:
    """Print debug messages to stderr to avoid interfering with MCP protocol."""
    print(message, file=sys.stderr, flush=True)


class VoidCatEngine:
    """
    An integrated RAG-enabled reasoning engine for VoidCat RDC.
    
    This engine combines document vectorization with OpenAI's reasoning
    capabilities to provide context-aware responses to user queries.
    
    Attributes:
        documents (List[str]): Loaded document contents
        vectorizer (TfidfVectorizer): TF-IDF vectorization engine
        doc_vectors: Vectorized document representations
        openai_api_key (str): OpenAI API authentication key
        api_url (str): OpenAI API endpoint URL
    """
    
    def __init__(self, knowledge_dir: str = "knowledge_source"):
        """
        Initialize the VoidCat Engine with knowledge base loading.
        
        Args:
            knowledge_dir (str): Directory containing knowledge base documents
            
        Raises:
            EnvironmentError: If OPENAI_API_KEY is not found
        """
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Ensure knowledge_dir is relative to the script's directory
        if not os.path.isabs(knowledge_dir):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            knowledge_dir = os.path.join(script_dir, knowledge_dir)
        self.api_url = "https://api.openai.com/v1/chat/completions"
        
        if not self.openai_api_key:
            debug_print("Warning: OPENAI_API_KEY not found in environment variables.")
            debug_print("Please ensure your .env file contains the API key.")
        
        self.documents: List[str] = []
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            lowercase=True,
            ngram_range=(1, 2)
        )
        self.doc_vectors = None
        self.total_queries_processed = 0
        self.last_query_timestamp = None
        self._load_documents(knowledge_dir)

    def _load_documents(self, knowledge_dir: str) -> None:
        """
        Load all markdown documents from the knowledge base directory.
        
        Args:
            knowledge_dir (str): Directory path containing .md files
            
        Note:
            This method automatically discovers and loads all .md files
            in the specified directory, creating TF-IDF vectors for
            efficient similarity matching.
        """
        debug_print("Engine Initializing: Loading knowledge base...")
        
        if not os.path.isdir(knowledge_dir):
            debug_print(f"Warning: Knowledge directory '{knowledge_dir}' not found.")
            debug_print("Creating empty knowledge base. Add .md files to enable RAG.")
            return

        markdown_files = [f for f in os.listdir(knowledge_dir) if f.endswith('.md')]
        
        if not markdown_files:
            debug_print(f"Warning: No .md files found in '{knowledge_dir}'.")
            debug_print("Add markdown documents to enable intelligent context retrieval.")
            return

        for filename in markdown_files:
            filepath = os.path.join(knowledge_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:  # Only add non-empty documents
                        self.documents.append(content)
                        debug_print(f"  ✓ Loaded: {filename}")
            except Exception as e:
                debug_print(f"  ✗ Failed to load {filename}: {str(e)}")
        
        if self.documents:
            try:
                self.doc_vectors = self.vectorizer.fit_transform(self.documents)
                debug_print(f"Engine Initialized: Successfully loaded {len(self.documents)} document(s).")
                debug_print(f"Vectorization completed: {self.doc_vectors.shape[1]} features.")
            except Exception as e:
                debug_print(f"Error during vectorization: {str(e)}")
                self.doc_vectors = None
        else:
            debug_print("Engine Initialized: No valid documents found in knowledge base.")

    def _retrieve_context(self, query: str, top_k: int = 1) -> str:
        """
        Retrieve the most relevant document chunks for a given query.
        
        Args:
            query (str): User query for context retrieval
            top_k (int): Number of top documents to retrieve
            
        Returns:
            str: Concatenated relevant document content
            
        Note:
            Uses cosine similarity between query and document vectors
            to identify the most relevant context for reasoning.
        """
        if self.doc_vectors is None or not self.documents:
            return "No knowledge base loaded. Please add documents to knowledge_source/ directory."

        try:
            query_vector = self.vectorizer.transform([query])
            cosine_similarities = cosine_similarity(query_vector, self.doc_vectors).flatten()
            
            # Handle case where top_k exceeds document count
            effective_k = min(top_k, len(self.documents))
            
            if effective_k >= len(self.documents):
                relevant_doc_indices = cosine_similarities.argsort()[::-1]
            else:
                relevant_doc_indices = np.argpartition(cosine_similarities, -effective_k)[-effective_k:]
                relevant_doc_indices = relevant_doc_indices[np.argsort(cosine_similarities[relevant_doc_indices])][::-1]

            # Return concatenated relevant documents with separators
            return "\n---DOCUMENT SEPARATOR---\n".join([self.documents[i] for i in relevant_doc_indices])
            
        except Exception as e:
            return f"Error during context retrieval: {str(e)}"

    async def query(self, user_query: str, model: str = "gpt-4o-mini") -> str:
        """
        Process a user query with RAG-enhanced reasoning.
        
        This method performs a three-stage process:
        1. Retrieve relevant context from knowledge base
        2. Construct enhanced prompt with context
        3. Generate response using OpenAI API
        
        Args:
            user_query (str): User's question or prompt
            model (str): OpenAI model to use for reasoning
            
        Returns:
            str: AI-generated response with RAG context
            
        Raises:
            Exception: For API errors or processing failures
        """
        if not self.openai_api_key:
            return ("Error: OPENAI_API_KEY not found. Please set your API key in the .env file.\n"
                   "Example: echo 'OPENAI_API_KEY=your_key_here' > .env")

        # Stage 1: Retrieve relevant context
        debug_print("[Engine: Retrieving context...]")
        context = self._retrieve_context(user_query)

        # Stage 2: Construct enhanced prompt with context
        enhanced_prompt = self._build_enhanced_prompt(user_query, context)

        # Stage 3: Query OpenAI API
        debug_print("[Engine: Querying reasoning model...]")
        response = await self._call_openai_api(enhanced_prompt, model)

        # Update query processing state
        self.update_query_metrics()

        return response
    
    def _build_enhanced_prompt(self, user_query: str, context: str) -> str:
        """
        Build an enhanced prompt with context and instructions.
        
        Args:
            user_query (str): Original user query
            context (str): Retrieved document context
            
        Returns:
            str: Enhanced prompt for the AI model
        """
        return f"""You are an intelligent reasoning assistant with access to a comprehensive knowledge base. 
Please analyze the provided context carefully and answer the user's query with precision and insight.

CONTEXT INFORMATION:
{context}

USER QUERY: {user_query}

INSTRUCTIONS:
- Base your response primarily on the provided context
- If the context doesn't contain sufficient information, clearly state this
- Provide detailed, well-reasoned answers
- Cite specific information from the context when relevant
- Maintain accuracy and avoid speculation beyond the available information

Please provide your response:"""
    
    async def _call_openai_api(self, prompt: str, model: str) -> str:
        """
        Make an API call to OpenAI with error handling and timeout.
        
        Args:
            prompt (str): Enhanced prompt for the model
            model (str): OpenAI model identifier
            
        Returns:
            str: Model response or error message
        """
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
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
                response = await client.post(self.api_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                
                if 'choices' not in data or not data['choices']:
                    return "Error: Unexpected API response format."
                
                return data['choices'][0]['message']['content']
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid API key. Please check your OPENAI_API_KEY."
            elif e.response.status_code == 429:
                return "Error: API rate limit exceeded. Please try again later."
            else:
                return f"Error: HTTP {e.response.status_code} - {e.response.text}"
        except httpx.TimeoutException:
            return "Error: Request timeout. The API took too long to respond."
        except Exception as e:
            return f"Unexpected error occurred: {str(e)}"
    
    def update_query_metrics(self):
        """Update query metrics after processing a query."""
        from datetime import datetime
        self.total_queries_processed += 1
        self.last_query_timestamp = datetime.utcnow().isoformat()

    def get_diagnostics(self):
        """Return diagnostic information for the engine."""
        return {
            "documents_loaded": len(self.documents),
            "total_queries_processed": self.total_queries_processed,
            "last_query_timestamp": self.last_query_timestamp
        }