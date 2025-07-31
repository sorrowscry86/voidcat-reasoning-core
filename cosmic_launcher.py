#!/usr/bin/env python3
"""
VoidCat Cosmic System Launcher - The Ultimate Zen-like Entry Point
Launch all cosmic components with perfect harmony! 🧘‍♂️

This launcher provides a unified way to start different components
of the VoidCat Cosmic system with our MultiProviderClient integration.
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def print_cosmic_banner():
    """Print the cosmic banner with zen-like vibes."""
    banner = """
🌟 ═══════════════════════════════════════════════════════════════ 🌟
    
    ██╗   ██╗ ██████╗ ██╗██████╗  ██████╗ █████╗ ████████╗
    ██║   ██║██╔═══██╗██║██╔══██╗██╔════╝██╔══██╗╚══██╔══╝
    ██║   ██║██║   ██║██║██║  ██║██║     ███████║   ██║   
    ╚██╗ ██╔╝██║   ██║██║██║  ██║██║     ██╔══██║   ██║   
     ╚████╔╝ ╚██████╔╝██║██████╔╝╚██████╗██║  ██║   ██║   
      ╚═══╝   ╚═════╝ ╚═╝╚═════╝  ╚═════╝╚═╝  ╚═╝   ╚═╝   
                                                           
         🧘‍♂️ COSMIC REASONING CORE 🧘‍♂️
         
    ✨ Powered by MultiProviderClient with Zen-like API Management ✨
    🌊 Rate Limiting • Circuit Breakers • Exponential Backoff 🌊
    🎯 DeepSeek • OpenRouter • OpenAI • Cosmic Fallbacks 🎯
    
🌟 ═══════════════════════════════════════════════════════════════ 🌟
"""
    print(banner)


def check_dependencies():
    """Check if all cosmic dependencies are available."""
    print("🔍 Checking cosmic dependencies...")
    
    dependencies = [
        ("cosmic_engine", "Cosmic Engine"),
        ("multi_provider_client", "MultiProvider Client"),
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("httpx", "HTTPX"),
        ("dotenv", "Python Dotenv")
    ]
    
    missing = []
    
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name}")
            missing.append(name)
    
    if missing:
        print(f"\n⚠️ Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("✨ All dependencies available!")
    return True


def check_api_keys():
    """Check API key configuration."""
    print("\n🔑 Checking API key configuration...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    keys = [
        ("OPENAI_API_KEY", "OpenAI"),
        ("DEEPSEEK_API_KEY", "DeepSeek"),
        ("OPENROUTER_API_KEY", "OpenRouter")
    ]
    
    available = []
    
    for env_var, provider in keys:
        key = os.getenv(env_var)
        if key and not key.startswith("your_"):
            print(f"  ✅ {provider}: {key[:10]}...{key[-4:] if len(key) > 14 else ''}")
            available.append(provider)
        else:
            print(f"  ❌ {provider}: Not configured")
    
    if available:
        print(f"✨ Ready with: {', '.join(available)}")
        return True
    else:
        print("⚠️ No valid API keys found! Please configure at least one provider.")
        return False


async def launch_api_gateway(host="0.0.0.0", port=8000):
    """Launch the cosmic API gateway."""
    print(f"\n🌐 Launching Cosmic API Gateway on {host}:{port}...")
    
    try:
        import uvicorn
        from api_gateway import app
        
        config = uvicorn.Config(
            app=app,
            host=host,
            port=port,
            log_level="info",
            reload=False
        )
        
        server = uvicorn.Server(config)
        await server.serve()
        
    except Exception as e:
        print(f"❌ Failed to launch API gateway: {e}")
        return False


async def launch_mcp_server():
    """Launch the cosmic MCP server."""
    print("\n🔗 Launching Cosmic MCP Server...")
    
    try:
        from cosmic_mcp_server import main
        await main()
        
    except Exception as e:
        print(f"❌ Failed to launch MCP server: {e}")
        return False


async def launch_fastmcp_server():
    """Launch the cosmic FastMCP server."""
    print("\n⚡ Launching Cosmic FastMCP Server...")
    
    try:
        from cosmic_fastmcp_server import main
        await main()
        
    except Exception as e:
        print(f"❌ Failed to launch FastMCP server: {e}")
        return False


async def test_cosmic_system():
    """Test the cosmic system components."""
    print("\n🧪 Testing Cosmic System...")
    
    try:
        from cosmic_engine import VoidCatCosmicEngine
        
        # Initialize engine
        engine = VoidCatCosmicEngine()
        print("✅ Cosmic engine initialized")
        
        # Test provider status
        status = engine.get_provider_metrics()
        print(f"✅ Provider status: {len(status)} providers")
        
        # Test health check
        health = await engine.health_check()
        healthy_count = sum(1 for h in health.values() if h)
        print(f"✅ Health check: {healthy_count}/{len(health)} providers healthy")
        
        # Test simple query
        response = await engine.query("Hello, cosmic system!", model="gpt-4o-mini")
        print(f"✅ Query test: {response[:50]}...")
        
        print("🎉 Cosmic system test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Cosmic system test failed: {e}")
        return False


def show_status():
    """Show current system status."""
    print("\n📊 Cosmic System Status")
    print("=" * 30)
    
    try:
        from cosmic_engine import VoidCatCosmicEngine
        
        engine = VoidCatCosmicEngine()
        status = engine.get_status()
        
        print(f"Engine Type: {status.get('engine_type', 'Unknown')}")
        print(f"Status: {status.get('status', 'Unknown')}")
        print(f"Queries Processed: {status.get('total_queries_processed', 0)}")
        print(f"Knowledge Documents: {status.get('knowledge_documents', 0)}")
        print(f"Cosmic Vibes: {status.get('cosmic_vibes', 'Unknown')}")
        
        # Provider status
        provider_status = engine.get_provider_metrics()
        print(f"\nProviders: {len(provider_status)} configured")
        
        for name, info in provider_status.items():
            print(f"  {name}: {info['status']} (priority: {info['priority']})")
        
    except Exception as e:
        print(f"❌ Failed to get status: {e}")


async def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(
        description="VoidCat Cosmic System Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cosmic_launcher.py api                    # Launch API Gateway
  python cosmic_launcher.py mcp                    # Launch MCP Server
  python cosmic_launcher.py fastmcp                # Launch FastMCP Server
  python cosmic_launcher.py test                   # Test System
  python cosmic_launcher.py status                 # Show Status
  python cosmic_launcher.py api --port 8080        # Custom port
        """
    )
    
    parser.add_argument(
        "command",
        choices=["api", "mcp", "fastmcp", "test", "status", "check"],
        help="Command to execute"
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host for API gateway (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for API gateway (default: 8000)"
    )
    
    args = parser.parse_args()
    
    # Show banner
    print_cosmic_banner()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Execute command
    if args.command == "check":
        check_api_keys()
        
    elif args.command == "status":
        show_status()
        
    elif args.command == "test":
        success = await test_cosmic_system()
        if not success:
            sys.exit(1)
            
    elif args.command == "api":
        if not check_api_keys():
            print("⚠️ Warning: No API keys configured, but starting anyway...")
        await launch_api_gateway(args.host, args.port)
        
    elif args.command == "mcp":
        if not check_api_keys():
            print("⚠️ Warning: No API keys configured, but starting anyway...")
        await launch_mcp_server()
        
    elif args.command == "fastmcp":
        if not check_api_keys():
            print("⚠️ Warning: No API keys configured, but starting anyway...")
        await launch_fastmcp_server()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Cosmic system stopped by user")
    except Exception as e:
        print(f"\n💥 Cosmic system crashed: {e}")
        sys.exit(1)