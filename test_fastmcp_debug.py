#!/usr/bin/env python3
"""
Quick test script to verify the FastMCP server response parsing fixes
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from fastmcp_server import voidcat_query, voidcat_ultimate_enhanced_query

async def test_fastmcp_tools():
    """Test FastMCP tools to see if response parsing is fixed."""
    print("🧪 Testing VoidCat FastMCP Server tools...")
    
    # Test basic query
    try:
        print("\n🤖 Testing basic query...")
        result = await voidcat_query("What is 2+2?")
        print(f"✅ Basic query success! Result preview: {result[:200]}...")
    except Exception as e:
        print(f"❌ Basic query error: {str(e)}")
    
    # Test ultimate enhanced query
    try:
        print("\n🏆 Testing ultimate enhanced query...")
        result = await voidcat_ultimate_enhanced_query("What is the capital of France?")
        print(f"✅ Ultimate query success! Result preview: {result[:200]}...")
    except Exception as e:
        print(f"❌ Ultimate query error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_fastmcp_tools())