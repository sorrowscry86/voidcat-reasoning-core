#!/usr/bin/env python3
"""
VoidCat Reasoning Core - Setup Verification Script

This script verifies that all dependencies are installed correctly
and that the MCP server can be launched successfully.
"""

import importlib
import os
import subprocess
import sys
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major > 3 or (version.major == 3 and version.minor >= 8):
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro} (Compatible)")
        return True
    else:
        print(f"  ❌ Python {version.major}.{version.minor}.{version.micro} (Requires Python 3.8+)")
        return False


def check_dependencies():
    """Check if all required dependencies are installed."""
    print("\n📦 Checking dependencies...")
    
    # Map package names to their import names
    packages = {
        "fastapi": "fastapi",
        "uvicorn": "uvicorn", 
        "httpx": "httpx",
        "python-dotenv": "dotenv",
        "scikit-learn": "sklearn",
        "numpy": "numpy"
    }
    
    missing_packages = []
    
    for package_name, import_name in packages.items():
        try:
            # Use subprocess to test import in current Python environment
            result = subprocess.run([
                sys.executable, "-c", f"import {import_name}"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"  ✅ {package_name}")
            else:
                print(f"  ❌ {package_name} (Not installed)")
                missing_packages.append(package_name)
        except Exception as e:
            print(f"  ❌ {package_name} (Error checking: {e})")
            missing_packages.append(package_name)
    
    
    return len(missing_packages) == 0, missing_packages


def check_openai_key():
    """Check if OpenAI API key is set."""
    print("\n🔑 Checking OpenAI API key...")
    
    # CRITICAL: Load .env file first to prevent overwriting variables
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your-openai-api-key-here":
        print("  ✅ OpenAI API key is set")
        return True
    else:
        print("  ⚠️  OpenAI API key not set (Required for full functionality)")
        return False


def check_mcp_server():
    """Check if the MCP server can be imported."""
    print("\n🔧 Checking MCP server...")
    
    try:
        # Add current directory to path
        current_dir = Path(__file__).parent
        sys.path.insert(0, str(current_dir))
        
        import mcp_server
        print("  ✅ MCP server module imports successfully")
        return True
    except Exception as e:
        print(f"  ❌ MCP server import failed: {e}")
        return False


def check_core_engine():
    """Check if the core engine can be imported and initialized."""
    print("\n⚙️ Checking VoidCat engine...")
    
    try:
        from engine import VoidCatEngine
        engine = VoidCatEngine()
        print("  ✅ VoidCat engine initializes successfully")
        return True
    except Exception as e:
        print(f"  ❌ VoidCat engine failed: {e}")
        return False


def check_api_gateway():
    """Check if the API gateway can be imported."""
    print("\n🌐 Checking API gateway...")
    
    try:
        import api_gateway
        print("  ✅ API gateway imports successfully")
        return True
    except Exception as e:
        print(f"  ❌ API gateway import failed: {e}")
        return False


def check_claude_config():
    """Check if Claude Desktop configuration is properly set up."""
    print("\n🎭 Checking Claude Desktop configuration...")
    
    config_path = Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
    
    if config_path.exists():
        try:
            import json
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            if "mcpServers" in config and "voidcat-reasoning-core" in config["mcpServers"]:
                print("  ✅ VoidCat MCP server found in Claude Desktop configuration")
                return True
            else:
                print("  ⚠️  VoidCat MCP server not found in Claude Desktop configuration")
                return False
        except Exception as e:
            print(f"  ❌ Error reading Claude Desktop configuration: {e}")
            return False
    else:
        print("  ⚠️  Claude Desktop configuration file not found")
        return False


def main():
    """Run all verification checks."""
    print("🚀 VoidCat Reasoning Core - Setup Verification")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", lambda: check_dependencies()[0]),
        ("OpenAI API Key", check_openai_key),
        ("MCP Server", check_mcp_server),
        ("VoidCat Engine", check_core_engine),
        ("API Gateway", check_api_gateway),
        ("Claude Config", check_claude_config)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ❌ {name} check failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n📊 Verification Summary")
    print("=" * 30)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {name}")
    
    print(f"\n🎯 Overall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! VoidCat Reasoning Core is ready for production.")
        print("\n📝 Next steps:")
        print("   1. Restart Claude Desktop to load the MCP server")
        print("   2. Test the integration by asking Claude to use VoidCat tools")
        print("   3. Optional: Start the API gateway for diagnostics")
    else:
        print("\n⚠️  Some checks failed. Please resolve the issues above.")
        
        # Check if dependencies failed
        deps_passed, missing = check_dependencies()
        if not deps_passed:
            print(f"\n💡 To install missing dependencies:")
            print(f"   pip install {' '.join(missing)}")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
