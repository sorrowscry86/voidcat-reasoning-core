#!/bin/bash
# ============================================================================
# VoidCat Reasoning Engine (VRE) - Universal Docker Entrypoint
# ============================================================================
# Flexible entrypoint supporting multiple operational modes:
# - API Gateway (default)
# - MCP Server 
# - Test Harness
# - Custom commands
# ============================================================================

set -e

# Function to log messages to stderr (avoid stdout contamination in MCP mode)
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [VoidCat-VRE] $1" >&2
}

# Function to detect operational mode based on command arguments
detect_mode() {
    case "$1" in
        "mcp"|"mcp_server"|"python mcp_server.py")
            echo "mcp"
            ;;
        "api"|"api_gateway"|"uvicorn"*)
            echo "api"
            ;;
        "test"|"main.py"|"python main.py")
            echo "test"
            ;;
        "bash"|"sh"|"/bin/bash"|"/bin/sh")
            echo "shell"
            ;;
        *)
            echo "custom"
            ;;
    esac
}

# Initialize container environment
initialize_environment() {
    log_message "Initializing VoidCat Reasoning Engine container..."
    
    # Ensure required directories exist
    mkdir -p /app/.agentic-tools-mcp /app/indexes /app/knowledge_source
    
    # Set proper permissions (non-root user)
    chown -R appuser:appuser /app/.agentic-tools-mcp /app/indexes /app/knowledge_source 2>/dev/null || true
    
    # Set essential environment variables
    export PYTHONPATH=/app:${PYTHONPATH}
    export PYTHONUNBUFFERED=1
    
    # Configure debug level
    if [ "${VOIDCAT_DEBUG:-false}" = "true" ]; then
        log_message "Debug mode enabled"
        export VOIDCAT_DEBUG=true
    else
        export VOIDCAT_DEBUG=false
    fi
    
    # Validate Python environment
    if ! python -c "import sys; print(f'Python {sys.version}', file=sys.stderr)"; then
        log_message "ERROR: Python validation failed"
        exit 1
    fi
    
    log_message "Environment initialization complete"
}

# Validate core modules based on operational mode
validate_modules() {
    local mode="$1"
    
    case "$mode" in
        "mcp")
            if ! python -c "import mcp_server" 2>/dev/null; then
                log_message "ERROR: Cannot import mcp_server module"
                exit 1
            fi
            log_message "MCP server module validated"
            ;;
        "api")
            if ! python -c "import api_gateway" 2>/dev/null; then
                log_message "ERROR: Cannot import api_gateway module"
                exit 1
            fi
            log_message "API gateway module validated"
            ;;
        "test")
            if ! python -c "import main" 2>/dev/null; then
                log_message "ERROR: Cannot import main module"
                exit 1
            fi
            log_message "Main test module validated"
            ;;
    esac
}

# Set mode-specific environment variables
configure_mode() {
    local mode="$1"
    
    case "$mode" in
        "mcp")
            export VOIDCAT_MCP_MODE=true
            export VOIDCAT_API_MODE=false
            log_message "Configured for MCP Server mode"
            ;;
        "api")
            export VOIDCAT_MCP_MODE=false
            export VOIDCAT_API_MODE=true
            log_message "Configured for API Gateway mode"
            ;;
        "test")
            export VOIDCAT_MCP_MODE=false
            export VOIDCAT_API_MODE=false
            export VOIDCAT_TEST_MODE=true
            log_message "Configured for Test Harness mode"
            ;;
        *)
            log_message "Configured for Custom mode"
            ;;
    esac
}

# Main entrypoint logic
main() {
    # Initialize environment
    initialize_environment
    
    # Detect operational mode
    MODE=$(detect_mode "$1")
    log_message "Detected operational mode: $MODE"
    
    # Configure mode-specific settings
    configure_mode "$MODE"
    
    # Validate required modules
    validate_modules "$MODE"
    
    # Handle different operational modes
    case "$MODE" in
        "mcp")
            log_message "Starting VoidCat MCP Server..."
            exec python -u mcp_server.py
            ;;
        "api")
            log_message "Starting VoidCat API Gateway..."
            if [ "$1" = "api" ]; then
                exec uvicorn api_gateway:app --host 0.0.0.0 --port 8000
            else
                # Execute the provided uvicorn command
                exec "$@"
            fi
            ;;
        "test")
            log_message "Starting VoidCat Test Harness..."
            exec python main.py
            ;;
        "shell")
            log_message "Starting interactive shell..."
            exec "$@"
            ;;
        "custom")
            log_message "Executing custom command: $*"
            exec "$@"
            ;;
    esac
}

# Trap signals for clean shutdown
trap 'log_message "Received shutdown signal, terminating..."; exit 0' SIGTERM SIGINT

# Execute main logic
main "$@"
