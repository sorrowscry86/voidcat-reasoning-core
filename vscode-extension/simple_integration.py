"""
Simple VS Code Integration
==========================

A simplified integration module that provides VS Code extension endpoints
without complex dependencies.
"""

def integrate_vscode_backend(app):
    """
    Integrate VS Code backend with the main FastAPI app using simplified backend.
    
    Args:
        app: FastAPI application instance
    """
    try:
        from simple_backend_api import integrate_simple_backend
        integrate_simple_backend(app)
        return True
    except Exception as e:
        print(f"❌ Simple VS Code backend integration failed: {e}")
        return False