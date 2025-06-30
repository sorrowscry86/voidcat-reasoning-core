# 🔗 VoidCat Reasoning Core - Claude Desktop MCP Integration

## Strategic Integration Guide for Model Context Protocol (MCP)

Through strategic foresight and systematic precision, this guide provides comprehensive instructions for integrating VoidCat Reasoning Core as an MCP server with Claude Desktop.

---

## 🎯 Claude Desktop Configuration

### Primary Configuration File Location
**Windows**: `C:\Users\[Username]\AppData\Roaming\Claude\claude_desktop_config.json`

### Complete Configuration Example

```json
{
    "mcpServers": {
        "voidcat-reasoning-core": {
            "command": "uvicorn",
            "args": [
                "api_gateway:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
                "--reload"
            ],
            "workingDirectory": "P:\\voidcat-reasoning-core\\",
            "env": {
                "OPENAI_API_KEY": "your_openai_api_key_here"
            }
        },
        "playwright": {
            "command": "npx",
            "args": [
                "@playwright/mcp@latest"
            ]
        },
        "filesystem": {
            "command": "npx",
            "args": [
                "-y",
                "@modelcontextprotocol/server-filesystem",
                "C:\\Users\\Wykeve",
                "P:\\",
                "D:\\"
            ]
        },
        "memory": {
            "command": "npx",
            "args": [
                "-y",
                "@modelcontextprotocol/server-memory"
            ]
        },
        "context7": {
            "command": "npx",
            "args": [
                "-y",
                "@upstash/context7-mcp@latest"
            ]
        },
        "hyperbrowser": {
            "command": "npx",
            "args": [
                "hyperbrowser-mcp"
            ],
            "env": {
                "HYPERBROWSER_API_KEY": "hb_9a9ef90d6c46f084a8602ff24378"
            }
        },
        "everything": {
            "command": "npx",
            "args": [
                "-y",
                "@modelcontextprotocol/server-everything"
            ]
        },
        "MCP_DOCKER": {
            "command": "docker",
            "args": [
                "run",
                "-l",
                "mcp.client=claude-desktop",
                "--rm",
                "-i",
                "alpine/socat",
                "STDIO",
                "TCP:host.docker.internal:8811"
            ]
        }
    }
}
```

---

## 🛡️ VoidCat-Specific Configuration

### Server Configuration Details

```json
"voidcat-reasoning-core": {
    "command": "uvicorn",
    "args": [
        "api_gateway:app",
        "--host", "127.0.0.1",
        "--port", "8000",
        "--reload",
        "--log-level", "info"
    ],
    "workingDirectory": "P:\\voidcat-reasoning-core\\",
    "env": {
        "OPENAI_API_KEY": "your_openai_api_key_here",
        "PYTHONPATH": "P:\\voidcat-reasoning-core"
    }
}
```

### Configuration Parameters Explained

- **command**: `uvicorn` - ASGI server for FastAPI applications
- **args**: Server startup parameters with optimal configuration
- **workingDirectory**: Absolute path to VoidCat project root
- **env**: Environment variables including OpenAI API key

---

## 🚀 Pre-Integration Setup

### 1. Environment Preparation

```bash
# Navigate to project directory
cd P:\voidcat-reasoning-core

# Activate virtual environment
.venv\Scripts\activate

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Verify installation
python main.py
```

### 2. Environment Variables Setup

Create `.env` file in project root:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Verify Server Functionality

```bash
# Test manual server startup
uvicorn api_gateway:app --host 127.0.0.1 --port 8000 --reload

# Verify endpoints
curl http://localhost:8000/
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "Test MCP integration"}'
```

---

## 🔧 Alternative Configuration Options

### Option 1: Python Direct Execution
```json
"voidcat-reasoning-core": {
    "command": "python",
    "args": [
        "-m", "uvicorn",
        "api_gateway:app",
        "--host", "127.0.0.1",
        "--port", "8000"
    ],
    "workingDirectory": "P:\\voidcat-reasoning-core\\",
    "env": {
        "OPENAI_API_KEY": "your_openai_api_key_here"
    }
}
```

### Option 2: Custom Port Configuration
```json
"voidcat-reasoning-core": {
    "command": "uvicorn",
    "args": [
        "api_gateway:app",
        "--host", "127.0.0.1",
        "--port", "8001",
        "--reload"
    ],
    "workingDirectory": "P:\\voidcat-reasoning-core\\",
    "env": {
        "OPENAI_API_KEY": "your_openai_api_key_here"
    }
}
```

### Option 3: Production Configuration (No Reload)
```json
"voidcat-reasoning-core": {
    "command": "uvicorn",
    "args": [
        "api_gateway:app",
        "--host", "127.0.0.1",
        "--port", "8000",
        "--workers", "1"
    ],
    "workingDirectory": "P:\\voidcat-reasoning-core\\",
    "env": {
        "OPENAI_API_KEY": "your_openai_api_key_here"
    }
}
```

---

## 📊 Integration Verification

### Step 1: Configure Claude Desktop
1. Open Claude Desktop configuration file
2. Add VoidCat MCP server configuration
3. Save and restart Claude Desktop

### Step 2: Verify Integration
1. Check Claude Desktop logs for successful MCP server startup
2. Verify VoidCat server responds to health checks
3. Test query processing through Claude interface

### Step 3: Test RAG Functionality
```json
// Example query through Claude:
"Use the VoidCat reasoning engine to analyze: What are the core MCP primitives?"
```

---

## 🛡️ Security Considerations

### Environment Variables Protection
- Never commit API keys to version control
- Use secure environment variable management
- Regularly rotate API keys

### Network Security
- MCP server runs on localhost only (127.0.0.1)
- No external network exposure by default
- Secure API key transmission through environment variables

---

## 🔍 Troubleshooting Guide

### Common Issues & Solutions

#### Issue 1: Server Startup Failure
```bash
# Check Python environment
python --version
pip list | findstr fastapi

# Verify working directory
cd P:\voidcat-reasoning-core
ls -la
```

#### Issue 2: API Key Not Found
```bash
# Verify .env file
cat .env
echo $OPENAI_API_KEY
```

#### Issue 3: Port Already in Use
```bash
# Check port usage
netstat -an | findstr 8000

# Use alternative port in configuration
```

#### Issue 4: Module Import Errors
```bash
# Verify Python path
python -c "import sys; print(sys.path)"

# Install missing dependencies
pip install -r requirements.txt
```

---

## 📈 Advanced Configuration

### Multi-Instance Setup
```json
{
    "voidcat-reasoning-primary": {
        "command": "uvicorn",
        "args": ["api_gateway:app", "--port", "8000"],
        "workingDirectory": "P:\\voidcat-reasoning-core\\"
    },
    "voidcat-reasoning-secondary": {
        "command": "uvicorn", 
        "args": ["api_gateway:app", "--port", "8001"],
        "workingDirectory": "P:\\voidcat-reasoning-core-backup\\"
    }
}
```

### Load Balancer Configuration
```json
"voidcat-reasoning-core": {
    "command": "uvicorn",
    "args": [
        "api_gateway:app",
        "--host", "127.0.0.1",
        "--port", "8000",
        "--workers", "4",
        "--worker-class", "uvicorn.workers.UvicornWorker"
    ],
    "workingDirectory": "P:\\voidcat-reasoning-core\\"
}
```

---

## 🎯 Integration Benefits

### Enhanced Claude Capabilities
- **Intelligent RAG Processing**: Document-aware reasoning with TF-IDF vectorization
- **Knowledge Base Integration**: Seamless access to markdown document collections  
- **Advanced Query Processing**: Context-enhanced responses with OpenAI integration
- **Production-Ready Performance**: Async processing with comprehensive error handling

### Strategic Workflow Enhancement
- **Automated Knowledge Retrieval**: Context-aware document selection
- **Multi-Document Analysis**: Comprehensive knowledge base processing
- **Professional Documentation**: Enterprise-grade API with automatic documentation
- **Scalable Architecture**: Production-ready deployment with monitoring capabilities

---

*Through strategic integration and compassionate protection, VoidCat Reasoning Core now enhances Claude Desktop with intelligent RAG capabilities, providing unprecedented access to contextual knowledge processing.* 🛡️
