# 🐾 VoidCat Reasoning Core

## Advanced RAG-Enhanced Reasoning Engine with Strategic Intelligence

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Overview

VoidCat Reasoning Core is a sophisticated Retrieval-Augmented Generation (RAG) engine designed for intelligent document analysis and query processing. Built with enterprise-grade architecture, it combines TF-IDF vectorization with OpenAI's reasoning models to deliver precise, context-aware responses.

## ✨ Features

### 🧠 Intelligent RAG Processing

- **Document Vectorization**: Advanced TF-IDF-based document embedding
- **Context Retrieval**: Cosine similarity matching for optimal relevance
- **Multi-Document Support**: Seamless processing of extensive knowledge bases
- **Adaptive Ranking**: Dynamic document ranking based on query relevance

### 🚀 Production-Ready API

- **FastAPI Framework**: High-performance async API with automatic documentation
- **RESTful Endpoints**: Clean, intuitive API design
- **Error Handling**: Comprehensive error management and graceful degradation
- **Health Monitoring**: Built-in status endpoints for system monitoring

### 🛡️ Enterprise Architecture

- **Modular Design**: Clean separation of concerns with scalable components
- **Environment Configuration**: Secure API key management with dotenv
- **Async Processing**: Non-blocking operations for optimal performance
- **Type Safety**: Pydantic models for request/response validation

## 🏗️ Architecture

```text
VoidCat Reasoning Core
├── 📄 engine.py           # Core RAG engine with vectorization
├── 🌐 api_gateway.py      # FastAPI web service layer
├── 📁 knowledge_source/   # Document knowledge base
├── 🔧 main.py            # Entry point and utilities
└── ⚙️ pyproject.toml     # Project configuration
```

### Core Components

#### 🎯 VoidCatEngine (engine.py)

The heart of the system, providing:

- **Knowledge Base Loading**: Automatic markdown document ingestion
- **TF-IDF Vectorization**: Scientific document similarity calculation
- **Context Retrieval**: Intelligent document chunk selection
- **OpenAI Integration**: Enhanced prompt construction and API communication

#### 🌐 API Gateway (api_gateway.py)

Production-ready web service featuring:

- **Async Lifespan Management**: Efficient resource initialization
- **Query Processing Endpoint**: `/query` for reasoning requests
- **Health Check Endpoint**: `/` for system status monitoring
- **Error Handling**: Comprehensive exception management

## 🚀 Quick Start

### Prerequisites

- **Python 3.13+**
- **OpenAI API Key**
- **Virtual Environment** (recommended)

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/voidcat-reasoning-core.git
   cd voidcat-reasoning-core
   ```

2. **Create Virtual Environment**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/macOS
   ```

3. **Install Dependencies**

   ```bash
   pip install -e .
   # Or using uv (recommended):
   uv pip install -e .
   ```

4. **Environment Configuration**

   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

5. **Add Knowledge Base**

   Place your markdown documents in the `knowledge_source/` directory.

### 🏃‍♂️ Running the System

#### Option 1: API Server (Recommended)

```bash
uvicorn api_gateway:app --reload --host 0.0.0.0 --port 8000
```

#### Option 2: Direct Engine Testing

```bash
python main.py
```

### 📡 API Usage

#### Query Endpoint

```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "What are the core MCP primitives?", "model": "gpt-4o-mini"}'
```

#### Health Check

```bash
curl http://localhost:8000/
```

## 📚 API Documentation

Once running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Request Schema

```json
{
  "query": "string",      // Required: Your question or prompt
  "model": "string"       // Optional: OpenAI model (default: gpt-4o-mini)
}
```

### Response Schema

```json
{
  "response": "string"    // AI-generated response with RAG context
}
```

## 🔧 Configuration

### Environment Variables

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### Knowledge Base Setup

1. Create markdown files in `knowledge_source/`
2. The engine automatically loads all `.md` files
3. Supports hierarchical document organization
4. Real-time document updates (restart required)

## 🧪 Testing

### Validation Test Suite

```bash
# Run comprehensive validation
python main.py

# Expected output:
# Engine Initializing: Loading knowledge base...
# Engine Initialized: Successfully loaded X document(s).
# Executing query: 'What are the core MCP primitives...'
# [Engine response with RAG-enhanced content]
```

### API Testing

```bash
# Start the server
uvicorn api_gateway:app --reload

# Test in another terminal
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "Test query"}'
```

## 🏗️ Development

### Project Structure

```text
voidcat-reasoning-core/
├── 📄 README.md              # This comprehensive documentation
├── 📄 LICENSE                # MIT License
├── 📄 .gitignore            # Git ignore patterns
├── 📄 pyproject.toml        # Project dependencies and metadata
├── 📄 requirements.txt      # Pip-compatible requirements
├── 📁 .venv/               # Virtual environment (local)
├── 📁 knowledge_source/    # Document knowledge base
│   └── 📄 *.md            # Markdown knowledge documents
├── 🐍 main.py             # Entry point and testing utilities
├── 🐍 engine.py           # Core RAG reasoning engine
├── 🐍 api_gateway.py      # FastAPI web service
└── 📁 __pycache__/        # Python cache (auto-generated)
```

### Dependencies

```toml
[project.dependencies]
httpx = ">=0.28.1"          # Async HTTP client
python-dotenv = ">=1.1.1"   # Environment management
scikit-learn = ">=1.7.0"    # TF-IDF vectorization
numpy = ">=2.3.1"           # Numerical computations
fastapi = ">=0.104.1"       # Web framework
uvicorn = ">=0.24.0"        # ASGI server
```

### Code Quality Standards

- **Type Hints**: Comprehensive typing throughout
- **Docstrings**: Clear documentation for all functions
- **Error Handling**: Graceful degradation and informative errors
- **Async Support**: Non-blocking operations where beneficial
- **Modular Design**: Clean separation of concerns

## 🔍 Advanced Usage

### Custom Knowledge Base

```python
from engine import VoidCatEngine

# Initialize with custom knowledge directory
engine = VoidCatEngine(knowledge_dir="custom_knowledge")

# Query the engine
response = await engine.query("Your question here")
```

### Multiple Document Retrieval

```python
# Retrieve top 3 most relevant documents
context = engine._retrieve_context("query", top_k=3)
```

### Custom OpenAI Models

```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "Complex reasoning task", "model": "gpt-4"}'
```

## 🛡️ Security Considerations

- **API Key Protection**: Never commit API keys to version control
- **Environment Isolation**: Use virtual environments for dependency management
- **Input Validation**: Pydantic models ensure request data integrity
- **Error Sanitization**: No sensitive information in error responses

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork the Repository**
2. **Create Feature Branch**: `git checkout -b feature/amazing-feature`
3. **Commit Changes**: `git commit -m 'Add amazing feature'`
4. **Push to Branch**: `git push origin feature/amazing-feature`
5. **Open Pull Request**

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/voidcat-reasoning-core.git

# Install in development mode
pip install -e ".[dev]"

# Run tests
python main.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI**: For providing the reasoning model APIs
- **FastAPI**: For the exceptional web framework
- **scikit-learn**: For robust machine learning utilities
- **The Open Source Community**: For continuous inspiration and support

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/voidcat-reasoning-core/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/voidcat-reasoning-core/discussions)
- **Email**: support@voidcat-reasoning.com

---

*Built with ❤️ and strategic foresight for the AI community*

**VoidCat Reasoning Core** - *Where Intelligence Meets Precision*
