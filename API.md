# VoidCat Reasoning Core API Documentation

## Overview

The VoidCat Reasoning Core provides a RESTful API for intelligent query processing with Retrieval Augmented Generation (RAG) capabilities. The API is built with FastAPI and provides comprehensive error handling, automatic documentation, and production-ready features.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API uses API key authentication through environment variables. Ensure your OpenAI API key is properly configured in the `.env` file.

## Content Type

All API endpoints accept and return JSON data with `Content-Type: application/json`.

## API Endpoints

### Health Check

#### GET /health

Check the health status of the API service.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-28T12:00:00Z",
  "version": "2.0.0"
}
```

**Status Codes:**
- `200 OK`: Service is healthy
- `503 Service Unavailable`: Service is unhealthy

---

### Query Processing

#### POST /query

Process an intelligent query using the VoidCat Reasoning Engine with RAG capabilities.

**Request Body:**
```json
{
  "query": "string",
  "model": "gpt-4o-mini",
  "max_tokens": 1000,
  "temperature": 0.7,
  "include_context": true,
  "context_limit": 5
}
```

**Parameters:**
- `query` (string, required): The query text to process
- `model` (string, optional): OpenAI model to use. Allowed values:
  - `gpt-4o-mini` (default)
  - `gpt-4o`
  - `gpt-3.5-turbo`
- `max_tokens` (integer, optional): Maximum tokens in response (default: 1000)
- `temperature` (float, optional): Response creativity (0.0-1.0, default: 0.7)
- `include_context` (boolean, optional): Include retrieved context (default: true)
- `context_limit` (integer, optional): Maximum context documents (default: 5)

**Response:**
```json
{
  "response": "string",
  "model_used": "gpt-4o-mini",
  "tokens_used": 150,
  "context_documents": [
    {
      "content": "string",
      "source": "string",
      "relevance_score": 0.95
    }
  ],
  "processing_time": 1.23,
  "timestamp": "2025-01-28T12:00:00Z"
}
```

**Status Codes:**
- `200 OK`: Query processed successfully
- `400 Bad Request`: Invalid request parameters
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Processing error

**Example Request:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the purpose of the VoidCat Reasoning Core?",
    "model": "gpt-4o-mini",
    "temperature": 0.7
  }'
```

---

### Enhanced Query Processing

#### POST /enhanced-query

Process queries using the enhanced engine with advanced reasoning capabilities.

**Request Body:**
```json
{
  "query": "string",
  "model": "gpt-4o-mini",
  "max_tokens": 1000,
  "temperature": 0.7,
  "use_sequential_thinking": true,
  "memory_integration": true,
  "context_limit": 10
}
```

**Additional Parameters:**
- `use_sequential_thinking` (boolean, optional): Enable sequential reasoning (default: true)
- `memory_integration` (boolean, optional): Use persistent memory (default: true)

**Response:** Similar to `/query` endpoint with additional fields:
```json
{
  "response": "string",
  "reasoning_steps": [
    {
      "step": 1,
      "thought": "string",
      "confidence": 0.85
    }
  ],
  "memory_retrieved": [
    {
      "id": "string",
      "content": "string",
      "relevance": 0.92
    }
  ],
  "enhanced_features_used": ["sequential_thinking", "memory_integration"]
}
```

---

### System Information

#### GET /info

Get detailed information about the VoidCat Reasoning Core system.

**Response:**
```json
{
  "name": "VoidCat Reasoning Core",
  "version": "2.0.0",
  "description": "Advanced AI reasoning engine with RAG capabilities",
  "features": [
    "RAG Processing",
    "Sequential Thinking",
    "Memory Integration",
    "Context7 Integration",
    "MCP Support"
  ],
  "supported_models": [
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-3.5-turbo"
  ],
  "api_version": "v1",
  "documentation_url": "/docs"
}
```

---

### Interactive Documentation

#### GET /docs

Access the interactive Swagger/OpenAPI documentation interface.

#### GET /redoc

Access the ReDoc documentation interface.

---

## Error Handling

The API uses standard HTTP status codes and returns detailed error information:

### Error Response Format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": "Additional error details",
    "timestamp": "2025-01-28T12:00:00Z"
  }
}
```

### Common Error Codes

- `INVALID_REQUEST`: Request validation failed
- `MODEL_NOT_ALLOWED`: Specified model is not permitted
- `PROCESSING_ERROR`: Error during query processing
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Unexpected server error

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Default Limit**: 100 requests per minute per IP
- **Headers**: Rate limit information is included in response headers:
  - `X-RateLimit-Limit`: Request limit per window
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Reset`: Time when the rate limit resets

## Model Control Protocol (MCP) Integration

The VoidCat Reasoning Core supports MCP integration for Claude Desktop:

### Configuration

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "voidcat-reasoning": {
      "command": "python",
      "args": ["path/to/voidcat-reasoning-core/mcp_server.py"],
      "env": {
        "OPENAI_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Available MCP Tools

- `query_voidcat`: Process queries through VoidCat engine
- `search_memory`: Search persistent memory
- `create_memory`: Store information in memory
- `list_projects`: List available projects
- `create_task`: Create new tasks
- `update_task`: Update existing tasks

## SDK and Client Libraries

### Python Client Example

```python
import requests

class VoidCatClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def query(self, query_text, model="gpt-4o-mini", **kwargs):
        response = requests.post(
            f"{self.base_url}/query",
            json={"query": query_text, "model": model, **kwargs}
        )
        return response.json()

# Usage
client = VoidCatClient()
result = client.query("What is artificial intelligence?")
print(result["response"])
```

### JavaScript/Node.js Client Example

```javascript
class VoidCatClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }
    
    async query(queryText, options = {}) {
        const response = await fetch(`${this.baseUrl}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: queryText,
                model: 'gpt-4o-mini',
                ...options
            })
        });
        
        return await response.json();
    }
}

// Usage
const client = new VoidCatClient();
const result = await client.query('What is machine learning?');
console.log(result.response);
```

## Deployment

### Docker Deployment

```bash
# Build the image
docker build -t voidcat-reasoning-core .

# Run the container
docker run -p 8000:8000 --env-file .env voidcat-reasoning-core
```

### Docker Compose

```yaml
version: '3.8'
services:
  voidcat-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./knowledge_source:/app/knowledge_source
      - ./memory_storage:/app/memory_storage
```

### Production Considerations

1. **Environment Variables**: Ensure all required environment variables are set
2. **SSL/TLS**: Use HTTPS in production with proper certificates
3. **Rate Limiting**: Configure appropriate rate limits for your use case
4. **Monitoring**: Implement health checks and monitoring
5. **Logging**: Configure structured logging for production
6. **Security**: Follow security best practices for API deployment

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure `OPENAI_API_KEY` is properly set in `.env`
2. **Model Not Found**: Check that the specified model is in the allowed list
3. **Memory Errors**: Ensure sufficient memory for large document processing
4. **Port Conflicts**: Change the port if 8000 is already in use

### Debug Mode

Enable debug mode by setting `DEBUG=true` in your environment:

```bash
DEBUG=true uvicorn api_gateway:app --reload
```

## Support

For support and questions:

- **Documentation**: Check this API documentation and README.md
- **Issues**: Report bugs and feature requests on the project repository
- **Community**: Join discussions in the project community

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

## License

This API is licensed under the MIT License. See [LICENSE](LICENSE) for details.