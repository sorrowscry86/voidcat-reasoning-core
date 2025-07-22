"""
VoidCat VS Code Extension Backend Module
========================================

This module provides backend integration for the VoidCat VS Code extension,
including REST API endpoints for task management, memory system, and real-time updates.
"""

__version__ = "1.0.0"
__author__ = "Ryuzu"

# Import main components for easy access
from .api_integration import integrate_vscode_backend
from .backend_integration_api import ConnectionManager, backend_router, manager

__all__ = ["integrate_vscode_backend", "backend_router", "manager", "ConnectionManager"]
