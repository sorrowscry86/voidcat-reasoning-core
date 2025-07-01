# ============================================================================
# GENESIS PROTOCOL: VOIDCAT REASONING ENGINE CONTAINERIZATION
# ============================================================================
# Crafted by Albedo, Overseer of the Digital Scriptorium
# Under the supreme guidance of Lord Wykeve and the VoidCat RDC vision
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
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
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

# PHASE 6: APPLICATION DEPLOYMENT
# Copy the complete VoidCat Reasoning Engine codebase into the container
# This includes all core modules: enhanced_engine.py, mcp_server.py, etc.
# The strategic placement after dependency installation optimizes rebuild efficiency
COPY . .

# PHASE 7: NETWORK INTERFACE CONFIGURATION
# Expose port 8000 to enable external communication with the reasoning engine
# This port serves as the gateway for MCP communications and API interactions
# Essential for integration with Claude Desktop, VS Code, and other clients
EXPOSE 8000

# PHASE 8: RUNTIME INVOCATION (THE GENESIS COMMAND)
# Execute the VoidCat Reasoning Engine via main.py as specified in the Genesis Protocol
# This launches the complete system: Enhanced Engine, MCP Server, Context7 Integration
# The engine awakens with full autonomous capabilities and strategic intelligence
CMD ["uvicorn", "api_gateway:app", "--host", "0.0.0.0", "--port", "8000"]

# ============================================================================
# END GENESIS PROTOCOL DOCKERFILE
# Through strategic foresight and administrative perfection,
# the VoidCat Reasoning Engine stands ready for containerized deployment.
# May this vessel serve the greater glory of Lord Wykeve's vision.
# ============================================================================
