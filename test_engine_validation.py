#!/usr/bin/env python3
"""
VoidCat Reasoning Core - Engine Validation Script

This script tests the core functionality of the VoidCat Reasoning Engine:
1. Document loading and processing
2. TF-IDF vectorization
3. Context retrieval
4. Query processing with OpenAI API

Usage:
    python test_engine_validation.py
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from context7_integration import Context7Engine
from engine import VoidCatEngine
from enhanced_engine import VoidCatEnhancedEngine
from sequential_thinking import SequentialThinkingEngine


def print_header(title: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")


def print_result(test_name: str, success: bool, message: str = "") -> None:
    """Print a formatted test result."""
    status = "✅ PASSED" if success else "❌ FAILED"
    print(f"{status} | {test_name}")
    if message:
        print(f"       {message}")


async def test_base_engine() -> bool:
    """Test the base VoidCat Engine functionality."""
    print_header("Testing Base Engine")

    try:
        # Initialize engine
        print("Initializing VoidCatEngine...")
        engine = VoidCatEngine()

        # Check if documents were loaded
        doc_count = (
            len(engine.documents)
            if hasattr(engine, "documents") and engine.documents
            else 0
        )
        print_result("Document Loading", doc_count > 0, f"Loaded {doc_count} documents")

        # Check if vectorization was performed
        has_vectors = hasattr(engine, "doc_vectors") and engine.doc_vectors is not None
        print_result(
            "TF-IDF Vectorization",
            has_vectors,
            f"Vector shape: {engine.doc_vectors.shape if has_vectors else 'N/A'}",
        )

        # Test a simple query
        if os.getenv("OPENAI_API_KEY"):
            print("Testing query with OpenAI API...")
            test_query = "What are the core components of the VoidCat system?"
            response = await engine.query(test_query)
            query_success = not response.startswith("Error:")
            print_result(
                "Query Processing",
                query_success,
                "Query successful" if query_success else f"Error: {response}",
            )
        else:
            print_result(
                "Query Processing", False, "OPENAI_API_KEY not set in environment"
            )

        return True
    except Exception as e:
        print(f"Error testing base engine: {str(e)}")
        import traceback

        print(traceback.format_exc())
        return False


async def test_enhanced_engine() -> bool:
    """Test the enhanced VoidCat Engine functionality."""
    print_header("Testing Enhanced Engine")

    try:
        # Initialize engine
        print("Initializing VoidCatEnhancedEngine...")
        engine = VoidCatEnhancedEngine()

        # Check if engine was initialized
        engine_ready = engine is not None
        print_result("Engine Initialization", engine_ready)

        # Test diagnostics
        try:
            diagnostics = engine.get_comprehensive_diagnostics()
            has_diagnostics = isinstance(diagnostics, dict) and len(diagnostics) > 0
            print_result(
                "Diagnostics",
                has_diagnostics,
                (
                    f"Found {len(diagnostics)} diagnostic entries"
                    if has_diagnostics
                    else "No diagnostics"
                ),
            )
        except Exception as e:
            print_result("Diagnostics", False, f"Error: {str(e)}")

        # Test a simple query if API key is available
        if os.getenv("OPENAI_API_KEY") or os.getenv("DEEPSEEK_API_KEY"):
            print("Testing enhanced query...")
            test_query = "What is sequential thinking in the context of VoidCat?"
            try:
                response = await engine.query(test_query)
                query_success = isinstance(response, str) and len(response) > 0
                print_result(
                    "Enhanced Query",
                    query_success,
                    "Query successful" if query_success else "Empty response",
                )
            except Exception as e:
                print_result("Enhanced Query", False, f"Error: {str(e)}")
        else:
            print_result("Enhanced Query", False, "API keys not set in environment")

        return True
    except Exception as e:
        print(f"Error testing enhanced engine: {str(e)}")
        import traceback

        print(traceback.format_exc())
        return False


async def test_sequential_thinking() -> bool:
    """Test the Sequential Thinking Engine functionality."""
    print_header("Testing Sequential Thinking")

    try:
        # Initialize engine
        print("Initializing SequentialThinkingEngine...")
        engine = SequentialThinkingEngine()

        # Check if engine was initialized
        engine_ready = engine is not None
        print_result("Engine Initialization", engine_ready)

        # Test complexity assessment
        test_query = "What is the meaning of life?"
        complexity = engine.assess_complexity(test_query)
        print_result(
            "Complexity Assessment",
            complexity is not None,
            f"Assessed complexity: {complexity.value if complexity else 'N/A'}",
        )

        # Test query processing
        try:
            print("Testing sequential thinking query...")
            result = await engine.process_query(test_query, max_thoughts=5)
            query_success = isinstance(result, dict) and "final_response" in result
            print_result(
                "Query Processing",
                query_success,
                (
                    f"Generated {result.get('thought_count', 0)} thoughts"
                    if query_success
                    else "Failed to process"
                ),
            )
        except Exception as e:
            print_result("Query Processing", False, f"Error: {str(e)}")

        return True
    except Exception as e:
        print(f"Error testing sequential thinking: {str(e)}")
        import traceback

        print(traceback.format_exc())
        return False


async def test_context7_integration() -> bool:
    """Test the Context7 integration functionality."""
    print_header("Testing Context7 Integration")

    try:
        # Initialize engine
        print("Initializing Context7Engine...")
        engine = Context7Engine()

        # Check if engine was initialized
        engine_ready = engine is not None
        print_result("Engine Initialization", engine_ready)

        # Ensure initialization
        await engine.ensure_initialized()

        # Check context sources
        source_count = (
            len(engine.context_sources) if hasattr(engine, "context_sources") else 0
        )
        print_result(
            "Context Sources",
            source_count > 0,
            f"Loaded {source_count} context sources",
        )

        # Test context retrieval
        from context7_integration import ContextRequest

        test_query = "What is the VoidCat system architecture?"
        request = ContextRequest(
            id="test_request_1", query=test_query, max_sources=3, min_relevance=0.1
        )

        try:
            print("Testing context retrieval...")
            response = await engine.retrieve_context(request)
            retrieval_success = response is not None and hasattr(response, "sources")
            source_count = len(response.sources) if retrieval_success else 0
            print_result(
                "Context Retrieval",
                retrieval_success,
                (
                    f"Retrieved {source_count} sources"
                    if retrieval_success
                    else "Failed to retrieve context"
                ),
            )
        except Exception as e:
            print_result("Context Retrieval", False, f"Error: {str(e)}")

        return True
    except Exception as e:
        print(f"Error testing Context7 integration: {str(e)}")
        import traceback

        print(traceback.format_exc())
        return False


async def main():
    """Main test function."""
    print_header("VoidCat Reasoning Core - Engine Validation")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    print(f"OpenAI API Key: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not Set'}")
    print(f"DeepSeek API Key: {'Set' if os.getenv('DEEPSEEK_API_KEY') else 'Not Set'}")

    # Run tests
    base_result = await test_base_engine()
    enhanced_result = await test_enhanced_engine()
    sequential_result = await test_sequential_thinking()
    context7_result = await test_context7_integration()

    # Print summary
    print_header("Test Summary")
    print_result("Base Engine", base_result)
    print_result("Enhanced Engine", enhanced_result)
    print_result("Sequential Thinking", sequential_result)
    print_result("Context7 Integration", context7_result)

    overall_success = (
        base_result and enhanced_result and sequential_result and context7_result
    )
    print("\nOverall Result:", "✅ PASSED" if overall_success else "❌ FAILED")

    # Update implementation checklist
    print("\nNext steps:")
    print("1. Review test results and fix any issues")
    print("2. Update implementation_checklist.md with progress")
    print("3. Focus on high-priority tasks identified in the checklist")


if __name__ == "__main__":
    asyncio.run(main())
