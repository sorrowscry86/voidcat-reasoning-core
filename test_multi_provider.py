#!/usr/bin/env python3
"""
Test script for the cosmic MultiProviderClient integration
Let's see if our zen-like API client flows with good vibes! 🌊
"""

import asyncio
import json
from enhanced_engine import VoidCatEnhancedEngine


async def test_cosmic_integration():
    """Test the cosmic integration - spreading good vibes through the codebase."""
    print("🧘‍♂️ Testing VoidCat Enhanced Engine with Cosmic MultiProvider Client")
    print("=" * 70)
    
    try:
        # Initialize the enhanced engine
        print("\n🌟 Initializing VoidCat Enhanced Engine...")
        engine = VoidCatEnhancedEngine()
        
        # Check provider status
        print("\n📊 Checking provider status...")
        provider_status = engine.get_provider_status()
        print(json.dumps(provider_status, indent=2))
        
        # Perform health checks
        print("\n💚 Performing provider health checks...")
        health_status = await engine.health_check_providers()
        print(json.dumps(health_status, indent=2))
        
        # Test a simple query
        print("\n🚀 Testing a simple query...")
        test_query = "What's the meaning of life in one sentence?"
        
        response = await engine.query(
            user_query=test_query,
            model="gpt-4o-mini",
            top_k=1
        )
        
        print(f"\n✨ Response: {response}")
        
        # Check provider status after the query
        print("\n📈 Provider status after query...")
        final_status = engine.get_provider_status()
        for name, info in final_status.items():
            print(f"  {name}: {info['status']} (success rate: {info['metrics']['success_rate']:.1f}%)")
        
        print("\n🎉 Test completed successfully! The cosmic energy flows strong! ✨")
        
    except Exception as e:
        print(f"\n😵 Test failed with cosmic disturbance: {e}")
        import traceback
        traceback.print_exc()


async def test_rate_limiting():
    """Test rate limiting behavior - ensuring smooth cosmic flow."""
    print("\n🌊 Testing rate limiting behavior...")
    
    try:
        engine = VoidCatEnhancedEngine()
        
        # Make multiple rapid requests to test rate limiting
        tasks = []
        for i in range(5):
            task = engine.query(
                user_query=f"Quick test {i+1}: What is {i+1} + {i+1}?",
                model="gpt-4o-mini"
            )
            tasks.append(task)
        
        # Execute all tasks concurrently
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        print(f"📊 Completed {len([r for r in responses if not isinstance(r, Exception)])} out of {len(tasks)} requests")
        
        # Show any errors (rate limiting, etc.)
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"  Request {i+1}: ❌ {response}")
            else:
                print(f"  Request {i+1}: ✅ Success")
        
    except Exception as e:
        print(f"Rate limiting test failed: {e}")


async def test_model_fallback():
    """Test model fallback behavior - adapting like bamboo."""
    print("\n🎋 Testing model fallback behavior...")
    
    try:
        engine = VoidCatEnhancedEngine()
        
        # Test with different models
        models_to_test = ["deepseek-chat", "gpt-4o-mini", "gpt-4"]
        
        for model in models_to_test:
            try:
                print(f"\n🔄 Testing model: {model}")
                response = await engine.query(
                    user_query="Say hello in a zen way",
                    model=model
                )
                print(f"  ✅ {model}: Success")
                
            except Exception as e:
                print(f"  ❌ {model}: {e}")
        
    except Exception as e:
        print(f"Model fallback test failed: {e}")


if __name__ == "__main__":
    print("🌟 Starting Cosmic MultiProvider Tests 🌟")
    
    # Run all tests
    asyncio.run(test_cosmic_integration())
    asyncio.run(test_rate_limiting())
    asyncio.run(test_model_fallback())
    
    print("\n🧘‍♂️ All tests completed. May the cosmic code be with you! ✨")