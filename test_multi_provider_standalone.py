#!/usr/bin/env python3
"""
Standalone test for the cosmic MultiProviderClient
Testing the zen-like API client without dependencies! 🌊
"""

import asyncio
import json
from multi_provider_client import MultiProviderClient


async def test_standalone_client():
    """Test the standalone MultiProviderClient - pure cosmic energy."""
    print("🧘‍♂️ Testing Standalone MultiProvider Client")
    print("=" * 50)
    
    try:
        # Initialize the client
        print("\n🌟 Initializing MultiProvider Client...")
        client = MultiProviderClient()
        
        # Check provider status
        print("\n📊 Checking provider status...")
        provider_status = client.get_provider_status()
        
        for name, info in provider_status.items():
            print(f"  {name}: {info['status']} (priority: {info['priority']})")
        
        # Test a simple chat completion
        print("\n🚀 Testing chat completion...")
        messages = [
            {"role": "user", "content": "What's the meaning of life in one sentence?"}
        ]
        
        response = await client.chat_completion(
            messages=messages,
            model="gpt-4o-mini"
        )
        
        if "choices" in response:
            content = response["choices"][0]["message"]["content"]
            print(f"\n✨ Response: {content}")
        else:
            print(f"\n⚠️ Unexpected response format: {response}")
        
        # Check final status
        print("\n📈 Final provider status...")
        final_status = client.get_provider_status()
        for name, info in final_status.items():
            metrics = info['metrics']
            print(f"  {name}: {metrics['total_requests']} requests, {metrics['success_rate']:.1f}% success")
        
        print("\n🎉 Standalone test completed! The cosmic energy flows! ✨")
        
    except Exception as e:
        print(f"\n😵 Test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_rate_limiting_standalone():
    """Test rate limiting with standalone client."""
    print("\n🌊 Testing rate limiting behavior...")
    
    try:
        client = MultiProviderClient()
        
        # Make multiple rapid requests
        print("Making 3 rapid requests...")
        tasks = []
        for i in range(3):
            messages = [{"role": "user", "content": f"Quick test {i+1}: What is {i+1} + {i+1}?"}]
            task = client.chat_completion(messages=messages, model="gpt-4o-mini")
            tasks.append(task)
        
        # Execute with some delay to avoid overwhelming
        responses = []
        for i, task in enumerate(tasks):
            try:
                if i > 0:
                    await asyncio.sleep(1)  # Small delay between requests
                response = await task
                responses.append(f"Request {i+1}: ✅ Success")
            except Exception as e:
                responses.append(f"Request {i+1}: ❌ {e}")
        
        for response in responses:
            print(f"  {response}")
        
    except Exception as e:
        print(f"Rate limiting test failed: {e}")


if __name__ == "__main__":
    print("🌟 Starting Standalone MultiProvider Tests 🌟")
    
    # Run tests
    asyncio.run(test_standalone_client())
    asyncio.run(test_rate_limiting_standalone())
    
    print("\n🧘‍♂️ Standalone tests completed. The cosmic code flows! ✨")