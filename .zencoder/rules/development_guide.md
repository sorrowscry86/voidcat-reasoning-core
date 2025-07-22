# VoidCat Reasoning Core Development Guide

This guide provides detailed instructions for developing and extending the VoidCat Reasoning Core system.

## Development Environment Setup

### Prerequisites

- Python 3.13 (for development)
- Docker and Docker Compose (for containerized development)
- Git
- OpenAI API key

### Initial Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/sorrowscry86/voidcat-reasoning-core.git
   cd voidcat-reasoning-core
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env to add your OpenAI API key
   ```

## Project Structure

The VoidCat Reasoning Core is organized as follows:

- **Core Engine Components**
  - `engine.py`: Base RAG engine with TF-IDF vectorization
  - `enhanced_engine.py`: Extended reasoning capabilities
  - `sequential_thinking.py`: Sequential reasoning implementation
  - `context7_integration.py`: Integration with Context7 system

- **API and Server Components**
  - `api_gateway.py`: FastAPI server with query endpoints
  - `mcp_server.py`: Model Control Protocol server

- **Testing and Validation**
  - `main.py`: Test harness and system validation
  - `test_*.py`: Test files for various components

- **Configuration and Documentation**
  - `.env.example`: Template for environment variables
  - `pyproject.toml`: Project configuration
  - `requirements.txt`: Dependency specifications
  - `.zencoder/docs/`: Documentation directory

## Development Workflow

### Running the Application

1. **Run the test harness**
   ```bash
   python main.py
   ```

2. **Start the API server**
   ```bash
   uvicorn api_gateway:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Access the API documentation**
   Open your browser and navigate to:
   ```
   http://localhost:8000/docs
   ```

### Docker Development

1. **Build the Docker image**
   ```bash
   docker build -t voidcat-reasoning-core .
   ```

2. **Run the container**
   ```bash
   docker run --env-file .env -p 8000:8000 voidcat-reasoning-core
   ```

3. **Use Docker Compose**
   ```bash
   docker-compose up
   ```

### Testing

1. **Run all tests**
   ```bash
   pytest
   ```

2. **Run specific tests**
   ```bash
   pytest test_enhanced.py
   ```

3. **Run tests with coverage**
   ```bash
   pytest --cov=.
   ```

## Extending the System

### Adding New Document Processors

To add support for a new document type, extend the `MultiFormatProcessor` class in `engine.py`:

1. Create a new processor class:
   ```python
   class NewFormatProcessor:
       def extract(self, file_path: str) -> Tuple[str, Dict]:
           # Implementation for extracting content and metadata
           return content, metadata
   ```

2. Register the processor in `MultiFormatProcessor.__init__`:
   ```python
   self.processors['.new_ext'] = NewFormatProcessor()
   ```

### Enhancing the RAG Engine

To improve the RAG capabilities:

1. Modify the vectorization in `VoidCatEngine`:
   ```python
   self.vectorizer = TfidfVectorizer(
       max_features=10000,  # Increase features
       stop_words='english',
       lowercase=True,
       ngram_range=(1, 3)   # Expand n-gram range
   )
   ```

2. Enhance context retrieval in `_retrieve_context` method.

3. Improve prompt construction in `_build_enhanced_prompt` method.

### Adding New API Endpoints

To add new API endpoints, modify `api_gateway.py`:

1. Define a new Pydantic model for request/response:
   ```python
   class NewFeatureRequest(BaseModel):
       parameter: str = Field(...)
   ```

2. Add a new endpoint:
   ```python
   @app.post(
       "/new-feature",
       response_model=ResponseModel,
       summary="New Feature"
   )
   async def new_feature(request: NewFeatureRequest):
       # Implementation
       return ResponseModel(...)
   ```

## Knowledge Base Management

The system uses markdown files in the `knowledge_source/` directory as its knowledge base:

1. **Adding documents**:
   - Create markdown files in the `knowledge_source/` directory
   - Use clear section headers for better chunking
   - Include relevant metadata where possible

2. **Document format**:
   - Use standard markdown formatting
   - Organize content with headers (# for main sections)
   - Use code blocks for code examples (```python)
   - Include tables where appropriate

## Deployment

### Local Deployment

```bash
uvicorn api_gateway:app --host 0.0.0.0 --port 8000
```

### Docker Deployment

```bash
docker build -t voidcat-reasoning-core .
docker run --env-file .env -p 8000:8000 voidcat-reasoning-core
```

### Production Deployment

For production deployment:

1. Use the GitHub Container Registry image:
   ```bash
   docker pull ghcr.io/[repository-owner]/voidcat-reasoning-core:latest
   ```

2. Run with proper environment configuration:
   ```bash
   docker run -d --name voidcat-reasoning -p 8000:8000 --env-file .env ghcr.io/[repository-owner]/voidcat-reasoning-core:latest
   ```

## Troubleshooting

### Common Issues

1. **OpenAI API Key Issues**:
   - Ensure the API key is correctly set in the .env file
   - Verify the API key has the necessary permissions

2. **Document Loading Problems**:
   - Check that documents are in the correct format
   - Verify file permissions on the knowledge_source directory

3. **Docker Issues**:
   - Ensure Docker is running
   - Check that ports are not already in use
   - Verify environment variables are correctly passed to the container

### Debugging

1. **Enable Debug Logging**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Check API Responses**:
   - Use the /diagnostics endpoint to check system status
   - Examine the API response for error messages

3. **Container Inspection**:
   ```bash
   docker logs voidcat-reasoning
   ```