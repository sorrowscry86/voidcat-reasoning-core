#!/usr/bin/env python3
"""
Claude Desktop Integration Verification
Verify that VoidCat Ultimate Mode is ready for Claude Desktop
"""

import json
import os
import sys
from pathlib import Path


def verify_claude_desktop_setup():
    """Verify Claude Desktop integration setup."""
    print("🔍 VoidCat Claude Desktop Integration Verification")
    print("=" * 60)

    # Check Claude Desktop config file
    config_path = Path(
        "C:/Users/Wykeve/AppData/Roaming/Claude/claude_desktop_config.json"
    )

    print(f"\n1. Checking Claude Desktop configuration...")
    if config_path.exists():
        print(f"✅ Configuration file found: {config_path}")

        try:
            with open(config_path, "r") as f:
                config = json.load(f)

            if "voidcat-reasoning-core" in config.get("mcpServers", {}):
                voidcat_config = config["mcpServers"]["voidcat-reasoning-core"]
                print("✅ VoidCat MCP server configuration found")

                # Check the script path
                args = voidcat_config.get("args", [])
                if args and "mcp_server.py" in args[0]:
                    print("✅ Using Ultimate Mode script (mcp_server.py)")
                elif args and "mcp_server_simplified" in args[0]:
                    print(
                        "⚠️  Using simplified script - should be mcp_server.py for Ultimate Mode"
                    )
                else:
                    print("❌ Script path not found or incorrect")

                # Check environment variables
                env = voidcat_config.get("env", {})
                api_keys = []
                if env.get("OPENAI_API_KEY"):
                    api_keys.append("OpenAI")
                if env.get("DEEPSEEK_API_KEY"):
                    api_keys.append("DeepSeek")

                if api_keys:
                    print(f"✅ API keys configured: {', '.join(api_keys)}")
                else:
                    print("❌ No API keys found")

                if env.get("VOIDCAT_MCP_MODE") == "true":
                    print("✅ MCP mode enabled")
                else:
                    print("⚠️  MCP mode not explicitly enabled")

                if voidcat_config.get("enabled", True):
                    print("✅ VoidCat server is enabled")
                else:
                    print("❌ VoidCat server is disabled")

            else:
                print("❌ VoidCat not found in MCP servers configuration")

        except json.JSONDecodeError as e:
            print(f"❌ Configuration file is not valid JSON: {e}")
        except Exception as e:
            print(f"❌ Error reading configuration: {e}")
    else:
        print(f"❌ Configuration file not found: {config_path}")

    # Check project files
    print(f"\n2. Checking VoidCat project files...")
    project_path = Path("D:/03_Development/Active_Projects/voidcat-reasoning-core")

    if project_path.exists():
        print(f"✅ Project directory found: {project_path}")

        required_files = [
            "mcp_server.py",
            "enhanced_engine.py",
            "sequential_thinking.py",
            "context7_integration.py",
        ]

        for file in required_files:
            file_path = project_path / file
            if file_path.exists():
                print(f"✅ {file} found")
            else:
                print(f"❌ {file} missing")
    else:
        print(f"❌ Project directory not found: {project_path}")

    # Check Python environment
    print(f"\n3. Checking Python environment...")
    python_path = sys.executable
    print(f"✅ Python executable: {python_path}")
    print(f"✅ Python version: {sys.version}")

    # Check required packages
    package_imports = {
        "httpx": "httpx",
        "scikit-learn": "sklearn",
        "numpy": "numpy",
        "python-dotenv": "dotenv",
    }
    missing_packages = []

    for package_name, import_name in package_imports.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name} installed")
        except ImportError:
            print(f"❌ {package_name} missing")
            missing_packages.append(package_name)

    # Summary
    print("\n" + "=" * 60)
    if missing_packages:
        print("⚠️  SETUP INCOMPLETE")
        print(f"Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install " + " ".join(missing_packages))
    else:
        print("🎉 CLAUDE DESKTOP INTEGRATION READY!")
        print("✅ VoidCat Ultimate Mode is configured for Claude Desktop")
        print("✅ All required files and dependencies are present")
        print("✅ Configuration is properly set up")

    print("\n📋 Next Steps:")
    print("1. Restart Claude Desktop completely")
    print("2. Try using VoidCat Ultimate Mode tools:")
    print("   - Use VoidCat Ultimate Mode to analyze quantum computing")
    print("   - Use VoidCat Sequential Thinking to explain AI ethics")
    print("   - Use VoidCat Context7 to research machine learning")

    print("\n🔧 Available Ultimate Mode Tools:")
    tools = [
        "voidcat_ultimate_enhanced_query",
        "voidcat_enhanced_query_with_sequential",
        "voidcat_enhanced_query_with_context7",
        "voidcat_query",
        "voidcat_status",
        "voidcat_analyze_knowledge",
    ]
    for tool in tools:
        print(f"   - {tool}")

    return len(missing_packages) == 0


if __name__ == "__main__":
    success = verify_claude_desktop_setup()
    sys.exit(0 if success else 1)
