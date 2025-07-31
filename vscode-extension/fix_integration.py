#!/usr/bin/env python3
"""
Quick fix script to test VS Code extension endpoints
This creates a simple test server with the missing endpoints
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(title="VoidCat VS Code Extension Test Server")

# Mock data for testing
mock_tasks = [
    {
        "id": "task-1",
        "name": "Test Task 1",
        "description": "A sample task for testing",
        "status": "pending",
        "priority": 5,
        "complexity": 3,
        "createdAt": "2025-01-29T10:00:00Z",
        "updatedAt": "2025-01-29T10:00:00Z"
    },
    {
        "id": "task-2", 
        "name": "Test Task 2",
        "description": "Another sample task",
        "status": "in-progress",
        "priority": 7,
        "complexity": 5,
        "createdAt": "2025-01-29T09:00:00Z",
        "updatedAt": "2025-01-29T11:00:00Z"
    }
]

@app.get("/")
async def root():
    return {"status": "healthy", "engine_ready": True, "message": "VoidCat VS Code Test Server"}

@app.get("/health")
async def health():
    return {"status": "healthy", "engine_ready": True, "message": "All systems go!"}

@app.get("/diagnostics")
async def diagnostics():
    return {
        "status": "online",
        "documents_loaded": 12,
        "total_queries_processed": 5,
        "last_query_timestamp": "2025-01-29T12:00:00Z",
        "health": "healthy"
    }

@app.get("/vscode/api/v1/system/status")
async def vscode_system_status():
    return {
        "system_status": "online",
        "uptime": "5 minutes",
        "websocket_connected": False,
        "websocket_url": "ws://localhost:8003/vscode/api/v1/ws",
        "task_statistics": {
            "total": 2,
            "completed": 0,
            "in_progress": 1,
            "pending": 1
        },
        "memory_statistics": {
            "total": 10,
            "categories": {
                "general": 5,
                "code": 3,
                "project": 2
            }
        },
        "documents_loaded": 12,
        "engine_initialized": True,
        "last_query_timestamp": "2025-01-29T12:00:00Z",
        "total_queries_processed": 5
    }

@app.get("/vscode/api/v1/tasks")
async def get_tasks():
    return mock_tasks

@app.post("/vscode/api/v1/tasks")
async def create_task(task_data: dict):
    new_task = {
        "id": f"task-{len(mock_tasks) + 1}",
        "name": task_data.get("name", "New Task"),
        "description": task_data.get("description", ""),
        "status": "pending",
        "priority": task_data.get("priority", 5),
        "complexity": task_data.get("complexity", 3),
        "createdAt": "2025-01-29T12:00:00Z",
        "updatedAt": "2025-01-29T12:00:00Z"
    }
    mock_tasks.append(new_task)
    return new_task

@app.get("/vscode/api/v1/memories")
async def get_memories():
    return [
        {
            "id": "mem-1",
            "title": "Sample Memory",
            "content": "This is a test memory",
            "category": "general",
            "created_at": "2025-01-29T10:00:00Z"
        }
    ]

if __name__ == "__main__":
    print("🚀 Starting VoidCat VS Code Extension Test Server...")
    print("📍 Server will run on http://localhost:8003")
    print("🔧 This provides the missing VS Code extension endpoints")
    print("=" * 60)
    
    uvicorn.run(app, host="localhost", port=8004, log_level="info")