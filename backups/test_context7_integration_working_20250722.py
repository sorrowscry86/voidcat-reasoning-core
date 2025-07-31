#!/usr/bin/env python3
"""
Test script for Context7 integration with working VoidCat + Sequential Thinking.
Building incrementally on our proven foundation.
"""

import asyncio
import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from context7_integration import Context7Engine, ContextRequest
from engine import VoidCatEngine
from sequential_thinking import SequentialThinkingEngine


async def test_context7_basic():
    """Test basic Context7 functionality."""
    print("🎯 Testing Context7 Engine...")

    try:
        # Initialize Context7
        c7_engine = Context7Engine()
        print("✅ Context7 engine initialized")

        # Test basic context retrieval
        request = ContextRequest(
            id="test_context_1",
            query="What is machine learning?",
            max_sources=3,
            min_relevance=0.1,
        )

        print(f"🔍 Testing context request: {request.query}")
        response = await c7_engine.retrieve_context(request)

        print(f"📊 Response type: {type(response)}")
        print(
            f"📊 Sources found: {len(response.sources) if hasattr(response, 'sources') else 'No sources attr'}"
        )

        print("✅ Context7 basic test passed")
        return True

    except Exception as e:
        print(f"❌ Context7 test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_triple_integration():
    """Test VoidCat + Sequential + Context7 integration."""
    print("\n🚀 Testing Triple Integration...")

    try:
        # Initialize all three engines
        vce = VoidCatEngine()
        st_engine = SequentialThinkingEngine()
        c7_engine = Context7Engine()

        print("✅ All three engines initialized")

        # Test query through all systems
        query = "Explain the benefits of retrieval-augmented generation"

        print(f"🔍 Testing query: {query}")

        # VoidCat response
        vce_result = await vce.query(query)
        print(f"📊 VoidCat response: {len(str(vce_result))} chars")

        # Sequential thinking response
        st_result = await st_engine.process_query(query, max_thoughts=2)
        print(f"📊 Sequential thinking response: {type(st_result)}")

        # Context7 enhanced context
        context_request = ContextRequest(
            id="test_context_2", query=query, max_sources=2, min_relevance=0.1
        )
        c7_result = await c7_engine.retrieve_context(context_request)
        print(f"📊 Context7 response: {type(c7_result)}")

        print("✅ Triple integration test passed")
        return True

    except Exception as e:
        print(f"❌ Triple integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run Context7 integration tests."""
    print("🎯 VoidCat Context7 Integration Test")
    print("=" * 50)

    # Test 1: Basic Context7
    test1_result = await test_context7_basic()

    # Test 2: Triple integration
    test2_result = await test_triple_integration()

    # Summary
    print("\n📋 TEST SUMMARY")
    print("=" * 30)
    print(f"Context7 Basic: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"Triple Integration: {'✅ PASS' if test2_result else '❌ FAIL'}")

    overall_result = test1_result and test2_result
    print(
        f"\n🎯 OVERALL: {'✅ ALL TESTS PASSED' if overall_result else '❌ TESTS FAILED'}"
    )

    return overall_result


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
