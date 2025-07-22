---
description: Repository Information Overview
alwaysApply: true
---

# VoidCat Reasoning Core Information

## Summary
VoidCat Reasoning Core (VRE) is a sophisticated AI-driven engine designed for strategic intelligence and automation tasks. It leverages advanced language models through a RAG (Retrieval Augmented Generation) architecture to provide context-aware responses with memory integration. The system is containerized with Docker for consistent deployment and includes a FastAPI-based API gateway.

## Structure
- **Root**: Core Python modules, configuration files, and documentation
- **knowledge_source/**: Directory containing knowledge base documents
- **vscode-extension/**: VS Code extension for integration with the engine
- **memory_retrieval/**: Memory retrieval and storage components
- **.agentic-tools-mcp/**: Memory and task storage for the MCP system
- **indexes/**: Vector indexes for document retrieval
- **projects/**: Project-specific configurations and resources
- **tasks/**: Task definitions and workflows

## Projects

### Core Engine

#### Language & Runtime
**Language**: Python
**Version**: Python 3.13 (development), Python 3.11 (Docker)
**Build System**: Hatchling
**Package Manager**: pip

#### Dependencies
**Main Dependencies**:
- httpx (≥0.28.1): Async HTTP client
- fastapi (≥0.104.1): API framework
- uvicorn (≥0.24.0): ASGI server
- pydantic (≥2.11.7): Data validation
- scikit-learn (≥1.7.0): ML utilities for TF-IDF
- numpy (≥2.3.1): Numerical computing
- python-dotenv (≥1.1.1): Environment variables
- openai (≥1.0.0): OpenAI API client
- PyPDF2 (3.0.0): PDF processing
- slowapi (≥0.1.7): Rate limiting

#### Build & Installation
```bash
# Set up environment
cp .env.example .env
# Edit .env to add API keys

# Install dependencies
pip install -r requirements.txt

# Run test harness
python main.py

# Start API server
uvicorn api_gateway:app --host 0.0.0.0 --port 8000
```

#### Docker
**Dockerfile**: Uses Python 3.11-slim base image
**Configuration**: Non-root user (appuser) for security
**Ports**: Exposes port 8000
**Run Command**:
```bash
docker build -t voidcat-reasoning-core .
docker run --env-file .env -p 8000:8000 voidcat-reasoning-core
```
**Docker Compose**:
```bash
docker-compose up
```

#### Main Components
- **engine.py/enhanced_engine.py**: Core reasoning engines
- **api_gateway.py**: FastAPI server with health checks and query endpoints
- **mcp_server.py**: Model Control Protocol server
- **voidcat_memory_integration.py**: Memory system integration
- **hybrid_vectorizer.py**: Advanced document vectorization
- **sequential_thinking.py**: Sequential reasoning implementation
- **voidcat_task_models.py**: Task definition and processing models
- **voidcat_persistence.py**: Data persistence layer
- **voidcat_operations.py**: Core operations and utilities
- **voidcat_context_integration.py**: Context integration system
- **voidcat_memory_models.py**: Memory data models
- **voidcat_memory_retrieval.py**: Memory retrieval system
- **voidcat_memory_search.py**: Memory search capabilities
- **voidcat_memory_storage.py**: Memory storage system
- **multi_format_processor.py**: Multi-format document processing

#### Testing
**Framework**: pytest with pytest-asyncio
**Test Location**: Root directory (test_*.py files)
**Test Categories**:
- Basic Components: task models, persistence, operations
- Comprehensive E2E: advanced scenarios, stress testing
- API Components: engine integration tests
- Memory Integration: memory system validation
- MCP Integration: Model Control Protocol testing
**Run Command**:
```bash
pytest
# Run specific E2E tests
pytest test_e2e_basic_components.py -v
```

### VS Code Extension

#### Language & Runtime
**Language**: TypeScript + Python
**Version**: TypeScript 5.0.0+, Python 3.13
**Build System**: npm
**Package Manager**: npm

#### Dependencies
**Main Dependencies**:
- axios (^1.4.0): HTTP client
- ws (^8.13.0): WebSocket client

**Development Dependencies**:
- @types/vscode (^1.85.0): VS Code type definitions
- @types/ws (^8.5.0): WebSocket type definitions
- typescript (^5.0.0): TypeScript compiler
- eslint (^8.0.0): Code linting

#### Build & Installation
```bash
cd vscode-extension
npm install
npm run compile
```

#### Main Components
- **extension.ts**: Main extension entry point
- **EngineDiagnosticsPanel.ts**: Diagnostics panel implementation
- **src/commands/**: Command implementations
- **api_integration.py**: Python API integration
- **backend_integration_api.py**: Backend integration API
- **security_config.py**: Security configuration

## Entry Points
- **main.py**: Test harness and system validation
- **api_gateway.py**: FastAPI application (uvicorn api_gateway:app)
- **voidcat_launcher.py**: System launcher script
- **deploy_enhanced.py**: Enhanced system deployment
- **launch_voidcat.bat/.sh**: Platform-specific launch scripts

## CI/CD
**Workflows**:
- test.yml: Runs tests on push/PR to main/enhanced branches
- docker-publish.yml: Builds and publishes Docker image to GitHub Container Registry
- security-scan.yml: Security scanning for vulnerabilities

## Environment Configuration
**Required Environment Variables**:
- OPENAI_API_KEY: OpenAI API key for model access
- Additional configuration in .env.example

## Security Features
- Non-root Docker user
- Rate limiting via slowapi
- Input validation with Pydantic
- Comprehensive error handling
- Security audit capabilities (security_audit.py)


