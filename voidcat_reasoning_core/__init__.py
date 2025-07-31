"""
VoidCat Reasoning Core - Advanced MCP Server Package
"""

__version__ = "1.0.0"
__author__ = "SorrowsCry86"
__description__ = "Advanced MCP Server with 31 AI reasoning tools"

# Only import the main function to avoid circular imports
from .mcp_server import main

__all__ = ["main", "__version__", "__author__", "__description__"]
