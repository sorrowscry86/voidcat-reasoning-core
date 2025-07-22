#!/bin/bash
# ============================================================================
# VoidCat Reasoning Core - Docker Entrypoint for MCP Server
# ============================================================================
# Ensures proper environment setup for Model Context Protocol communication
# Handles stdin/stdout properly for JSON protocol
# ============================================================================

set -e

# Function to log messages to stderr (not stdout to avoid JSON contamination)
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [VoidCat-Entrypoint] $1" >&2
}

# Log container startup
log_message "Starting VoidCat MCP Server container..."

# Ensure required directories exist
mkdir -p /app/.agentic-tools-mcp /app/indexes /app/knowledge_source

# Set proper permissions
chown -R voidcat:voidcat /app/.agentic-tools-mcp /app/indexes /app/knowledge_source 2>/dev/null || true

# Validate essential files exist
if [ ! -f "/app/mcp_server.py" ]; then
    log_message "ERROR: mcp_server.py not found"
    exit 1
fi

# Set environment variables for MCP mode
export VOIDCAT_MCP_MODE=true
export VOIDCAT_DOCKER=true
export PYTHONPATH=/app
export PYTHONUNBUFFERED=1

# Configure debug level based on environment
if [ "${VOIDCAT_DEBUG:-false}" = "true" ]; then
    log_message "Debug mode enabled"
    export VOIDCAT_DEBUG=true
else
    log_message "Production mode - minimal logging"
    export VOIDCAT_DEBUG=false
fi

# Validate Python environment
if ! python -c "import sys; print(f'Python {sys.version}', file=sys.stderr)"; then
    log_message "ERROR: Python validation failed"
    exit 1
fi

# Test MCP server module import
if ! python -c "import mcp_server" 2>/dev/null; then
    log_message "ERROR: Cannot import mcp_server module"
    exit 1
fi

log_message "Environment validation complete"
log_message "Starting MCP server with command: $@"

# Execute the command with proper signal handling
exec "$@"
