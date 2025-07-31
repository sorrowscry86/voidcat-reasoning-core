#!/usr/bin/env python3
"""
Test the enhanced engine with our cosmic MultiProviderClient integration
Let's see the full VoidCat system flow with zen-like API calls! 🌊
"""

import asyncio
import json
import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from enhanced_engine import VoidCatEnhancedEngine
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("This might be due to missing dependencies. Let's test the core functionality...")
    sys.exit(1)


async def test_enhanced_engine_with_cosmic_client():
    """Test the enhanced engine with our cosmic MultiProviderClient."""
    print("🧘‍♂️ Testing VoidCat Enhanced Engine with Cosmic MultiProvider")
    print("=" * 65)
    
    try:
        # Initialize the enhanced engine (this will use our MultiProviderClient)
        print("\n🌟 Initializing VoidCat Enhanced Engine...")
        engine = VoidCatEnhancedEngine()
        
        # Check provider status through the engine
        print("\n📊 Checking provider status through engine...")
        try:
            provider_status = engine.get_provider_status()
            for name, info in provider_status.items():
                print(f"  {name}: {info['status']} (priority: {info['priority']})")
        except Exception as e:
            print(f"  ⚠️ Provider status check failed: {e}")
        
        # Test a simple query through the enhanced engine
        print("\n🚀 Testing query through enhanced engine...")
        test_query = "What are the key principles of good software architecture?"
        
        response = await engine.query(
            user_query=test_query,
            model="deepseek-chat",  # Test with DeepSeek model
            top_k=1
        )
        
        print(f"\n✨ Enhanced Engine Response:")
        print(f"Query: {test_query}")
        print(f"Response: {response[:200]}..." if len(response) > 200 else f"Response: {response}")
        
        # Test with different model
        print(f"\n🔄 Testing with different model (gpt-4o-mini)...")
        test_query2 = "Explain the concept of rate limiting in APIs"
        
        response2 = await engine.query(
            user_query=test_query2,
            model="gpt-4o-mini",
            top_k=1
        )
        
        print(f"Query: {test_query2}")
        print(f"Response: {response2[:200]}..." if len(response2) > 200 else f"Response: {response2}")
        
        # Check final provider metrics
        print(f"\n📈 Final Provider Metrics:")
        try:
            final_status = engine.get_provider_status()
            for name, info in final_status.items():
                metrics = info['metrics']
                print(f"  {name}: {metrics['total_requests']} requests, {metrics['success_rate']:.1f}% success")
        except Exception as e:
            print(f"  ⚠️ Metrics check failed: {e}")
        
        # Test health check
        print(f"\n💚 Provider Health Check:")
        try:
            health = await engine.health_check_providers()
            for name, is_healthy in health.items():
                status_emoji = "💚" if is_healthy else "💔"
                print(f"  {name}: {status_emoji} {'Healthy' if is_healthy else 'Unhealthy'}")
        except Exception as e:
            print(f"  ⚠️ Health check failed: {e}")
        
        print(f"\n🎉 Enhanced engine integration test completed! The cosmic flow is strong! ✨")
        
    except Exception as e:
        print(f"\n😵 Test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_fallback_behavior():
    """Test the fallback behavior between providers."""
    print(f"\n🎋 Testing Provider Fallback Behavior")
    print("=" * 40)
    
    try:
        engine = VoidCatEnhancedEngine()
        
        # Test with different models to trigger different providers
        test_cases = [
            ("deepseek-chat", "DeepSeek model test"),
            ("gpt-4o-mini", "OpenAI model test"),
            ("gpt-4", "GPT-4 model test")
        ]
        
        for model, description in test_cases:
            try:
                print(f"\n🔄 {description} (model: {model})")
                response = await engine.query(
                    user_query=f"Say hello and mention you're using {model}",
                    model=model,
                    top_k=1
                )
                print(f"  ✅ Success: {response[:100]}...")
                
            except Exception as e:
                print(f"  ❌ Failed: {e}")
        
    except Exception as e:
        print(f"Fallback test failed: {e}")


async def test_concurrent_requests():
    """Test concurrent requests to see rate limiting and load balancing."""
    print(f"\n🌊 Testing Concurrent Requests")
    print("=" * 35)
    
    try:
        engine = VoidCatEnhancedEngine()
        
        # Create multiple concurrent requests
        print("Making 5 concurrent requests...")
        tasks = []
        for i in range(5):
            task = engine.query(
                user_query=f"Quick test {i+1}: What is the square of {i+1}?",
                model="gpt-4o-mini",
                top_k=1
            )
            tasks.append(task)
        
        # Execute all tasks concurrently
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze results
        successful = 0
        failed = 0
        
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"  Request {i+1}: ❌ {response}")
                failed += 1
            else:
                print(f"  Request {i+1}: ✅ Success")
                successful += 1
        
        print(f"\n📊 Concurrent Request Results:")
        print(f"  Successful: {successful}/{len(tasks)}")
        print(f"  Failed: {failed}/{len(tasks)}")
        
        # Check provider status after concurrent load
        try:
            status = engine.get_provider_status()
            print(f"\n📈 Provider Status After Concurrent Load:")
            for name, info in status.items():
                metrics = info['metrics']
                rate_limiter = info['rate_limiter']
                print(f"  {name}: {metrics['total_requests']} requests, "
                      f"{rate_limiter['current_tokens']:.1f} tokens remaining")
        except Exception as e:
            print(f"  ⚠️ Status check failed: {e}")
        
    except Exception as e:
        print(f"Concurrent test failed: {e}")


if __name__ == "__main__":
    print("🌟 Starting Enhanced Engine Integration Tests 🌟")
    
    # Run all tests
    asyncio.run(test_enhanced_engine_with_cosmic_client())
    asyncio.run(test_fallback_behavior())
    asyncio.run(test_concurrent_requests())
    
    print("\n🧘‍♂️ All integration tests completed! The cosmic code flows through VoidCat! ✨")