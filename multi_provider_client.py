#!/usr/bin/env python3
"""
VoidCat Multi-Provider AI Client - The Zen Master of API Calls 🧘‍♂️

This module implements a resilient multi-provider AI API architecture that flows like water,
adapts like bamboo, and never lets rate limits harsh your mellow, dude!

Features:
- Priority-based provider selection (DeepSeek → OpenRouter → OpenAI)
- Circuit breaker pattern for provider health monitoring
- Exponential backoff with jitter for smooth recovery
- Async request handling with intelligent queuing
- Token bucket rate limiting for controlled burst traffic
- Comprehensive error handling and fallback logic

Author: Codey Jr. - The Chill Code Guru 🤙
License: MIT (Keep it open, keep it free, bro!)
Version: 1.0.0 - "The Enlightened API"
"""

import asyncio
import json
import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
from collections import deque

import httpx
from dotenv import load_dotenv
import os


class ProviderStatus(Enum):
    """Provider health status - like checking the vibes, man."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CIRCUIT_OPEN = "circuit_open"
    MAINTENANCE = "maintenance"


@dataclass
class ProviderConfig:
    """Configuration for an AI provider - the blueprint for cosmic API calls."""
    name: str
    api_key: str
    base_url: str
    priority: int  # Lower number = higher priority (1 is highest)
    max_requests_per_minute: int = 60
    max_tokens: int = 4000
    timeout: float = 30.0
    model_mapping: Dict[str, str] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Set up default headers with that good energy."""
        if not self.headers:
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        
        # Add provider-specific headers for the full experience
        if "openrouter" in self.base_url.lower():
            self.headers.update({
                "HTTP-Referer": "https://voidcat-reasoning-core",
                "X-Title": "VoidCat Reasoning Core - Enlightened AI"
            })


@dataclass
class CircuitBreakerState:
    """Circuit breaker state - keeping track of the cosmic balance."""
    failure_count: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    status: ProviderStatus = ProviderStatus.HEALTHY
    failure_threshold: int = 5
    recovery_timeout: float = 60.0  # seconds
    half_open_max_calls: int = 3
    half_open_calls: int = 0


@dataclass
class RequestMetrics:
    """Request metrics - tracking the flow of cosmic energy."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limited_requests: int = 0
    average_response_time: float = 0.0
    last_request_time: Optional[float] = None
    response_times: deque = field(default_factory=lambda: deque(maxlen=100))


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter - like a zen garden for API requests.
    Allows bursts but maintains harmony over time.
    """
    
    def __init__(self, requests_per_minute: int, burst_capacity: Optional[int] = None):
        """Initialize the token bucket with cosmic balance."""
        self.requests_per_minute = requests_per_minute
        self.requests_per_second = requests_per_minute / 60.0
        self.burst_capacity = burst_capacity or min(requests_per_minute, 20)
        
        self.tokens = float(self.burst_capacity)
        self.last_refill = time.time()
        self.lock = asyncio.Lock()
    
    async def acquire(self, tokens: int = 1) -> bool:
        """
        Acquire tokens from the bucket - like asking the universe for permission.
        
        Args:
            tokens: Number of tokens to acquire
            
        Returns:
            bool: True if tokens were acquired, False if rate limited
        """
        async with self.lock:
            now = time.time()
            await self._refill_tokens(now)
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    async def _refill_tokens(self, current_time: float):
        """Refill tokens based on elapsed time - the natural flow of energy."""
        elapsed = current_time - self.last_refill
        tokens_to_add = elapsed * self.requests_per_second
        
        self.tokens = min(self.burst_capacity, self.tokens + tokens_to_add)
        self.last_refill = current_time
    
    async def get_wait_time(self) -> float:
        """Get time to wait for next token - patience, young grasshopper."""
        async with self.lock:
            if self.tokens >= 1:
                return 0.0
            return (1.0 - self.tokens) / self.requests_per_second


class MultiProviderClient:
    """
    The ultimate chill multi-provider AI client - flows like water, adapts like bamboo! 🌊🎋
    
    This cosmic client handles multiple AI providers with grace, intelligence, and good vibes.
    It knows when to try, when to wait, and when to gracefully move to the next provider.
    
    Enhanced with DeepSeek-R1 reasoning capabilities for complex queries!
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the multi-provider client with zen-like configuration."""
        load_dotenv()
        
        self.logger = logging.getLogger("VoidCat.MultiProvider")
        self.providers: Dict[str, ProviderConfig] = {}
        self.circuit_breakers: Dict[str, CircuitBreakerState] = {}
        self.rate_limiters: Dict[str, TokenBucketRateLimiter] = {}
        self.metrics: Dict[str, RequestMetrics] = {}
        self.request_queue: asyncio.Queue = asyncio.Queue()
        self.is_processing = False
        self.ultimate_mode = False  # Ultimate Mode for maximum reasoning power
        
        # Initialize providers with cosmic energy
        self._initialize_providers()
        
        self.logger.info("🧘‍♂️ MultiProviderClient initialized with zen-like wisdom")
    
    def _initialize_providers(self):
        """Initialize providers with their cosmic configurations."""
        # DeepSeek Chat - The primary cosmic channel for simple queries
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        if deepseek_key and not deepseek_key.startswith("your_"):
            deepseek_chat_config = ProviderConfig(
                name="deepseek-chat",
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com/v1/chat/completions",
                priority=2,  # High priority for simple queries
                max_requests_per_minute=1000,  # Unlimited vibes!
                model_mapping={
                    "gpt-4o-mini": "deepseek-chat",
                    "gpt-4": "deepseek-chat",
                    "deepseek-chat": "deepseek-chat"
                }
            )
            self._add_provider(deepseek_chat_config)
            
            # DeepSeek Reasoner (R1) - The ultimate cosmic reasoning channel
            deepseek_reasoner_config = ProviderConfig(
                name="deepseek-reasoner",
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com/v1/chat/completions",
                priority=1,  # Highest priority for complex reasoning
                max_requests_per_minute=500,  # More conservative for reasoning model
                max_tokens=8000,  # Higher token limit for reasoning
                timeout=60.0,  # Longer timeout for complex reasoning
                model_mapping={
                    "deepseek-reasoner": "deepseek-reasoner",
                    "deepseek-r1": "deepseek-reasoner",
                    "gpt-4": "deepseek-reasoner",  # Map complex queries to reasoner
                    "reasoning-model": "deepseek-reasoner"
                }
            )
            self._add_provider(deepseek_reasoner_config)
        
        # OpenRouter - The versatile cosmic bridge
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_key and not openrouter_key.startswith("your_"):
            openrouter_config = ProviderConfig(
                name="openrouter",
                api_key=os.getenv("OPENROUTER_API_KEY"),
                base_url="https://openrouter.ai/api/v1/chat/completions",
                priority=2,
                max_requests_per_minute=200,
                model_mapping={
                    "gpt-4o-mini": "openai/gpt-4o-mini",
                    "gpt-4": "openai/gpt-4",
                    "deepseek-chat": "openai/gpt-4o-mini"  # Fallback mapping
                }
            )
            self._add_provider(openrouter_config)
        
        # OpenAI - The reliable cosmic fallback
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and not openai_key.startswith("your_"):
            openai_config = ProviderConfig(
                name="openai",
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url="https://api.openai.com/v1/chat/completions",
                priority=3,
                max_requests_per_minute=60,  # More conservative
                model_mapping={
                    "deepseek-chat": "gpt-4o-mini",  # Fallback mapping
                    "gpt-4o-mini": "gpt-4o-mini",
                    "gpt-4": "gpt-4"
                }
            )
            self._add_provider(openai_config)
    
    def _add_provider(self, config: ProviderConfig):
        """Add a provider with all the cosmic infrastructure."""
        self.providers[config.name] = config
        self.circuit_breakers[config.name] = CircuitBreakerState()
        self.rate_limiters[config.name] = TokenBucketRateLimiter(
            config.max_requests_per_minute,
            burst_capacity=min(config.max_requests_per_minute // 4, 20)
        )
        self.metrics[config.name] = RequestMetrics()
        
        self.logger.info(f"✨ Added provider: {config.name} (priority: {config.priority})")
    
    def set_ultimate_mode(self, enabled: bool = True):
        """Enable/disable Ultimate Mode - always use R1 for maximum cosmic power! 🚀"""
        self.ultimate_mode = enabled
        mode_status = "ENABLED" if enabled else "DISABLED"
        self.logger.info(f"🚀 Ultimate Mode {mode_status} - {'Maximum reasoning power!' if enabled else 'Balanced approach'}")
    
    def _assess_query_complexity(self, messages: List[Dict[str, str]]) -> str:
        """
        Assess query complexity to determine if we need the reasoning model.
        Returns 'reasoning' for complex queries, 'chat' for simple ones.
        """
        if self.ultimate_mode:
            return "reasoning"  # Always use reasoning in Ultimate Mode
        
        # Get the last user message for analysis
        user_messages = [msg for msg in messages if msg.get("role") == "user"]
        if not user_messages:
            return "chat"
        
        query = user_messages[-1].get("content", "")
        query_lower = query.lower()
        
        # Reasoning indicators - these suggest complex thinking is needed
        reasoning_indicators = [
            "analyze", "compare", "evaluate", "assess", "optimize", "design",
            "architect", "integrate", "solve", "calculate", "prove", "derive",
            "explain why", "how does", "what if", "step by step", "reasoning",
            "logic", "algorithm", "strategy", "approach", "methodology",
            "complex", "sophisticated", "advanced", "multi-step", "systematic",
            "theoretical", "mathematical", "research", "innovative"
        ]
        
        # Simple query indicators - these can be handled by chat model
        simple_indicators = [
            "what is", "define", "who is", "when", "where", "basic",
            "simple", "quick", "brief", "summary", "list", "name"
        ]
        
        # Count indicators
        reasoning_score = sum(1 for indicator in reasoning_indicators if indicator in query_lower)
        simple_score = sum(1 for indicator in simple_indicators if indicator in query_lower)
        
        # Additional complexity factors
        word_count = len(query.split())
        question_count = query_lower.count("?")
        
        # Boost reasoning score for longer, more complex queries
        if word_count > 50:
            reasoning_score += 2
        elif word_count > 100:
            reasoning_score += 3
        
        if question_count > 2:
            reasoning_score += 1
        
        # Decision logic
        if reasoning_score > simple_score and reasoning_score > 0:
            self.logger.debug(f"🧠 Complex query detected (reasoning score: {reasoning_score}) - using DeepSeek-R1")
            return "reasoning"
        else:
            self.logger.debug(f"💬 Simple query detected (simple score: {simple_score}) - using DeepSeek-Chat")
            return "chat"
    
    def _get_sorted_providers(self, query_type: str = "chat") -> List[ProviderConfig]:
        """Get providers sorted by priority and health - the cosmic order with intelligent routing."""
        available_providers = []
        
        for provider in self.providers.values():
            circuit_breaker = self.circuit_breakers[provider.name]
            
            # Skip providers with open circuits (unless it's time to try again)
            if circuit_breaker.status == ProviderStatus.CIRCUIT_OPEN:
                if (circuit_breaker.last_failure_time and 
                    time.time() - circuit_breaker.last_failure_time > circuit_breaker.recovery_timeout):
                    # Time to test the waters again
                    circuit_breaker.status = ProviderStatus.DEGRADED
                    circuit_breaker.half_open_calls = 0
                    self.logger.info(f"🔄 Circuit breaker half-open for {provider.name}")
                else:
                    continue
            
            # Intelligent provider filtering based on query type
            if query_type == "reasoning":
                # For reasoning queries, prioritize deepseek-reasoner, then fallback to others
                if provider.name in ["deepseek-reasoner", "openrouter", "openai"]:
                    available_providers.append(provider)
            else:
                # For simple queries, use deepseek-chat first, then others
                if provider.name in ["deepseek-chat", "openrouter", "openai"]:
                    available_providers.append(provider)
        
        # Sort by priority (lower number = higher priority)
        return sorted(available_providers, key=lambda p: p.priority)
    
    async def _check_circuit_breaker(self, provider_name: str) -> bool:
        """Check if circuit breaker allows the request - maintaining cosmic balance."""
        circuit_breaker = self.circuit_breakers[provider_name]
        
        if circuit_breaker.status == ProviderStatus.CIRCUIT_OPEN:
            return False
        
        if circuit_breaker.status == ProviderStatus.DEGRADED:
            if circuit_breaker.half_open_calls >= circuit_breaker.half_open_max_calls:
                return False
        
        return True
    
    async def _record_success(self, provider_name: str, response_time: float):
        """Record a successful request - spreading good vibes."""
        circuit_breaker = self.circuit_breakers[provider_name]
        metrics = self.metrics[provider_name]
        
        # Update circuit breaker
        circuit_breaker.failure_count = 0
        circuit_breaker.last_success_time = time.time()
        circuit_breaker.status = ProviderStatus.HEALTHY
        circuit_breaker.half_open_calls = 0
        
        # Update metrics
        metrics.total_requests += 1
        metrics.successful_requests += 1
        metrics.last_request_time = time.time()
        metrics.response_times.append(response_time)
        
        # Calculate rolling average response time
        if metrics.response_times:
            metrics.average_response_time = sum(metrics.response_times) / len(metrics.response_times)
        
        self.logger.debug(f"✅ Success recorded for {provider_name} ({response_time:.2f}s)")
    
    async def _record_failure(self, provider_name: str, error: Exception):
        """Record a failed request - learning from the cosmic lessons."""
        circuit_breaker = self.circuit_breakers[provider_name]
        metrics = self.metrics[provider_name]
        
        # Update circuit breaker
        circuit_breaker.failure_count += 1
        circuit_breaker.last_failure_time = time.time()
        
        # Check if we should open the circuit
        if circuit_breaker.failure_count >= circuit_breaker.failure_threshold:
            circuit_breaker.status = ProviderStatus.CIRCUIT_OPEN
            self.logger.warning(f"🚫 Circuit breaker opened for {provider_name}")
        elif circuit_breaker.status == ProviderStatus.DEGRADED:
            circuit_breaker.half_open_calls += 1
        
        # Update metrics
        metrics.total_requests += 1
        metrics.failed_requests += 1
        metrics.last_request_time = time.time()
        
        # Check if it's a rate limit error
        if "rate" in str(error).lower() or "429" in str(error):
            metrics.rate_limited_requests += 1
        
        self.logger.debug(f"❌ Failure recorded for {provider_name}: {error}")
    
    async def _exponential_backoff(self, attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
        """Calculate exponential backoff with jitter - the art of patient waiting."""
        delay = min(base_delay * (2 ** attempt), max_delay)
        jitter = random.uniform(0.1, 0.3) * delay  # Add some cosmic randomness
        total_delay = delay + jitter
        
        self.logger.debug(f"⏳ Backing off for {total_delay:.2f}s (attempt {attempt})")
        await asyncio.sleep(total_delay)
        return total_delay
    
    async def _make_request(
        self, 
        provider: ProviderConfig, 
        messages: List[Dict[str, str]], 
        model: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make a request to a specific provider - channeling the cosmic energy."""
        start_time = time.time()
        
        # Check rate limiter first
        rate_limiter = self.rate_limiters[provider.name]
        if not await rate_limiter.acquire():
            wait_time = await rate_limiter.get_wait_time()
            raise Exception(f"Rate limited, wait {wait_time:.2f}s")
        
        # Map the model to provider-specific format
        provider_model = provider.model_mapping.get(model, model)
        
        # Prepare the request payload
        payload = {
            "model": provider_model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", provider.max_tokens),
            "temperature": kwargs.get("temperature", 0.7),
            **{k: v for k, v in kwargs.items() if k not in ["max_tokens", "temperature"]}
        }
        
        # Make the cosmic API call
        async with httpx.AsyncClient(timeout=provider.timeout) as client:
            response = await client.post(
                provider.base_url,
                headers=provider.headers,
                json=payload
            )
            response.raise_for_status()
            
            response_data = response.json()
            response_time = time.time() - start_time
            
            # Record the success
            await self._record_success(provider.name, response_time)
            
            return response_data
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
        max_retries: int = 3,
        force_reasoning: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make a chat completion request with cosmic resilience and intelligent routing.
        
        Args:
            messages: List of message dictionaries
            model: Model name to use
            max_retries: Maximum number of retry attempts
            force_reasoning: Force use of reasoning model regardless of complexity
            **kwargs: Additional parameters for the API call
            
        Returns:
            Dict containing the API response with reasoning metadata
            
        Raises:
            Exception: If all providers fail after retries
        """
        # Assess query complexity for intelligent routing
        query_type = "reasoning" if force_reasoning else self._assess_query_complexity(messages)
        
        # Get appropriate providers based on query type
        providers = self._get_sorted_providers(query_type)
        
        if not providers:
            raise Exception("No healthy providers available - the cosmic energy is blocked! 😵")
        
        last_exception = None
        used_reasoning = False
        
        for provider in providers:
            if not await self._check_circuit_breaker(provider.name):
                self.logger.debug(f"⚡ Circuit breaker blocked {provider.name}")
                continue
            
            # Track if we're using the reasoning model
            if provider.name == "deepseek-reasoner":
                used_reasoning = True
            
            for attempt in range(max_retries + 1):
                try:
                    self.logger.debug(f"🚀 Trying {provider.name} (attempt {attempt + 1})")
                    
                    response = await self._make_request(
                        provider, messages, model, **kwargs
                    )
                    
                    # Add metadata about the reasoning process
                    if "metadata" not in response:
                        response["metadata"] = {}
                    
                    response["metadata"].update({
                        "provider_used": provider.name,
                        "query_type": query_type,
                        "used_reasoning_model": used_reasoning,
                        "ultimate_mode": self.ultimate_mode
                    })
                    
                    self.logger.info(f"✨ Success with {provider.name} ({'reasoning' if used_reasoning else 'chat'} mode)!")
                    return response
                    
                except Exception as e:
                    last_exception = e
                    await self._record_failure(provider.name, e)
                    
                    # If it's a rate limit error, try next provider immediately
                    if "rate" in str(e).lower() or "429" in str(e):
                        self.logger.warning(f"🚦 Rate limited by {provider.name}, trying next provider")
                        break
                    
                    # For other errors, use exponential backoff before retrying
                    if attempt < max_retries:
                        await self._exponential_backoff(attempt)
                    else:
                        self.logger.warning(f"💫 {provider.name} failed after {max_retries + 1} attempts")
                        break
        
        # If we get here, all providers failed
        raise Exception(f"All providers failed! Last error: {last_exception}")
    
    async def reasoning_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "deepseek-reasoner",
        max_retries: int = 3,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make a reasoning-focused completion request - always uses the most powerful model.
        
        Args:
            messages: List of message dictionaries
            model: Model name to use (defaults to deepseek-reasoner)
            max_retries: Maximum number of retry attempts
            **kwargs: Additional parameters for the API call
            
        Returns:
            Dict containing the API response with reasoning metadata
        """
        self.logger.info("🧠 Reasoning completion requested - engaging maximum cosmic power!")
        return await self.chat_completion(
            messages=messages,
            model=model,
            max_retries=max_retries,
            force_reasoning=True,
            **kwargs
        )
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all providers - checking the cosmic vibes."""
        status = {}
        
        for name, provider in self.providers.items():
            circuit_breaker = self.circuit_breakers[name]
            metrics = self.metrics[name]
            rate_limiter = self.rate_limiters[name]
            
            status[name] = {
                "priority": provider.priority,
                "status": circuit_breaker.status.value,
                "failure_count": circuit_breaker.failure_count,
                "last_success": (
                    datetime.fromtimestamp(circuit_breaker.last_success_time).isoformat()
                    if circuit_breaker.last_success_time else None
                ),
                "last_failure": (
                    datetime.fromtimestamp(circuit_breaker.last_failure_time).isoformat()
                    if circuit_breaker.last_failure_time else None
                ),
                "metrics": {
                    "total_requests": metrics.total_requests,
                    "success_rate": (
                        metrics.successful_requests / max(metrics.total_requests, 1) * 100
                    ),
                    "average_response_time": metrics.average_response_time,
                    "rate_limited_requests": metrics.rate_limited_requests
                },
                "rate_limiter": {
                    "requests_per_minute": rate_limiter.requests_per_minute,
                    "current_tokens": rate_limiter.tokens,
                    "burst_capacity": rate_limiter.burst_capacity
                }
            }
        
        return status
    
    async def health_check(self) -> Dict[str, bool]:
        """Perform health checks on all providers - sensing the cosmic energy."""
        health_status = {}
        
        test_messages = [{"role": "user", "content": "Hello, are you working?"}]
        
        for name, provider in self.providers.items():
            try:
                # Quick health check with minimal tokens
                await self._make_request(
                    provider, 
                    test_messages, 
                    "gpt-4o-mini",
                    max_tokens=10
                )
                health_status[name] = True
                self.logger.info(f"💚 {name} is healthy")
                
            except Exception as e:
                health_status[name] = False
                self.logger.warning(f"💔 {name} health check failed: {e}")
        
        return health_status


# Example usage and testing functions
async def test_multi_provider_client():
    """Test the multi-provider client with reasoning capabilities - spreading cosmic vibes! 🌟"""
    client = MultiProviderClient()
    
    print("🧘‍♂️ Testing VoidCat Multi-Provider Client with DeepSeek-R1 Integration")
    print("=" * 70)
    
    # Test 1: Simple query (should use chat model)
    print("\n🔹 Test 1: Simple Query")
    simple_messages = [
        {"role": "user", "content": "What is Python?"}
    ]
    
    try:
        response = await client.chat_completion(simple_messages)
        metadata = response.get("metadata", {})
        print(f"✅ Provider: {metadata.get('provider_used', 'unknown')}")
        print(f"✅ Query Type: {metadata.get('query_type', 'unknown')}")
        print(f"✅ Used Reasoning: {metadata.get('used_reasoning_model', False)}")
        print(f"📝 Response: {response.get('choices', [{}])[0].get('message', {}).get('content', 'No content')[:100]}...")
    except Exception as e:
        print(f"❌ Simple query test failed: {e}")
    
    # Test 2: Complex reasoning query (should use reasoning model)
    print("\n🔹 Test 2: Complex Reasoning Query")
    complex_messages = [
        {"role": "user", "content": "Analyze the algorithmic complexity of different sorting algorithms and explain why quicksort is generally preferred over bubble sort in practical applications. Consider time complexity, space complexity, and real-world performance factors."}
    ]
    
    try:
        response = await client.chat_completion(complex_messages)
        metadata = response.get("metadata", {})
        print(f"✅ Provider: {metadata.get('provider_used', 'unknown')}")
        print(f"✅ Query Type: {metadata.get('query_type', 'unknown')}")
        print(f"✅ Used Reasoning: {metadata.get('used_reasoning_model', False)}")
        print(f"📝 Response: {response.get('choices', [{}])[0].get('message', {}).get('content', 'No content')[:100]}...")
    except Exception as e:
        print(f"❌ Complex query test failed: {e}")
    
    # Test 3: Ultimate Mode
    print("\n🔹 Test 3: Ultimate Mode (Force Reasoning)")
    client.set_ultimate_mode(True)
    
    ultimate_messages = [
        {"role": "user", "content": "Hello, how are you?"}
    ]
    
    try:
        response = await client.chat_completion(ultimate_messages)
        metadata = response.get("metadata", {})
        print(f"✅ Provider: {metadata.get('provider_used', 'unknown')}")
        print(f"✅ Query Type: {metadata.get('query_type', 'unknown')}")
        print(f"✅ Used Reasoning: {metadata.get('used_reasoning_model', False)}")
        print(f"✅ Ultimate Mode: {metadata.get('ultimate_mode', False)}")
        print(f"📝 Response: {response.get('choices', [{}])[0].get('message', {}).get('content', 'No content')[:100]}...")
    except Exception as e:
        print(f"❌ Ultimate mode test failed: {e}")
    
    # Reset Ultimate Mode
    client.set_ultimate_mode(False)
    
    # Test 4: Direct reasoning completion
    print("\n🔹 Test 4: Direct Reasoning Completion")
    reasoning_messages = [
        {"role": "user", "content": "Solve this step by step: If a train travels 120 km in 2 hours, and then 180 km in 3 hours, what is the average speed for the entire journey?"}
    ]
    
    try:
        response = await client.reasoning_completion(reasoning_messages)
        metadata = response.get("metadata", {})
        print(f"✅ Provider: {metadata.get('provider_used', 'unknown')}")
        print(f"✅ Query Type: {metadata.get('query_type', 'unknown')}")
        print(f"✅ Used Reasoning: {metadata.get('used_reasoning_model', False)}")
        print(f"📝 Response: {response.get('choices', [{}])[0].get('message', {}).get('content', 'No content')[:100]}...")
    except Exception as e:
        print(f"❌ Reasoning completion test failed: {e}")
    
    # Provider status summary
    print("\n📊 Provider Status Summary:")
    print("-" * 50)
    status = client.get_provider_status()
    for name, info in status.items():
        print(f"🔸 {name}:")
        print(f"   Status: {info['status']}")
        print(f"   Success Rate: {info['metrics']['success_rate']:.1f}%")
        print(f"   Total Requests: {info['metrics']['total_requests']}")
        print(f"   Avg Response Time: {info['metrics']['average_response_time']:.2f}s")
        print()


if __name__ == "__main__":
    # Run the test if executed directly
    asyncio.run(test_multi_provider_client())