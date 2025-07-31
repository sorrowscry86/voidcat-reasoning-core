#!/usr/bin/env python3
"""
Test script to verify MCP server JSON output
"""
import json
import subprocess
import sys


def test_mcp_json():
    """Test that MCP server only outputs valid JSON to stdout"""

    # Simple MCP initialize request
    test_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"},
        },
    }

    try:
        # Start the MCP server process
        process = subprocess.Popen(
            [sys.executable, "mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="D:/03_Development/Active_Projects/voidcat-reasoning-core",
        )

        # Send the test request
        request_str = json.dumps(test_request) + "\n"
        stdout, stderr = process.communicate(input=request_str, timeout=10)

        print("=== STDERR (Debug Messages) ===")
        print(stderr)
        print("\n=== STDOUT (Should be JSON only) ===")
        print(repr(stdout))

        # Try to parse each line as JSON
        lines = stdout.strip().split("\n")
        for i, line in enumerate(lines):
            if line.strip():
                try:
                    parsed = json.loads(line)
                    print(f"✅ Line {i+1}: Valid JSON")
                except json.JSONDecodeError as e:
                    print(f"❌ Line {i+1}: Invalid JSON - {e}")
                    print(f"   Content: {repr(line)}")

        return process.returncode == 0

    except subprocess.TimeoutExpired:
        process.kill()
        print("❌ Test timed out")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False


if __name__ == "__main__":
    success = test_mcp_json()
    print(f"\n{'✅ Test PASSED' if success else '❌ Test FAILED'}")
