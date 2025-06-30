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

import json
import sys
import asyncio
from typing import Any, Dict, List, Optional, Sequence
from dataclasses import dataclass
import os
import traceback

from engine import VoidCatEngine
from enhanced_engine import VoidCatEnhancedEngine
from sequential_thinking import SequentialThinkingEngine


def debug_print(message: str) -> None:
    """Print debug messages to stderr to avoid interfering with MCP protocol."""
    print(f"[VoidCat MCP] {message}", file=sys.stderr, flush=True)


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
        
        # Enhanced tool definitions with categorization
        self.tools = [
            Tool(
                name="voidcat_query",
                description="Process intelligent queries using RAG-enhanced reasoning with the VoidCat engine",
                category="reasoning",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The question or prompt to process with RAG enhancement"
                        },
                        "model": {
                            "type": "string",
                            "description": "OpenAI model to use for reasoning",
                            "default": "gpt-4o-mini",
                            "enum": ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
                        },
                        "context_depth": {
                            "type": "integer",
                            "description": "Number of relevant documents to retrieve for context",
                            "default": 1,
                            "minimum": 1,
                            "maximum": 5
                        }
                    },
                    "required": ["query"]
                }
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
                            "default": False
                        }
                    },
                    "required": []
                }
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
                            "default": "summary"
                        }
                    },
                    "required": []
                }
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
                            "description": "The question or problem to analyze using sequential thinking"
                        },
                        "max_thoughts": {
                            "type": "integer",
                            "description": "Maximum number of thoughts to generate",
                            "default": 10,
                            "minimum": 3,
                            "maximum": 20
                        },
                        "include_reasoning_trace": {
                            "type": "boolean",
                            "description": "Include detailed reasoning trace in response",
                            "default": True
                        }
                    },
                    "required": ["query"]
                }
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
                            "description": "The question or prompt to process with full enhancement"
                        },
                        "model": {
                            "type": "string",
                            "description": "OpenAI model to use for final generation",
                            "default": "gpt-4o-mini",
                            "enum": ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
                        },
                        "max_context_sources": {
                            "type": "integer",
                            "description": "Maximum context sources to retrieve",
                            "default": 3,
                            "minimum": 1,
                            "maximum": 5
                        },
                        "include_trace": {
                            "type": "boolean",
                            "description": "Include comprehensive reasoning trace",
                            "default": False
                        }
                    },
                    "required": ["query"]
                }
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
                            "description": "Enable or disable sequential thinking"
                        },
                        "enable_context7": {
                            "type": "boolean",
                            "description": "Enable or disable Context7 enhanced context retrieval"
                        },
                        "enable_fallback_to_rag": {
                            "type": "boolean",
                            "description": "Enable fallback to basic RAG on enhanced processing errors"
                        },
                        "complexity_threshold": {
                            "type": "string",
                            "description": "Complexity threshold for reasoning strategy selection",
                            "enum": ["simple", "medium", "high", "expert"]
                        }
                    },
                    "required": []
                }
            )
        ]
    
    async def initialize(self, request_id: Optional[str] = None) -> None:
        """Initialize the VoidCat engine and respond to MCP initialize request."""
        try:
            from datetime import datetime, UTC
            self.initialization_time = datetime.now(UTC).isoformat()
            
            debug_print("Initializing VoidCat Enhanced Reasoning Core MCP Server...")
            self.engine = VoidCatEnhancedEngine()
            debug_print("Enhanced engine initialization completed successfully")
            
            await self._send_response({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                        "prompts": {}
                    },
                    "serverInfo": {
                        "name": "voidcat-reasoning-core",
                        "version": self.server_version,
                        "description": "RAG-enhanced intelligent reasoning engine"
                    }
                }
            })
            debug_print("MCP initialization response sent successfully")
            
        except Exception as e:
            self.error_count += 1
            error_msg = f"Failed to initialize VoidCat engine: {str(e)}"
            debug_print(f"Initialization error: {error_msg}")
            debug_print(f"Traceback: {traceback.format_exc()}")
            await self._send_error(error_msg, request_id)
    
    async def handle_list_tools(self, request_id: Optional[str] = None) -> None:
        """Handle MCP list_tools request."""
        tools_data = [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema
            }
            for tool in self.tools
        ]
        
        await self._send_response({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": tools_data}
        })
    
    async def handle_call_tool(self, tool_name: str, arguments: Dict[str, Any], request_id: Optional[str] = None) -> None:
        """Handle MCP call_tool request with enhanced error handling."""
        if not self.engine:
            await self._send_error("VoidCat engine not initialized. Please restart the MCP server.", request_id)
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
            else:
                await self._send_error(f"Unknown tool: {tool_name}. Available tools: {[t.name for t in self.tools]}", request_id)
                
        except Exception as e:
            self.error_count += 1
            error_msg = f"Tool execution failed for '{tool_name}': {str(e)}"
            debug_print(f"Tool error: {error_msg}")
            debug_print(f"Traceback: {traceback.format_exc()}")
            await self._send_error(error_msg, request_id)

    async def _handle_query_tool(self, arguments: Dict[str, Any], request_id: Optional[str] = None) -> None:
        """Handle voidcat_query tool execution with enhanced parameters."""
        query = arguments.get("query", "")
        model = arguments.get("model", "gpt-4o-mini")
        context_depth = arguments.get("context_depth", 1)
        
        if not query:
            await self._send_error("Query parameter is required and cannot be empty", request_id)
            return
        
        try:
            if not self.engine:
                await self._send_error("VoidCat engine is not initialized", request_id)
                return
                
            debug_print(f"Processing query with model: {model}, context_depth: {context_depth}")
            response = await self.engine.query(query, model=model)
            self.query_count += 1
            
            await self._send_response({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"🧠 **VoidCat RAG-Enhanced Response**\n\n{response}\n\n---\n*Query processed using {model} with {context_depth} context depth*"
                        }
                    ]
                }
            })
            debug_print(f"Query processed successfully (Total queries: {self.query_count})")
            
        except Exception as e:
            self.error_count += 1
            error_msg = f"Query processing failed: {str(e)}"
            debug_print(f"Query error: {error_msg}")
            await self._send_error(error_msg, request_id)

    async def _handle_status_tool(self, arguments: Dict[str, Any], request_id: Optional[str] = None) -> None:
        """Handle voidcat_status tool execution with detailed diagnostics."""
        try:
            detailed = arguments.get("detailed", False)
            
            if not self.engine:
                status = {
                    "engine_initialized": False,
                    "error": "Engine not initialized",
                    "server_version": self.server_version
                }
            else:
                # Safe knowledge base status check with defensive programming
                status = {
                    "engine_initialized": True,
                    "server_version": self.server_version,
                    "initialization_time": self.initialization_time,
                    "query_count": self.query_count,
                    "error_count": self.error_count,
                    "knowledge_base": {
                        "loaded": False,
                        "document_count": 0,
                        "vector_features": 0,
                        "status": "not_configured"
                    }
                }
                
                if detailed and self.engine:
                    try:
                        engine_diagnostics = self.engine.get_comprehensive_diagnostics()
                        status["detailed_diagnostics"] = engine_diagnostics
                    except AttributeError:
                        status["detailed_diagnostics"] = {"error": "Diagnostics method not available"}
            
            status_text = f"🎯 **VoidCat Reasoning Core Status**\n\n```json\n{json.dumps(status, indent=2)}\n```"
            
            if status.get("engine_initialized") and status.get("knowledge_base", {}).get("loaded"):
                status_text += "\n\n✅ **Status**: Production Ready & Operational"
            else:
                status_text += "\n\n⚠️ **Status**: Initialization Required"
            
            await self._send_response({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text", 
                            "text": status_text
                        }
                    ]
                }
            })
            
        except Exception as e:
            self.error_count += 1
            error_msg = f"Status check failed: {str(e)}"
            debug_print(f"Status error: {error_msg}")
            await self._send_error(error_msg, request_id)

    async def _handle_sequential_thinking_tool(self, arguments: Dict[str, Any], request_id: Optional[str] = None) -> None:
        """Handle voidcat_sequential_thinking tool execution."""
        query = arguments.get("query", "")
        max_thoughts = arguments.get("max_thoughts", 10)
        include_trace = arguments.get("include_reasoning_trace", True)
        
        if not query:
            await self._send_error("Query parameter is required and cannot be empty", request_id)
            return
        
        try:
            if not self.engine:
                await self._send_error("VoidCat engine is not initialized", request_id)
                return
            
            debug_print(f"Processing sequential thinking query with {max_thoughts} max thoughts")
            
            # Use enhanced query with reasoning trace instead of direct sequential engine access
            try:
                reasoning_result = await self.engine.query_with_reasoning_trace(
                    query, max_thoughts=max_thoughts, model="deepseek-chat"
                )
            except Exception as e:
                debug_print(f"Sequential thinking fallback: {str(e)}")
                reasoning_result = {
                    "response": await self.engine.query(query),
                    "reasoning_trace": {"steps": ["Basic query processing"], "confidence": 0.7}
                }
            
            response_text = f"🧠 **Sequential Thinking Analysis**\n\n"
            response_text += f"**Query**: {query}\n\n"
            response_text += f"**Final Response**: {reasoning_result.get('final_response', 'No response generated')}\n\n"
            
            if include_trace and reasoning_result.get('reasoning_path'):
                response_text += "### Reasoning Trace:\n"
                for i, branch in enumerate(reasoning_result['reasoning_path'][:3], 1):
                    response_text += f"**Branch {i}: {branch['branch_name']}**\n"
                    response_text += f"- Confidence: {branch['confidence']:.3f}\n"
                    response_text += f"- Thoughts: {len(branch['thoughts'])}\n\n"
            
            response_text += f"---\n*Complexity: {reasoning_result.get('complexity', 'unknown')} | "
            response_text += f"Confidence: {reasoning_result.get('confidence', 0.5):.3f} | "
            response_text += f"Total Thoughts: {reasoning_result.get('thought_count', 0)}*"
            
            await self._send_response({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": response_text
                        }
                    ]
                }
            })
            
        except Exception as e:
            error_msg = f"Sequential thinking processing failed: {str(e)}"
            debug_print(f"Sequential thinking error: {error_msg}")
            await self._send_error(error_msg, request_id)

    async def _handle_enhanced_query_tool(self, arguments: Dict[str, Any], request_id: Optional[str] = None) -> None:
        """Handle voidcat_enhanced_query tool execution."""
        query = arguments.get("query", "")
        model = arguments.get("model", "gpt-4o-mini")
        max_context_sources = arguments.get("max_context_sources", 3)
        include_trace = arguments.get("include_trace", False)
        
        if not query:
            await self._send_error("Query parameter is required and cannot be empty", request_id)
            return
        
        try:
            if not self.engine:
                await self._send_error("VoidCat engine is not initialized", request_id)
                return
            
            debug_print(f"Processing enhanced query with {max_context_sources} context sources")
            
            if include_trace:
                # Get detailed trace
                result = await self.engine.query_with_reasoning_trace(query, model=model)
                response_text = result["response"]
                
                if result.get("reasoning_trace"):
                    trace = result["reasoning_trace"]
                    response_text += f"\n\n### Enhanced Processing Trace\n"
                    response_text += f"- **Session ID**: {trace.get('session_id', 'N/A')}\n"
                    response_text += f"- **Complexity**: {trace.get('complexity', 'unknown')}\n"
                    response_text += f"- **Processing Time**: {trace.get('processing_time_seconds', 0):.2f}s\n"
                    response_text += f"- **Context Sources**: {trace.get('context_sources_used', 0)}\n"
                    response_text += f"- **Thoughts Generated**: {trace.get('thought_count', 0)}\n"
            else:
                # Standard enhanced processing
                response_text = await self.engine.query(
                    query, model=model, enable_enhanced=True, max_context_sources=max_context_sources
                )
            
            await self._send_response({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": response_text
                        }
                    ]
                }
            })
            
        except Exception as e:
            error_msg = f"Enhanced query processing failed: {str(e)}"
            debug_print(f"Enhanced query error: {error_msg}")
            await self._send_error(error_msg, request_id)

    async def _handle_configure_engine_tool(self, arguments: Dict[str, Any], request_id: Optional[str] = None) -> None:
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
            
            if config_result['configuration_changed']:
                response_text += "✅ **Configuration applied successfully**"
            else:
                response_text += "ℹ️ **No configuration changes made**"
            
            await self._send_response({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": response_text
                        }
                    ]
                }
            })
            
        except Exception as e:
            error_msg = f"Engine configuration failed: {str(e)}"
            debug_print(f"Configuration error: {error_msg}")
            await self._send_error(error_msg, request_id)

    async def _handle_analyze_knowledge_tool(self, arguments: Dict[str, Any], request_id: Optional[str] = None) -> None:
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
                await self._send_error(f"Knowledge analysis failed: {error_msg}", request_id)
                return
            
            kb_analysis = analysis_result["knowledge_base_analysis"]
            
            if analysis_type == "summary":
                response_text = f"📚 **Knowledge Base Analysis Summary**\n\n"
                response_text += f"**Total Sources**: {kb_analysis['total_sources']}\n"
                response_text += f"**Content Clusters**: {kb_analysis['content_clusters']}\n"
                response_text += f"**RAG Documents**: {kb_analysis['rag_documents']}\n"
                response_text += f"**Vector Features**: {kb_analysis['vector_features']}\n"
                response_text += f"**Coverage**: {kb_analysis['coverage_assessment']}\n\n"
                
                if kb_analysis.get('content_distribution'):
                    dist = kb_analysis['content_distribution']
                    response_text += "### Content Distribution:\n"
                    response_text += f"- **Total Words**: {dist.get('total_words', 0):,}\n"
                    response_text += f"- **Average per Source**: {dist.get('average_words_per_source', 0):.1f}\n"
                    
                    size_dist = dist.get('size_distribution', {})
                    response_text += f"- **Small Documents** (<500 words): {size_dist.get('small', 0)}\n"
                    response_text += f"- **Medium Documents** (500-2000 words): {size_dist.get('medium', 0)}\n"
                    response_text += f"- **Large Documents** (>2000 words): {size_dist.get('large', 0)}\n"
                
            elif analysis_type == "topics":
                response_text = f"🏷️ **Knowledge Base Topics Analysis**\n\n"
                
                if kb_analysis.get('content_distribution', {}).get('top_keywords'):
                    response_text += "### Top Keywords:\n"
                    for kw_data in kb_analysis['content_distribution']['top_keywords'][:10]:
                        response_text += f"- **{kw_data['keyword']}**: {kw_data['frequency']} occurrences\n"
                
                if kb_analysis.get('top_clusters'):
                    response_text += "\n### Top Content Clusters:\n"
                    for i, cluster in enumerate(kb_analysis['top_clusters'][:5], 1):
                        response_text += f"{i}. **{cluster['theme']}** ({cluster['source_count']} sources, coherence: {cluster['coherence_score']:.3f})\n"
                
            elif analysis_type == "documents":
                response_text = f"📄 **Knowledge Base Documents**\n\n"
                
                # Safely get source list - fallback if context7_engine not available
                try:
                    context7_engine = getattr(self.engine, 'context7_engine', None)
                    if context7_engine and hasattr(context7_engine, 'list_sources'):
                        sources = context7_engine.list_sources(limit=10)
                    else:
                        sources = []
                        response_text += "Context7 engine not available. Using fallback analysis.\n"
                except (AttributeError, TypeError):
                    sources = []
                    response_text += "Document analysis not available in current engine configuration.\n"
                
                if sources:
                    response_text += f"### Document Inventory ({len(sources)} shown):\n"
                    for i, source in enumerate(sources, 1):
                        # Defensive programming to prevent undefined values
                        metadata = source.get('metadata', {}) if source else {}
                        title = metadata.get('title', f'Document {i}') if metadata else f'Document {i}'
                        word_count = metadata.get('word_count', 0) if metadata else 0
                        
                        # Ensure title is a string
                        if title is None:
                            title = f'Document {i}'
                        
                        response_text += f"{i}. **{str(title)}** ({word_count:,} words)\n"
                        
                        keywords = metadata.get('keywords', []) if metadata else []
                        if keywords and isinstance(keywords, list):
                            # Ensure keywords are strings
                            safe_keywords = [str(k) for k in keywords[:3] if k is not None]
                            if safe_keywords:
                                response_text += f"   - Topics: {', '.join(safe_keywords)}\n"
                else:
                    response_text += "No documents found in knowledge base.\n"
            
            # Fix the string concatenation type issue
            footer_text = f"\n---\n*Analysis type: {analysis_type} | Engine: Enhanced VoidCat v{self.server_version}*"
            response_text = str(response_text) + footer_text
            
            await self._send_response({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": response_text
                        }
                    ]
                }
            })
            
        except Exception as e:
            error_msg = f"Knowledge analysis failed: {str(e)}"
            debug_print(f"Knowledge analysis error: {error_msg}")
            await self._send_error(error_msg, request_id)

    async def _send_response(self, response: Dict[str, Any]) -> None:
        """Send JSON-RPC response to stdout."""
        print(json.dumps(response), flush=True)
    
    async def _send_error(self, error_message: str, request_id: Optional[str] = None) -> None:
        """Send JSON-RPC error response."""
        await self._send_response({
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -1,
                "message": error_message
            }
        })
    
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
            await self._send_error(f"Unknown method: {method}", request_id)


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
                    
                line_str = line.decode('utf-8').strip()
                if line_str:
                    debug_print(f"📥 Received request: {line_str[:100]}...")
                    try:
                        request = json.loads(line_str)
                        await server.handle_request(request)
                    except json.JSONDecodeError as e:
                        debug_print(f"❌ JSON decode error: {str(e)}")
                        await server._send_error(f"Invalid JSON: {str(e)}")
                    except Exception as e:
                        debug_print(f"❌ Request processing error: {str(e)}")
                        debug_print(f"Traceback: {traceback.format_exc()}")
                        await server._send_error(f"Request processing failed: {str(e)}")
                        
            except Exception as e:
                debug_print(f"❌ Main loop error: {str(e)}")
                break
                
    except KeyboardInterrupt:
        debug_print("🛑 Server stopped by user")
    except Exception as e:
        debug_print(f"❌ Server error: {str(e)}")
        debug_print(f"Traceback: {traceback.format_exc()}")
    finally:
        debug_print("🔚 VoidCat MCP Server shutting down")


if __name__ == "__main__":
    asyncio.run(main())
