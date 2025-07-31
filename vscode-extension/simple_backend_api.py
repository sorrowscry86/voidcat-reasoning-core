"""
Simplified VoidCat Backend API for VS Code Extension
====================================================

A minimal implementation of the VS Code backend API endpoints
that provides the necessary functionality without complex dependencies.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

# Create API router for backend integration
backend_router = APIRouter(prefix="/api/v1", tags=["VS Code Backend"])

# Mock data for testing
mock_tasks = [
    {
        "id": "task-1",
        "name": "Implement VS Code Extension",
        "description": "Create a comprehensive VS Code extension for VoidCat",
        "status": "in-progress",
        "priority": 8,
        "complexity": 7,
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
        "tags": ["vscode", "extension", "development"]
    },
    {
        "id": "task-2",
        "name": "Fix Backend Integration",
        "description": "Resolve API endpoint connectivity issues",
        "status": "pending",
        "priority": 9,
        "complexity": 5,
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
        "tags": ["backend", "api", "integration"]
    }
]

mock_memories = [
    {
        "id": "mem-1",
        "title": "VS Code Extension Architecture",
        "content": "The extension follows a modular architecture with separate panels for tasks, memory, and diagnostics.",
        "category": "project",
        "tags": ["architecture", "vscode"],
        "created_at": datetime.now().isoformat()
    },
    {
        "id": "mem-2", 
        "title": "API Integration Patterns",
        "content": "Best practices for integrating VS Code extensions with backend APIs using REST and WebSocket connections.",
        "category": "code",
        "tags": ["api", "integration", "patterns"],
        "created_at": datetime.now().isoformat()
    }
]

# Request/Response Models
class TaskCreateRequest(BaseModel):
    name: str = Field(..., description="Task name")
    description: str = Field(..., description="Task description")
    priority: int = Field(5, ge=1, le=10, description="Task priority (1-10)")
    complexity: int = Field(3, ge=1, le=10, description="Task complexity (1-10)")
    tags: Optional[List[str]] = Field([], description="Task tags")

class MemoryCreateRequest(BaseModel):
    title: str = Field(..., description="Memory title")
    content: str = Field(..., description="Memory content")
    category: str = Field("general", description="Memory category")
    tags: Optional[List[str]] = Field([], description="Memory tags")

# System Status Endpoint
@backend_router.get("/system/status")
async def get_system_status():
    """Get comprehensive system status for VS Code extension dashboard"""
    return {
        "system_status": "online",
        "uptime": "15 minutes",
        "websocket_connected": len(manager.active_connections) > 0,
        "websocket_url": "ws://localhost:8003/vscode/api/v1/ws",
        "task_statistics": {
            "total": len(mock_tasks),
            "completed": len([t for t in mock_tasks if t["status"] == "completed"]),
            "in_progress": len([t for t in mock_tasks if t["status"] == "in-progress"]),
            "pending": len([t for t in mock_tasks if t["status"] == "pending"])
        },
        "memory_statistics": {
            "total": len(mock_memories),
            "categories": {
                "general": len([m for m in mock_memories if m["category"] == "general"]),
                "code": len([m for m in mock_memories if m["category"] == "code"]),
                "project": len([m for m in mock_memories if m["category"] == "project"])
            }
        },
        "documents_loaded": 12,
        "engine_initialized": True,
        "last_query_timestamp": datetime.now().isoformat(),
        "total_queries_processed": 42
    }

# Task Management Endpoints
@backend_router.get("/tasks")
async def get_tasks(status: Optional[str] = None):
    """Get all tasks with optional status filtering"""
    tasks = mock_tasks
    if status:
        tasks = [task for task in tasks if task["status"] == status]
    return tasks

@backend_router.post("/tasks")
async def create_task(task_request: TaskCreateRequest):
    """Create a new task"""
    new_task = {
        "id": f"task-{len(mock_tasks) + 1}",
        "name": task_request.name,
        "description": task_request.description,
        "status": "pending",
        "priority": task_request.priority,
        "complexity": task_request.complexity,
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
        "tags": task_request.tags or []
    }
    mock_tasks.append(new_task)
    return new_task

@backend_router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """Get a specific task by ID"""
    task = next((t for t in mock_tasks if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@backend_router.put("/tasks/{task_id}")
async def update_task(task_id: str, updates: dict):
    """Update a specific task"""
    task = next((t for t in mock_tasks if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Apply updates
    for key, value in updates.items():
        if key in task:
            task[key] = value
    task["updatedAt"] = datetime.now().isoformat()
    
    return task

@backend_router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a specific task"""
    global mock_tasks
    task = next((t for t in mock_tasks if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    mock_tasks = [t for t in mock_tasks if t["id"] != task_id]
    return {"message": "Task deleted successfully"}

# Memory Management Endpoints
@backend_router.get("/memories")
async def get_memories(category: Optional[str] = None, limit: int = 50):
    """Get all memories with optional filtering"""
    memories = mock_memories
    if category:
        memories = [memory for memory in memories if memory["category"] == category]
    return memories[:limit]

@backend_router.post("/memories")
async def create_memory(memory_request: MemoryCreateRequest):
    """Create a new memory"""
    new_memory = {
        "id": f"mem-{len(mock_memories) + 1}",
        "title": memory_request.title,
        "content": memory_request.content,
        "category": memory_request.category,
        "tags": memory_request.tags or [],
        "created_at": datetime.now().isoformat()
    }
    mock_memories.append(new_memory)
    return new_memory

@backend_router.post("/memories/search")
async def search_memories(search_request: dict):
    """Search memories by query"""
    query = search_request.get("query", "").lower()
    results = []
    
    for memory in mock_memories:
        if (query in memory["title"].lower() or 
            query in memory["content"].lower() or
            any(query in tag.lower() for tag in memory["tags"])):
            results.append(memory)
    
    return results

@backend_router.get("/memories/{memory_id}")
async def get_memory(memory_id: str):
    """Get a specific memory by ID"""
    memory = next((m for m in mock_memories if m["id"] == memory_id), None)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory

# Project Management (simplified)
@backend_router.get("/projects")
async def get_projects():
    """Get all projects"""
    return [
        {
            "id": "proj-1",
            "name": "VoidCat VS Code Extension",
            "description": "Comprehensive VS Code extension for VoidCat reasoning core",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"🔌 WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"🔌 WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"❌ Failed to send WebSocket message: {e}")

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"❌ WebSocket broadcast failed: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            self.disconnect(conn)

# Global connection manager
manager = ConnectionManager()

# WebSocket endpoint
@backend_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        # Send initial connection message
        await manager.send_personal_message(
            json.dumps({
                "type": "connection_established",
                "message": "Connected to VoidCat VS Code backend",
                "timestamp": datetime.now().isoformat()
            }),
            websocket
        )
        
        # Send periodic updates
        import asyncio
        while True:
            # Send a heartbeat every 30 seconds
            await asyncio.sleep(30)
            await manager.send_personal_message(
                json.dumps({
                    "type": "heartbeat",
                    "timestamp": datetime.now().isoformat(),
                    "active_connections": len(manager.active_connections)
                }),
                websocket
            )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        manager.disconnect(websocket)

def integrate_simple_backend(app):
    """
    Integrate the simplified VS Code backend with the main FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    app.include_router(backend_router, prefix="/vscode")
    print("✅ Simplified VS Code backend integration loaded successfully")
    print("🔌 WebSocket endpoint available at: ws://localhost:8003/vscode/api/v1/ws")