@echo off
REM ============================================================================
REM VoidCat Reasoning Core - Docker MCP Launcher for Windows
REM ============================================================================
REM This launcher runs the VoidCat MCP server in a Docker container
REM Eliminates Windows compatibility issues and provides clean environment
REM ============================================================================

setlocal enabledelayedexpansion

REM Set working directory to script location
cd /d "%~dp0"

REM Check if Docker is installed and running
docker --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    exit /b 1
)

REM Check if Docker daemon is running
docker info >nul 2>&1
if %ERRORLEVEL% neq 0 (
    exit /b 1
)

REM Check for .env file
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul 2>&1
    )
)

REM Build the Docker image if it doesn't exist
docker image inspect voidcat-reasoning-core-mcp >nul 2>&1
if %ERRORLEVEL% neq 0 (
    docker build -f Dockerfile.mcp -t voidcat-reasoning-core-mcp . >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        exit /b 1
    )
)

REM Stop any existing container
docker stop voidcat-reasoning-core-mcp >nul 2>&1
docker rm voidcat-reasoning-core-mcp >nul 2>&1

REM Run the MCP server in Docker with proper stdio handling for Claude Desktop
REM No debug output to stderr to avoid contaminating MCP JSON protocol
docker run --name voidcat-reasoning-core-mcp ^
    --rm ^
    -i ^
    --env-file ".env" ^
    -v "%CD%\knowledge_source:/app/knowledge_source:ro" ^
    -v "%CD%\.agentic-tools-mcp:/app/.agentic-tools-mcp" ^
    -v "%CD%\indexes:/app/indexes" ^
    -e "VOIDCAT_DEBUG=false" ^
    -e "VOIDCAT_DOCKER=true" ^
    -e "VOIDCAT_MCP_MODE=true" ^
    voidcat-reasoning-core-mcp 2>nul

REM If we reach here, the container has stopped
exit /b %ERRORLEVEL%
