# api_gateway.py
"""
VoidCat Reasoning Core API Gateway

This module implements an API-based web service for the VoidCat Reasoning Core
engine, providing RESTful endpoints for intelligent query processing with RAG
capabilities.

Features:
- Async request processing
- Automatic API documentation
- Health monitoring endpoints
- Comprehensive error handling
- Production-ready deployment

Author: VoidCat Reasoning Core Team
License: MIT
"""

import logging
from contextlib import asynccontextmanager
from enum import Enum
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from engine import VoidCatEngine


class AllowedModels(str, Enum):
    """Enum of allowed OpenAI models to prevent unauthorized model usage."""

    GPT4O_MINI = "gpt-4o-mini"
    GPT4O = "gpt-4o"
    GPT35_TURBO = "gpt-3.5-turbo"


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global engine instance
vce: Optional[VoidCatEngine] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage the application lifespan with proper resource initialization.

    This context manager ensures the VoidCat Engine is properly initialized
    on startup and cleaned up on shutdown.
    """
    global vce
    logger.info("ðŸš€ VoidCat Reasoning Core API Gateway starting up...")

    try:
        vce = VoidCatEngine()
        logger.info("âœ… Engine initialization completed successfully")
        yield
    except Exception as e:
        logger.error(f"âŒ Engine initialization failed: {str(e)}")
        yield
    finally:
        logger.info("ðŸ”„ VoidCat Reasoning Core API Gateway shutting down...")


# Initialize FastAPI application with metadata
app = FastAPI(
    title="VoidCat Reasoning Core API",
    description="""
    ## Advanced RAG-Enhanced Reasoning Engine
    The VoidCat Reasoning Core API provides intelligent query processing
    capabilities using Retrieval-Augmented Generation (RAG) with OpenAI's
    reasoning models.
    
    ### Key Features:
    - **Intelligent Context Retrieval**: TF-IDF based document similarity
      matching
    - **Multi-Document Processing**: Seamless handling of extensive knowledge
      bases
    - **Async Processing**: High-performance non-blocking operations
    - **Production Ready**: Enterprise-grade error handling and monitoring
    
    Built with strategic foresight for the AI community.
    """,
    version="0.1.0",
    contact={
        "name": "VoidCat Reasoning Core Team",
        "email": "team@voidcat-reasoning.com",
        "url": "https://github.com/yourusername/voidcat-reasoning-core",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
)


class QueryRequest(BaseModel):
    """Request model for query processing."""

    query: str = Field(
        description="The question or prompt to process with RAG enhancement",
        min_length=1,
        max_length=5000,
        examples=["What are the core MCP primitives and who controls them?"],
    )
    model: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model to use for reasoning",
        examples=["gpt-4o-mini"],
    )


class QueryResponse(BaseModel):
    """Response model for query results."""

    response: str = Field(
        ..., description="AI-generated response with RAG context integration"
    )
    status: str = Field(
        default="success", description="Processing status indicator"
    )


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str = Field(description="Service health status")
    engine_ready: bool = Field(description="Engine initialization status")
    message: str = Field(description="Detailed status message")


@app.post(
    "/query",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Process Intelligent Query",
    description="""
    Process a user query using RAG-enhanced reasoning capabilities.
    This endpoint:
    1. Retrieves relevant context from the knowledge base
    2. Constructs an enhanced prompt with retrieved context
    3. Generates a response using the specified OpenAI model
    4. Returns the contextually-aware AI response
    """,
    responses={
        200: {"description": "Query processed successfully"},
        400: {"description": "Invalid request parameters"},
        500: {"description": "Internal server error"},
        503: {"description": "Service unavailable - engine not initialized"},
    },
)
async def process_query(request: QueryRequest) -> QueryResponse:
    """
    Process a query with RAG-enhanced reasoning.

    Args:
        request (QueryRequest): Query request containing question and model

    Returns:
        QueryResponse: AI-generated response with RAG context

    Raises:
        HTTPException: For various error conditions
    """
    if not vce:
        logger.error("Query attempted with uninitialized engine")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Engine not initialized. Please check server logs and "
            "restart.",
        )

    try:
        logger.info(f"Processing query: {request.query[:100]}...")
        response = await vce.query(request.query, model=request.model)

        # Check for error responses from the engine
        if response.startswith("Error:"):
            logger.warning(f"Engine returned error: {response}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response
            )

        logger.info("Query processed successfully")
        return QueryResponse(response=response, status="success")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during query processing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )


@app.get(
    "/",
    response_model=HealthResponse,
    summary="Health Check",
    description="Get the current health status of the VoidCat Reasoning Core "
    "API",
    responses={
        200: {"description": "Service is healthy and operational"},
        503: {"description": "Service is unavailable"},
    },
)
async def health_check() -> HealthResponse:
    """
    Perform a comprehensive health check of the service.

    Returns:
        HealthResponse: Current service health status
    """
    engine_ready = vce is not None

    if engine_ready:
        status_msg = (
            "VoidCat Reasoning Core API is online and ready for "
            "intelligent processing."
        )
        return HealthResponse(
            status="healthy", engine_ready=True, message=status_msg
        )
    else:
        status_msg = (
            "VoidCat Reasoning Core API is online but engine is not "
            "initialized."
        )
        return HealthResponse(
            status="degraded", engine_ready=False, message=status_msg
        )


@app.get(
    "/info",
    summary="System Information",
    description="Get detailed information about the VoidCat Reasoning Core "
    "system",
)
async def system_info():
    """
    Retrieve system information and capabilities.

    Returns:
        dict: System information including engine status and capabilities
    """
    info = {
        "name": "VoidCat Reasoning Core",
        "version": "0.1.0",
        "description": (
            "Advanced RAG-Enhanced Reasoning Engine with Strategic "
            "Intelligence"
        ),
        "capabilities": [
            "Document vectorization with TF-IDF",
            "Cosine similarity context retrieval",
            "OpenAI API integration",
            "Async query processing",
            "Multi-document knowledge base",
            "Production-ready error handling",
        ],
        "engine_status": {
            "initialized": vce is not None,
            "knowledge_base_loaded": (
                vce.doc_vectors is not None if vce else False
            ),
            "document_count": len(vce.documents) if vce else 0,
        },
    }

    return info


@app.get("/diagnostics")
async def diagnostics():
    """Provide real-time diagnostics for the VoidCat Reasoning Core."""
    if not vce:
        return {"status": "offline", "message": "Engine not initialized"}

    return {
        "status": "online",
        "documents_loaded": vce.get_diagnostics()["documents_loaded"],
        "total_queries_processed": vce.total_queries_processed,
        "last_query_timestamp": vce.last_query_timestamp,
        "health": "healthy",
    }


# ==========================================
# VS Code Extension Backend Integration
# ==========================================
try:
    from vscode_extension.api_integration import integrate_vscode_backend

    integrate_vscode_backend(app)
    logger.info("✅ VS Code backend integration loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ VS Code backend integration not available: {e}")
except Exception as e:
    logger.error(f"❌ VS Code backend integration failed: {e}")


# Add custom exception handler for better error responses
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unexpected errors."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred. Please try again later.",
            "status": "error",
        },
    )
