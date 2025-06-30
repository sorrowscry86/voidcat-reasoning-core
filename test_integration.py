#!/usr/bin/env python3
"""
VoidCat System Integration Test
Comprehensive testing of all VoidCat components
"""

import asyncio
import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from enhanced_engine import VoidCatEnhancedEngine
    print("✅ Enhanced Engine imported successfully")
except ImportError as e:
    print(f"❌ Enhanced Engine import failed: {e}")

try:
    from sequential_thinking import SequentialThinkingEngine
    print("✅ Sequential Thinking Engine imported successfully")
except ImportError as e:
    print(f"❌ Sequential Thinking Engine import failed: {e}")
    print("   (This module may not exist yet - that's okay)")

try:
    from context7_integration import Context7Engine
    print("✅ Context7 Engine imported successfully")
except ImportError as e:
    print(f"❌ Context7 Engine import failed: {e}")
    print("   (This module may not exist yet - that's okay)")

async def test_basic_functionality():
    """Test basic VoidCat functionality"""
    print("\n" + "="*60)
    print("🎯 VOIDCAT SYSTEM INTEGRATION TEST")
    print("="*60)
    print(f"Test started at: {datetime.now()}")
    
    # Test 1: Enhanced Engine Basic Functionality
    print("\n🚀 Testing Enhanced Engine...")
    try:
        enhanced = VoidCatEnhancedEngine()
        print("   ✅ Enhanced Engine initialized")
        
        # Test diagnostics
        diagnostics = enhanced.get_comprehensive_diagnostics()
        print("   ✅ Diagnostics retrieved")
        
        # Check API configuration
        api_config = diagnostics.get("api_configuration", {})
        deepseek_configured = api_config.get("deepseek_configured", False)
        print(f"   DeepSeek API: {'✅ Configured' if deepseek_configured else '❌ Not configured'}")
        
        # Test a simple reasoning pipeline
        print("   🧠 Testing reasoning pipeline...")
        result = await enhanced._enhanced_reasoning_pipeline(
            "What is the capital of France?",
            model="deepseek-chat"
        )
        print(f"   ✅ Pipeline completed: {len(result)} characters returned")
        
    except Exception as e:
        print(f"   ❌ Enhanced Engine test failed: {e}")
    
    # Test 2: Environment Configuration
    print("\n🔧 Testing Environment Configuration...")
    
    # Check for API keys
    deepseek_key = os.getenv('DEEPSEEK_API_KEY')
    if deepseek_key:
        print(f"   ✅ DEEPSEEK_API_KEY found (length: {len(deepseek_key)})")
    else:
        print("   ❌ DEEPSEEK_API_KEY not found in environment")
    
    # Check .env file
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        print("   ✅ .env file exists")
        # Read .env file to check for keys
        try:
            with open(env_file, 'r') as f:
                env_content = f.read()
                if 'DEEPSEEK_API_KEY' in env_content:
                    print("   ✅ DEEPSEEK_API_KEY found in .env file")
                if 'OPENAI_API_KEY' in env_content:
                    print("   ✅ OPENAI_API_KEY found in .env file")
        except Exception as e:
            print(f"   ⚠️  Could not read .env file: {e}")
    else:
        print("   ❌ .env file not found")
    
    # Test 3: MCP Server Readiness
    print("\n🔗 Testing MCP Server Readiness...")
    mcp_server_file = os.path.join(os.path.dirname(__file__), 'mcp_server.py')
    if os.path.exists(mcp_server_file):
        print("   ✅ mcp_server.py exists")
        try:
            from mcp_server import VoidCatMCPServer
            print("   ✅ MCP Server class imported successfully")
        except ImportError as e:
            print(f"   ⚠️  MCP Server import warning: {e}")
    else:
        print("   ❌ mcp_server.py not found")
    
    # Test 4: Claude Desktop Configuration
    print("\n🏠 Testing Claude Desktop Configuration...")
    claude_config_path = os.path.expanduser("~\\AppData\\Roaming\\Claude\\claude_desktop_config.json")
    if os.path.exists(claude_config_path):
        print("   ✅ Claude Desktop config file exists")
        try:
            import json
            with open(claude_config_path, 'r') as f:
                config = json.load(f)
                if 'mcpServers' in config and 'voidcat-reasoning-core' in config['mcpServers']:
                    print("   ✅ VoidCat MCP server configured in Claude Desktop")
                    # Check if DeepSeek API key is configured
                    voidcat_config = config['mcpServers']['voidcat-reasoning-core']
                    if 'env' in voidcat_config and 'DEEPSEEK_API_KEY' in voidcat_config['env']:
                        print("   ✅ DeepSeek API key configured in Claude Desktop")
                    else:
                        print("   ⚠️  DeepSeek API key missing in Claude Desktop config")
                else:
                    print("   ⚠️  VoidCat MCP server not configured in Claude Desktop")
        except Exception as e:
            print(f"   ⚠️  Could not read Claude config: {e}")
    else:
        print("   ❌ Claude Desktop config file not found")
    
    print("\n" + "="*60)
    print("🎉 INTEGRATION TEST COMPLETE")
    print("="*60)
    
    return True

async def test_full_reasoning():
    """Test the full reasoning capabilities"""
    print("\n🧠 FULL REASONING TEST")
    print("-" * 40)
    
    try:
        enhanced = VoidCatEnhancedEngine()
        
        test_queries = [
            "Explain the concept of artificial intelligence",
            "What are the benefits of modular programming?",
            "How does machine learning work?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\nTest {i}: {query}")
            result = await enhanced._enhanced_reasoning_pipeline(query)
            print(f"Result length: {len(result)} characters")
            print(f"Preview: {result[:100]}...")
            
    except Exception as e:
        print(f"❌ Full reasoning test failed: {e}")

def test_system_requirements():
    """Test system requirements and dependencies"""
    print("\n📦 TESTING SYSTEM REQUIREMENTS")
    print("-" * 40)
    
    required_modules = [
        'httpx', 'numpy', 'scikit-learn', 'python-dotenv'
    ]
    
    for module in required_modules:
        try:
            __import__(module.replace('-', '_'))
            print(f"   ✅ {module} installed")
        except ImportError:
            print(f"   ❌ {module} NOT installed")

if __name__ == "__main__":
    print("🛡️ Starting VoidCat Integration Test...")
    print("Through strategic analysis, we shall validate all systems!")
    
    # Test system requirements first
    test_system_requirements()
    
    # Run the main tests
    asyncio.run(test_basic_functionality())
    
    # Optionally run full reasoning test
    user_input = input("\n🤔 Run full reasoning test? (y/n): ")
    if user_input.lower() == 'y':
        asyncio.run(test_full_reasoning())
    
    print("\n✅ All tests completed with strategic precision!")
    print("🛡️ The VoidCat system status has been thoroughly assessed!")
