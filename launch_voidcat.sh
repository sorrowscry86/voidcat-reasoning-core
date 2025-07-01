#!/bin/bash
# VoidCat Reasoning Core - Unix/Linux/macOS Launcher
# Strategic deployment automation for Lord Wykeve
# Author: Albedo, Overseer of the Digital Scriptorium

echo ""
echo "================================================"
echo "   🛡️ VOIDCAT REASONING CORE LAUNCHER"
echo "================================================"
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    echo "Please install Python 3.13+ and try again"
    exit 1
fi

# Launch VoidCat system
echo "🚀 Launching VoidCat Reasoning Core..."
echo ""

python3 voidcat_launcher.py

echo ""
echo "🛡️ VoidCat deployment session complete"
