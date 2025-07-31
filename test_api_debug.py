#!/usr/bin/env python3
"""
Quick test script to verify the enhanced API error logging
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from enhanced_engine import VoidCatEnhancedEngine

async def test_api_calls():
    """Test API calls to see the enhanced error logging."""
    print("🧪 Testing VoidCat Enhanced Engine API calls...")
    
    # Initialize engine
    engine = VoidCatEnhancedEngine()
    
    # Test a simple query
    try:
        result = await engine.query("What is the meaning of life?", model="gpt-4o-mini")
        print(f"✅ Success! Result: {result[:100]}...")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_api_calls())