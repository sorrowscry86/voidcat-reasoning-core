# 🐾 VoidCat Reasoning Core

## Advanced RAG-Enhanced Reasoning Engine with Strategic Intelligence

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The VoidCat Reasoning Core (VRE) is a sophisticated AI-driven engine designed for strategic intelligence and automation tasks. It combines advanced RAG (Retrieval-Augmented Generation) capabilities with OpenAI's reasoning models and is deployed as a production-ready containerized solution.

## ✨ Features

### 🧠 Intelligent RAG Processing
- **Advanced TF-IDF Vectorization**: Scientific document similarity calculation
- **Context-Aware Retrieval**: Intelligent document chunk selection for optimal relevance
- **Multi-Document Support**: Seamless processing of extensive knowledge bases
- **Enhanced Memory Integration**: Persistent memory system with intelligent archiving

### 🚀 Production-Ready API
- **FastAPI Framework**: High-performance async API with automatic documentation
- **MCP Server Integration**: Full Model Context Protocol support for Claude Desktop
- **Comprehensive Error Handling**: Robust error management and graceful degradation
- **Health Monitoring**: Built-in status endpoints and system diagnostics

### 🛡️ Enterprise Architecture
- **Modular Design**: Clean separation of concerns with scalable components
- **Enhanced Engine**: Multi-branch sequential thinking with Context7 integration
- **Containerized Deployment**: Docker support for consistent and portable deployments
- **Automated CI/CD**: GitHub Actions integration for continuous deployment

### 🎯 Advanced Tools Available
- `voidcat_query`: Basic RAG processing
- `voidcat_enhanced_query`: Full enhanced pipeline with sequential thinking
- `voidcat_sequential_thinking`: Pure sequential reasoning capabilities
- `voidcat_status`: Comprehensive system diagnostics
- `voidcat_analyze_knowledge`: Knowledge base analysis
- `voidcat_configure_engine`: Runtime configuration management

## Prerequisites

- [Docker](https://www.docker.com/get-started) (recommended)
- [Python 3.13+](https://www.python.org/downloads/)
- OpenAI API Key

## 🚀 Quick Start

### Option 1: Docker Deployment (Recommended)

1. **Clone the Repository**
```bash
git clone https://github.com/sorrowscry86/voidcat-reasoning-core.git
cd voidcat-reasoning-core
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

3. **Build and Run**
```bash
docker build -t voidcat-reasoning-core .
docker run --env-file .env -p 8000:8000 voidcat-reasoning-core
```

### Option 2: Local Development

1. **Set Up Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Environment**
```bash
cp .env.example .env
# Add your OpenAI API key to .env
```

4. **Run the Application**
```bash
python main.py
```

## 🔧 System Validation

Verify your installation:

```bash
python validate_system.py
```

This will check:
- ✅ Enhanced Engine initialization
- ✅ MCP Server functionality  
- ✅ Sequential Thinking Engine
- ✅ Context7 Engine
- ✅ Environment configuration

## 📚 API Usage

### Query Endpoint
```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "What are the core MCP primitives?", "model": "gpt-4o-mini"}'
```

### Health Check
```bash
curl http://localhost:8000/
```

## 🔗 Claude Desktop Integration

For complete MCP integration with Claude Desktop, see [MCP_INTEGRATION.md](MCP_INTEGRATION.md).

Quick setup:
1. Add configuration to `claude_desktop_config.json`
2. Set your OpenAI API key
3. Restart Claude Desktop
4. Access VoidCat tools in Claude conversations

## 🧪 Recent Improvements

### Version 2.0.0 - Enhanced Production Release
- ✅ **Import Error Resolution**: Fixed VoidCatStorage implementation
- ✅ **Dependency Updates**: All packages updated to latest versions
- ✅ **Enhanced Architecture**: Improved memory integration and context processing
- ✅ **Production Readiness**: Comprehensive error handling and system validation
- ✅ **MCP Compatibility**: Full Claude Desktop integration support

## 🛡️ Security & Performance

- **API Key Protection**: Secure environment variable management
- **Input Validation**: Comprehensive request validation with Pydantic
- **Error Sanitization**: No sensitive information in error responses
- **Concurrent Processing**: Optimized for multi-user environments
- **Memory Management**: Intelligent caching and resource optimization

## 📊 System Status

**Current Status**: ✅ **Production Ready**
- Core system validation: **100% Pass**
- Integration tests: **All Passing**
- Dependencies: **Up to Date**
- Security audit: **Complete**

*The VoidCat Reasoning Core exemplifies strategic foresight and technical excellence, ensuring reliable operation and seamless integration with Claude Desktop's MCP ecosystem.*