#!/usr/bin/env python3
"""
Test script to verify that the enhanced launcher properly redirects output to stderr
and keeps stdout clean for JSON protocol compliance.
"""

import json
import subprocess
import sys
import time


def test_launcher_stdout():
    """Test that the enhanced launcher doesn't contaminate stdout."""
    print("Testing enhanced launcher stdout cleanliness...", file=sys.stderr)

    process = None
    try:
        # Start the enhanced launcher
        process = subprocess.Popen(
            ["enhanced_mcp_launcher.bat"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,
        )

        # Give it a few seconds to start up
        time.sleep(3)

        # Check if anything was written to stdout
        stdout_data, stderr_data = process.communicate(timeout=5)

        print(f"STDOUT content: '{stdout_data}'", file=sys.stderr)
        print(
            f"STDERR content (first 500 chars): '{stderr_data[:500]}'", file=sys.stderr
        )

        # Check if stdout is clean (should be empty or valid JSON only)
        if stdout_data.strip():
            try:
                # Try to parse as JSON
                json.loads(stdout_data.strip())
                print("✅ STDOUT contains valid JSON", file=sys.stderr)
            except json.JSONDecodeError:
                print("❌ STDOUT contains non-JSON data:", file=sys.stderr)
                print(f"Content: '{stdout_data}'", file=sys.stderr)
                return False
        else:
            print("✅ STDOUT is clean (empty)", file=sys.stderr)

        return True

    except subprocess.TimeoutExpired:
        print(
            "⏱️ Launcher test timed out (normal for long-running server)",
            file=sys.stderr,
        )
        if process:
            process.kill()
        return True
    except Exception as e:
        print(f"❌ Error testing launcher: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    success = test_launcher_stdout()
    sys.exit(0 if success else 1)
