#!/usr/bin/env python3
"""
VoidCat MCP Server Python Launcher
=================================

This launcher ensures proper environment setup and dependency loading
for the VoidCat MCP server when running from Claude Desktop.
"""

import os
import sys

# Add the project directory to Python path
project_dir = r"D:\03_Development\Active_Projects\voidcat-reasoning-core"
sys.path.insert(0, project_dir)

# Change to project directory
os.chdir(project_dir)

# Set environment variables if not already set
if not os.getenv("PYTHONPATH"):
    os.environ["PYTHONPATH"] = project_dir

# Import and run the MCP server
try:
    import mcp_server

    # The mcp_server.py will handle the rest
except ImportError as e:
    print(f"Error importing MCP server: {e}", file=sys.stderr)
    sys.exit(1)
