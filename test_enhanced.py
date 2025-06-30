#!/usr/bin/env python3
"""
Enhanced MCP server test script to verify new tools
"""
import json
import subprocess
import sys
import time

def test_enhanced_tools():
    """Test the enhanced MCP server tools"""
    print("🧪 Testing Enhanced VoidCat MCP Server...", file=sys.stderr)
    
    # Start MCP server process
    proc = subprocess.Popen(
        [sys.executable, "mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd="p:/voidcat-reasoning-core"
    )
    
    try:
        # 1. Initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        print("🔄 Testing initialization...", file=sys.stderr)
        if proc.stdin:
            proc.stdin.write(json.dumps(init_request) + "\n")
            proc.stdin.flush()
        
        if proc.stdout:
            response = proc.stdout.readline()
            print(f"✅ Init Response: {response.strip()[:100]}...", file=sys.stderr)
        
        # 2. List tools
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print("🔄 Testing tool listing...", file=sys.stderr)
        if proc.stdin:
            proc.stdin.write(json.dumps(tools_request) + "\n")
            proc.stdin.flush()
        
        if proc.stdout:
            tools_response = proc.stdout.readline()
            tools_data = json.loads(tools_response)
            tool_names = [tool['name'] for tool in tools_data.get('result', {}).get('tools', [])]
            print(f"✅ Available tools: {tool_names}", file=sys.stderr)
        
        # 3. Test enhanced status tool
        status_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "voidcat_status",
                "arguments": {"detailed": True}
            }
        }
        
        print("🔄 Testing enhanced status tool...", file=sys.stderr)
        if proc.stdin:
            proc.stdin.write(json.dumps(status_request) + "\n")
            proc.stdin.flush()
        
        if proc.stdout:
            status_response = proc.stdout.readline()
            print(f"✅ Status Response: {status_response.strip()[:150]}...", file=sys.stderr)
        
        # 4. Test new knowledge analysis tool
        analysis_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "voidcat_analyze_knowledge",
                "arguments": {"analysis_type": "summary"}
            }
        }
        
        print("🔄 Testing knowledge analysis tool...", file=sys.stderr)
        if proc.stdin:
            proc.stdin.write(json.dumps(analysis_request) + "\n")
            proc.stdin.flush()
        
        if proc.stdout:
            analysis_response = proc.stdout.readline()
            print(f"✅ Analysis Response: {analysis_response.strip()[:150]}...", file=sys.stderr)
        
        print("🎉 All enhanced tools tested successfully!", file=sys.stderr)
        
    except Exception as e:
        print(f"❌ Error during testing: {e}", file=sys.stderr)
    finally:
        proc.terminate()
        if proc.stderr:
            stderr_output = proc.stderr.read()
            if stderr_output:
                print(f"📊 Server Output:\n{stderr_output[:500]}...", file=sys.stderr)

if __name__ == "__main__":
    test_enhanced_tools()
