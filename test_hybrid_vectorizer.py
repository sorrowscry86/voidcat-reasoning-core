#!/usr/bin/env python3
"""
Test script for the Hybrid Vectorizer.

This script tests the functionality of the hybrid vectorizer
with the multi-format processor.
"""

import os
import time
from pathlib import Path

from hybrid_vectorizer import HybridVectorizer
from multi_format_processor import MultiFormatProcessor


def print_separator():
    """Print a separator line."""
    print("\n" + "=" * 80 + "\n")


def test_vectorizer():
    """Test the hybrid vectorizer with the multi-format processor."""
    print("Testing Hybrid Vectorizer")
    print_separator()

    # Check if OpenAI API key is set
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("Warning: OPENAI_API_KEY not set. Semantic embeddings will be disabled.")
        semantic_embeddings = False
    else:
        semantic_embeddings = True

    # Initialize processor and vectorizer
    processor = MultiFormatProcessor()
    vectorizer = HybridVectorizer(
        tfidf_features=5000,
        semantic_embeddings=semantic_embeddings,
        compression_enabled=True,
    )

    # Process documents
    knowledge_dir = "knowledge_source"
    files = processor.discover_files(knowledge_dir)

    print(f"Found {len(files)} files in {knowledge_dir}:")

    all_chunks = []
    all_metadata = []

    start_time = time.time()

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

    processing_time = time.time() - start_time
    print(f"Processing completed in {processing_time:.2f} seconds")
    print(f"Total chunks: {len(all_chunks)}")

    # Build index
    print_separator()
    print("Building index...")

    start_time = time.time()
    index = vectorizer.build_index(all_chunks, all_metadata)
    indexing_time = time.time() - start_time

    print(f"Indexing completed in {indexing_time:.2f} seconds")
    print(f"Index features: {index['tfidf_features']}")
    print(
        f"Semantic embeddings: {'Enabled' if index['semantic_embeddings'] else 'Disabled'}"
    )
    print(f"Compression: {'Enabled' if index['compression_enabled'] else 'Disabled'}")

    # Test queries
    print_separator()
    print("Testing queries...")

    test_queries = [
        "What are the core MCP primitives?",
        "How does the Model Context Protocol work?",
        "What tools are available in the MCP?",
        "Explain the JSON-RPC protocol used in MCP",
        "What clients support the Model Context Protocol?",
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")

        start_time = time.time()
        results = vectorizer.query(query, top_k=3)
        query_time = time.time() - start_time

        print(f"Query completed in {query_time:.4f} seconds")
        print(f"Top {len(results)} results:")

        for i, result in enumerate(results):
            print(f"\n{i+1}. Similarity: {result['similarity']:.4f}")
            print(f"   TF-IDF Similarity: {result['tfidf_similarity']:.4f}")
            if "semantic_similarity" in result:
                print(f"   Semantic Similarity: {result['semantic_similarity']:.4f}")
            print(f"   Metadata: {result['metadata'].get('title', 'No title')}")
            print(f"   Content Preview: {result['content'][:100]}...")

    # Test cached loading
    print_separator()
    print("Testing cached loading...")

    start_time = time.time()
    vectorizer2 = HybridVectorizer(
        tfidf_features=5000,
        semantic_embeddings=semantic_embeddings,
        compression_enabled=True,
    )
    index2 = vectorizer2.build_index(all_chunks, all_metadata)
    cached_loading_time = time.time() - start_time

    print(f"Cached loading completed in {cached_loading_time:.2f} seconds")
    print(f"Speedup: {indexing_time / cached_loading_time:.2f}x faster")

    # Clean up cache
    cache_dir = ".cache"
    if os.path.exists(cache_dir):
        print(f"\nCache directory: {cache_dir}")
        cache_files = list(Path(cache_dir).glob("index_*.pkl"))
        print(f"Cache files: {len(cache_files)}")

    print_separator()
    print("Hybrid Vectorizer Test Completed")


if __name__ == "__main__":
    test_vectorizer()
