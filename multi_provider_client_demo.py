#!/usr/bin/env python3
"""
Demo version of MultiProviderClient with mock responses
Shows off all the cosmic functionality without needing real API keys! 🌟
"""

import asyncio
import json
import random
import time
from typing import Dict, List, Any
from multi_provider_client import MultiProviderClient, ProviderStatus


class MockMultiProviderClient(MultiProviderClient):
    """
    Mock version of MultiProviderClient for demonstration purposes.
    Shows all the zen-like functionality with simulated responses! 🧘‍♂️
    """
    
    def __init__(self):
        """Initialize with mock providers."""
        # Don't call super().__init__() to avoid loading real API keys
        self.logger = self._setup_logger()
        self.providers = {}
        self.circuit_breakers = {}
        self.rate_limiters = {}
        self.metrics = {}
        self.request_queue = asyncio.Queue()
        self.is_processing = False
        
        # Initialize mock providers
        self._initialize_mock_providers()
        
        self.logger.info("🎭 Mock MultiProviderClient initialized for demo purposes")
    
    def _setup_logger(self):
        """Set up a simple logger."""
        import logging
        logger = logging.getLogger("VoidCat.MockMultiProvider")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def _initialize_mock_providers(self):
        """Initialize mock providers with simulated configurations."""
        from multi_provider_client import ProviderConfig, CircuitBreakerState, TokenBucketRateLimiter, RequestMetrics
        import os
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv()
        
        # Mock DeepSeek
        deepseek_config = ProviderConfig(
            name="deepseek",
            api_key=os.getenv("DEEPSEEK_API_KEY", "DEMO_MODE_NO_API_KEY_NEEDED"),
            base_url="https://api.deepseek.com/v1/chat/completions",
            priority=1,
            max_requests_per_minute=1000,
            model_mapping={
                "gpt-4o-mini": "deepseek-chat",
                "gpt-4": "deepseek-chat",
                "deepseek-chat": "deepseek-chat"
            }
        )
        self._add_mock_provider(deepseek_config)
        
        # Mock OpenRouter
        openrouter_config = ProviderConfig(
            name="openrouter",
            api_key=os.getenv("OPENROUTER_API_KEY", "DEMO_MODE_NO_API_KEY_NEEDED"),
            base_url="https://openrouter.ai/api/v1/chat/completions",
            priority=2,
            max_requests_per_minute=200,
            model_mapping={
                "gpt-4o-mini": "openai/gpt-4o-mini",
                "gpt-4": "openai/gpt-4",
                "deepseek-chat": "openai/gpt-4o-mini"
            }
        )
        self._add_mock_provider(openrouter_config)
        
        # Mock OpenAI
        openai_config = ProviderConfig(
            name="openai",
            api_key=os.getenv("OPENAI_API_KEY", "DEMO_MODE_NO_API_KEY_NEEDED"),
            base_url="https://api.openai.com/v1/chat/completions",
            priority=3,
            max_requests_per_minute=60,
            model_mapping={
                "deepseek-chat": "gpt-4o-mini",
                "gpt-4o-mini": "gpt-4o-mini",
                "gpt-4": "gpt-4"
            }
        )
        self._add_mock_provider(openai_config)
    
    def _add_mock_provider(self, config):
        """Add a mock provider with all the cosmic infrastructure."""
        from multi_provider_client import CircuitBreakerState, TokenBucketRateLimiter, RequestMetrics
        
        self.providers[config.name] = config
        self.circuit_breakers[config.name] = CircuitBreakerState()
        self.rate_limiters[config.name] = TokenBucketRateLimiter(
            config.max_requests_per_minute,
            burst_capacity=min(config.max_requests_per_minute // 4, 20)
        )
        self.metrics[config.name] = RequestMetrics()
        
        self.logger.info(f"🎭 Added mock provider: {config.name} (priority: {config.priority})")
    
    async def _make_request(
        self, 
        provider, 
        messages: List[Dict[str, str]], 
        model: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make a mock request with simulated responses."""
        start_time = time.time()
        
        # Check rate limiter
        rate_limiter = self.rate_limiters[provider.name]
        if not await rate_limiter.acquire():
            wait_time = await rate_limiter.get_wait_time()
            raise Exception(f"Rate limited, wait {wait_time:.2f}s")
        
        # Simulate different response times and occasional failures
        await asyncio.sleep(random.uniform(0.1, 0.5))  # Simulate network delay
        
        # Simulate occasional failures for demonstration
        if random.random() < 0.1:  # 10% failure rate
            raise Exception(f"Simulated {provider.name} API error")
        
        # Generate mock response based on the query
        user_message = messages[0]["content"] if messages else "Hello"
        
        # Create different responses based on provider
        if provider.name == "deepseek":
            mock_content = f"🧠 DeepSeek says: {self._generate_mock_response(user_message)} (Unlimited rate limits, bro!)"
        elif provider.name == "openrouter":
            mock_content = f"🌉 OpenRouter says: {self._generate_mock_response(user_message)} (Versatile bridge to AI!)"
        else:  # openai
            mock_content = f"🤖 OpenAI says: {self._generate_mock_response(user_message)} (Classic reliability!)"
        
        # Record success
        response_time = time.time() - start_time
        await self._record_success(provider.name, response_time)
        
        # Return mock response in OpenAI format
        return {
            "choices": [
                {
                    "message": {
                        "content": mock_content,
                        "role": "assistant"
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(user_message.split()),
                "completion_tokens": len(mock_content.split()),
                "total_tokens": len(user_message.split()) + len(mock_content.split())
            },
            "model": provider.model_mapping.get(model, model),
            "provider": provider.name
        }
    
    def _generate_mock_response(self, query: str) -> str:
        """Generate contextual mock responses."""
        query_lower = query.lower()
        
        if "meaning of life" in query_lower:
            responses = [
                "The meaning of life is to find your zen and spread good vibes! 🧘‍♂️",
                "Life's meaning flows like water - be present, be kind, be awesome! 🌊",
                "42, but with more cosmic consciousness and fewer towels! ✨"
            ]
        elif "hello" in query_lower or "hi" in query_lower:
            responses = [
                "Greetings, cosmic coder! May your APIs flow with zen-like wisdom! 🙏",
                "Hey there, fellow digital surfer! Ready to ride the waves of code? 🏄‍♂️",
                "Namaste, beautiful soul! The universe welcomes your query! ✨"
            ]
        elif any(word in query_lower for word in ["add", "plus", "+"]):
            responses = [
                "Math flows through the cosmic calculator of existence! The answer resonates with universal harmony! 🔢",
                "Numbers dance in perfect mathematical meditation! ➕",
                "The arithmetic chakras align to reveal the numerical truth! 🧮"
            ]
        else:
            responses = [
                "Your query resonates with cosmic wisdom! The answer flows like a gentle stream! 🌊",
                "The universe has heard your question and responds with enlightened knowledge! ✨",
                "Through the lens of zen-like understanding, clarity emerges! 🧘‍♂️",
                "The cosmic code compiler has processed your request with good vibes! 💫"
            ]
        
        return random.choice(responses)
    
    async def health_check(self) -> Dict[str, bool]:
        """Perform mock health checks."""
        health_status = {}
        
        for name in self.providers.keys():
            # Simulate mostly healthy providers with occasional issues
            is_healthy = random.random() > 0.2  # 80% healthy
            health_status[name] = is_healthy
            
            if is_healthy:
                self.logger.info(f"💚 {name} is healthy (mock)")
            else:
                self.logger.warning(f"💔 {name} health check failed (mock)")
        
        return health_status


async def demo_multi_provider_client():
    """Demonstrate the cosmic MultiProviderClient functionality."""
    print("🎭 VoidCat MultiProvider Client Demo")
    print("=" * 50)
    print("This demo shows all functionality with mock responses!")
    print("No real API keys needed - pure cosmic demonstration! ✨\n")
    
    # Initialize mock client
    client = MockMultiProviderClient()
    
    # Show provider status
    print("📊 Initial Provider Status:")
    status = client.get_provider_status()
    for name, info in status.items():
        print(f"  {name}: {info['status']} (priority: {info['priority']})")
    
    # Test different types of queries
    test_queries = [
        "What's the meaning of life?",
        "Hello, how are you?",
        "What is 2 + 2?",
        "Tell me about quantum computing"
    ]
    
    print(f"\n🚀 Testing {len(test_queries)} different queries...")
    
    for i, query in enumerate(test_queries, 1):
        try:
            print(f"\n--- Query {i}: {query} ---")
            
            messages = [{"role": "user", "content": query}]
            response = await client.chat_completion(
                messages=messages,
                model="gpt-4o-mini"
            )
            
            if "choices" in response:
                content = response["choices"][0]["message"]["content"]
                provider = response.get("provider", "unknown")
                print(f"✅ Response from {provider}: {content}")
            else:
                print(f"⚠️ Unexpected response: {response}")
                
        except Exception as e:
            print(f"❌ Query failed: {e}")
    
    # Show final metrics
    print(f"\n📈 Final Provider Metrics:")
    final_status = client.get_provider_status()
    for name, info in final_status.items():
        metrics = info['metrics']
        print(f"  {name}: {metrics['total_requests']} requests, {metrics['success_rate']:.1f}% success")
    
    # Test health check
    print(f"\n💚 Health Check Results:")
    health = await client.health_check()
    for name, is_healthy in health.items():
        status_emoji = "💚" if is_healthy else "💔"
        print(f"  {name}: {status_emoji} {'Healthy' if is_healthy else 'Unhealthy'}")
    
    print(f"\n🎉 Demo completed! This shows how the real client would work with actual API keys! ✨")


async def demo_rate_limiting():
    """Demonstrate rate limiting behavior."""
    print(f"\n🌊 Rate Limiting Demo")
    print("=" * 30)
    
    client = MockMultiProviderClient()
    
    # Make rapid requests to show rate limiting
    print("Making 5 rapid requests to demonstrate rate limiting...")
    
    tasks = []
    for i in range(5):
        messages = [{"role": "user", "content": f"Quick test {i+1}"}]
        task = client.chat_completion(messages=messages, model="gpt-4o-mini")
        tasks.append(task)
    
    # Execute with minimal delay
    results = []
    for i, task in enumerate(tasks):
        try:
            start_time = time.time()
            response = await task
            duration = time.time() - start_time
            results.append(f"Request {i+1}: ✅ Success ({duration:.2f}s)")
        except Exception as e:
            results.append(f"Request {i+1}: ❌ {e}")
        
        # Small delay between requests
        if i < len(tasks) - 1:
            await asyncio.sleep(0.1)
    
    for result in results:
        print(f"  {result}")


async def demo_circuit_breaker():
    """Demonstrate circuit breaker functionality."""
    print(f"\n⚡ Circuit Breaker Demo")
    print("=" * 30)
    
    client = MockMultiProviderClient()
    
    # Simulate failures to trigger circuit breaker
    print("Simulating failures to demonstrate circuit breaker...")
    
    # Force failures by manipulating the failure rate
    original_failure_rate = 0.1
    
    # Temporarily increase failure rate to trigger circuit breaker
    for provider_name in client.providers.keys():
        circuit_breaker = client.circuit_breakers[provider_name]
        # Simulate multiple failures
        for _ in range(6):  # More than failure_threshold (5)
            await client._record_failure(provider_name, Exception("Simulated failure"))
    
    # Check status after failures
    print("Provider status after simulated failures:")
    status = client.get_provider_status()
    for name, info in status.items():
        print(f"  {name}: {info['status']} (failures: {client.circuit_breakers[name].failure_count})")
    
    # Try to make a request (should fail due to circuit breaker)
    try:
        messages = [{"role": "user", "content": "Test after circuit breaker"}]
        response = await client.chat_completion(messages=messages, model="gpt-4o-mini")
        print("  ✅ Request succeeded despite circuit breaker")
    except Exception as e:
        print(f"  ❌ Request failed as expected: {e}")


if __name__ == "__main__":
    print("🌟 Starting VoidCat MultiProvider Demo 🌟")
    
    # Run all demos
    asyncio.run(demo_multi_provider_client())
    asyncio.run(demo_rate_limiting())
    asyncio.run(demo_circuit_breaker())
    
    print("\n🧘‍♂️ Demo completed! This shows the full cosmic functionality! ✨")
    print("To use with real APIs, just add your API keys to the .env file! 🔑")