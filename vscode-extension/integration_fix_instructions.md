# VS Code Extension Integration Fix Instructions

## Problem
The VS Code extension can't connect because the backend server doesn't have the required `/vscode/api/v1/*` endpoints.

## Solution
Replace the VS Code integration section in `api_gateway.py` (around lines 283-294) with this code:

```python
# ==========================================
# VS Code Extension Backend Integration
# ==========================================
try:
    import sys
    from pathlib import Path
    
    # Add vscode-extension directory to path
    vscode_extension_path = Path(__file__).parent / "vscode-extension"
    sys.path.insert(0, str(vscode_extension_path))
    
    from simple_integration import integrate_vscode_backend

    integrate_vscode_backend(app)
    logger.info("✅ VS Code backend integration loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ VS Code backend integration not available: {e}")
except Exception as e:
    logger.error(f"❌ VS Code backend integration failed: {e}")
```

## What This Does
1. Adds the vscode-extension directory to Python path
2. Imports our simplified integration module
3. Provides all the endpoints your VS Code extension needs:
   - `/vscode/api/v1/system/status`
   - `/vscode/api/v1/tasks`
   - `/vscode/api/v1/memories`
   - `/vscode/api/v1/projects`

## After Making This Change
1. Restart the server: `uvicorn api_gateway:app --host localhost --port 8003 --reload`
2. Test the connection: Your VS Code extension should now connect successfully!

## Test Endpoints
Once the server is running, you can test these URLs:
- http://localhost:8003/vscode/api/v1/system/status
- http://localhost:8003/vscode/api/v1/tasks
- http://localhost:8003/diagnostics (original endpoint)