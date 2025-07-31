#!/usr/bin/env python3
"""
VoidCat Reasoning Core MCP Server
Enhanced with VS Code integration patterns

This module implements a Model Context Protocol (MCP) server for the VoidCat
Reasoning Core system, providing RAG-enhanced intelligent reasoning capabilities
to Claude Desktop and other MCP clients.

Enhanced Features:
- Comprehensive error handling and recovery
- Detailed status reporting and diagnostics
- File analysis capabilities
- VS Code integration patterns
- Production-ready deployment

Author: VoidCat Reasoning Core Team
License: MIT
Version: 0.2.0 (Enhanced)
"""

import asyncio
import json
import os
import sys
import traceback
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional, Sequence

from enhanced_engine import VoidCatEnhancedEngine
from enhanced_engine import VoidCatEnhancedEngine as VoidCatEngine
from sequential_thinking import SequentialThinkingEngine
from voidcat_context_integration import create_context_integration
from voidcat_mcp_tools import create_mcp_task_tools
from voidcat_memory_mcp_tools import create_memory_mcp_tools


def debug_print(message: str, force: bool = False) -> None:
    """Enhanced debug printing with stderr output for MCP debugging."""
    # Check if we're in MCP mode - if so, only print critical messages
    mcp_mode = os.getenv("VOIDCAT_MCP_MODE", "false").lower() == "true"
    debug_enabled = os.getenv("VOIDCAT_DEBUG", "true").lower() == "true"

    # Only print if debug is enabled or force is True
    if not debug_enabled and not force:
        return

    # In MCP mode, only print critical/forced messages to avoid noise
    if mcp_mode and not force:
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    debug_message = f"[{timestamp}] [VoidCat-Debug] {message}"

    # Always print to stderr for MCP server visibility
    # NEVER print to stdout as it contaminates the JSON MCP protocol
    print(debug_message, file=sys.stderr, flush=True)


@dataclass
class Tool:
    """MCP Tool definition with enhanced metadata."""

    name: str
    description: str
    inputSchema: Dict[str, Any]
    category: str = "general"  # Enhanced: Tool categorization


class VoidCatMCPServer:
    """
    Enhanced Model Context Protocol server for VoidCat Reasoning Core.

    Provides comprehensive MCP-compliant interface for Claude Desktop integration
    with enhanced error handling, diagnostics, and VS Code integration patterns.

    Features:
    - RAG-enhanced intelligent reasoning
    - Comprehensive status monitoring
    - File analysis capabilities (planned)
    - Robust error handling and recovery
    - Performance metrics tracking
    """

    def __init__(self):
        """Initialize the enhanced MCP server with VoidCat enhanced engine."""
        self.engine: Optional[VoidCatEnhancedEngine] = None
        self.server_version = "0.3.0"  # Updated version
        self.initialization_time = None
        self.query_count = 0
        self.error_count = 0

        # Task management and context integration
        self.task_tools = None
        self.context_integration = None

        # Enhanced tool definitions with categorization
        self.tools = [
            Tool(
                name="voidcat_query",
                description="Process intelligent queries using memory-enhanced RAG reasoning with the VoidCat engine",
                category="reasoning",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The question or prompt to process with memory-enhanced RAG",
                        },
                        "model": {
                            "type": "string",
                            "description": "AI model to use for reasoning",
                            "default": "deepseek-chat",
                            "enum": [
                                "deepseek-chat",
                                "gpt-4o-mini",
                                "gpt-4o",
                                "gpt-3.5-turbo",
                            ],
                        },
                        "context_depth": {
                            "type": "integer",
                            "description": "Number of relevant documents to retrieve for context",
                            "default": 2,
                            "minimum": 1,
                            "maximum": 5,
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Session identifier for conversation tracking and memory context",
                        },
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="voidcat_status",
                description="Get comprehensive status and health information of the VoidCat reasoning engine",
                category="diagnostics",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "detailed": {
                            "type": "boolean",
                            "description": "Include detailed diagnostic information",
                            "default": False,
                        }
                    },
                    "required": [],
                },
            ),
            Tool(
                name="voidcat_analyze_knowledge",
                description="Analyze and explore the loaded knowledge base content",
                category="analysis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "analysis_type": {
                            "type": "string",
                            "description": "Type of analysis to perform",
                            "enum": ["summary", "topics", "documents"],
                            "default": "summary",
                        }
                    },
                    "required": [],
                },
            ),
            Tool(
                name="voidcat_sequential_thinking",
                description="Process queries using structured sequential thinking with multi-branch reasoning",
                category="reasoning",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The question or problem to analyze using sequential thinking",
                        },
                        "max_thoughts": {
                            "type": "integer",
                            "description": "Maximum number of thoughts to generate",
                            "default": 10,
                            "minimum": 3,
                            "maximum": 20,
                        },
                        "include_reasoning_trace": {
                            "type": "boolean",
                            "description": "Include detailed reasoning trace in response",
                            "default": True,
                        },
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="voidcat_enhanced_query",
                description="Process queries using the full enhanced pipeline: Sequential Thinking + Context7 + RAG",
                category="reasoning",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The question or prompt to process with full enhancement",
                        },
                        "model": {
                            "type": "string",
                            "description": "OpenAI model to use for final generation",
                            "default": "gpt-4o-mini",
                            "enum": ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
                        },
                        "max_context_sources": {
                            "type": "integer",
                            "description": "Maximum context sources to retrieve",
                            "default": 3,
                            "minimum": 1,
                            "maximum": 5,
                        },
                        "include_trace": {
                            "type": "boolean",
                            "description": "Include comprehensive reasoning trace",
                            "default": False,
                        },
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="voidcat_configure_engine",
                description="Configure the enhanced reasoning engine behavior and features",
                category="configuration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "enable_sequential_thinking": {
                            "type": "boolean",
                            "description": "Enable or disable sequential thinking",
                        },
                        "enable_context7": {
                            "type": "boolean",
                            "description": "Enable or disable Context7 enhanced context retrieval",
                        },
                        "enable_fallback_to_rag": {
                            "type": "boolean",
                            "description": "Enable fallback to basic RAG on enhanced processing errors",
                        },
                        "complexity_threshold": {
                            "type": "string",
                            "description": "Complexity threshold for reasoning strategy selection",
                            "enum": ["simple", "medium", "high", "expert"],
                        },
                    },
                    "required": [],
                },
            ),
            Tool(
                name="voidcat_context_query",
                description="Process queries with automatic task and project context awareness",
                category="reasoning",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The question or prompt to process with context awareness",
                        },
                        "model": {
                            "type": "string",
                            "description": "OpenAI model to use for reasoning",
                            "default": "gpt-4o-mini",
                            "enum": ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
                        },
                        "include_tasks": {
                            "type": "boolean",
                            "description": "Include current task context in the query",
                            "default": True,
                        },
                        "include_projects": {
                            "type": "boolean",
                            "description": "Include active project context in the query",
                            "default": True,
                        },
                        "context_depth": {
                            "type": "integer",
                            "description": "Number of relevant documents to retrieve for context",
                            "default": 2,
                            "minimum": 1,
                            "maximum": 5,
                        },
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="voidcat_get_context",
                description="Get current active context including projects, tasks, and workflow state",
                category="context",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User identifier for context scoping",
                            "default": "default",
                        },
                        "format": {
                            "type": "string",
                            "description": "Output format for context information",
                            "enum": ["detailed", "summary", "json"],
                            "default": "detailed",
                        },
                    },
                    "required": [],
                },
            ),
            Tool(
                name="voidcat_task_context",
                description="Get detailed context for a specific task including related tasks and project info",
                category="context",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "ID of the task to get context for",
                        }
                    },
                    "required": ["task_id"],
                },
            ),
            Tool(
                name="voidcat_project_context",
                description="Get detailed context for a specific project including task distribution and activity",
                category="context",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "ID of the project to get context for",
                        }
                    },
                    "required": ["project_id"],
                },
            ),
            Tool(
                name="voidcat_memory_stats",
                description="Get memory system statistics and usage information",
                category="memory",
                inputSchema={"type": "object", "properties": {}, "required": []},
            ),
            Tool(
                name="voidcat_user_preferences",
                description="Get current user preferences from memory",
                category="memory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Optional category filter for preferences",
                        }
                    },
                    "required": [],
                },
            ),
            Tool(
                name="voidcat_set_preference",
                description="Set a user preference in memory",
                category="memory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "description": "Preference key"},
                        "value": {"type": "string", "description": "Preference value"},
                    },
                    "required": ["key", "value"],
                },
            ),
            Tool(
                name="voidcat_conversation_history",
                description="Get recent conversation history from memory",
                category="memory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of conversations to retrieve",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 50,
                        }
                    },
                    "required": [],
                },
            ),
            Tool(
                name="voidcat_new_session",
                description="Start a new conversation session for memory tracking",
                category="memory",
                inputSchema={"type": "object", "properties": {}, "required": []},
            ),
        ]

        # Initialize task management tools
        self.task_tools = None

    async def initialize(self, request_id: Optional[str] = None) -> None:
        """Initialize the VoidCat engine and respond to MCP initialize request."""
        try:
            debug_print(f"Starting VoidCat MCP Server initialization...", force=True)

            # Initialize the enhanced engine
            from enhanced_engine import VoidCatEnhancedEngine

            debug_print("Importing VoidCatEnhancedEngine...", force=True)

            # Initialize with knowledge directory
            knowledge_dir = os.path.join(os.getcwd(), "knowledge_source")
            self.engine = VoidCatEnhancedEngine(knowledge_dir=knowledge_dir)
            debug_print("VoidCat engine created with knowledge directory", force=True)

            # Initialize the engine
            # The enhanced engine initializes itself upon creation
            debug_print("VoidCat enhanced engine ready", force=True)
            debug_print("VoidCat engine initialized successfully", force=True)

            # Initialize task management tools, memory tools, and context integration
            try:
                self.task_tools = create_mcp_task_tools()
                self.memory_tools = create_memory_mcp_tools()
                self.context_integration = create_context_integration()
                debug_print("VoidCat task management tools initialized", force=True)
                debug_print("VoidCat memory management tools initialized", force=True)
                debug_print("VoidCat context integration initialized", force=True)

                # Add task management tools to the tools list
                task_tool_definitions = self.task_tools.get_tool_definitions()
                for tool_def in task_tool_definitions:
                    self.tools.append(
                        Tool(
                            name=tool_def["name"],
                            description=tool_def["description"],
                            category=tool_def["category"],
                            inputSchema=tool_def["inputSchema"],
                        )
                    )

                debug_print(
                    f"Added {len(task_tool_definitions)} task management tools",
                    force=True,
                )

                # Add memory management tools to the tools list
                memory_tool_definitions = self.memory_tools.get_tools()
                for tool_def in memory_tool_definitions:
                    self.tools.append(
                        Tool(
                            name=tool_def["name"],
                            description=tool_def["description"],
                            category=tool_def["category"],
                            inputSchema=tool_def["inputSchema"],
                        )
                    )

                debug_print(
                    f"Added {len(memory_tool_definitions)} memory management tools",
                    force=True,
                )

            except Exception as e:
                debug_print(
                    f"Warning: Task management tools initialization failed: {e}",
                    force=True,
                )
                # Continue without task tools - they're optional

            self.initialization_time = datetime.now().isoformat()
            debug_print(
                f"VoidCat MCP Server fully initialized at {self.initialization_time}",
                force=True,
            )

            await self._send_response(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}, "logging": {}},
                        "serverInfo": {
                            "name": "voidcat-reasoning-core",
                            "version": self.server_version,
                        },
                    },
                }
            )
            debug_print("MCP initialization response sent successfully", force=True)

        except Exception as e:
            error_msg = f"VoidCat engine initialization failed: {str(e)}"
            debug_print(f"CRITICAL ERROR: {error_msg}", force=True)
            debug_print(f"Traceback: {traceback.format_exc()}", force=True)

            await self._send_error(
                error_msg, request_id, details=traceback.format_exc()
            )

    async def handle_list_tools(self, request_id: Optional[str] = None) -> None:
        """Handle MCP list_tools request."""
        tools_data = [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema,
            }
            for tool in self.tools
        ]

        await self._send_response(
            {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools_data}}
        )

    async def handle_call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        request_id: Optional[str] = None,
    ) -> None:
        """Handle MCP call_tool request with enhanced error handling."""
        if not self.engine:
            await self._send_error(
                "VoidCat engine not initialized. Please restart the MCP server.",
                request_id,
            )
            return

        try:
            debug_print(f"Executing tool: {tool_name} with arguments: {arguments}")

            if tool_name == "voidcat_query":
                await self._handle_query_tool(arguments, request_id)
            elif tool_name == "voidcat_status":
                await self._handle_status_tool(arguments, request_id)
            elif tool_name == "voidcat_analyze_knowledge":
                await self._handle_analyze_knowledge_tool(arguments, request_id)
            elif tool_name == "voidcat_sequential_thinking":
                await self._handle_sequential_thinking_tool(arguments, request_id)
            elif tool_name == "voidcat_enhanced_query":
                await self._handle_enhanced_query_tool(arguments, request_id)
            elif tool_name == "voidcat_configure_engine":
                await self._handle_configure_engine_tool(arguments, request_id)
            elif tool_name == "voidcat_context_query":
                await self._handle_context_query_tool(arguments, request_id)
            elif tool_name == "voidcat_get_context":
                await self._handle_get_context_tool(arguments, request_id)
            elif tool_name == "voidcat_task_context":
                await self._handle_task_context_tool(arguments, request_id)
            elif tool_name == "voidcat_project_context":
                await self._handle_project_context_tool(arguments, request_id)
            elif tool_name == "voidcat_memory_stats":
                await self._handle_memory_stats_tool(arguments, request_id)
            elif tool_name == "voidcat_user_preferences":
                await self._handle_user_preferences_tool(arguments, request_id)
            elif tool_name == "voidcat_set_preference":
                await self._handle_set_preference_tool(arguments, request_id)
            elif tool_name == "voidcat_conversation_history":
                await self._handle_conversation_history_tool(arguments, request_id)
            elif tool_name == "voidcat_new_session":
                await self._handle_new_session_tool(arguments, request_id)
            elif (
                tool_name.startswith("voidcat_memory_")
                or tool_name.startswith("voidcat_preference_")
                or tool_name.startswith("voidcat_conversation_")
                or tool_name.startswith("voidcat_heuristic_")
            ):
                # Handle memory management tools
                await self._handle_memory_management_tool(
                    tool_name, arguments, request_id
                )
            elif (
                tool_name.startswith("voidcat_task_")
                or tool_name.startswith("voidcat_project_")
                or tool_name.startswith("voidcat_dependency_")
            ):
                # Handle task management tools
                await self._handle_task_management_tool(
                    tool_name, arguments, request_id
                )
            else:
                await self._send_error(
                    f"Unknown tool: {tool_name}. Available tools: {[t.name for t in self.tools]}",
                    request_id,
                )

        except Exception as e:
            self.error_count += 1
            error_msg = f"Tool execution failed for '{tool_name}': {str(e)}"
            debug_print(f"Tool error: {error_msg}")
            debug_print(f"Traceback: {traceback.format_exc()}")
            await self._send_error(error_msg, request_id)

    async def _handle_query_tool(
        self, arguments: Dict[str, Any], request_id: Optional[str] = None
    ) -> None:
        """Handle voidcat_query tool execution with memory-enhanced parameters."""
        query = arguments.get("query", "")
        model = arguments.get("model", "deepseek-chat")
        context_depth = arguments.get("context_depth", 2)
        session_id = arguments.get("session_id", None)

        if not query:
            await self._send_error(
                "Query parameter is required and cannot be empty", request_id
            )
            return

        try:
            if not self.engine:
                await self._send_error("VoidCat engine is not initialized", request_id)
                return

            debug_print(
                f"Processing memory-enhanced query with model: {model}, context_depth: {context_depth}, session: {session_id}"
            )
            response = await self.engine.query(
                query, model=model, top_k=context_depth, session_id=session_id
            )
            self.query_count += 1

            await self._send_response(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"🧠 **VoidCat Memory-Enhanced Response**\n\n{response}\n\n---\n*Query processed using {model} with memory context and {context_depth} context depth*",
                            }
                        ]
                    },
                }
            )
            debug_print(
                f"Query processed successfully (Total queries: {self.query_count})"
            )

        except Exception as e:
            self.error_count += 1
            error_msg = f"Query processing failed: {str(e)}"
            debug_print(f"Query error: {error_msg}")
            await self._send_error(
                error_msg, request_id, details=traceback.format_exc()
            )

    async def _handle_status_tool(
        self, arguments: Dict[str, Any], request_id: Optional[str] = None
    ) -> None:
        """Handle voidcat_status tool execution with detailed diagnostics."""
        try:
            detailed = arguments.get("detailed", False)

            # Get comprehensive health status
            health_status = await self.validate_mcp_server_health()

            if not self.engine:
                status = {
                    "engine_initialized": False,
                    "error": "Engine not initialized",
                    "server_version": self.server_version,
                    "mcp_health": health_status,
                }
            else:
                # Safe knowledge base status check with defensive programming
                status = {
                    "engine_initialized": True,
                    "server_version": self.server_version,
                    "initialization_time": self.initialization_time,
                    "query_count": self.query_count,
                    "error_count": self.error_count,
                    "mcp_health": health_status,
                    "knowledge_base": {
                        "loaded": False,
                        "document_count": 0,
                        "vector_features": 0,
                        "status": "not_configured",
                    },
                }

                if detailed and self.engine:
                    try:
                        engine_diagnostics = self.engine.get_comprehensive_diagnostics()
                        status["detailed_diagnostics"] = engine_diagnostics
                    except AttributeError:
                        status["detailed_diagnostics"] = {
                            "error": "Diagnostics method not available"
                        }

            status_text = f"🎯 **VoidCat Reasoning Core Status**\n\n```json\n{json.dumps(status, indent=2)}\n```"

            if status.get("engine_initialized") and status.get(
                "knowledge_base", {}
            ).get("loaded"):
                status_text += "\n\n✅ **Status**: Production Ready & Operational"
            else:
                status_text += "\n\n⚠️ **Status**: Initialization Required"

            # Add MCP-specific diagnostics
            if not health_status.get("mcp_server_operational", True):
                status_text += "\n\n🚨 **MCP Server Issues Detected** - Check environment and dependencies"

            await self._send_response(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"content": [{"type": "text", "text": status_text}]},
                }
            )

        except Exception as e:
            self.error_count += 1
            error_msg = f"Status check failed: {str(e)}"
            debug_print(f"Status error: {error_msg}", force=True)
            await self._send_error(
                error_msg, request_id, details=traceback.format_exc()
            )

    async def _handle_sequential_thinking_tool(
        self, arguments: Dict[str, Any], request_id: Optional[str] = None
    ) -> None:
        """Handle voidcat_sequential_thinking tool execution."""
        query = arguments.get("query", "")
        max_thoughts = arguments.get("max_thoughts", 10)
        include_trace = arguments.get("include_reasoning_trace", True)

        if not query:
            await self._send_error(
                "Query parameter is required and cannot be empty", request_id
            )
            return

        try:
            if not self.engine:
                await self._send_error("VoidCat engine is not initialized", request_id)
                return

            debug_print(
                f"Processing sequential thinking query with {max_thoughts} max thoughts"
            )

            # Use enhanced query with reasoning trace instead of direct sequential engine access
            try:
                reasoning_result = await self.engine.query_with_reasoning_trace(
                    query, max_thoughts=max_thoughts, model="deepseek-chat"
                )
            except Exception as e:
                debug_print(f"Sequential thinking fallback: {str(e)}")
                reasoning_result = {
                    "response": await self.engine.query(query),
                    "reasoning_trace": {
                        "steps": ["Basic query processing"],
                        "confidence": 0.7,
                    },
                }

            response_text = f"🧠 **Sequential Thinking Analysis**\n\n"
            response_text += f"**Query**: {query}\n\n"
            response_text += f"**Final Response**: {reasoning_result.get('final_response', 'No response generated')}\n\n"

            if include_trace and reasoning_result.get("reasoning_path"):
                response_text += "### Reasoning Trace:\n"
                for i, branch in enumerate(reasoning_result["reasoning_path"][:3], 1):
                    response_text += f"**Branch {i}: {branch['branch_name']}**\n"
                    response_text += f"- Confidence: {branch['confidence']:.3f}\n"
                    response_text += f"- Thoughts: {len(branch['thoughts'])}\n\n"

            response_text += (
                f"---\n*Complexity: {reasoning_result.get('complexity', 'unknown')} | "
            )
            response_text += (
                f"Confidence: {reasoning_result.get('confidence', 0.5):.3f} | "
            )
            response_text += (
                f"Total Thoughts: {reasoning_result.get('thought_count', 0)}*"
            )

            await self._send_response(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"content": [{"type": "text", "text": response_text}]},
                }
            )

        except Exception as e:
            error_msg = f"Sequential thinking processing failed: {str(e)}"
            debug_print(f"Sequential thinking error: {error_msg}")
            await self._send_error(
                error_msg, request_id, details=traceback.format_exc()
            )

    async def _handle_enhanced_query_tool(
        self, arguments: Dict[str, Any], request_id: Optional[str] = None
    ) -> None:
        """Handle voidcat_enhanced_query tool execution."""
        query = arguments.get("query", "")
        model = arguments.get("model", "gpt-4o-mini")
        max_context_sources = arguments.get("max_context_sources", 3)
        include_trace = arguments.get("include_trace", False)

        if not query:
            await self._send_error(
                "Query parameter is required and cannot be empty", request_id
            )
            return

        try:
            if not self.engine:
                await self._send_error("VoidCat engine is not initialized", request_id)
                return

            debug_print(
                f"Processing enhanced query with {max_context_sources} context sources"
            )

            if include_trace:
                # Get detailed trace
                result = await self.engine.query_with_reasoning_trace(
                    query, model=model
                )
                response_text = result["response"]

                if result.get("reasoning_trace"):
                    trace = result["reasoning_trace"]
                    response_text += f"\n\n### Enhanced Processing Trace\n"
                    response_text += (
                        f"- **Session ID**: {trace.get('session_id', 'N/A')}\n"
                    )
                    response_text += (
                        f"- **Complexity**: {trace.get('complexity', 'unknown')}\n"
                    )
                    response_text += f"- **Processing Time**: {trace.get('processing_time_seconds', 0):.2f}s\n"
                    response_text += f"- **Context Sources**: {trace.get('context_sources_used', 0)}\n"
                    response_text += (
                        f"- **Thoughts Generated**: {trace.get('thought_count', 0)}\n"
                    )
            else:
                # Standard enhanced processing
                response_text = await self.engine.query(
                    query,
                    model=model,
                    enable_enhanced=True,
                    max_context_sources=max_context_sources,
                )

            await self._send_response(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"content": [{"type": "text", "text": response_text}]},
                }
            )

        except Exception as e:
            error_msg = f"Enhanced query processing failed: {str(e)}"
            debug_print(f"Enhanced query error: {error_msg}")
            await self._send_error(
                error_msg, request_id, details=traceback.format_exc()
            )

    async def _handle_configure_engine_tool(
        self, arguments: Dict[str, Any], request_id: Optional[str] = None
    ) -> None:
        """Handle voidcat_configure_engine tool execution."""
        try:
            if not self.engine:
                await self._send_error("VoidCat engine is not initialized", request_id)
                return

            debug_print(f"Configuring engine with parameters: {arguments}")

            # Configure the engine
            config_result = self.engine.configure_engine(**arguments)

            response_text = f"⚙️ **VoidCat Engine Configuration**\n\n"
            response_text += f"**Configuration Updated**: {'Yes' if config_result['configuration_changed'] else 'No'}\n\n"
            response_text += "### Current Settings:\n"
            response_text += f"- **Sequential Thinking**: {'Enabled' if config_result['enable_sequential_thinking'] else 'Disabled'}\n"
            response_text += f"- **Context7 Enhancement**: {'Enabled' if config_result['enable_context7'] else 'Disabled'}\n"
            response_text += f"- **RAG Fallback**: {'Enabled' if config_result['enable_fallback_to_rag'] else 'Disabled'}\n"
            response_text += f"- **Complexity Threshold**: {config_result['complexity_threshold'].title()}\n\n"

            if config_result["configuration_changed"]:
                response_text += "✅ **Configuration applied successfully**"
            else:
                response_text += "ℹ️ **No configuration changes made**"

            await self._send_response(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"content": [{"type": "text", "text": response_text}]},
                }
            )

        except Exception as e:
            error_msg = f"Engine configuration failed: {str(e)}"
            debug_print(f"Configuration error: {error_msg}")
            await self._send_error(
                error_msg, request_id, details=traceback.format_exc()
            )

    async def _handle_context_query_tool(
        self, arguments: Dict[str, Any], request_id: Optional[str] = None
    ) -> None:
        """Handle context-aware query tool execution."""
        query = arguments.get("query", "")
        model = arguments.get("model", "gpt-4o-mini")
        include_tasks = arguments.get("include_tasks", True)
        include_projects = arguments.get("include_projects", True)
        context_depth = arguments.get("context_depth", 2)

        if not query:
            await self._send_error(
                "Query parameter is required and cannot be empty", request_id
            )
            return

        try:
            if not self.engine:
                await self._send_error("VoidCat engine is not initialized", request_id)
                return

            if not self.context_integration:
                await self._send_error(
                    "Context integration is not initialized", request_id
                )
                return

            debug_print(f"Processing context-aware query: {query[:100]}...")

            # Enhance query with context
            enhanced_query = self.context_integration.enhance_query_with_context(
                query, include_tasks=include_tasks, include_projects=include_projects
            )

            debug_print(f"Enhanced query length: {len(enhanced_query)} characters")

            # Process with enhanced engine
            response = await self.engine.query(enhanced_query, model=model)
            self.query_count += 1

            # Get context summary for response metadata
            context_summary = self.context_integration.get_context_summary()

            await self._send_response(
                {
                    "content": [{"type": "text", "text": response}],
                    "metadata": {
                        "model_used": model,
                        "context_enhanced": True,
                        "context_summary": context_summary,
                        "include_tasks": include_tasks,
                        "include_projects": include_projects,
                        "query_length": len(query),
                        "enhanced_query_length": len(enhanced_query),
                    },
                },
                request_id,
            )

        except Exception as e:
            error_msg = f"Context-aware query failed: {str(e)}"
            debug_print(f"Context query error: {error_msg}")
            await self._send_error(
                error_msg, request_id, details=traceback.format_exc()
            )

    async def _handle_get_context_tool(
        self, arguments: Dict[str, Any], request_id: Optional[str] = None
    ) -> None:
        """Handle get context tool execution."""
        user_id = arguments.get("user_id", "default")
        format_type = arguments.get("format", "detailed")

        try:
            if not self.context_integration:
                await self._send_error(
                    "Context integration is not initialized", request_id
                )
                return

            debug_print(f"Getting context for user: {user_id}, format: {format_type}")

            if format_type == "json":
                context = self.context_integration.get_active_context(user_id)
                response_text = f"```json\n{json.dumps(context, indent=2)}\n```"
            elif format_type == "summary":
                response_text = self.context_integration.get_context_summary(user_id)
            else:  # detailed
                context = self.context_integration.get_active_context(user_id)

                if context.get("error"):
                    response_text = f"❌ **Context Error**: {context['error']}"
                else:
                    response_parts = []

                    # Workflow state
                    workflow = context.get("workflow_state", {})
                    response_parts.append(f"📊 **Workflow Overview**")
                    response_parts.append(
                        f"• Projects: {workflow.get('total_projects', 0)} total, {workflow.get('active_projects', 0)} active"
                    )
                    response_parts.append(
                        f"• Tasks: {workflow.get('total_tasks', 0)} total, {workflow.get('pending_tasks', 0)} pending, {workflow.get('in_progress_tasks', 0)} in progress"
                    )
                    if workflow.get("blocked_tasks", 0) > 0:
                        response_parts.append(
                            f"• ⚠️ {workflow['blocked_tasks']} tasks are blocked"
                        )

                    # Active projects
                    if context.get("active_projects"):
                        response_parts.append(f"\n🎯 **Active Projects**")
                        for project in context["active_projects"][:5]:
                            response_parts.append(
                                f"• **{project['name']}**: {project['active_task_count']} active tasks"
                            )

                    # Current tasks
                    if context.get("current_tasks"):
                        response_parts.append(f"\n📋 **High-Priority Tasks**")
                        for task in context["current_tasks"][:5]:
                            status_emoji = (
                                "🔄" if task["status"] == "in-progress" else "⏳"
                            )
                            response_parts.append(
                                f"• {status_emoji} **{task['name']}** ({task['priority']}) - {task['project_name']}"
                            )

                    # Recent activity
                    if context.get("recent_activity"):
                        response_parts.append(f"\n🕒 **Recent Activity**")
                        for activity in context["recent_activity"][-3:]:
                            response_parts.append(
                                f"• {activity['task_name']} → {activity['status']} ({activity['project_name']})"
                            )

                    response_text = "\n".join(response_parts)

            await self._send_response(
                {
                    "content": [{"type": "text", "text": response_text}],
                    "metadata": {
                        "user_id": user_id,
                        "format": format_type,
                        "timestamp": datetime.now(UTC).isoformat(),
                    },
                },
                request_id,
            )

        except Exception as e:
            error_msg = f"Get context failed: {str(e)}"
            debug_print(f"Get context error: {error_msg}")
            await self._send_error(
                error_msg, request_id, details=traceback.format_exc()
            )

    async def _handle_task_context_tool(
        self, arguments: Dict[str, Any], request_id: Optional[str] = None
    ) -> None:
        """Handle task context tool execution."""
        task_id = arguments.get("task_id", "")

        if not task_id:
            await self._send_error("task_id parameter is required", request_id)
            return

        try:
            if not self.context_integration:
                await self._send_error(
                    "Context integration is not initialized", request_id
                )
                return

            debug_print(f"Getting context for task: {task_id}")

            context = self.context_integration.get_task_specific_context(task_id)

            if context.get("error"):
                await self._send_error(context["error"], request_id)
                return

            # Format response
            task_info = context["task"]
            project_info = context.get("project")
            related_tasks = context.get("related_tasks", [])

            response_parts = []

            # Task details
            response_parts.append(f"📋 **Task Details**")
            response_parts.append(f"• **Name**: {task_info['name']}")
            response_parts.append(f"• **Status**: {task_info['status']}")
            response_parts.append(f"• **Priority**: {task_info['priority']}")
            response_parts.append(f"• **Complexity**: {task_info['complexity']}/10")
            if task_info.get("tags"):
                response_parts.append(f"• **Tags**: {', '.join(task_info['tags'])}")

            # Project context
            if project_info:
                response_parts.append(f"\n🎯 **Project Context**")
                response_parts.append(f"• **Project**: {project_info['name']}")
                response_parts.append(
                    f"• **Description**: {project_info['description']}"
                )

            # Time tracking
            if task_info.get("estimated_hours") or task_info.get("actual_hours"):
                response_parts.append(f"\n⏱️ **Time Tracking**")
                if task_info.get("estimated_hours"):
                    response_parts.append(
                        f"• **Estimated**: {task_info['estimated_hours']} hours"
                    )
                if task_info.get("actual_hours"):
                    response_parts.append(
                        f"• **Actual**: {task_info['actual_hours']} hours"
                    )

            # Related tasks
            if related_tasks:
                response_parts.append(f"\n🔗 **Related Tasks**")
                for related in related_tasks[:5]:
                    relationship = related["relationship"].title()
                    response_parts.append(
                        f"• **{related['name']}** ({relationship}) - {related['status']}"
                    )

            # Task description
            if task_info.get("description"):
                response_parts.append(f"\n📝 **Description**")
                response_parts.append(task_info["description"])

            response_text = "\n".join(response_parts)

            await self._send_response(
                {
                    "content": [{"type": "text", "text": response_text}],
                    "metadata": {
                        "task_id": task_id,
                        "context_summary": context.get("context_summary", ""),
                        "related_task_count": len(related_tasks),
                    },
                },
                request_id,
            )

        except Exception as e:
            error_msg = f"Task context failed: {str(e)}"
            debug_print(f"Task context error: {error_msg}")
            await self._send_error(
                error_msg, request_id, details=traceback.format_exc()
            )

    async def _handle_project_context_tool(
        self, arguments: Dict[str, Any], request_id: Optional[str] = None
    ) -> None:
        """Handle project context tool execution."""
        project_id = arguments.get("project_id", "")

        if not project_id:
            await self._send_error("project_id parameter is required", request_id)
            return

        try:
            if not self.context_integration:
                await self._send_error(
                    "Context integration is not initialized", request_id
                )
                return

            debug_print(f"Getting context for project: {project_id}")

            context = self.context_integration.get_project_specific_context(project_id)

            if context.get("error"):
                await self._send_error(context["error"], request_id)
                return

            # Format response
            project_info = context["project"]
            task_summary = context.get("task_summary", {})
            recent_activity = context.get("recent_activity", [])

            response_parts = []

            # Project details
            response_parts.append(f"🎯 **Project Details**")
            response_parts.append(f"• **Name**: {project_info['name']}")
            response_parts.append(f"• **Description**: {project_info['description']}")
            response_parts.append(f"• **Created**: {project_info['created_at'][:10]}")

            # Task summary
            response_parts.append(f"\n📊 **Task Summary**")
            response_parts.append(
                f"• **Total Tasks**: {task_summary.get('total_tasks', 0)}"
            )

            # Status distribution
            status_dist = task_summary.get("status_distribution", {})
            if status_dist:
                response_parts.append(f"• **Status Distribution**:")
                for status, count in status_dist.items():
                    status_emoji = {
                        "done": "✅",
                        "in-progress": "🔄",
                        "pending": "⏳",
                        "blocked": "🚫",
                    }.get(status, "📋")
                    response_parts.append(
                        f"  - {status_emoji} {status.title()}: {count}"
                    )

            # Priority distribution
            priority_dist = task_summary.get("priority_distribution", {})
            if priority_dist:
                response_parts.append(f"• **Priority Distribution**:")
                for priority, count in priority_dist.items():
                    priority_emoji = {
                        "CRITICAL": "🔴",
                        "URGENT": "🟠",
                        "HIGH": "🟡",
                        "MEDIUM": "🔵",
                        "LOW": "🟢",
                        "LOWEST": "⚪",
                    }.get(priority, "📋")
                    response_parts.append(f"  - {priority_emoji} {priority}: {count}")

            # Metrics
            if task_summary.get("average_complexity"):
                response_parts.append(
                    f"• **Average Complexity**: {task_summary['average_complexity']}/10"
                )
            if task_summary.get("total_estimated_hours"):
                response_parts.append(
                    f"• **Total Estimated Hours**: {task_summary['total_estimated_hours']}"
                )

            # Recent activity
            if recent_activity:
                response_parts.append(f"\n🕒 **Recent Activity**")
                for activity in recent_activity:
                    response_parts.append(
                        f"• **{activity['task_name']}** → {activity['status']}"
                    )

            response_text = "\n".join(response_parts)

            await self._send_response(
                {
                    "content": [{"type": "text", "text": response_text}],
                    "metadata": {
                        "project_id": project_id,
                        "context_summary": context.get("context_summary", ""),
                        "total_tasks": task_summary.get("total_tasks", 0),
                    },
                },
                request_id,
            )

        except Exception as e:
            error_msg = f"Project context failed: {str(e)}"
            debug_print(f"Project context error: {error_msg}")
            await self._send_error(
                error_msg, request_id, details=traceback.format_exc()
            )

    async def _handle_memory_stats_tool(
        self, arguments: Dict[str, Any], request_id: Optional[str] = None
    ) -> None:
        """Handle memory stats tool execution."""
        try:
            if not self.engine:
                await self._send_error("VoidCat engine is not initialized", request_id)
                return

            debug_print("Getting memory system statistics")
            stats = await self.engine.get_memory_stats()

            if stats.get("error"):
                await self._send_error(stats["error"], request_id)
                return

            # Format response
            response_parts = []
            response_parts.append("🧠 **Memory System Statistics**")
            response_parts.append(f"• **User ID**: {stats['user_id']}")
            response_parts.append(f"• **Session ID**: {stats['session_id']}")

            response_parts.append("\n📊 **Memory Categories**")
            for category, count in stats.get("categories", {}).items():
                response_parts.append(
                    f"• **{category.replace('_', ' ').title()}**: {count} memories"
                )

            response_text = "\n".join(response_parts)

            await self._send_response(
                {
                    "content": [{"type": "text", "text": response_text}],
                    "metadata": stats,
                },
                request_id,
            )

        except Exception as e:
            error_msg = f"Memory stats failed: {str(e)}"
            debug_print(f"Memory stats error: {error_msg}")
            await self._send_error(
                error_msg, request_id, details=traceback.format_exc()
            )

    async def _handle_user_preferences_tool(
        self, arguments: Dict[str, Any], request_id: Optional[str] = None
    ) -> None:
        """Handle user preferences tool execution."""
        try:
            if not self.engine:
                await self._send_error("VoidCat engine is not initialized", request_id)
                return

            category = arguments.get("category", None)
            debug_print(f"Getting user preferences, category: {category}")

            preferences = await self.engine.get_user_preferences()

            # Filter by category if specified
            if category:
                preferences = {
                    k: v
                    for k, v in preferences.items()
                    if category.lower() in k.lower()
                }

            # Format response
            response_parts = []
            response_parts.append("⚙️ **User Preferences**")

            if preferences:
                for key, value in preferences.items():
                    response_parts.append(
                        f"• **{key.replace('_', ' ').title()}**: {value}"
                    )
            else:
                response_parts.append("• No preferences found")
                if category:
                    response_parts.append(f"  (filtered by category: {category})")

            response_text = "\n".join(response_parts)

            await self._send_response(
                {
                    "content": [{"type": "text", "text": response_text}],
                    "metadata": {
                        "preferences": preferences,
                        "category_filter": category,
                    },
                },
                request_id,
            )

        except Exception as e:
            error_msg = f"User preferences failed: {str(e)}"
            debug_print(f"User preferences error: {error_msg}")
            await self._send_error(
                error_msg, request_id, details=traceback.format_exc()
            )

    async def _handle_set_preference_tool(
        self, arguments: Dict[str, Any], request_id: Optional[str] = None
    ) -> None:
        """Handle set preference tool execution."""
        try:
            if not self.engine:
                await self._send_error("VoidCat engine is not initialized", request_id)
                return

            key = arguments.get("key", "")
            value = arguments.get("value", "")

            if not key:
                await self._send_error("key parameter is required", request_id)
                return

            if not value:
                await self._send_error("value parameter is required", request_id)
                return

            debug_print(f"Setting user preference: {key} = {value}")

            success = await self.engine.set_user_preference(key, value)

            if success:
                response_text = (
                    f"✅ **Preference Set Successfully**\n• **{key}**: {value}"
                )
            else:
                response_text = f"❌ **Failed to Set Preference**\n• **{key}**: {value}"

            await self._send_response(
                {
                    "content": [{"type": "text", "text": response_text}],
                    "metadata": {"key": key, "value": value, "success": success},
                },
                request_id,
            )

        except Exception as e:
            error_msg = f"Set preference failed: {str(e)}"
            debug_print(f"Set preference error: {error_msg}")
            await self._send_error(
                error_msg, request_id, details=traceback.format_exc()
            )

    async def _handle_conversation_history_tool(
        self, arguments: Dict[str, Any], request_id: Optional[str] = None
    ) -> None:
        """Handle conversation history tool execution."""
        try:
            if not self.engine:
                await self._send_error("VoidCat engine is not initialized", request_id)
                return

            limit = arguments.get("limit", 10)
            debug_print(f"Getting conversation history, limit: {limit}")

            history = await self.engine.get_conversation_history(limit)

            # Format response
            response_parts = []
            response_parts.append("💬 **Conversation History**")

            if history:
                for i, conv in enumerate(history[-limit:], 1):  # Show most recent first
                    response_parts.append(
                        f"\n**{i}. Session: {conv.get('session_id', 'unknown')}**"
                    )
                    response_parts.append(
                        f"• **Query**: {conv.get('query', '')[:100]}..."
                    )
                    response_parts.append(
                        f"• **Response**: {conv.get('response', '')[:100]}..."
                    )
                    response_parts.append(f"• **Time**: {conv.get('timestamp', '')}")
            else:
                response_parts.append("• No conversation history found")

            response_text = "\n".join(response_parts)

            await self._send_response(
                {
                    "content": [{"type": "text", "text": response_text}],
                    "metadata": {"history_count": len(history), "limit": limit},
                },
                request_id,
            )

        except Exception as e:
            error_msg = f"Conversation history failed: {str(e)}"
            debug_print(f"Conversation history error: {error_msg}")
            await self._send_error(
                error_msg, request_id, details=traceback.format_exc()
            )

    async def _handle_new_session_tool(
        self, arguments: Dict[str, Any], request_id: Optional[str] = None
    ) -> None:
        """Handle new session tool execution."""
        try:
            if not self.engine:
                await self._send_error("VoidCat engine is not initialized", request_id)
                return

            debug_print("Starting new conversation session")

            new_session_id = self.engine.start_new_session()

            response_text = f"🆕 **New Session Started**\n• **Session ID**: {new_session_id}\n• Memory context reset for fresh conversation tracking"

            await self._send_response(
                {
                    "content": [{"type": "text", "text": response_text}],
                    "metadata": {"session_id": new_session_id},
                },
                request_id,
            )

        except Exception as e:
            error_msg = f"New session failed: {str(e)}"
            debug_print(f"New session error: {error_msg}")
            await self._send_error(
                error_msg, request_id, details=traceback.format_exc()
            )

    async def _handle_task_management_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        request_id: Optional[str] = None,
    ) -> None:
        """Handle task management tool execution."""
        try:
            if not self.task_tools:
                await self._send_error(
                    "Task management tools are not initialized", request_id
                )
                return

            debug_print(f"Executing task management tool: {tool_name}")

            # Call the task tools handler
            result = await self.task_tools.handle_tool_call(tool_name, arguments)

            # Send the response
            await self._send_response(
                {"jsonrpc": "2.0", "id": request_id, "result": result}
            )

        except Exception as e:
            error_msg = (
                f"Task management tool execution failed for '{tool_name}': {str(e)}"
            )
            debug_print(f"Task tool error: {error_msg}")
            debug_print(f"Traceback: {traceback.format_exc()}")
            await self._send_error(error_msg, request_id)

    async def _handle_memory_management_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        request_id: Optional[str] = None,
    ) -> None:
        """Handle memory management tool execution with comprehensive error handling."""
        try:
            if not self.memory_tools:
                await self._send_error(
                    "Memory management tools are not initialized", request_id
                )
                return

            debug_print(f"Executing memory management tool: {tool_name}")

            # Call the memory tools handler
            result = await self.memory_tools.handle_tool_call(tool_name, arguments)

            # Send the response
            await self._send_response(
                {"jsonrpc": "2.0", "id": request_id, "result": result}
            )

        except Exception as e:
            error_msg = (
                f"Memory management tool execution failed for '{tool_name}': {str(e)}"
            )
            debug_print(f"Memory tool error: {error_msg}")
            debug_print(f"Traceback: {traceback.format_exc()}")
            await self._send_error(
                error_msg, request_id, details=traceback.format_exc()
            )

    async def _handle_analyze_knowledge_tool(
        self, arguments: Dict[str, Any], request_id: Optional[str] = None
    ) -> None:
        """Handle voidcat_analyze_knowledge tool execution with enhanced analysis."""
        try:
            analysis_type = arguments.get("analysis_type", "summary")

            if not self.engine:
                await self._send_error("VoidCat engine is not initialized", request_id)
                return

            debug_print(f"Analyzing knowledge base: {analysis_type}")

            # Get comprehensive knowledge analysis
            analysis_result = await self.engine.analyze_knowledge_base()

            if "error" in analysis_result.get("knowledge_base_analysis", {}):
                error_msg = analysis_result["knowledge_base_analysis"]["error"]
                await self._send_error(
                    f"Knowledge analysis failed: {error_msg}", request_id
                )
                return

            kb_analysis = analysis_result["knowledge_base_analysis"]

            if analysis_type == "summary":
                response_text = f"📚 **Knowledge Base Analysis Summary**\n\n"
                response_text += f"**Total Sources**: {kb_analysis['total_sources']}\n"
                response_text += (
                    f"**Content Clusters**: {kb_analysis['content_clusters']}\n"
                )
                response_text += f"**RAG Documents**: {kb_analysis['rag_documents']}\n"
                response_text += (
                    f"**Vector Features**: {kb_analysis['vector_features']}\n"
                )
                response_text += (
                    f"**Coverage**: {kb_analysis['coverage_assessment']}\n\n"
                )

                if kb_analysis.get("content_distribution"):
                    dist = kb_analysis["content_distribution"]
                    response_text += "### Content Distribution:\n"
                    response_text += (
                        f"- **Total Words**: {dist.get('total_words', 0):,}\n"
                    )
                    response_text += f"- **Average per Source**: {dist.get('average_words_per_source', 0):.1f}\n"

                    size_dist = dist.get("size_distribution", {})
                    response_text += f"- **Small Documents** (<500 words): {size_dist.get('small', 0)}\n"
                    response_text += f"- **Medium Documents** (500-2000 words): {size_dist.get('medium', 0)}\n"
                    response_text += f"- **Large Documents** (>2000 words): {size_dist.get('large', 0)}\n"

            elif analysis_type == "topics":
                response_text = f"🏷️ **Knowledge Base Topics Analysis**\n\n"

                if kb_analysis.get("content_distribution", {}).get("top_keywords"):
                    response_text += "### Top Keywords:\n"
                    for kw_data in kb_analysis["content_distribution"]["top_keywords"][
                        :10
                    ]:
                        response_text += f"- **{kw_data['keyword']}**: {kw_data['frequency']} occurrences\n"

                if kb_analysis.get("top_clusters"):
                    response_text += "\n### Top Content Clusters:\n"
                    for i, cluster in enumerate(kb_analysis["top_clusters"][:5], 1):
                        response_text += f"{i}. **{cluster['theme']}** ({cluster['source_count']} sources, coherence: {cluster['coherence_score']:.3f})\n"

            elif analysis_type == "documents":
                response_text = f"📄 **Knowledge Base Documents**\n\n"

                # Safely get source list - fallback if context7_engine not available
                try:
                    context7_engine = getattr(self.engine, "context7_engine", None)
                    if context7_engine and hasattr(context7_engine, "list_sources"):
                        sources = context7_engine.list_sources(limit=10)
                    else:
                        sources = []
                        response_text += (
                            "Context7 engine not available. Using fallback analysis.\n"
                        )
                except (AttributeError, TypeError):
                    sources = []
                    response_text += "Document analysis not available in current engine configuration.\n"

                if sources:
                    response_text += f"### Document Inventory ({len(sources)} shown):\n"
                    for i, source in enumerate(sources, 1):
                        # Defensive programming to prevent undefined values
                        metadata = source.get("metadata", {}) if source else {}
                        title = (
                            metadata.get("title", f"Document {i}")
                            if metadata
                            else f"Document {i}"
                        )
                        word_count = metadata.get("word_count", 0) if metadata else 0

                        # Ensure title is a string
                        if title is None:
                            title = f"Document {i}"

                        response_text += (
                            f"{i}. **{str(title)}** ({word_count:,} words)\n"
                        )

                        keywords = metadata.get("keywords", []) if metadata else []
                        if keywords and isinstance(keywords, list):
                            # Ensure keywords are strings
                            safe_keywords = [
                                str(k) for k in keywords[:3] if k is not None
                            ]
                            if safe_keywords:
                                response_text += (
                                    f"   - Topics: {', '.join(safe_keywords)}\n"
                                )
                else:
                    response_text += "No documents found in knowledge base.\n"

            # Fix the string concatenation type issue
            footer_text = f"\n---\n*Analysis type: {analysis_type} | Engine: Enhanced VoidCat v{self.server_version}*"
            response_text = str(response_text) + footer_text

            await self._send_response(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"content": [{"type": "text", "text": response_text}]},
                }
            )

        except Exception as e:
            error_msg = f"Knowledge analysis failed: {str(e)}"
            debug_print(f"Knowledge analysis error: {error_msg}")
            await self._send_error(
                error_msg, request_id, details=traceback.format_exc()
            )

    async def _send_response(self, response: Dict[str, Any]) -> None:
        """Send JSON-RPC response to stdout."""
        print(json.dumps(response), flush=True)

    async def _send_error(
        self,
        error_message: str,
        request_id: Optional[str] = None,
        details: Optional[str] = None,
    ) -> None:
        """Send JSON-RPC error response with optional details."""
        error_obj = {"code": -1, "message": error_message}  # Generic error code for now
        if details:
            error_obj["data"] = {"details": details}

        await self._send_response(
            {"jsonrpc": "2.0", "id": request_id, "error": error_obj}
        )

    async def handle_request(self, request: Dict[str, Any]) -> None:
        """Handle incoming MCP request."""
        method = request.get("method", "")
        params = request.get("params", {})
        request_id = request.get("id")

        if method == "initialize":
            await self.initialize(request_id)
        elif method == "tools/list":
            await self.handle_list_tools(request_id)
        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            await self.handle_call_tool(tool_name, arguments, request_id)
        else:
            await self._send_error(
                f"Unknown method: {method}",
                request_id,
                details="Invalid method received",
            )

    async def validate_mcp_server_health(self) -> Dict[str, Any]:
        """Comprehensive MCP server health validation."""
        health_status = {
            "mcp_server_operational": True,
            "engine_status": "unknown",
            "dependencies_available": {},
            "environment_variables": {},
            "python_path": sys.executable,
            "working_directory": os.getcwd(),
            "timestamp": datetime.now().isoformat(),
        }

        try:
            # Check critical dependencies
            dependencies = ["httpx", "openai", "dotenv", "sklearn", "numpy"]
            for dep in dependencies:
                try:
                    __import__(dep.replace("-", "_"))
                    health_status["dependencies_available"][dep] = True
                except ImportError:
                    health_status["dependencies_available"][dep] = False
                    health_status["mcp_server_operational"] = False

            # Check environment variables
            env_vars = ["OPENAI_API_KEY", "DEEPSEEK_API_KEY", "PYTHONPATH"]
            for var in env_vars:
                value = os.getenv(var, "NOT_SET")
                health_status["environment_variables"][var] = (
                    "SET" if value != "NOT_SET" else "NOT_SET"
                )

            # Check engine status
            if self.engine:
                health_status["engine_status"] = "initialized"
            else:
                health_status["engine_status"] = "not_initialized"
                health_status["mcp_server_operational"] = False

        except Exception as e:
            health_status["mcp_server_operational"] = False
            health_status["validation_error"] = str(e)
            health_status["traceback"] = traceback.format_exc()

        return health_status


# Configuration and debugging
DEBUG = os.getenv("VOIDCAT_DEBUG", "false").lower() == "true"


async def main():
    """Main MCP server entry point with proper async stdin handling."""
    server = VoidCatMCPServer()
    debug_print("🚀 VoidCat MCP Server starting...")

    try:
        # Use asyncio to read from stdin
        import asyncio

        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)

        debug_print("📡 Listening for MCP requests...")

        while True:
            try:
                line = await reader.readline()
                if not line:
                    break

                line_str = line.decode("utf-8").strip()
                if line_str:
                    debug_print(f"📥 Received request: {line_str[:100]}...")
                    try:
                        request = json.loads(line_str)
                        await server.handle_request(request)
                    except json.JSONDecodeError as e:
                        debug_print(f"❌ JSON decode error: {str(e)}")
                        await server._send_error(
                            f"Invalid JSON: {str(e)}", details=traceback.format_exc()
                        )
                    except Exception as e:
                        debug_print(f"❌ Request processing error: {str(e)}")
                        debug_print(f"Traceback: {traceback.format_exc()}")
                        await server._send_error(
                            f"Request processing failed: {str(e)}",
                            details=traceback.format_exc(),
                        )

            except Exception as e:
                debug_print(f"❌ Main loop error: {str(e)}")
                break

    except KeyboardInterrupt:
        debug_print("🛑 Server stopped by user")
    except Exception as e:
        debug_print(f"❌ Server error: {str(e)}")
        debug_print(f"Traceback: {traceback.format_exc()}")
        # No request_id here, so just log the error
        # await self._send_error(f"Server error: {str(e)}", details=traceback.format_exc())
    finally:
        debug_print("🔚 VoidCat MCP Server shutting down")


if __name__ == "__main__":
    asyncio.run(main())
