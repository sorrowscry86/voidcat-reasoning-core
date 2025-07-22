#!/bin/bash
# ============================================================================
# VoidCat Reasoning Core - Docker Management Script
# ============================================================================
# Quick commands for Docker container management
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

case "$1" in
    "build")
        echo "Building VoidCat MCP Docker image..."
        docker build -f Dockerfile.mcp -t voidcat-reasoning-core-mcp .
        ;;
    "start")
        echo "Starting VoidCat MCP Server with Docker Compose..."
        docker-compose -f docker-compose.mcp.yml up -d voidcat-mcp
        ;;
    "stop")
        echo "Stopping VoidCat MCP Server..."
        docker-compose -f docker-compose.mcp.yml down
        ;;
    "restart")
        echo "Restarting VoidCat MCP Server..."
        docker-compose -f docker-compose.mcp.yml restart voidcat-mcp
        ;;
    "logs")
        echo "Showing VoidCat MCP Server logs..."
        docker-compose -f docker-compose.mcp.yml logs -f voidcat-mcp
        ;;
    "shell")
        echo "Opening shell in VoidCat MCP container..."
        docker-compose -f docker-compose.mcp.yml exec voidcat-mcp /bin/bash
        ;;
    "clean")
        echo "Cleaning up Docker resources..."
        docker-compose -f docker-compose.mcp.yml down -v
        docker system prune -f
        ;;
    "status")
        echo "VoidCat MCP Server status:"
        docker-compose -f docker-compose.mcp.yml ps
        ;;
    *)
        echo "VoidCat Reasoning Core - Docker Management"
        echo "Usage: $0 {build|start|stop|restart|logs|shell|clean|status}"
        echo ""
        echo "Commands:"
        echo "  build   - Build the Docker image"
        echo "  start   - Start the MCP server"
        echo "  stop    - Stop the MCP server"
        echo "  restart - Restart the MCP server"
        echo "  logs    - Show server logs"
        echo "  shell   - Open shell in container"
        echo "  clean   - Clean up Docker resources"
        echo "  status  - Show container status"
        exit 1
        ;;
esac
