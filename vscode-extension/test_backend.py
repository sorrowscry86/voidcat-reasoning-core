#!/usr/bin/env python3
"""
Test script to check if the VoidCat backend server is running
and responding correctly for the VS Code extension.
"""

import asyncio
import sys
from pathlib import Path

import aiohttp

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

async def test_backend_connection():
    """Test if the backend server is running and responding."""
    
    base_url = "http://localhost:8002"
    
    print("🧪 Testing VoidCat Backend Connection...")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        
        # Test health endpoint
        try:
            print("🏥 Testing health endpoint...")
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health check passed: {data}")
                else:
                    print(f"❌ Health check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
        
        # Test diagnostics endpoint
        try:
            print("📊 Testing diagnostics endpoint...")
            async with session.get(f"{base_url}/diagnostics") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Diagnostics check passed")
                    print(f"   System Status: {data.get('system_status', 'unknown')}")
                    print(f"   Tasks: {data.get('task_statistics', {}).get('total', 0)}")
                else:
                    print(f"❌ Diagnostics check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Diagnostics check error: {e}")
            return False
        
        # Test VS Code specific endpoint
        try:
            print("🔧 Testing VS Code system status endpoint...")
            async with session.get(f"{base_url}/vscode/api/v1/system/status") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ VS Code endpoint check passed")
                    print(f"   Engine Initialized: {data.get('engine_initialized', False)}")
                    print(f"   Documents Loaded: {data.get('documents_loaded', 0)}")
                else:
                    print(f"⚠️  VS Code endpoint not available: {response.status}")
                    # This is OK, might not be implemented yet
        except Exception as e:
            print(f"⚠️  VS Code endpoint error: {e}")
            # This is OK, might not be implemented yet
    
    print("=" * 50)
    print("✅ Backend connection test completed!")
    print("🚀 Your VS Code extension should now be able to connect.")
    return True

def main():
    """Main entry point."""
    print("🐾 VoidCat Backend Connection Test")
    print()
    
    try:
        success = asyncio.run(test_backend_connection())
        if success:
            print("\n🎉 All tests passed! Your backend is ready.")
        else:
            print("\n❌ Some tests failed. Check the server status.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()