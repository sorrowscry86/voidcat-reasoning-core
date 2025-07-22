"""
VoidCat VS Code Extension Configuration
=======================================

Configuration and authentication module for VS Code extension backend integration.
Handles security, authentication, and configuration management.
"""

import hashlib
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel


class ExtensionConfig(BaseModel):
    """Configuration for VS Code extension backend"""

    api_key: Optional[str] = None
    allow_anonymous: bool = True
    max_connections: int = 10
    session_timeout: int = 3600  # 1 hour in seconds
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # 1 minute in seconds


class SecurityManager:
    """Handles security and authentication for VS Code extension"""

    def __init__(self, config: ExtensionConfig):
        self.config = config
        self.active_sessions = {}
        self.rate_limits = {}

    def generate_session_token(self) -> str:
        """Generate a secure session token"""
        return secrets.token_urlsafe(32)

    def validate_session(self, token: str) -> bool:
        """Validate a session token"""
        if token in self.active_sessions:
            session = self.active_sessions[token]
            if datetime.now() < session["expires"]:
                return True
            else:
                # Clean up expired session
                del self.active_sessions[token]
        return False

    def create_session(self, client_id: str) -> str:
        """Create a new session"""
        token = self.generate_session_token()
        self.active_sessions[token] = {
            "client_id": client_id,
            "created": datetime.now(),
            "expires": datetime.now() + timedelta(seconds=self.config.session_timeout),
        }
        return token

    def check_rate_limit(self, client_id: str) -> bool:
        """Check if client has exceeded rate limit"""
        now = datetime.now()

        if client_id not in self.rate_limits:
            self.rate_limits[client_id] = []

        # Clean up old requests
        self.rate_limits[client_id] = [
            req_time
            for req_time in self.rate_limits[client_id]
            if now - req_time < timedelta(seconds=self.config.rate_limit_window)
        ]

        # Check if under limit
        if len(self.rate_limits[client_id]) < self.config.rate_limit_requests:
            self.rate_limits[client_id].append(now)
            return True

        return False

    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        now = datetime.now()
        expired_tokens = [
            token
            for token, session in self.active_sessions.items()
            if now >= session["expires"]
        ]

        for token in expired_tokens:
            del self.active_sessions[token]


# Global configuration instance
extension_config = ExtensionConfig(
    allow_anonymous=True,
    max_connections=10,
    session_timeout=3600,
    rate_limit_requests=100,
    rate_limit_window=60,
)

# Global security manager
security_manager = SecurityManager(extension_config)


# Authentication dependency for FastAPI
async def get_current_session(token: str = None) -> Optional[str]:
    """FastAPI dependency for authentication"""
    if extension_config.allow_anonymous:
        return "anonymous"

    if not token:
        return None

    if security_manager.validate_session(token):
        return token

    return None


# Rate limiting dependency
async def check_rate_limit(client_id: str = "anonymous") -> bool:
    """FastAPI dependency for rate limiting"""
    return security_manager.check_rate_limit(client_id)


# Export configuration and security components
__all__ = [
    "ExtensionConfig",
    "SecurityManager",
    "extension_config",
    "security_manager",
    "get_current_session",
    "check_rate_limit",
]
