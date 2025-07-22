"""
VoidCat API Gateway Integration
===============================

Integration module to add VS Code extension backend API endpoints
to the main VoidCat API gateway.

This module extends the existing api_gateway.py with additional routes
for comprehensive VS Code extension support.
"""

import os
import sys
from pathlib import Path

# Ensure the main project directory is in Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the backend integration API
from .backend_integration_api import backend_router, manager


def integrate_vscode_backend(app):
    """
    Integrate the VS Code backend API with the main FastAPI app.

    Args:
        app: FastAPI application instance
    """
    # Include the backend router
    app.include_router(backend_router, prefix="/vscode")

    # Add startup event for backend initialization
    @app.on_event("startup")
    async def startup_backend():
        """Initialize backend services on startup"""
        try:
            # Initialize the operations engine and memory storage
            # This ensures they're ready when the VS Code extension connects
            from backend_integration_api import (
                get_memory_storage,
                get_operations_engine,
            )

            ops_engine = await get_operations_engine()
            memory_storage = await get_memory_storage()

            print("✅ VS Code backend integration initialized successfully")
        except Exception as e:
            print(f"❌ VS Code backend initialization failed: {e}")

    # Add shutdown event for cleanup
    @app.on_event("shutdown")
    async def shutdown_backend():
        """Cleanup backend services on shutdown"""
        try:
            # Cleanup WebSocket connections
            for connection in manager.active_connections:
                await connection.close()

            print("✅ VS Code backend integration cleaned up successfully")
        except Exception as e:
            print(f"❌ VS Code backend cleanup failed: {e}")

    print("🔗 VS Code backend integration routes added to main API gateway")


# Export the integration function
__all__ = ["integrate_vscode_backend"]
