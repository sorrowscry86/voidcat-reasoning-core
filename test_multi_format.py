#!/usr/bin/env python3
"""
Test script for the Multi-Format Processor.

This script tests the functionality of the multi-format processor
with different document types.
"""

import json
import os
from pathlib import Path

from multi_format_processor import MultiFormatProcessor


def print_separator():
    """Print a separator line."""
    print("\n" + "=" * 80 + "\n")


def test_processor():
    """Test the multi-format processor with different document types."""
    print("Testing Multi-Format Processor")
    print_separator()

    # Initialize processor
    processor = MultiFormatProcessor()

    # Test with existing files
    knowledge_dir = "knowledge_source"
    files = processor.discover_files(knowledge_dir)

    print(f"Found {len(files)} files in {knowledge_dir}:")
    for file in files:
        print(f"\nProcessing: {file}")
        chunks, metadata = processor.process(file)
        print(f"  Metadata:")
        for key, value in metadata.items():
            if key in ["keywords", "content_chunks"]:
                print(f"    {key}: {value[:3]}...")
            else:
                print(f"    {key}: {value}")
        print(f"  Chunks: {len(chunks)}")
        if chunks:
            print(f"  First chunk preview: {chunks[0][:100]}...")

    # Create test files for other formats
    test_dir = "test_files"
    os.makedirs(test_dir, exist_ok=True)

    # Create a test text file
    text_file = os.path.join(test_dir, "test.txt")
    with open(text_file, "w", encoding="utf-8") as f:
        f.write(
            "This is a test text file.\nIt has multiple lines.\nEach line contains some text."
        )

    # Create a test JSON file
    json_file = os.path.join(test_dir, "test.json")
    json_data = {
        "title": "Test JSON Document",
        "description": "This is a test JSON document for the multi-format processor.",
        "keywords": ["test", "json", "processor"],
        "sections": [
            {"name": "Introduction", "content": "This is the introduction."},
            {"name": "Methods", "content": "These are the methods."},
            {"name": "Results", "content": "These are the results."},
        ],
    }
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)

    # Create a test JSON-LD file
    jsonld_file = os.path.join(test_dir, "test.jsonld")
    jsonld_data = {
        "@context": "https://voidcat.dev/knowledge/v2",
        "@type": "OptimizedKnowledgeDocument",
        "id": "test-document",
        "version": "1.0",
        "title": "Test JSON-LD Document",
        "keywords": ["test", "jsonld", "processor"],
        "content_chunks": [
            {
                "chunk_id": "chunk_001",
                "content": "This is the first chunk of content.",
                "keywords": ["first", "chunk", "content"],
            },
            {
                "chunk_id": "chunk_002",
                "content": "This is the second chunk of content.",
                "keywords": ["second", "chunk", "content"],
            },
        ],
    }
    with open(jsonld_file, "w", encoding="utf-8") as f:
        json.dump(jsonld_data, f, indent=2)

    # Test with created files
    print_separator()
    print("Testing with created files:")
    test_files = [text_file, json_file, jsonld_file]

    for file in test_files:
        print(f"\nProcessing: {file}")
        chunks, metadata = processor.process(file)
        print(f"  Metadata:")
        for key, value in metadata.items():
            if key in ["keywords", "content_chunks"]:
                print(f"    {key}: {value[:3]}...")
            else:
                print(f"    {key}: {value}")
        print(f"  Chunks: {len(chunks)}")
        if chunks:
            print(f"  First chunk preview: {chunks[0][:100]}...")

    # Clean up test files
    for file in test_files:
        os.remove(file)
    os.rmdir(test_dir)

    print_separator()
    print("Multi-Format Processor Test Completed")


if __name__ == "__main__":
    test_processor()
