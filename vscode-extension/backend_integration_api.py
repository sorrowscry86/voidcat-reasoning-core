"""
VoidCat Backend Integration API Extensions
==========================================

Extended API endpoints for VS Code extension integration with VoidCat V2 system.
Provides REST API access to task management, memory system, and enhanced features.

Author: Ryuzu
License: MIT
"""

import os
import sys
from pathlib import Path

# Ensure the main project directory is in Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from voidcat_memory_models import MemoryCategory, VoidCatMemory
from voidcat_memory_storage import VoidCatMemoryStorage
from voidcat_operations import create_operations_engine

# Import VoidCat modules
from voidcat_task_models import Priority, TaskStatus, VoidCatProject, VoidCatTask

# Create API router for backend integration
backend_router = APIRouter(prefix="/api/v1", tags=["Backend Integration"])


# WebSocket connection manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


# Request/Response Models
class TaskCreateRequest(BaseModel):
    name: str = Field(..., description="Task name")
    description: str = Field(..., description="Task description")
    priority: int = Field(5, ge=1, le=10, description="Task priority (1-10)")
    complexity: int = Field(3, ge=1, le=10, description="Task complexity (1-10)")
    project_id: Optional[str] = Field(None, description="Project ID")
    parent_id: Optional[str] = Field(None, description="Parent task ID")
    tags: Optional[List[str]] = Field([], description="Task tags")
    estimated_hours: Optional[float] = Field(None, description="Estimated hours")


class TaskUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[int] = Field(None, ge=1, le=10)
    complexity: Optional[int] = Field(None, ge=1, le=10)
    parent_id: Optional[str] = None
    tags: Optional[List[str]] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None


class ProjectCreateRequest(BaseModel):
    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project description")


class MemoryCreateRequest(BaseModel):
    title: str = Field(..., description="Memory title")
    content: str = Field(..., description="Memory content")
    category: Optional[MemoryCategory] = Field(
        MemoryCategory.GENERAL, description="Memory category"
    )
    tags: Optional[List[str]] = Field([], description="Memory tags")
    metadata: Optional[Dict[str, Any]] = Field({}, description="Additional metadata")


# Initialize engines (will be properly configured in main app)
operations_engine = None
memory_storage = None


async def get_operations_engine():
    """Dependency to get operations engine"""
    global operations_engine
    if operations_engine is None:
        operations_engine = create_operations_engine()
    return operations_engine


async def get_memory_storage():
    """Dependency to get memory storage"""
    global memory_storage
    if memory_storage is None:
        memory_storage = VoidCatMemoryStorage()
    return memory_storage


# Task Management Endpoints
@backend_router.get("/tasks", response_model=List[Dict[str, Any]])
async def get_tasks(
    project_id: Optional[str] = None,
    status: Optional[TaskStatus] = None,
    ops_engine=Depends(get_operations_engine),
):
    """Get all tasks with optional filtering"""
    try:
        tasks = await ops_engine.get_all_tasks()

        # Apply filters
        if project_id:
            tasks = [task for task in tasks if task.project_id == project_id]
        if status:
            tasks = [task for task in tasks if task.status == status]

        return [task.to_dict() for task in tasks]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tasks: {str(e)}")


@backend_router.post("/tasks", response_model=Dict[str, Any])
async def create_task(
    task_request: TaskCreateRequest, ops_engine=Depends(get_operations_engine)
):
    """Create a new task"""
    try:
        task = VoidCatTask(
            name=task_request.name,
            description=task_request.description,
            priority=Priority(task_request.priority),
            complexity=task_request.complexity,
            project_id=task_request.project_id,
            parent_id=task_request.parent_id,
            tags=task_request.tags or [],
            estimated_hours=task_request.estimated_hours,
        )

        created_task = await ops_engine.create_task(task)

        # Broadcast update to connected clients
        await manager.broadcast(
            json.dumps({"type": "task_created", "task": created_task.to_dict()})
        )

        return created_task.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")


@backend_router.get("/tasks/{task_id}", response_model=Dict[str, Any])
async def get_task(task_id: str, ops_engine=Depends(get_operations_engine)):
    """Get a specific task by ID"""
    try:
        task = await ops_engine.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task: {str(e)}")


@backend_router.put("/tasks/{task_id}", response_model=Dict[str, Any])
async def update_task(
    task_id: str,
    task_update: TaskUpdateRequest,
    ops_engine=Depends(get_operations_engine),
):
    """Update a specific task"""
    try:
        # Get existing task
        existing_task = await ops_engine.get_task(task_id)
        if not existing_task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Apply updates
        update_dict = task_update.dict(exclude_unset=True)
        updated_task = await ops_engine.update_task(task_id, update_dict)

        # Broadcast update to connected clients
        await manager.broadcast(
            json.dumps({"type": "task_updated", "task": updated_task.to_dict()})
        )

        return updated_task.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update task: {str(e)}")


@backend_router.delete("/tasks/{task_id}")
async def delete_task(task_id: str, ops_engine=Depends(get_operations_engine)):
    """Delete a specific task"""
    try:
        # Check if task exists
        existing_task = await ops_engine.get_task(task_id)
        if not existing_task:
            raise HTTPException(status_code=404, detail="Task not found")

        await ops_engine.delete_task(task_id)

        # Broadcast update to connected clients
        await manager.broadcast(
            json.dumps({"type": "task_deleted", "task_id": task_id})
        )

        return {"message": "Task deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete task: {str(e)}")


# Project Management Endpoints
@backend_router.get("/projects", response_model=List[Dict[str, Any]])
async def get_projects(ops_engine=Depends(get_operations_engine)):
    """Get all projects"""
    try:
        projects = await ops_engine.get_all_projects()
        return [project.to_dict() for project in projects]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get projects: {str(e)}")


@backend_router.post("/projects", response_model=Dict[str, Any])
async def create_project(
    project_request: ProjectCreateRequest, ops_engine=Depends(get_operations_engine)
):
    """Create a new project"""
    try:
        project = VoidCatProject(
            name=project_request.name, description=project_request.description
        )

        created_project = await ops_engine.create_project(project)

        # Broadcast update to connected clients
        await manager.broadcast(
            json.dumps(
                {"type": "project_created", "project": created_project.to_dict()}
            )
        )

        return created_project.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create project: {str(e)}"
        )


@backend_router.get("/projects/{project_id}", response_model=Dict[str, Any])
async def get_project(project_id: str, ops_engine=Depends(get_operations_engine)):
    """Get a specific project by ID"""
    try:
        project = await ops_engine.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project: {str(e)}")


@backend_router.delete("/projects/{project_id}")
async def delete_project(project_id: str, ops_engine=Depends(get_operations_engine)):
    """Delete a specific project"""
    try:
        # Check if project exists
        existing_project = await ops_engine.get_project(project_id)
        if not existing_project:
            raise HTTPException(status_code=404, detail="Project not found")

        await ops_engine.delete_project(project_id)

        # Broadcast update to connected clients
        await manager.broadcast(
            json.dumps({"type": "project_deleted", "project_id": project_id})
        )

        return {"message": "Project deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete project: {str(e)}"
        )


# Memory Management Endpoints
@backend_router.get("/memories", response_model=List[Dict[str, Any]])
async def get_memories(
    category: Optional[MemoryCategory] = None,
    limit: int = 50,
    memory_storage=Depends(get_memory_storage),
):
    """Get all memories with optional filtering"""
    try:
        memories = await memory_storage.get_all_memories(limit=limit)

        # Apply category filter
        if category:
            memories = [memory for memory in memories if memory.category == category]

        return [memory.to_dict() for memory in memories]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get memories: {str(e)}")


@backend_router.post("/memories", response_model=Dict[str, Any])
async def create_memory(
    memory_request: MemoryCreateRequest, memory_storage=Depends(get_memory_storage)
):
    """Create a new memory"""
    try:
        memory = VoidCatMemory(
            title=memory_request.title,
            content=memory_request.content,
            category=memory_request.category,
            tags=memory_request.tags or [],
            metadata=memory_request.metadata or {},
        )

        created_memory = await memory_storage.store_memory(memory)

        # Broadcast update to connected clients
        await manager.broadcast(
            json.dumps({"type": "memory_created", "memory": created_memory.to_dict()})
        )

        return created_memory.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create memory: {str(e)}"
        )


@backend_router.get("/memories/search")
async def search_memories(
    query: str,
    category: Optional[MemoryCategory] = None,
    limit: int = 10,
    memory_storage=Depends(get_memory_storage),
):
    """Search memories by query"""
    try:
        results = await memory_storage.search_memories(
            query=query, category=category, limit=limit
        )

        return [result.to_dict() for result in results]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to search memories: {str(e)}"
        )


@backend_router.get("/memories/{memory_id}", response_model=Dict[str, Any])
async def get_memory(memory_id: str, memory_storage=Depends(get_memory_storage)):
    """Get a specific memory by ID"""
    try:
        memory = await memory_storage.get_memory(memory_id)
        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        return memory.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get memory: {str(e)}")


@backend_router.delete("/memories/{memory_id}")
async def delete_memory(memory_id: str, memory_storage=Depends(get_memory_storage)):
    """Delete a specific memory"""
    try:
        # Check if memory exists
        existing_memory = await memory_storage.get_memory(memory_id)
        if not existing_memory:
            raise HTTPException(status_code=404, detail="Memory not found")

        await memory_storage.delete_memory(memory_id)

        # Broadcast update to connected clients
        await manager.broadcast(
            json.dumps({"type": "memory_deleted", "memory_id": memory_id})
        )

        return {"message": "Memory deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete memory: {str(e)}"
        )


# WebSocket endpoint for real-time updates
@backend_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if needed
            message_data = json.loads(data)

            if message_data.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            elif message_data.get("type") == "subscribe":
                # Handle subscription to specific update types
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "subscribed",
                            "message": "Successfully subscribed to updates",
                        }
                    )
                )
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# System Information Endpoints
@backend_router.get("/system/status")
async def get_system_status():
    """Get comprehensive system status"""
    try:
        # Get task statistics
        ops_engine = await get_operations_engine()
        tasks = await ops_engine.get_all_tasks()
        projects = await ops_engine.get_all_projects()

        # Get memory statistics
        memory_storage = await get_memory_storage()
        memories = await memory_storage.get_all_memories(limit=1000)

        # Calculate statistics
        task_stats = {
            "total": len(tasks),
            "completed": len([t for t in tasks if t.status == TaskStatus.COMPLETED]),
            "in_progress": len(
                [t for t in tasks if t.status == TaskStatus.IN_PROGRESS]
            ),
            "pending": len([t for t in tasks if t.status == TaskStatus.PENDING]),
            "blocked": len([t for t in tasks if t.status == TaskStatus.BLOCKED]),
        }

        memory_stats = {"total": len(memories), "categories": {}}

        # Count memories by category
        for memory in memories:
            category = memory.category.value if memory.category else "general"
            memory_stats["categories"][category] = (
                memory_stats["categories"].get(category, 0) + 1
            )

        return {
            "system_status": "online",
            "timestamp": datetime.now().isoformat(),
            "task_statistics": task_stats,
            "memory_statistics": memory_stats,
            "project_count": len(projects),
            "websocket_connections": len(manager.active_connections),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get system status: {str(e)}"
        )


@backend_router.get("/system/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "VoidCat Backend Integration API",
    }


# Utility endpoints
@backend_router.get("/system/recommendations")
async def get_task_recommendations(
    limit: int = 5, ops_engine=Depends(get_operations_engine)
):
    """Get intelligent task recommendations"""
    try:
        # This would integrate with the recommendation engine
        # For now, return basic recommendations based on priority and status
        tasks = await ops_engine.get_all_tasks()

        # Filter pending tasks and sort by priority
        pending_tasks = [t for t in tasks if t.status == TaskStatus.PENDING]
        pending_tasks.sort(
            key=lambda x: (x.priority.value, -x.complexity), reverse=True
        )

        recommendations = []
        for task in pending_tasks[:limit]:
            recommendations.append(
                {
                    "task": task.to_dict(),
                    "reason": f"High priority ({task.priority.value}/10) task ready to start",
                    "score": task.priority.value * 10 + (10 - task.complexity),
                }
            )

        return {"recommendations": recommendations, "total_pending": len(pending_tasks)}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get recommendations: {str(e)}"
        )


# Export the router for integration with main app
__all__ = ["backend_router", "ConnectionManager", "manager"]
