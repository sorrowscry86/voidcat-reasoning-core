#!/usr/bin/env python3
"""
Test script for Sequential Thinking integration with working VoidCat engine.
This builds upon our known working foundation.
"""

import asyncio
import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import VoidCatEngine
from sequential_thinking import SequentialThinkingEngine


async def test_sequential_thinking_basic():
    """Test basic sequential thinking functionality."""
    print("🧠 Testing Sequential Thinking Engine...")

    try:
        # Initialize sequential thinking
        st_engine = SequentialThinkingEngine()
        print("✅ Sequential thinking engine initialized")

        # Test simple query
        test_query = "What is the main purpose of the VoidCat system?"

        print(f"🔍 Testing query: {test_query}")
        result = await st_engine.process_query(test_query, max_thoughts=3)

        print(f"📊 Result type: {type(result)}")
        print(
            f"� Result keys: {result.keys() if isinstance(result, dict) else 'Not dict'}"
        )

        print("✅ Sequential thinking basic test passed")
        return True

    except Exception as e:
        print(f"❌ Sequential thinking test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_integration_with_voidcat():
    """Test sequential thinking integration with VoidCat engine."""
    print("\n🔗 Testing Sequential + VoidCat Integration...")

    try:
        # Initialize both engines
        vce = VoidCatEngine()
        st_engine = SequentialThinkingEngine()

        print("✅ Both engines initialized")

        # Test combined functionality
        query = "How does RAG enhance reasoning capabilities?"

        print(f"🔍 VoidCat query: {query}")
        vce_result = await vce.query(query)

        print(f"🧠 Sequential thinking query: {query}")
        st_result = await st_engine.process_query(query, max_thoughts=2)

        print("✅ Both engines responded successfully")
        print(f"📊 VoidCat result length: {len(str(vce_result))}")
        print(f"📊 Sequential result type: {type(st_result)}")

        return True

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run sequential thinking integration tests."""
    print("🚀 VoidCat Sequential Thinking Integration Test")
    print("=" * 50)

    # Test 1: Basic sequential thinking
    test1_result = await test_sequential_thinking_basic()

    # Test 2: Integration with VoidCat
    test2_result = await test_integration_with_voidcat()

    # Summary
    print("\n📋 TEST SUMMARY")
    print("=" * 30)
    print(f"Sequential Thinking Basic: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"VoidCat Integration: {'✅ PASS' if test2_result else '❌ FAIL'}")

    overall_result = test1_result and test2_result
    print(
        f"\n🎯 OVERALL: {'✅ ALL TESTS PASSED' if overall_result else '❌ TESTS FAILED'}"
    )

    return overall_result


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
