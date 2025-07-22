#!/usr/bin/env python3
"""
VoidCat Rate Limiting System - Pillar IV Infrastructure Component

This module implements comprehensive rate limiting for the VoidCat enhanced MCP server
to ensure efficient resource utilization, prevent abuse, and maintain system stability.

Features:
- Token bucket algorithm for smooth rate limiting
- Per-client and per-tool rate limiting
- Configurable limits with different tiers
- Burst handling and queue management
- Rate limit status reporting and monitoring
- Integration with enhanced MCP server logging

Author: VoidCat Reasoning Core Team - Pillar IV Infrastructure
License: MIT
Version: 1.0.0
"""

import asyncio
import json
import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, NamedTuple, Optional, Tuple


# Rate limiting configuration
@dataclass
class RateLimit:
    """Rate limit configuration for a specific context."""

    requests_per_second: float
    burst_size: int
    window_size_seconds: int = 60
    enabled: bool = True

    def __post_init__(self):
        # Calculate derived values
        self.bucket_size = max(self.burst_size, self.requests_per_second * 2)
        self.refill_rate = self.requests_per_second


@dataclass
class RateLimitStatus:
    """Current rate limit status for a client/tool."""

    current_tokens: float
    last_refill: float
    request_count: int
    blocked_count: int
    first_request: float
    last_request: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert status to dictionary for JSON serialization."""
        return {
            "current_tokens": round(self.current_tokens, 2),
            "last_refill": self.last_refill,
            "request_count": self.request_count,
            "blocked_count": self.blocked_count,
            "first_request": self.first_request,
            "last_request": self.last_request,
            "requests_per_minute": self._calculate_rpm(),
            "block_percentage": (self.blocked_count / max(1, self.request_count)) * 100,
        }

    def _calculate_rpm(self) -> float:
        """Calculate requests per minute."""
        if self.first_request == self.last_request:
            return 0.0

        duration_minutes = (self.last_request - self.first_request) / 60
        if duration_minutes <= 0:
            return 0.0

        return self.request_count / duration_minutes


class TokenBucket:
    """Token bucket implementation for rate limiting."""

    def __init__(self, rate_limit: RateLimit):
        self.rate_limit = rate_limit
        self.tokens = float(rate_limit.bucket_size)
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def consume_token(self) -> bool:
        """
        Attempt to consume a token from the bucket.

        Returns:
            bool: True if token was consumed, False if rate limited
        """
        with self.lock:
            now = time.time()
            self._refill_tokens(now)

            if self.tokens >= 1.0:
                self.tokens -= 1.0
                return True
            else:
                return False

    def _refill_tokens(self, current_time: float) -> None:
        """Refill tokens based on elapsed time."""
        if not self.rate_limit.enabled:
            self.tokens = self.rate_limit.bucket_size
            return

        elapsed = current_time - self.last_refill
        tokens_to_add = elapsed * self.rate_limit.refill_rate

        self.tokens = min(self.rate_limit.bucket_size, self.tokens + tokens_to_add)
        self.last_refill = current_time

    def get_status(self) -> Dict[str, Any]:
        """Get current bucket status."""
        with self.lock:
            now = time.time()
            self._refill_tokens(now)

            return {
                "current_tokens": round(self.tokens, 2),
                "max_tokens": self.rate_limit.bucket_size,
                "refill_rate": self.rate_limit.refill_rate,
                "enabled": self.rate_limit.enabled,
                "time_to_token": (
                    max(0, (1.0 - self.tokens) / self.rate_limit.refill_rate)
                    if self.tokens < 1.0
                    else 0
                ),
            }


class VoidCatRateLimiter:
    """
    Comprehensive rate limiting system for VoidCat enhanced MCP server.

    Provides multi-level rate limiting with configurable limits, monitoring,
    and integration with the enhanced MCP server architecture.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the rate limiter with configuration.

        Args:
            config: Rate limiting configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger("VoidCat.RateLimiter")

        # Rate limit configurations
        self.limits = self._initialize_rate_limits()

        # Token buckets for different contexts
        self.client_buckets: Dict[str, TokenBucket] = {}
        self.tool_buckets: Dict[str, TokenBucket] = {}
        self.global_bucket: Optional[TokenBucket] = None

        # Statistics tracking
        self.client_stats: Dict[str, RateLimitStatus] = defaultdict(self._create_status)
        self.tool_stats: Dict[str, RateLimitStatus] = defaultdict(self._create_status)
        self.global_stats = self._create_status()

        # Request history for analysis
        self.request_history: deque = deque(maxlen=10000)

        # Initialize global rate limiter if configured
        if "global" in self.limits:
            self.global_bucket = TokenBucket(self.limits["global"])

        self.logger.info(
            "VoidCat Rate Limiter initialized with comprehensive protection"
        )

    def _initialize_rate_limits(self) -> Dict[str, RateLimit]:
        """Initialize rate limit configurations."""
        default_limits = {
            # Global rate limits (all requests)
            "global": RateLimit(
                requests_per_second=10.0, burst_size=20, window_size_seconds=60
            ),
            # Per-client rate limits
            "client_default": RateLimit(
                requests_per_second=2.0, burst_size=5, window_size_seconds=60
            ),
            # Per-tool rate limits
            "tool_default": RateLimit(
                requests_per_second=1.0, burst_size=3, window_size_seconds=60
            ),
            # Specific tool limits for resource-intensive operations
            "tool_code_analyze": RateLimit(
                requests_per_second=0.5, burst_size=2, window_size_seconds=120
            ),
            "tool_file_search": RateLimit(
                requests_per_second=1.0, burst_size=3, window_size_seconds=60
            ),
            "tool_bulk_operations": RateLimit(
                requests_per_second=0.2, burst_size=1, window_size_seconds=300
            ),
            # Memory and task operations (more lenient)
            "tool_memory": RateLimit(
                requests_per_second=2.0, burst_size=5, window_size_seconds=60
            ),
            "tool_task": RateLimit(
                requests_per_second=3.0, burst_size=8, window_size_seconds=60
            ),
        }

        # Override with user configuration
        user_limits = self.config.get("rate_limits", {})
        for key, user_config in user_limits.items():
            if isinstance(user_config, dict):
                default_limits[key] = RateLimit(**user_config)

        return default_limits

    def _create_status(self) -> RateLimitStatus:
        """Create a new rate limit status object."""
        now = time.time()
        return RateLimitStatus(
            current_tokens=0.0,
            last_refill=now,
            request_count=0,
            blocked_count=0,
            first_request=now,
            last_request=now,
        )

    def _get_client_id(self, request_context: Dict[str, Any]) -> str:
        """Extract client ID from request context."""
        # For MCP, we can use the request ID pattern or source info
        client_id = request_context.get("client_id")
        if client_id:
            return str(client_id)

        # Fallback to request ID pattern analysis
        request_id = request_context.get("request_id", "unknown")
        if isinstance(request_id, str) and "-" in request_id:
            # Extract potential client identifier from request ID
            return request_id.split("-")[0]

        return "default_client"

    def _get_tool_name(self, request_context: Dict[str, Any]) -> str:
        """Extract tool name from request context."""
        return request_context.get("tool_name", "unknown_tool")

    def _get_bucket_for_client(self, client_id: str) -> TokenBucket:
        """Get or create token bucket for client."""
        if client_id not in self.client_buckets:
            limit_key = (
                f"client_{client_id}"
                if f"client_{client_id}" in self.limits
                else "client_default"
            )
            self.client_buckets[client_id] = TokenBucket(self.limits[limit_key])

        return self.client_buckets[client_id]

    def _get_bucket_for_tool(self, tool_name: str) -> TokenBucket:
        """Get or create token bucket for tool."""
        if tool_name not in self.tool_buckets:
            # Check for specific tool configuration
            limit_key = f"tool_{tool_name}"
            if limit_key not in self.limits:
                # Check for tool category configuration
                if "code" in tool_name or "analyze" in tool_name:
                    limit_key = "tool_code_analyze"
                elif "file" in tool_name or "search" in tool_name:
                    limit_key = "tool_file_search"
                elif "bulk" in tool_name:
                    limit_key = "tool_bulk_operations"
                elif "memory" in tool_name:
                    limit_key = "tool_memory"
                elif "task" in tool_name:
                    limit_key = "tool_task"
                else:
                    limit_key = "tool_default"

            self.tool_buckets[tool_name] = TokenBucket(self.limits[limit_key])

        return self.tool_buckets[tool_name]

    def _update_stats(self, stats: RateLimitStatus, allowed: bool) -> None:
        """Update statistics for a rate limiting decision."""
        now = time.time()

        if stats.request_count == 0:
            stats.first_request = now

        stats.request_count += 1
        stats.last_request = now

        if not allowed:
            stats.blocked_count += 1

    async def check_rate_limit(
        self, request_context: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request should be rate limited.

        Args:
            request_context: Request context containing client and tool information

        Returns:
            Tuple[bool, Dict[str, Any]]: (allowed, rate_limit_info)
        """
        now = time.time()
        client_id = self._get_client_id(request_context)
        tool_name = self._get_tool_name(request_context)

        # Check global rate limit first
        global_allowed = True
        if self.global_bucket:
            global_allowed = self.global_bucket.consume_token()
            self._update_stats(self.global_stats, global_allowed)

        # Check client rate limit
        client_bucket = self._get_bucket_for_client(client_id)
        client_allowed = client_bucket.consume_token()
        self._update_stats(self.client_stats[client_id], client_allowed)

        # Check tool rate limit
        tool_bucket = self._get_bucket_for_tool(tool_name)
        tool_allowed = tool_bucket.consume_token()
        self._update_stats(self.tool_stats[tool_name], tool_allowed)

        # Request is allowed only if all limits pass
        allowed = global_allowed and client_allowed and tool_allowed

        # Record request in history
        self.request_history.append(
            {
                "timestamp": now,
                "client_id": client_id,
                "tool_name": tool_name,
                "allowed": allowed,
                "global_allowed": global_allowed,
                "client_allowed": client_allowed,
                "tool_allowed": tool_allowed,
            }
        )

        # Prepare rate limit information
        rate_limit_info = {
            "allowed": allowed,
            "client_id": client_id,
            "tool_name": tool_name,
            "limits_checked": {
                "global": {
                    "allowed": global_allowed,
                    "status": (
                        self.global_bucket.get_status() if self.global_bucket else None
                    ),
                },
                "client": {
                    "allowed": client_allowed,
                    "status": client_bucket.get_status(),
                },
                "tool": {"allowed": tool_allowed, "status": tool_bucket.get_status()},
            },
            "retry_after": self._calculate_retry_after(
                global_allowed, client_allowed, tool_allowed, client_bucket, tool_bucket
            ),
        }

        if not allowed:
            self.logger.warning(
                f"Rate limit exceeded for client {client_id}, tool {tool_name}"
            )

        return allowed, rate_limit_info

    def _calculate_retry_after(
        self,
        global_allowed: bool,
        client_allowed: bool,
        tool_allowed: bool,
        client_bucket: TokenBucket,
        tool_bucket: TokenBucket,
    ) -> float:
        """Calculate suggested retry-after time in seconds."""
        retry_times = []

        if not global_allowed and self.global_bucket:
            retry_times.append(self.global_bucket.get_status()["time_to_token"])

        if not client_allowed:
            retry_times.append(client_bucket.get_status()["time_to_token"])

        if not tool_allowed:
            retry_times.append(tool_bucket.get_status()["time_to_token"])

        return max(retry_times) if retry_times else 0.0

    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive rate limiting status and statistics."""
        now = time.time()

        # Calculate recent request rates
        recent_requests = [
            r for r in self.request_history if now - r["timestamp"] < 300
        ]  # Last 5 minutes

        status = {
            "rate_limiter": {
                "enabled": True,
                "total_clients": len(self.client_stats),
                "total_tools": len(self.tool_stats),
                "request_history_size": len(self.request_history),
            },
            "global_stats": (
                self.global_stats.to_dict()
                if hasattr(self.global_stats, "to_dict")
                else {}
            ),
            "recent_activity": {
                "requests_last_5min": len(recent_requests),
                "blocked_last_5min": sum(
                    1 for r in recent_requests if not r["allowed"]
                ),
                "active_clients": len(set(r["client_id"] for r in recent_requests)),
                "active_tools": len(set(r["tool_name"] for r in recent_requests)),
            },
            "top_clients": self._get_top_clients(5),
            "top_tools": self._get_top_tools(5),
            "rate_limits": {
                key: {
                    "requests_per_second": limit.requests_per_second,
                    "burst_size": limit.burst_size,
                    "enabled": limit.enabled,
                }
                for key, limit in self.limits.items()
            },
        }

        return status

    def _get_top_clients(self, limit: int) -> List[Dict[str, Any]]:
        """Get top clients by request count."""
        client_data = []
        for client_id, stats in self.client_stats.items():
            client_data.append(
                {
                    "client_id": client_id,
                    "request_count": stats.request_count,
                    "blocked_count": stats.blocked_count,
                    "block_rate": (stats.blocked_count / max(1, stats.request_count))
                    * 100,
                }
            )

        return sorted(client_data, key=lambda x: x["request_count"], reverse=True)[
            :limit
        ]

    def _get_top_tools(self, limit: int) -> List[Dict[str, Any]]:
        """Get top tools by request count."""
        tool_data = []
        for tool_name, stats in self.tool_stats.items():
            tool_data.append(
                {
                    "tool_name": tool_name,
                    "request_count": stats.request_count,
                    "blocked_count": stats.blocked_count,
                    "block_rate": (stats.blocked_count / max(1, stats.request_count))
                    * 100,
                }
            )

        return sorted(tool_data, key=lambda x: x["request_count"], reverse=True)[:limit]

    def update_configuration(self, new_config: Dict[str, Any]) -> bool:
        """
        Update rate limiting configuration dynamically.

        Args:
            new_config: New configuration to apply

        Returns:
            bool: True if configuration was updated successfully
        """
        try:
            # Update rate limits
            rate_limits = new_config.get("rate_limits", {})
            for key, limit_config in rate_limits.items():
                if isinstance(limit_config, dict):
                    self.limits[key] = RateLimit(**limit_config)

                    # Update existing buckets with new configuration
                    if key.startswith("client_"):
                        client_id = key[7:]  # Remove "client_" prefix
                        if client_id in self.client_buckets:
                            self.client_buckets[client_id] = TokenBucket(
                                self.limits[key]
                            )

                    elif key.startswith("tool_"):
                        tool_name = key[5:]  # Remove "tool_" prefix
                        if tool_name in self.tool_buckets:
                            self.tool_buckets[tool_name] = TokenBucket(self.limits[key])

                    elif key == "global" and self.global_bucket:
                        self.global_bucket = TokenBucket(self.limits[key])

            self.config.update(new_config)
            self.logger.info("Rate limiting configuration updated successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to update rate limiting configuration: {str(e)}")
            return False

    def reset_client_limits(self, client_id: Optional[str] = None) -> bool:
        """
        Reset rate limits for a specific client or all clients.

        Args:
            client_id: Specific client to reset, or None for all clients

        Returns:
            bool: True if reset was successful
        """
        try:
            if client_id:
                if client_id in self.client_buckets:
                    del self.client_buckets[client_id]
                if client_id in self.client_stats:
                    del self.client_stats[client_id]
                self.logger.info(f"Reset rate limits for client: {client_id}")
            else:
                self.client_buckets.clear()
                self.client_stats.clear()
                self.logger.info("Reset rate limits for all clients")

            return True

        except Exception as e:
            self.logger.error(f"Failed to reset client limits: {str(e)}")
            return False


# Integration helper for enhanced MCP server
def create_rate_limiter_middleware(rate_limiter: VoidCatRateLimiter):
    """
    Create middleware function for integration with enhanced MCP server.

    Args:
        rate_limiter: Configured VoidCatRateLimiter instance

    Returns:
        Async middleware function
    """

    async def rate_limit_middleware(
        request_context: Dict[str, Any],
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Middleware function to check rate limits for MCP requests.

        Args:
            request_context: MCP request context

        Returns:
            Tuple[bool, Optional[Dict[str, Any]]]: (proceed, error_response)
        """
        allowed, rate_limit_info = await rate_limiter.check_rate_limit(request_context)

        if not allowed:
            error_response = {
                "error": {
                    "code": 429,
                    "message": "Rate limit exceeded",
                    "data": {
                        "retry_after": rate_limit_info["retry_after"],
                        "limits": rate_limit_info["limits_checked"],
                    },
                }
            }
            return False, error_response

        return True, None

    return rate_limit_middleware


# Example usage and testing
if __name__ == "__main__":

    async def test_rate_limiter():
        """Test the rate limiting system."""
        print("Testing VoidCat Rate Limiting System")
        print("=" * 40)

        # Create rate limiter with test configuration
        config = {
            "rate_limits": {
                "global": {"requests_per_second": 5.0, "burst_size": 10},
                "client_default": {"requests_per_second": 2.0, "burst_size": 5},
                "tool_default": {"requests_per_second": 1.0, "burst_size": 3},
            }
        }

        rate_limiter = VoidCatRateLimiter(config)

        # Test requests
        test_requests = [
            {"client_id": "test_client_1", "tool_name": "voidcat_task_create"},
            {"client_id": "test_client_1", "tool_name": "voidcat_task_list"},
            {"client_id": "test_client_2", "tool_name": "voidcat_code_analyze"},
            {
                "client_id": "test_client_1",
                "tool_name": "voidcat_task_create",
            },  # Should hit tool limit
        ]

        for i, request in enumerate(test_requests):
            allowed, info = await rate_limiter.check_rate_limit(request)
            print(f"Request {i+1}: {request['tool_name']} from {request['client_id']}")
            print(f"  Allowed: {allowed}")
            if not allowed:
                print(f"  Retry after: {info['retry_after']:.2f}s")
            print()

        # Show comprehensive status
        status = rate_limiter.get_comprehensive_status()
        print("Rate Limiter Status:")
        print(json.dumps(status, indent=2))

    asyncio.run(test_rate_limiter())
