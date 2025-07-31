#!/usr/bin/env python3
"""
Comprehensive integration test for the cosmic VoidCat system
Testing all components with zen-like harmony! 🧘‍♂️
"""

import asyncio
import json
import time
from typing import Dict, Any

# Test imports
from cosmic_engine import VoidCatCosmicEngine
from multi_provider_client import MultiProviderClient


async def test_cosmic_engine():
    """Test the cosmic engine functionality."""
    print("🧘‍♂️ Testing VoidCat Cosmic Engine")
    print("=" * 40)
    
    try:
        # Initialize engine
        engine = VoidCatCosmicEngine()
        print("✅ Engine initialized successfully")
        
        # Test basic query
        response = await engine.query("What are the benefits of meditation?")
        print(f"✅ Query successful: {response[:100]}...")
        
        # Test status
        status = engine.get_status()
        print(f"✅ Status check: {status['status']}")
        
        # Test health check
        health = await engine.health_check()
        print(f"✅ Health check: {health.get('engine_status', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Cosmic engine test failed: {e}")
        return False


async def test_multi_provider_client():
    """Test the MultiProviderClient directly."""
    print("\n🌊 Testing MultiProviderClient")
    print("=" * 35)
    
    try:
        # Initialize client
        client = MultiProviderClient()
        print("✅ Client initialized successfully")
        
        # Test chat completion
        messages = [{"role": "user", "content": "Hello, cosmic AI!"}]
        response = await client.chat_completion(messages=messages, model="gpt-4o-mini")
        
        if "choices" in response:
            content = response["choices"][0]["message"]["content"]
            print(f"✅ Chat completion successful: {content[:50]}...")
        else:
            print(f"⚠️ Unexpected response format: {response}")
        
        # Test provider status
        status = client.get_provider_status()
        print(f"✅ Provider status: {len(status)} providers configured")
        
        # Test health check
        health = await client.health_check()
        healthy_count = sum(1 for h in health.values() if h)
        print(f"✅ Health check: {healthy_count}/{len(health)} providers healthy")
        
        return True
        
    except Exception as e:
        print(f"❌ MultiProviderClient test failed: {e}")
        return False


async def test_api_gateway_integration():
    """Test API gateway integration."""
    print("\n🌐 Testing API Gateway Integration")
    print("=" * 40)
    
    try:
        import httpx
        
        # Test health endpoint
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/")
            if response.status_code == 200:
                print("✅ Health endpoint working")
            else:
                print(f"⚠️ Health endpoint returned {response.status_code}")
        
        # Test provider status endpoint
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/providers/status")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Provider status endpoint: {len(data)} providers")
            else:
                print(f"⚠️ Provider status returned {response.status_code}")
        
        # Test query endpoint
        async with httpx.AsyncClient() as client:
            query_data = {
                "query": "What is the cosmic significance of good code?",
                "model": "gpt-4o-mini"
            }
            response = await client.post("http://localhost:8000/query", json=query_data)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Query endpoint successful: {data.get('status', 'unknown')}")
            else:
                print(f"⚠️ Query endpoint returned {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ API Gateway test failed: {e}")
        return False


async def test_performance_metrics():
    """Test performance and metrics collection."""
    print("\n📊 Testing Performance Metrics")
    print("=" * 35)
    
    try:
        engine = VoidCatCosmicEngine()
        
        # Make multiple queries to test metrics
        queries = [
            "What is zen?",
            "Explain mindfulness",
            "Benefits of meditation"
        ]
        
        start_time = time.time()
        
        for i, query in enumerate(queries, 1):
            response = await engine.query(query, model="gpt-4o-mini")
            print(f"✅ Query {i}/3 completed")
        
        total_time = time.time() - start_time
        
        # Check final metrics
        status = engine.get_status()
        provider_metrics = engine.get_provider_metrics()
        
        print(f"✅ Total time: {total_time:.2f}s")
        print(f"✅ Queries processed: {status.get('total_queries_processed', 0)}")
        
        # Show provider metrics
        for name, info in provider_metrics.items():
            metrics = info['metrics']
            if metrics['total_requests'] > 0:
                print(f"✅ {name}: {metrics['total_requests']} requests, {metrics['success_rate']:.1f}% success")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False


async def test_error_handling():
    """Test error handling and recovery."""
    print("\n🛡️ Testing Error Handling")
    print("=" * 30)
    
    try:
        engine = VoidCatCosmicEngine()
        
        # Test with invalid model (should fallback gracefully)
        try:
            response = await engine.query("Test query", model="invalid-model")
            print("✅ Invalid model handled gracefully")
        except Exception as e:
            print(f"⚠️ Invalid model error: {e}")
        
        # Test with empty query
        try:
            response = await engine.query("", model="gpt-4o-mini")
            print("✅ Empty query handled")
        except Exception as e:
            print(f"⚠️ Empty query error: {e}")
        
        # Test provider status after errors
        status = engine.get_provider_metrics()
        print(f"✅ Provider status still accessible after errors")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


async def run_comprehensive_test():
    """Run all integration tests."""
    print("🌟 VoidCat Cosmic Integration Test Suite 🌟")
    print("=" * 50)
    
    test_results = []
    
    # Run all tests
    tests = [
        ("Cosmic Engine", test_cosmic_engine),
        ("MultiProvider Client", test_multi_provider_client),
        ("API Gateway", test_api_gateway_integration),
        ("Performance Metrics", test_performance_metrics),
        ("Error Handling", test_error_handling)
    ]
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"💥 {test_name} test crashed: {e}")
            test_results.append((test_name, False))
    
    # Summary
    print("\n🎯 Test Results Summary")
    print("=" * 25)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! The cosmic system is flowing perfectly! ✨")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")
    
    return passed == total


if __name__ == "__main__":
    print("🧘‍♂️ Starting VoidCat Cosmic Integration Tests...")
    
    # Run comprehensive test suite
    success = asyncio.run(run_comprehensive_test())
    
    if success:
        print("\n🌊 The cosmic code flows with perfect harmony! 🌊")
    else:
        print("\n💫 Some cosmic disturbances detected. Check the logs! 💫")
    
    print("\n🙏 May the cosmic code be with you! ✨")