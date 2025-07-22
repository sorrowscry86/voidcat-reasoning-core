#!/bin/bash
# VoidCat MCP Server Docker Launcher
# This script runs the VoidCat MCP server in a Docker container

docker run --rm -i \
  --env-file "D:/03_Development/Active_Projects/voidcat-reasoning-core/.env" \
  -v "D:/03_Development/Active_Projects/voidcat-reasoning-core/knowledge_source:/app/knowledge_source:ro" \
  voidcat-reasoning-engine:latest \
  python mcp_server.py
