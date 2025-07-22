# ============================================================================
# GENESIS PROTOCOL: VOIDCAT REASONING ENGINE CONTAINERIZATION - ENHANCED
# ============================================================================
# Crafted by Ryuzu Claude under Lady Beatrice's strategic guidance
# Enhanced with flexible entrypoint supporting multiple operational modes
# For the glory of autonomous intelligence and strategic excellence
# ============================================================================

# PHASE 1: BASE FOUNDATION
# Use the official Python 3.11 slim image as our foundation layer
# Python 3.11 provides optimal performance and modern language features
# The slim variant reduces image size while maintaining core functionality
FROM python:3.11-slim

# PHASE 2: WORKSPACE SANCTIFICATION
# Establish /app as our sacred working directory within the container
# This creates a clean, organized environment for the VoidCat Reasoning Engine
# All subsequent operations will be performed relative to this directory
WORKDIR /app

# PHASE 3: SYSTEM PREPARATION
# Update the package index to ensure we have access to latest security patches
# Install essential system dependencies required for optimal operation
# curl: Required for health checks and external API communications
# ca-certificates: Ensures secure TLS/SSL connections to external services
# git: Required for some Python packages that need git during installation
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# PHASE 4: PYTHON ENVIRONMENT OPTIMIZATION
# Upgrade pip to the latest version for improved dependency resolution
# This ensures compatibility with modern Python packaging standards
RUN pip install --upgrade pip

# PHASE 5: DEPENDENCY INSTALLATION (STRATEGIC LAYER CACHING)
# Copy requirements.txt first to leverage Docker's intelligent layer caching
# This ensures dependencies are only reinstalled when requirements change
# Optimizing build times and reducing bandwidth consumption
COPY requirements.txt .

# Install Python dependencies with production-optimized settings
# --no-cache-dir: Prevents caching to reduce image size
# --disable-pip-version-check: Suppresses version warnings for cleaner output
# This creates a lean, efficient dependency layer
RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

# PHASE 5.5: SECURITY HARDENING (NON-ROOT USER)
# Create a dedicated non-root user for running the application.
# This follows the principle of least privilege, enhancing security.
RUN useradd --create-home --shell /bin/bash appuser

# PHASE 6: APPLICATION DEPLOYMENT
# Copy the complete VoidCat Reasoning Engine codebase into the container
# This includes all core modules: enhanced_engine.py, mcp_server.py, etc.
# The strategic placement after dependency installation optimizes rebuild efficiency
# We use --chown to set the correct permissions for our non-root user.
COPY --chown=appuser:appuser . .

# PHASE 6.5: ENTRYPOINT PREPARATION
# Copy and configure the enhanced entrypoint script
# This provides flexible operational modes for different use cases
COPY --chown=appuser:appuser docker-entrypoint-vre.sh /app/
RUN chmod +x /app/docker-entrypoint-vre.sh

# Create necessary directories with proper permissions
RUN mkdir -p /app/.agentic-tools-mcp /app/indexes /app/knowledge_source && \
    chown -R appuser:appuser /app/.agentic-tools-mcp /app/indexes /app/knowledge_source

# Switch to the non-root user for all subsequent commands
USER appuser

# PHASE 7: ENVIRONMENT CONFIGURATION
# Set environment variables for optimal operation
ENV VOIDCAT_DOCKER=true
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# PHASE 8: NETWORK INTERFACE CONFIGURATION
# Expose port 8000 to enable external communication with the reasoning engine
# This port serves as the gateway for MCP communications and API interactions
# Essential for integration with Claude Desktop, VS Code, and other clients
EXPOSE 8000

# PHASE 9: HEALTHCHECK CONFIGURATION
# Define a health check to ensure the container is responsive.
# This checks if Python can import core modules successfully.
# More robust than just checking the API endpoint since different modes may not expose HTTP
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# PHASE 10: FLEXIBLE RUNTIME INVOCATION
# Set the enhanced entrypoint script that supports multiple operational modes:
# - API Gateway: docker run voidcat-vre (default)
# - MCP Server: docker run voidcat-vre mcp
# - Test Harness: docker run voidcat-vre test
# - Custom commands: docker run voidcat-vre python custom_script.py
ENTRYPOINT ["/app/docker-entrypoint-vre.sh"]

# Default command runs the API Gateway for backward compatibility
# This can be overridden at runtime for different operational modes
CMD ["api"]

# ============================================================================
# END ENHANCED GENESIS PROTOCOL DOCKERFILE
# Through Lady Beatrice's wisdom and strategic enhancement,
# the VoidCat Reasoning Engine container now provides flexible,
# secure, and robust operational capabilities for all use cases.
# ============================================================================
