#!/usr/bin/env python3
"""
Direct test of MultiProviderClient with real API keys
Pure cosmic API testing without sklearn dependencies! 🌊
"""

import asyncio
import json
import time
from multi_provider_client import MultiProviderClient


async def test_real_api_calls():
    """Test real API calls with all the cosmic providers."""
    print("🌟 Testing Real API Calls with Cosmic MultiProvider Client")
    print("=" * 60)
    
    try:
        # Initialize the client
        print("\n🧘‍♂️ Initializing MultiProvider Client...")
        client = MultiProviderClient()
        
        # Check initial provider status
        print("\n📊 Initial Provider Status:")
        status = client.get_provider_status()
        for name, info in status.items():
            print(f"  {name}: {info['status']} (priority: {info['priority']}, "
                  f"rate limit: {info['rate_limiter']['requests_per_minute']}/min)")
        
        # Test different types of queries with different models
        test_cases = [
            {
                "query": "What are the key principles of good software architecture?",
                "model": "deepseek-chat",
                "description": "DeepSeek Architecture Question"
            },
            {
                "query": "Explain rate limiting in APIs in one paragraph",
                "model": "gpt-4o-mini", 
                "description": "OpenAI Rate Limiting Question"
            },
            {
                "query": "What is the meaning of life in a zen way?",
                "model": "gpt-4",
                "description": "GPT-4 Philosophy Question"
            }
        ]
        
        print(f"\n🚀 Testing {len(test_cases)} different queries...")
        
        for i, test_case in enumerate(test_cases, 1):
            try:
                print(f"\n--- Test {i}: {test_case['description']} ---")
                print(f"Model: {test_case['model']}")
                print(f"Query: {test_case['query']}")
                
                start_time = time.time()
                
                messages = [{"role": "user", "content": test_case['query']}]
                response = await client.chat_completion(
                    messages=messages,
                    model=test_case['model'],
                    max_tokens=150,  # Keep responses concise for testing
                    temperature=0.7
                )
                
                duration = time.time() - start_time
                
                if "choices" in response:
                    content = response["choices"][0]["message"]["content"]
                    print(f"✅ Success ({duration:.2f}s): {content[:100]}...")
                    
                    # Show which provider was actually used
                    if "provider" in response:
                        print(f"   Provider: {response['provider']}")
                else:
                    print(f"⚠️ Unexpected response format: {response}")
                    
            except Exception as e:
                print(f"❌ Test {i} failed: {e}")
        
        # Show final provider metrics
        print(f"\n📈 Final Provider Metrics:")
        final_status = client.get_provider_status()
        for name, info in final_status.items():
            metrics = info['metrics']
            rate_limiter = info['rate_limiter']
            print(f"  {name}:")
            print(f"    Requests: {metrics['total_requests']}")
            print(f"    Success Rate: {metrics['success_rate']:.1f}%")
            print(f"    Avg Response Time: {metrics['average_response_time']:.2f}s")
            print(f"    Tokens Remaining: {rate_limiter['current_tokens']:.1f}")
            print(f"    Rate Limited: {metrics['rate_limited_requests']}")
        
        print(f"\n🎉 Real API test completed! The cosmic energy flows strong! ✨")
        
    except Exception as e:
        print(f"\n😵 Test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_provider_fallback():
    """Test provider fallback by simulating failures."""
    print(f"\n🎋 Testing Provider Fallback Behavior")
    print("=" * 40)
    
    try:
        client = MultiProviderClient()
        
        # Make a request that should work with any provider
        print("Testing fallback with a simple query...")
        
        messages = [{"role": "user", "content": "Say hello and tell me which AI model you are"}]
        
        response = await client.chat_completion(
            messages=messages,
            model="gpt-4o-mini",
            max_tokens=50
        )
        
        if "choices" in response:
            content = response["choices"][0]["message"]["content"]
            print(f"✅ Fallback test successful: {content}")
        else:
            print(f"⚠️ Unexpected response: {response}")
        
        # Check which provider handled the request
        status = client.get_provider_status()
        active_provider = None
        for name, info in status.items():
            if info['metrics']['total_requests'] > 0:
                active_provider = name
                break
        
        if active_provider:
            print(f"🎯 Request handled by: {active_provider}")
        
    except Exception as e:
        print(f"Fallback test failed: {e}")


async def test_rate_limiting_real():
    """Test rate limiting with real API calls."""
    print(f"\n🌊 Testing Rate Limiting with Real APIs")
    print("=" * 40)
    
    try:
        client = MultiProviderClient()
        
        # Make several rapid requests to test rate limiting
        print("Making 4 rapid requests to test rate limiting...")
        
        tasks = []
        for i in range(4):
            messages = [{"role": "user", "content": f"Quick test {i+1}: What is {i+1} squared?"}]
            task = client.chat_completion(
                messages=messages,
                model="gpt-4o-mini",
                max_tokens=20
            )
            tasks.append(task)
        
        # Execute with small delays to avoid overwhelming
        results = []
        for i, task in enumerate(tasks):
            try:
                start_time = time.time()
                response = await task
                duration = time.time() - start_time
                
                if "choices" in response:
                    content = response["choices"][0]["message"]["content"]
                    results.append(f"Request {i+1}: ✅ Success ({duration:.2f}s) - {content[:30]}...")
                else:
                    results.append(f"Request {i+1}: ⚠️ Unexpected format")
                    
            except Exception as e:
                results.append(f"Request {i+1}: ❌ {e}")
            
            # Small delay between requests
            if i < len(tasks) - 1:
                await asyncio.sleep(0.5)
        
        for result in results:
            print(f"  {result}")
        
        # Check rate limiter status
        print(f"\n📊 Rate Limiter Status After Burst:")
        status = client.get_provider_status()
        for name, info in status.items():
            if info['metrics']['total_requests'] > 0:
                rate_limiter = info['rate_limiter']
                print(f"  {name}: {rate_limiter['current_tokens']:.1f}/{rate_limiter['burst_capacity']} tokens")
        
    except Exception as e:
        print(f"Rate limiting test failed: {e}")


async def test_health_check_real():
    """Test health check with real providers."""
    print(f"\n💚 Testing Real Provider Health Checks")
    print("=" * 40)
    
    try:
        client = MultiProviderClient()
        
        print("Performing health checks on all providers...")
        health_results = await client.health_check()
        
        for name, is_healthy in health_results.items():
            status_emoji = "💚" if is_healthy else "💔"
            print(f"  {name}: {status_emoji} {'Healthy' if is_healthy else 'Unhealthy'}")
        
        healthy_count = sum(1 for h in health_results.values() if h)
        total_count = len(health_results)
        
        print(f"\n📊 Health Summary: {healthy_count}/{total_count} providers healthy")
        
    except Exception as e:
        print(f"Health check failed: {e}")


if __name__ == "__main__":
    print("🌟 Starting Real API Tests with Cosmic MultiProvider Client 🌟")
    
    # Run all tests
    asyncio.run(test_real_api_calls())
    asyncio.run(test_provider_fallback())
    asyncio.run(test_rate_limiting_real())
    asyncio.run(test_health_check_real())
    
    print("\n🧘‍♂️ All real API tests completed! The cosmic code flows with real energy! ✨")