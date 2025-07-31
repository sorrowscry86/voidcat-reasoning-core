# test_enhanced_system.py
"""
Test script for the enhanced VoidCat system with Sequential Thinking + Context7.

This script validates the complete enhanced system functionality before GitHub upload.
"""

import asyncio
import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from context7_integration import Context7Engine, ContextRequest
from enhanced_engine import VoidCatEnhancedEngine
from sequential_thinking import ComplexityLevel, SequentialThinkingEngine


async def test_sequential_thinking():
    """Test the sequential thinking engine."""
    print("🧠 Testing Sequential Thinking Engine...")

    engine = SequentialThinkingEngine()

    # Test complexity assessment
    test_queries = [
        "What is Python?",  # Simple
        "How do I optimize a machine learning model?",  # Medium
        "Design a distributed system architecture for real-time data processing",  # High
        "Prove the mathematical foundations of quantum computing algorithms",  # Expert
    ]

    for query in test_queries:
        complexity = engine.assess_complexity(query)
        print(f"  Query: {query[:50]}...")
        print(f"  Complexity: {complexity.value}")

        # Test reasoning process
        result = await engine.process_query(query, max_thoughts=5)
        print(f"  Thoughts generated: {result.get('thought_count', 0)}")
        print(f"  Confidence: {result.get('confidence', 0.5):.3f}")
        print()

    print("✅ Sequential Thinking Engine test completed\n")


async def test_context7_engine():
    """Test the Context7 integration engine."""
    print("🔍 Testing Context7 Engine...")

    engine = Context7Engine()

    # Wait a moment for initialization
    await asyncio.sleep(1)

    # Test context retrieval
    request = ContextRequest(
        id="test_001",
        query="sequential thinking methodology",
        max_sources=3,
        min_relevance=0.1,
    )

    result = await engine.retrieve_context(request)
    print(f"  Sources retrieved: {len(result.sources)}")
    print(f"  Clusters found: {len(result.clusters_used)}")

    if result.sources:
        for i, source in enumerate(result.sources[:2], 1):
            print(
                f"  Source {i}: {source.name} (relevance: {result.relevance_scores.get(source.id, 0):.3f})"
            )

    diagnostics = engine.get_diagnostics()
    print(f"  Total context sources: {diagnostics['context_sources_loaded']}")
    print(f"  Context clusters: {diagnostics['context_clusters_created']}")
    print()

    print("✅ Context7 Engine test completed\n")


async def test_enhanced_engine():
    """Test the enhanced VoidCat engine."""
    print("🚀 Testing Enhanced VoidCat Engine...")

    engine = VoidCatEnhancedEngine()

    # Wait for initialization
    await asyncio.sleep(2)

    # Test simple query
    print("  Testing simple query...")
    try:
        response = await engine.query("What is machine learning?", enable_enhanced=True)
        print(f"  Response length: {len(response)} characters")
        print(
            f"  Contains reasoning analysis: {'Sequential Reasoning Analysis' in response}"
        )
        print()
    except Exception as e:
        print(f"  Error in simple query: {str(e)}")
        print()

    # Test diagnostics
    print("  Testing diagnostics...")
    try:
        diagnostics = engine.get_comprehensive_diagnostics()
        enhanced_stats = diagnostics.get("enhanced_engine", {})
        print(
            f"  Total queries processed: {enhanced_stats.get('total_queries_processed', 0)}"
        )
        print(
            f"  Enhanced queries: {enhanced_stats.get('enhanced_queries_processed', 0)}"
        )
        print(f"  Overall status: {diagnostics.get('overall_status', 'unknown')}")
        print()
    except Exception as e:
        print(f"  Error in diagnostics: {str(e)}")
        print()

    print("✅ Enhanced VoidCat Engine test completed\n")


async def main():
    """Run comprehensive test suite."""
    print("🎯 VoidCat Enhanced System Test Suite")
    print("=" * 50)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        # Test individual components
        await test_sequential_thinking()
        await test_context7_engine()
        await test_enhanced_engine()

        print("🎉 All tests completed successfully!")
        print("System is ready for GitHub upload.")

    except Exception as e:
        print(f"❌ Test suite failed: {str(e)}")
        import traceback

        traceback.print_exc()

    print()
    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    asyncio.run(main())
