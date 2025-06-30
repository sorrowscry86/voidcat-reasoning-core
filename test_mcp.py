#!/usr/bin/env python3
"""
Quick MCP server test script
"""
import json
import subprocess
import sys

def test_mcp_server():
    """Test the MCP server initialization and tool listing"""
    print("Testing MCP server initialization...", file=sys.stderr)
    
    # Start MCP server process
    proc = subprocess.Popen(
        [sys.executable, "mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd="p:/voidcat-reasoning-core"
    )
    
    # Send initialization request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    print(f"Sending: {json.dumps(init_request)}", file=sys.stderr)
    if proc.stdin:
        proc.stdin.write(json.dumps(init_request) + "\n")
        proc.stdin.flush()
    
    # Read response
    try:
        if proc.stdout:
            response_line = proc.stdout.readline()
            print(f"Received: {response_line.strip()}", file=sys.stderr)
        
        # Send tools list request
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print(f"Sending: {json.dumps(tools_request)}", file=sys.stderr)
        if proc.stdin:
            proc.stdin.write(json.dumps(tools_request) + "\n")
            proc.stdin.flush()
        
        # Read tools response
        if proc.stdout:
            tools_response = proc.stdout.readline()
            print(f"Received: {tools_response.strip()}", file=sys.stderr)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
    finally:
        proc.terminate()
        if proc.stderr:
            stderr_output = proc.stderr.read()
            if stderr_output:
                print(f"Server stderr: {stderr_output}", file=sys.stderr)

if __name__ == "__main__":
    test_mcp_server()
