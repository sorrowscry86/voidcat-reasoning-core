@echo off
REM ============================================================================
REM VoidCat Reasoning Engine - Enhanced Docker Management (Windows)
REM ============================================================================
REM Comprehensive management script for VRE Docker container operations
REM Supports multiple operational modes and service configurations
REM ============================================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

REM Color definitions for enhanced output
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "CYAN=[96m"
set "RESET=[0m"

REM Function to display help information
:show_help
echo %CYAN%========================================================%RESET%
echo %CYAN%  VoidCat Reasoning Engine - Docker Management%RESET%
echo %CYAN%========================================================%RESET%
echo.
echo %YELLOW%Basic Operations:%RESET%
echo   %0 build         - Build the VRE Docker image
echo   %0 start         - Start API Gateway service
echo   %0 stop          - Stop all services
echo   %0 restart       - Restart API Gateway service
echo   %0 logs          - Show API Gateway logs
echo   %0 status        - Show all service status
echo.
echo %YELLOW%Operational Modes:%RESET%
echo   %0 api           - Start API Gateway (port 8000)
echo   %0 mcp           - Start MCP Server (for Claude Desktop)
echo   %0 dev           - Start Development mode (port 8001, reload)
echo   %0 test          - Run Test Harness
echo.
echo %YELLOW%Advanced Operations:%RESET%
echo   %0 shell         - Open interactive shell in container
echo   %0 clean         - Clean up Docker resources
echo   %0 rebuild       - Clean rebuild of image
echo   %0 healthcheck   - Check container health status
echo.
echo %YELLOW%MCP Integration:%RESET%
echo   %0 mcp-build     - Build MCP-optimized image
echo   %0 mcp-run       - Run MCP server for Claude Desktop
echo   %0 mcp-test      - Test MCP server functionality
echo.
goto :eof

REM Check Docker availability
:check_docker
docker --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo %RED%ERROR: Docker not found or not running%RESET%
    echo Please install Docker and ensure it's running
    exit /b 1
)
goto :eof

REM Main command dispatcher
if "%1"=="" goto show_help
if "%1"=="help" goto show_help
if "%1"=="/?" goto show_help

call :check_docker

REM Basic operations
if "%1"=="build" (
    echo %BLUE%Building VoidCat Reasoning Engine Docker image...%RESET%
    docker build -t voidcat-reasoning-engine .
    if %ERRORLEVEL%==0 (
        echo %GREEN%Build completed successfully!%RESET%
    ) else (
        echo %RED%Build failed!%RESET%
    )
    goto :eof
)

if "%1"=="start" (
    echo %BLUE%Starting VoidCat API Gateway...%RESET%
    docker-compose up -d voidcat-api
    goto :eof
)

if "%1"=="stop" (
    echo %BLUE%Stopping all VoidCat services...%RESET%
    docker-compose down
    goto :eof
)

if "%1"=="restart" (
    echo %BLUE%Restarting VoidCat API Gateway...%RESET%
    docker-compose restart voidcat-api
    goto :eof
)

if "%1"=="logs" (
    echo %BLUE%Showing VoidCat API Gateway logs...%RESET%
    docker-compose logs -f voidcat-api
    goto :eof
)

if "%1"=="status" (
    echo %BLUE%VoidCat Services Status:%RESET%
    docker-compose ps
    goto :eof
)

REM Operational modes
if "%1"=="api" (
    echo %BLUE%Starting VoidCat API Gateway Service...%RESET%
    docker-compose up -d voidcat-api
    echo %GREEN%API Gateway running on http://localhost:8000%RESET%
    goto :eof
)

if "%1"=="mcp" (
    echo %BLUE%Starting VoidCat MCP Server...%RESET%
    docker-compose --profile mcp up -d voidcat-mcp
    echo %GREEN%MCP Server ready for Claude Desktop integration%RESET%
    goto :eof
)

if "%1"=="dev" (
    echo %BLUE%Starting VoidCat Development Mode...%RESET%
    docker-compose --profile development up -d voidcat-dev
    echo %GREEN%Development server running on http://localhost:8001 with auto-reload%RESET%
    goto :eof
)

if "%1"=="test" (
    echo %BLUE%Running VoidCat Test Harness...%RESET%
    docker-compose --profile testing run --rm voidcat-test
    goto :eof
)

REM Advanced operations
if "%1"=="shell" (
    echo %BLUE%Opening interactive shell in VoidCat container...%RESET%
    docker run --rm -it --env-file .env -v "%CD%:/app" voidcat-reasoning-engine bash
    goto :eof
)

if "%1"=="clean" (
    echo %BLUE%Cleaning up Docker resources...%RESET%
    docker-compose down -v --remove-orphans
    docker system prune -f
    echo %GREEN%Cleanup completed%RESET%
    goto :eof
)

if "%1"=="rebuild" (
    echo %BLUE%Performing clean rebuild...%RESET%
    docker-compose down -v --remove-orphans
    docker build --no-cache -t voidcat-reasoning-engine .
    echo %GREEN%Rebuild completed%RESET%
    goto :eof
)

if "%1"=="healthcheck" (
    echo %BLUE%Checking container health status...%RESET%
    docker run --rm --env-file .env voidcat-reasoning-engine python -c "
import sys
try:
    import engine, api_gateway, mcp_server
    print('✅ All core modules imported successfully')
    sys.exit(0)
except Exception as e:
    print(f'❌ Module import failed: {e}')
    sys.exit(1)
"
    goto :eof
)

REM MCP-specific operations
if "%1"=="mcp-build" (
    echo %BLUE%Building MCP-optimized Docker image...%RESET%
    docker build -f Dockerfile.mcp -t voidcat-reasoning-core-mcp .
    goto :eof
)

if "%1"=="mcp-run" (
    echo %BLUE%Running MCP Server for Claude Desktop integration...%RESET%
    echo %YELLOW%Note: This runs in interactive mode for Claude Desktop%RESET%
    docker run --rm -i --env-file .env ^
        -v "%CD%\knowledge_source:/app/knowledge_source:ro" ^
        -v "%CD%\.agentic-tools-mcp:/app/.agentic-tools-mcp" ^
        -v "%CD%\indexes:/app/indexes" ^
        voidcat-reasoning-core-mcp
    goto :eof
)

if "%1"=="mcp-test" (
    echo %BLUE%Testing MCP Server functionality...%RESET%
    docker run --rm --env-file .env voidcat-reasoning-core-mcp python -c "
import json
import sys
try:
    import mcp_server
    print('✅ MCP server module imported successfully')
    print('✅ MCP server ready for Claude Desktop integration')
    sys.exit(0)
except Exception as e:
    print(f'❌ MCP server test failed: {e}')
    sys.exit(1)
"
    goto :eof
)

REM Unknown command
echo %RED%Unknown command: %1%RESET%
echo Use '%0 help' to see available commands
exit /b 1
