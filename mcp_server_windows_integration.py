"""
VoidCat Reasoning Core - MCP Server Windows Integration
======================================================

This module provides integration between the VoidCat MCP server and
the Windows compatibility module, ensuring smooth operation on Windows systems.

Author: VoidCat Reasoning Core Team
License: MIT
Version: 1.0.0
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional, Union

# Import Windows compatibility module
try:
    from windows_compat import (
        WindowsConsoleColors,
        WindowsEnvironment,
        WindowsFileSystem,
        WindowsPathHandler,
        WindowsProcessManager,
        is_windows_compatible,
        normalize_path,
        setup_windows_compatibility,
        to_posix_path,
        to_windows_path,
    )
except ImportError:
    # Fallback if windows_compat.py is not available
    def setup_windows_compatibility():
        pass

    def is_windows_compatible():
        return os.name == "nt"

    def normalize_path(path):
        return str(path)

    def to_posix_path(path):
        return path.replace("\\", "/")

    def to_windows_path(path):
        return path.replace("/", "\\")


class MCPWindowsIntegration:
    """Integration between MCP server and Windows compatibility module."""

    def __init__(self):
        """Initialize Windows integration."""
        # Set up Windows compatibility
        setup_windows_compatibility()

        # Store Windows-specific paths
        self.appdata_path = os.environ.get("APPDATA", "")
        self.localappdata_path = os.environ.get("LOCALAPPDATA", "")
        self.temp_path = os.environ.get("TEMP", "")
        self.windows_compatible = is_windows_compatible()

        # Initialize Windows-specific MCP tools
        self._init_windows_mcp_tools()

    def _init_windows_mcp_tools(self):
        """Initialize Windows-specific MCP tools."""
        self.windows_tools = {
            "normalize_path": {
                "description": "Normalize a path for Windows compatibility",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to normalize"}
                    },
                    "required": ["path"],
                },
            },
            "to_posix_path": {
                "description": "Convert a Windows path to a POSIX-compatible path",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "windows_path": {
                            "type": "string",
                            "description": "Windows-style path",
                        }
                    },
                    "required": ["windows_path"],
                },
            },
            "to_windows_path": {
                "description": "Convert a POSIX path to a Windows-compatible path",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "posix_path": {
                            "type": "string",
                            "description": "POSIX-style path",
                        }
                    },
                    "required": ["posix_path"],
                },
            },
            "run_windows_command": {
                "description": "Run a command with Windows compatibility",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Command to run"},
                        "shell": {
                            "type": "boolean",
                            "description": "Whether to run in shell",
                        },
                        "cwd": {"type": "string", "description": "Working directory"},
                    },
                    "required": ["command"],
                },
            },
            "get_windows_paths": {
                "description": "Get Windows-specific paths",
                "parameters": {"type": "object", "properties": {}},
            },
        }

    def get_windows_tools(self) -> Dict[str, Any]:
        """
        Get Windows-specific MCP tools.

        Returns:
            Dictionary of Windows-specific MCP tools
        """
        return self.windows_tools

    async def handle_windows_tool_call(
        self, tool_name: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle a Windows-specific tool call.

        Args:
            tool_name: Name of the tool to call
            params: Tool parameters

        Returns:
            Tool result
        """
        if tool_name == "normalize_path":
            return {"normalized_path": normalize_path(params.get("path", ""))}
        elif tool_name == "to_posix_path":
            return {"posix_path": to_posix_path(params.get("windows_path", ""))}
        elif tool_name == "to_windows_path":
            return {"windows_path": to_windows_path(params.get("posix_path", ""))}
        elif tool_name == "run_windows_command":
            command = params.get("command", "")
            shell = params.get("shell", True)
            cwd = params.get("cwd", None)

            if not command:
                return {"error": "Command is required"}

            try:
                returncode, stdout, stderr = WindowsProcessManager.run_command(
                    command=command, shell=shell, cwd=cwd
                )

                return {
                    "returncode": returncode,
                    "stdout": stdout,
                    "stderr": stderr,
                    "success": returncode == 0,
                }
            except Exception as e:
                return {"error": str(e), "success": False}
        elif tool_name == "get_windows_paths":
            return {
                "appdata_path": self.appdata_path,
                "localappdata_path": self.localappdata_path,
                "temp_path": self.temp_path,
                "windows_compatible": self.windows_compatible,
            }
        else:
            return {"error": f"Unknown Windows tool: {tool_name}"}


# Create a singleton instance
windows_integration = MCPWindowsIntegration()


# Convenience function to get the singleton instance
def get_windows_integration() -> MCPWindowsIntegration:
    """Get the Windows integration singleton instance."""
    return windows_integration
