# VoidCat Reasoning Core - Comprehensive Documentation

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Installation & Setup](#installation--setup)
4. [Core Components](#core-components)
5. [API Reference](#api-reference)
6. [Memory System](#memory-system)
7. [MCP Integration](#mcp-integration)
8. [Testing](#testing)
9. [Deployment](#deployment)
10. [Troubleshooting](#troubleshooting)

## 🎯 System Overview

The **VoidCat Reasoning Core (VRE)** is a sophisticated AI-driven engine designed for strategic intelligence and automation tasks. It leverages advanced language models and provides a comprehensive reasoning framework with memory integration, MCP (Model Context Protocol) support, and enhanced RAG capabilities.

### Key Features
- **AI-Powered Reasoning**: Advanced language model integration
- **Memory System**: Persistent, context-aware memory with user preferences
- **MCP Protocol**: Full Model Context Protocol compliance
- **Enhanced RAG**: Multi-layer reasoning with context retrieval
- **Sequential Thinking**: Multi-stage reasoning with complexity assessment
- **Context7 Integration**: Advanced context analysis and retrieval
- **Docker Support**: Containerized deployment ready

## 🏗️ Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    VoidCat Reasoning Core                   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   API Gateway   │  │  Enhanced Engine│  │   Memory    │ │
│  │   (FastAPI)     │  │   (Pipeline)    │  │  Integration│ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │  MCP Server     │  │  RAG Engine     │  │  Context7   │ │
│  │  (Protocol)     │  │  (Retrieval)    │  │  Integration│ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow
1. **Query Input**: User query received via API or MCP
2. **Memory Enhancement**: Query enhanced with user context and preferences
3. **Complexity Assessment**: Query complexity and type analysis
4. **Multi-layer Reasoning**: Sequential thinking and context retrieval
5. **Response Generation**: AI-powered response with memory integration
6. **Learning Update**: Response processed for memory learning

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- Docker (optional)
- OpenAI API key or DeepSeek API key

### Quick Start
```bash
# Clone repository
git clone https://github.com/sorrowscry86/voidcat-reasoning-core.git
cd voidcat-reasoning-core

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Run test harness
python main.py

# Start API server
uvicorn api_gateway:app --reload
```

### Docker Setup
```bash
# Build image
docker build -t voidcat-reasoning-core .

# Run container
docker run --env-file .env -p 8000:8000 voidcat-reasoning-core
```

## 🔧 Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_openai_key
# OR
DEEPSEEK_API_KEY=your_deepseek_key

# Optional
WORKING_DIRECTORY=/path/to/working/dir
USER_ID=default_user
LOG_LEVEL=INFO
```

### MCP Server Configuration
Add to Claude Desktop config:
```json
{
  "mcpServers": {
    "voidcat-reasoning-core": {
      "command": "python",
      "args": ["path/to/mcp_server.py"],
      "env": {
        "OPENAI_API_KEY": "your_key"
      }
    }
  }
}
```

## 🎯 Core Components

### 1. Enhanced Engine (`enhanced_engine.py`)
The main reasoning engine with memory integration.

**Key Methods:**
- `query()`: Main query interface
- `_enhanced_reasoning_pipeline()`: Multi-stage reasoning
- `get_comprehensive_diagnostics()`: System diagnostics

### 2. Memory System (`voidcat_memory_*`)
Persistent memory with user preferences and context.

**Features:**
- User preference storage
- Conversation history
- Behavioral insights
- Task context tracking

### 3. MCP Server (`mcp_server.py`)
Full MCP protocol implementation.

**Available Tools:**
- `voidcat_query`: Basic RAG processing
- `voidcat_enhanced_query`: Full enhanced pipeline
- `voidcat_sequential_thinking`: Pure reasoning analysis
- `voidcat_status`: System diagnostics

### 4. API Gateway (`api_gateway.py`)
FastAPI-based REST API.

**Endpoints:**
- `POST /query`: Process queries
- `GET /status`: System status
- `GET /docs`: API documentation

## 📚 API Reference

### Core Engine API

#### `query(user_query: str, **kwargs) -> str`
Process a user query through the enhanced reasoning pipeline.

**Parameters:**
- `user_query`: The user's input query
- `model`: AI model to use (default: deepseek-chat)
- `top_k`: Number of context items (default: 2)
- `session_id`: Session identifier

**Example:**
```python
engine = VoidCatEnhancedEngine()
response = await engine.query(
    "Explain quantum computing",
    model="gpt-4",
    session_id="user_session_123"
)
```

### MCP Tools

#### `voidcat_enhanced_query`
Full enhanced pipeline with memory integration.

**Usage:**
```json
{
  "name": "voidcat_enhanced_query",
  "arguments": {
    "query": "What is the meaning of life?",
    "model": "deepseek-chat",
    "enable_enhanced": true
  }
}
```

## 🧠 Memory System

### Architecture
The memory system provides persistent, context-aware storage with:

- **User Preferences**: Personalized settings and behaviors
- **Conversation History**: Recent interactions and topics
- **Behavioral Insights**: Usage patterns and preferences
- **Task Context**: Active projects and ongoing work

### Usage
```python
# Get user preferences
preferences = await engine.get_user_preferences()

# Set preference
await engine.set_user_preference("response_style", "detailed")

# Get conversation history
history = await engine.get_conversation_history(limit=5)
```

## 🔍 Testing

### Running Tests
```bash
# Run all tests
python test_enhanced_system.py

# Run specific test
python test_e2e_complete_system.py

# Run memory tests
python test_memory_integration.py
```

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **E2E Tests**: End-to-end workflow testing
- **Memory Tests**: Memory system validation

## 🚀 Deployment

### Production Deployment
```bash
# Build production image
docker build -t voidcat-prod .

# Deploy with environment variables
docker run -d \
  --name voidcat-prod \
  --env-file .env \
  -p 80:8000 \
  voidcat-prod
```

### Environment-Specific Configurations
- **Development**: Local setup with debug logging
- **Staging**: Test environment with limited data
- **Production**: Optimized configuration with monitoring

## 🔧 Troubleshooting

### Common Issues

#### API Key Issues
```
Error: API key not configured
```
**Solution:** Set OPENAI_API_KEY or DEEPSEEK_API_KEY in .env file

#### Memory Storage Issues
```
Error: Memory storage not accessible
```
**Solution:** Check WORKING_DIRECTORY permissions and disk space

#### MCP Connection Issues
```
Error: MCP server not responding
```
**Solution:** Verify MCP configuration and restart Claude Desktop

### Debug Mode
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Performance Monitoring

### Metrics
- Query processing time
- Memory usage
- API response times
- Error rates

### Monitoring Setup
```python
# Enable diagnostics
engine = VoidCatEnhancedEngine()
diagnostics = engine.get_comprehensive_diagnostics()
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

### Code Style
- Follow PEP 8
- Add type hints
- Include docstrings
- Write tests

## 📄 License
MIT License - see LICENSE file for details

## 📞 Support
- GitHub Issues: [Create issue](https://github.com/sorrowscry86/voidcat-reasoning-core/issues)
- Documentation: [View docs](http://localhost:8000/docs)
- Community: [Discussions](https://github.com/sorrowscry86/voidcat-reasoning-core/discussions)
