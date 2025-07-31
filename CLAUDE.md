# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VoidCat Reasoning Core (VRE) is an advanced AI-driven reasoning engine that combines RAG (Retrieval-Augmented Generation) capabilities with OpenAI's reasoning models. It provides a comprehensive MCP (Model Context Protocol) server for Claude Desktop integration and a production-ready FastAPI gateway with 31+ AI reasoning tools.

## Core Architecture

### Main Engines
- **`engine.py`**: Base RAG engine with TF-IDF vectorization and multi-format document processing
- **`enhanced_engine.py`**: Advanced engine with Context7 integration, Sequential Thinking, and multi-provider API support
- **`sequential_thinking.py`**: Multi-branch structured reasoning capabilities
- **`context7_integration.py`**: Advanced context retrieval with relevance scoring

### Server Components  
- **`mcp_server.py`**: Primary MCP server with 31+ reasoning tools for Claude Desktop integration
- **`api_gateway.py`**: FastAPI-based HTTP gateway with health checks and query endpoints
- **`fastmcp_server.py`**: Enhanced MCP server implementation with improved performance

### Memory and Persistence
- **`voidcat_memory_*.py`**: Persistent memory system with semantic search and intelligent archiving
- **`voidcat_persistence.py`**: Task and project data persistence layer  
- **`voidcat_task_models.py`**: Pydantic models for tasks and projects
- **`hybrid_vectorizer.py`**: Advanced document vectorization with scientific similarity calculation

## Common Development Commands

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Development installation (enables global commands)
pip install -e .

# Create environment from template
cp .env.example .env
# Edit .env to add API keys
```

### Running the System
```bash
# Run system validation
python main.py
python validate_system.py

# Start API gateway
uvicorn api_gateway:app --host 127.0.0.1 --port 8000 --reload

# Start MCP server for Claude Desktop
python mcp_server.py

# Available global commands after pip install -e .
voidcat-mcp                 # Start MCP server
voidcat-reasoning          # Alternative MCP entry point
```

### Testing
```bash
# Run all tests
pytest

# Run specific test categories
pytest test_mcp_tools.py                     # MCP server functionality
pytest test_persistence.py                   # Data persistence
pytest test_enhanced_engine_integration.py   # Enhanced engine features
pytest test_e2e_basic_components.py         # End-to-end testing

# Run with coverage
pytest --cov=.
```

### Code Quality (run before commits)
```bash
black .
isort .
flake8 .
mypy .
```

### Docker Operations
```bash
# Build image
docker build -t voidcat-reasoning-core .

# Run API mode
docker run --env-file .env -p 8000:8000 voidcat-reasoning-core

# Run MCP mode with compose
docker-compose --profile mcp up voidcat-mcp

# Development mode
docker-compose --profile development up voidcat-dev
```

## Environment Configuration

### Required API Keys (.env file)
The system uses a 3-tier fallback strategy for maximum reliability:

```ini
# Primary API (cost-effective, high performance)
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Secondary fallback (reliable, multiple models)  
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Tertiary fallback (premium option)
OPENAI_API_KEY=your_openai_api_key_here
```

### Recommended OpenRouter Models
- `deepseek/deepseek-r1-0528:free`
- `deepseek/deepseek-r1:free` 
- `tngtech/deepseek-r1t2-chimera:free`
- `qwen/qwen3-235b-a22b-07-25:free`
- `google/gemini-2.0-flash-exp:free`

## Claude Desktop MCP Integration

### Configuration Location
**Windows**: `C:\Users\[Username]\AppData\Roaming\Claude\claude_desktop_config.json`

### Basic MCP Server Setup
```json
{
    "mcpServers": {
        "voidcat-reasoning-core": {
            "command": "python",
            "args": ["mcp_server.py"],
            "workingDirectory": "D:\\path\\to\\voidcat-reasoning-core",
            "env": {
                "DEEPSEEK_API_KEY": "your_deepseek_key_here",
                "OPENROUTER_API_KEY": "your_openrouter_key_here",
                "OPENAI_API_KEY": "your_openai_key_here"
            }
        }
    }
}
```

## Available VoidCat Tools (31 total)

### Core Reasoning
- `voidcat_query`: Basic RAG processing with TF-IDF retrieval
- `voidcat_enhanced_query`: Full pipeline (Sequential Thinking + Context7 + RAG)
- `voidcat_sequential_thinking`: Multi-branch structured reasoning
- `voidcat_ultimate_enhanced_query`: 85% performance boost with parallel processing
- `voidcat_status`: Comprehensive system diagnostics and health monitoring

### Memory Management
- `voidcat_store_memory`: Persistent storage with semantic indexing
- `voidcat_search_memory`: Semantic search and retrieval
- `voidcat_analyze_knowledge`: Knowledge base exploration and insights
- `voidcat_configure_engine`: Runtime configuration management

### Task & Project Management
- `voidcat_create_task`: Task creation with intelligent categorization
- `voidcat_update_task`: Task modification and status tracking
- `voidcat_list_tasks`: Task retrieval with filtering and sorting
- `voidcat_create_project`: Project initialization and setup

### Advanced Integration Tools
- `voidcat_enhanced_query_with_sequential`: Direct Sequential Thinking access
- `voidcat_enhanced_query_with_context7`: Advanced context retrieval with relevance scoring

## Development Guidelines

### Code Standards
- **Python 3.13** for development, **Python 3.11** for Docker
- **Black** formatting (line length: 88)
- **Type hints required** for all public functions
- **No comments** unless explicitly requested
- **MCP compatibility**: Always log to stderr, never stdout

### Windows-Specific Requirements
```python
# Required for Windows asyncio compatibility
if sys.platform == 'win32':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
```

### Testing Strategy
- **Unit tests**: Individual component testing
- **Integration tests**: Engine interaction validation  
- **E2E tests**: Complete workflow verification
- **Memory tests**: Persistence and retrieval validation

### Error Handling Philosophy
- Comprehensive try-catch blocks in all MCP server startup code
- Graceful degradation when APIs unavailable
- Detailed error logging to stderr for debugging
- Health checks and diagnostic endpoints

## Project Structure Insights

### Core Directories
- **`voidcat_reasoning_core/`**: Main Python package with engine components
- **`vscode-extension/`**: TypeScript-based VS Code integration
- **`knowledge_source/`**: Markdown knowledge base documents
- **`.agentic-tools-mcp/`**: Memory and task storage for MCP system
- **`indexes/`**: Vector indexes for document retrieval

### Key Entry Points
- **`main.py`**: Test harness and system validation
- **`api_gateway.py`**: FastAPI application entry
- **`mcp_server.py`**: MCP server for Claude Desktop
- **`voidcat_launcher.py`**: Unified system launcher

## VS Code Extension Integration

The project includes a comprehensive VS Code extension with:
- Dashboard panels for system monitoring
- Task management interfaces  
- Memory browser capabilities
- Code analysis providers
- Engine diagnostics panels

### Extension Development
```bash
cd vscode-extension
npm install
npm run compile
vsce package
code --install-extension voidcat-reasoning-core-0.2.0.vsix
```

## Docker Architecture

### Operational Modes
The enhanced Docker setup supports multiple operational modes:
- **`api`**: FastAPI gateway mode
- **`mcp`**: MCP server mode for Claude Desktop
- **`test`**: Test harness execution  
- **`diagnostics`**: System health validation
- **`cache`**: Redis diagnostics (with redis-tools support)

### Security Features
- Non-root Docker user (`voidcat`)
- Rate limiting via slowapi
- Input validation with Pydantic models
- Comprehensive error handling and sanitization
- Local-only MCP server operation (127.0.0.1)

## Performance Optimization

### Model Selection Strategy
- **`gpt-4o-mini`**: Quick lookups, established patterns
- **`gpt-4o`**: Complex analysis, architecture decisions
- **`deepseek-chat`**: Cost-effective bulk processing

### Caching and Memory
- Intelligent context caching to avoid redundant API calls
- Semantic similarity matching for query optimization  
- Memory archiving with intelligent retrieval
- Cross-session persistence with JSON-based storage

## Production Considerations

### Health Monitoring
- Built-in health check endpoints (`/` and `/health`)
- System diagnostics via `voidcat_status` tool
- Comprehensive error reporting and logging
- Multi-tier API fallback system

### Security Best Practices
- Never commit API keys to version control
- Environment variable management via .env files
- No sensitive information in error responses
- Secure local-only operation for MCP servers

### Global Package Installation
After running `pip install -e .`, these commands become globally available:
- `voidcat-mcp`: Start MCP server
- `voidcat-mcp-server`: Alternative MCP server command  
- `voidcat-reasoning`: Main reasoning entry point