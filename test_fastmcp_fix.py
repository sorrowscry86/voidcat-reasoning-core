#!/usr/bin/env python3
"""
Test script to verify FastMCP server fixes
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_voidcat_status():
    """Test the fixed voidcat_status function."""
    print("🧪 Testing VoidCat Status function...")
    
    try:
        # Import the function
        from fastmcp_server import voidcat_status
        
        # Test with detailed=True (the problematic parameter)
        result = await voidcat_status(detailed=True)
        print(f"✅ Status with detailed=True: Success!")
        print(f"Preview: {result[:100]}...")
        
        # Test with detailed=False
        result = await voidcat_status(detailed=False)
        print(f"✅ Status with detailed=False: Success!")
        
        # Test with no parameters (default)
        result = await voidcat_status()
        print(f"✅ Status with default params: Success!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_voidcat_status())