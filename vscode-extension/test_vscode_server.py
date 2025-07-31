#!/usr/bin/env python3
"""
Test Server for VS Code Extension
=================================

A standalone server that provides all the endpoints your VS Code extension needs.
Run this to test your extension while you fix the main integration.
"""

import sys
from pathlib import Path

# Add parent directory to path for engine imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
import uvicorn
from simple_backend_api import integrate_simple_backend

# Create FastAPI app
app = FastAPI(
    title="VoidCat VS Code Extension Test Server",
    description="Test server providing VS Code extension endpoints",
    version="1.0.0"
)

# Basic endpoints (mimicking api_gateway.py)
@app.get("/")
async def root():
    return {
        "status": "healthy", 
        "engine_ready": True, 
        "message": "VoidCat VS Code Extension Test Server is running!"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "engine_ready": True,
        "message": "All systems operational"
    }

@app.get("/diagnostics")
async def diagnostics():
    return {
        "status": "online",
        "documents_loaded": 12,
        "total_queries_processed": 42,
        "last_query_timestamp": "2025-01-29T12:00:00Z",
        "health": "healthy"
    }

# Integrate VS Code backend
integrate_simple_backend(app)

if __name__ == "__main__":
    print("🚀 Starting VoidCat VS Code Extension Test Server...")
    print("📍 Server running on: http://localhost:8003")
    print("🔧 Provides all VS Code extension endpoints")
    print("📋 Available endpoints:")
    print("   • http://localhost:8003/vscode/api/v1/system/status")
    print("   • http://localhost:8003/vscode/api/v1/tasks")
    print("   • http://localhost:8003/vscode/api/v1/memories")
    print("   • http://localhost:8003/diagnostics")
    print("=" * 60)
    
    uvicorn.run(app, host="localhost", port=8003, log_level="info")