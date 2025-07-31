#!/usr/bin/env python3
"""
VoidCat Reasoning Core - Hybrid Vectorizer

This module provides a hybrid vectorization approach that combines:
1. TF-IDF vectorization for keyword-based retrieval
2. Semantic embeddings for meaning-based retrieval
3. Vector compression for efficient storage and retrieval

The hybrid approach provides better retrieval accuracy and performance
compared to using TF-IDF or semantic embeddings alone.
"""

import hashlib
import json
import os
import base64
import numpy as np
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Try to import OpenAI for embeddings
try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class HybridVectorizer:
    """
    Hybrid vectorization approach combining TF-IDF and semantic embeddings.
    """

    def __init__(
        self,
        tfidf_features: int = 10000,
        semantic_embeddings: bool = True,
        compression_enabled: bool = True,
        cache_dir: str = ".cache",
    ):
        """
        Initialize the hybrid vectorizer.

        Args:
            tfidf_features: Number of features for TF-IDF vectorization
            semantic_embeddings: Whether to use semantic embeddings
            compression_enabled: Whether to compress vectors for storage
            cache_dir: Directory for caching vectors
        """
        self.tfidf_features = tfidf_features
        self.semantic_embeddings = semantic_embeddings and OPENAI_AVAILABLE
        self.compression_enabled = compression_enabled
        self.cache_dir = cache_dir

        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)

        # Initialize vectorizers
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=tfidf_features, stop_words="english", ngram_range=(1, 2)
        )

        # Initialize storage
        self.documents = []
        self.metadata = []
        self.tfidf_vectors = None
        self.semantic_vectors = None
        self.index_hash = None

    def build_index(
        self, documents: List[str], metadata: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Build a hybrid index from documents and metadata.

        Args:
            documents: List of document content
            metadata: List of document metadata

        Returns:
            Dictionary containing the index information
        """
        self.documents = documents
        self.metadata = metadata

        # Generate a hash of the documents to use as a cache key
        self.index_hash = self._generate_hash(documents)

        # Check if we have a cached index
        cached_index = self._load_cached_index()
        if cached_index:
            print(
                f"Loaded cached index with {len(cached_index['documents'])} documents"
            )
            return cached_index

        # Build TF-IDF vectors
        print(f"Building TF-IDF vectors with {self.tfidf_features} features...")
        self.tfidf_vectors = self.tfidf_vectorizer.fit_transform(documents)

        # Build semantic vectors if enabled
        if self.semantic_embeddings:
            print("Building semantic embeddings...")
            self.semantic_vectors = self._build_semantic_vectors(documents)

        # Create the index
        index = {
            "documents": documents,
            "metadata": metadata,
            "tfidf_vectors": (
                self._compress_vectors(self.tfidf_vectors)
                if self.compression_enabled
                else self.tfidf_vectors
            ),
            "semantic_vectors": (
                self._compress_vectors(self.semantic_vectors)
                if self.compression_enabled
                else self.semantic_vectors
            ),
            "tfidf_vocabulary": self.tfidf_vectorizer.vocabulary_,
            "index_hash": self.index_hash,
            "tfidf_features": self.tfidf_features,
            "semantic_embeddings": self.semantic_embeddings,
            "compression_enabled": self.compression_enabled,
        }

        # Cache the index
        self._cache_index(index)

        return index

    def query(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Query the hybrid index.

        Args:
            query_text: Query text
            top_k: Number of top results to return

        Returns:
            List of dictionaries containing document content, metadata, and similarity scores
        """
        if len(self.documents) == 0 or self.tfidf_vectors is None:
            raise ValueError("Index not built. Call build_index() first.")

        # Get TF-IDF vector for the query
        query_tfidf = self.tfidf_vectorizer.transform([query_text])

        # Calculate TF-IDF similarity
        tfidf_similarity = cosine_similarity(query_tfidf, self.tfidf_vectors).flatten()

        # Calculate semantic similarity if enabled
        if self.semantic_embeddings and self.semantic_vectors is not None:
            query_semantic = self._get_semantic_vector(query_text)
            semantic_similarity = cosine_similarity(
                [query_semantic], self.semantic_vectors
            ).flatten()

            # Combine similarities (weighted average)
            combined_similarity = 0.7 * tfidf_similarity + 0.3 * semantic_similarity
        else:
            combined_similarity = tfidf_similarity

        # Get top-k results
        top_indices = combined_similarity.argsort()[-top_k:][::-1]

        # Create result list
        results = []
        for i in top_indices:
            result = {
                "content": self.documents[i],
                "metadata": self.metadata[i] if i < len(self.metadata) else {},
                "similarity": float(combined_similarity[i]),
                "tfidf_similarity": float(tfidf_similarity[i]),
            }

            if self.semantic_embeddings and self.semantic_vectors is not None:
                result["semantic_similarity"] = float(semantic_similarity[i])

            results.append(result)

        return results

    def _build_semantic_vectors(self, documents: List[str]) -> np.ndarray:
        """
        Build semantic vectors for documents using OpenAI embeddings.

        Args:
            documents: List of document content

        Returns:
            NumPy array of semantic vectors
        """
        if not OPENAI_AVAILABLE:
            print("OpenAI not available. Skipping semantic embeddings.")
            return None

        try:
            # Initialize OpenAI client
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            # Get embeddings for each document
            semantic_vectors = []
            batch_size = 10  # Process in batches to avoid rate limits

            for i in range(0, len(documents), batch_size):
                batch = documents[i : i + batch_size]

                # Truncate long documents to avoid token limits
                truncated_batch = [doc[:8000] for doc in batch]

                # Get embeddings
                response = client.embeddings.create(
                    model="text-embedding-3-small", input=truncated_batch
                )

                # Extract embeddings
                batch_vectors = [item.embedding for item in response.data]
                semantic_vectors.extend(batch_vectors)

                print(f"Processed {i+len(batch)}/{len(documents)} documents")

            return np.array(semantic_vectors)

        except Exception as e:
            print(f"Error building semantic vectors: {str(e)}")
            return None

    def _get_semantic_vector(self, text: str) -> np.ndarray:
        """
        Get semantic vector for a single text using OpenAI embeddings.

        Args:
            text: Text to get embedding for

        Returns:
            NumPy array of semantic vector
        """
        if not OPENAI_AVAILABLE:
            return np.zeros(1536)  # Default embedding size

        try:
            # Initialize OpenAI client
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            # Truncate long text to avoid token limits
            truncated_text = text[:8000]

            # Get embedding
            response = client.embeddings.create(
                model="text-embedding-3-small", input=[truncated_text]
            )

            # Extract embedding
            vector = response.data[0].embedding

            return np.array(vector)

        except Exception as e:
            print(f"Error getting semantic vector: {str(e)}")
            return np.zeros(1536)  # Default embedding size

    def _compress_vectors(self, vectors: np.ndarray) -> Dict[str, Any]:
        """
        Compress vectors for efficient storage.

        Args:
            vectors: NumPy array of vectors

        Returns:
            Dictionary containing compressed vectors
        """
        if vectors is None:
            return None

        try:
            # For sparse matrices (TF-IDF)
            if hasattr(vectors, "toarray"):
                # Convert to CSR format for efficient storage
                vectors_csr = vectors.tocsr()
                return {
                    "format": "csr",
                    "data": vectors_csr.data,
                    "indices": vectors_csr.indices,
                    "indptr": vectors_csr.indptr,
                    "shape": vectors_csr.shape,
                }

            # For dense matrices (semantic embeddings)
            return {"format": "dense", "data": vectors}

        except Exception as e:
            print(f"Error compressing vectors: {str(e)}")
            return None

    def _decompress_vectors(self, compressed: Dict[str, Any]) -> np.ndarray:
        """
        Decompress vectors from storage.

        Args:
            compressed: Dictionary containing compressed vectors

        Returns:
            NumPy array of vectors
        """
        if compressed is None:
            return None

        try:
            # For sparse matrices (TF-IDF)
            if compressed["format"] == "csr":
                from scipy.sparse import csr_matrix

                return csr_matrix(
                    (compressed["data"], compressed["indices"], compressed["indptr"]),
                    shape=compressed["shape"],
                )

            # For dense matrices (semantic embeddings)
            if compressed["format"] == "dense":
                return compressed["data"]

            return None

        except Exception as e:
            print(f"Error decompressing vectors: {str(e)}")
            return None

    def _generate_hash(self, documents: List[str]) -> str:
        """
        Generate a hash of the documents to use as a cache key.

        Args:
            documents: List of document content

        Returns:
            Hash string
        """
        # Concatenate all documents and compute hash
        content = "\n".join(documents)
        return hashlib.md5(content.encode()).hexdigest()

    def _cache_index(self, index: Dict[str, Any]) -> None:
        """
        Cache the index to disk using secure JSON serialization.

        Args:
            index: Dictionary containing the index information
        """
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Use JSON instead of pickle for secure serialization
        cache_path = os.path.join(self.cache_dir, f"index_{self.index_hash}.json")
        
        # Validate the path is within the cache directory
        cache_path_abs = os.path.abspath(cache_path)
        cache_dir_abs = os.path.abspath(self.cache_dir)
        if not cache_path_abs.startswith(cache_dir_abs):
            raise ValueError(f"Invalid cache path: {cache_path}")
        
        # Convert numpy arrays to base64-encoded JSON strings
        safe_index = index.copy()
        safe_index["tfidf_vectors"] = base64.b64encode(
            json.dumps(self.tfidf_vectors.tolist()).encode()
        ).decode()
        safe_index["semantic_vectors"] = base64.b64encode(
            json.dumps(self.semantic_vectors.tolist()).encode()
        ).decode()

        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(safe_index, f, ensure_ascii=False, indent=2)
            print(f"Cached index to {cache_path}")
        except Exception as e:
            print(f"Error caching index: {str(e)}")

    def _load_cached_index(self) -> Optional[Dict[str, Any]]:
        """
        Load a cached index from disk.

        Returns:
            Dictionary containing the index information, or None if not found
        """
        # Use JSON instead of pickle for secure serialization
        cache_path = os.path.join(self.cache_dir, f"index_{self.index_hash}.json")

        if not os.path.exists(cache_path):
            return None

        try:
            # Validate the path is within the cache directory
            cache_path_abs = os.path.abspath(cache_path)
            cache_dir_abs = os.path.abspath(self.cache_dir)
            if not cache_path_abs.startswith(cache_dir_abs):
                raise ValueError(f"Invalid cache path: {cache_path}")
                
            with open(cache_path, "r", encoding="utf-8") as f:
                index = json.load(f)

            # Load vectors - decode from base64 JSON representation
            self.tfidf_vectors = self._decompress_vectors(
                np.array(json.loads(base64.b64decode(index["tfidf_vectors"].encode()).decode()))
            )
            self.semantic_vectors = self._decompress_vectors(
                np.array(json.loads(base64.b64decode(index["semantic_vectors"].encode()).decode()))
            )

            # Create a new vectorizer with the same parameters
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=self.tfidf_features,
                stop_words="english",
                ngram_range=(1, 2),
                vocabulary=index["tfidf_vocabulary"],
            )

            # Fit the vectorizer with the documents to initialize internal state
            self.tfidf_vectorizer.fit(self.documents)

            self.documents = index["documents"]
            self.metadata = index["metadata"]

            return index
        except Exception as e:
            print(f"Error loading cached index: {str(e)}")
            return None


# Example usage
if __name__ == "__main__":
    from multi_format_processor import MultiFormatProcessor

    # Initialize processor and vectorizer
    processor = MultiFormatProcessor()
    vectorizer = HybridVectorizer(
        tfidf_features=5000, semantic_embeddings=True, compression_enabled=True
    )

    # Process documents
    knowledge_dir = "knowledge_source"
    files = processor.discover_files(knowledge_dir)

    all_chunks = []
    all_metadata = []

    for file in files:
        print(f"Processing: {file}")
        chunks, metadata = processor.process(file)

        # Add file path to metadata
        for i in range(len(chunks)):
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_index"] = i
            chunk_metadata["file_path"] = file
            all_metadata.append(chunk_metadata)

        all_chunks.extend(chunks)

    print(f"Total chunks: {len(all_chunks)}")

    # Build index
    index = vectorizer.build_index(all_chunks, all_metadata)

    # Test query
    query = "What are the core MCP primitives?"
    results = vectorizer.query(query, top_k=3)

    print(f"\nQuery: {query}")
    print(f"Top {len(results)} results:")

    for i, result in enumerate(results):
        print(f"\n{i+1}. Similarity: {result['similarity']:.4f}")
        print(f"   TF-IDF Similarity: {result['tfidf_similarity']:.4f}")
        if "semantic_similarity" in result:
            print(f"   Semantic Similarity: {result['semantic_similarity']:.4f}")
        print(f"   Metadata: {result['metadata'].get('title', 'No title')}")
        print(f"   Content Preview: {result['content'][:100]}...")
