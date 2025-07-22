#!/usr/bin/env python3
"""
Test script for knowledge retrieval from the new knowledge files.

This script tests the retrieval of information from the sequential-thinking.jsonld
and context7-overview.txt files.
"""

import os

from hybrid_vectorizer import HybridVectorizer
from multi_format_processor import MultiFormatProcessor


def print_separator():
    """Print a separator line."""
    print("\n" + "=" * 80 + "\n")


def test_knowledge_retrieval():
    """Test knowledge retrieval from the new knowledge files."""
    print("Testing Knowledge Retrieval")
    print_separator()

    # Initialize processor and vectorizer
    processor = MultiFormatProcessor()
    vectorizer = HybridVectorizer(
        tfidf_features=5000,
        semantic_embeddings=False,  # Disable semantic embeddings for testing
        compression_enabled=True,
    )

    # Process documents
    knowledge_dir = "knowledge_source"
    files = processor.discover_files(knowledge_dir)

    print(f"Found {len(files)} files in {knowledge_dir}:")
    for file in files:
        print(f"  - {file}")

    all_chunks = []
    all_metadata = []

    for file in files:
        print(f"\nProcessing: {file}")
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
    print_separator()
    print("Building index...")

    index = vectorizer.build_index(all_chunks, all_metadata)

    print(f"Index built with {len(all_chunks)} chunks")

    # Test queries about sequential thinking
    print_separator()
    print("Testing queries about Sequential Thinking:")

    sequential_thinking_queries = [
        "What is sequential thinking?",
        "What are the complexity levels in sequential thinking?",
        "What reasoning types are used in sequential thinking?",
        "How can sequential thinking be implemented?",
        "How does sequential thinking integrate with MCP?",
    ]

    for query in sequential_thinking_queries:
        print(f"\nQuery: {query}")

        results = vectorizer.query(query, top_k=1)

        for i, result in enumerate(results):
            print(f"Similarity: {result['similarity']:.4f}")
            print(f"Metadata: {result['metadata'].get('title', 'No title')}")
            print(
                f"File: {os.path.basename(result['metadata'].get('file_path', 'Unknown'))}"
            )
            print(f"Content Preview: {result['content'][:200]}...")

    # Test queries about Context7
    print_separator()
    print("Testing queries about Context7:")

    context7_queries = [
        "What is Context7?",
        "What are the core components of Context7?",
        "How does Context7 score relevance?",
        "What is context coherence in Context7?",
        "How does Context7 integrate with Sequential Thinking?",
    ]

    for query in context7_queries:
        print(f"\nQuery: {query}")

        results = vectorizer.query(query, top_k=1)

        for i, result in enumerate(results):
            print(f"Similarity: {result['similarity']:.4f}")
            print(f"Metadata: {result['metadata'].get('title', 'No title')}")
            print(
                f"File: {os.path.basename(result['metadata'].get('file_path', 'Unknown'))}"
            )
            print(f"Content Preview: {result['content'][:200]}...")

    print_separator()
    print("Knowledge Retrieval Test Completed")


if __name__ == "__main__":
    test_knowledge_retrieval()
