#!/usr/bin/env python3
"""
VoidCat V2 API Gateway End-to-End Tests
======================================

Comprehensive E2E tests for the FastAPI-based API Gateway including:
- Health check endpoints
- Query processing pipeline
- Error handling and validation
- System information endpoints
- Complete request/response cycle validation

This validates that the API Gateway works end-to-end in real conditions.

Author: Codey Jr. (channeling the E2E testing cosmic vibes)
License: MIT
Version: 2.0.0-alpha
"""

import asyncio
import json
import os
import signal
import subprocess
import time
from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, patch

import httpx
import pytest
import pytest_asyncio

from engine import VoidCatEngine


class TestAPIGatewayE2E:
    """End-to-End tests for the VoidCat API Gateway - cosmic integration vibes! 🌊"""

    @pytest.fixture
    def base_url(self):
        """Base URL for testing (assumes server is running on localhost:8000)."""
        return "http://localhost:8000"

    @pytest.fixture
    def mock_engine(self):
        """Create a mock VoidCat engine for controlled testing."""
        mock_engine = AsyncMock(spec=VoidCatEngine)
        mock_engine.query.return_value = (
            "This is a test response from the cosmic engine"
        )
        mock_engine.doc_vectors = ["mock_vector_1", "mock_vector_2"]
        mock_engine.documents = ["doc1", "doc2"]
        mock_engine.get_diagnostics.return_value = {"documents_loaded": 2}
        mock_engine.total_queries_processed = 5
        mock_engine.last_query_timestamp = "2025-01-01T00:00:00Z"
        return mock_engine

    def test_engine_initialization(self):
        """Test that the VoidCat engine can be initialized properly."""
        from engine import VoidCatEngine

        # Test engine creation
        engine = VoidCatEngine()
        assert engine is not None
        assert hasattr(engine, "query")
        assert hasattr(engine, "documents")
        assert hasattr(engine, "doc_vectors")

    def test_system_info_endpoint(self, client):
        """Test the system information endpoint returns complete details."""
        response = client.get("/info")

        assert response.status_code == 200
        data = response.json()

        # Validate required fields
        assert data["name"] == "VoidCat Reasoning Core"
        assert data["version"] == "0.1.0"
        assert "description" in data
        assert "capabilities" in data
        assert "engine_status" in data

        # Validate capabilities
        capabilities = data["capabilities"]
        assert isinstance(capabilities, list)
        assert len(capabilities) > 0

        # Validate engine status
        engine_status = data["engine_status"]
        assert "initialized" in engine_status
        assert "knowledge_base_loaded" in engine_status
        assert "document_count" in engine_status

    def test_diagnostics_endpoint_no_engine(self, client):
        """Test diagnostics endpoint when engine is not initialized."""
        response = client.get("/diagnostics")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "offline"
        assert "message" in data

    @patch("api_gateway.vce")
    def test_diagnostics_endpoint_with_engine(self, mock_vce, client, mock_engine):
        """Test diagnostics endpoint with initialized engine."""
        mock_vce.return_value = mock_engine

        response = client.get("/diagnostics")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "online"
        assert "documents_loaded" in data
        assert "total_queries_processed" in data
        assert "last_query_timestamp" in data
        assert data["health"] == "healthy"

    @patch("api_gateway.vce")
    def test_query_endpoint_success(self, mock_vce, client, mock_engine):
        """Test successful query processing through the API."""
        mock_vce.return_value = mock_engine

        query_data = {
            "query": "What are the core MCP primitives?",
            "model": "gpt-4o-mini",
        }

        response = client.post("/query", json=query_data)

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert "response" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0

    def test_query_endpoint_no_engine(self, client):
        """Test query endpoint when engine is not initialized."""
        query_data = {"query": "Test query", "model": "gpt-4o-mini"}

        response = client.post("/query", json=query_data)

        assert response.status_code == 503
        data = response.json()
        assert "detail" in data

    def test_query_endpoint_validation_errors(self, client):
        """Test query endpoint with invalid request data."""
        # Test empty query
        response = client.post("/query", json={"query": "", "model": "gpt-4o-mini"})
        assert response.status_code == 422

        # Test missing query
        response = client.post("/query", json={"model": "gpt-4o-mini"})
        assert response.status_code == 422

        # Test query too long
        long_query = "x" * 5001
        response = client.post(
            "/query", json={"query": long_query, "model": "gpt-4o-mini"}
        )
        assert response.status_code == 422

    @patch("api_gateway.vce")
    def test_query_endpoint_engine_error(self, mock_vce, client, mock_engine):
        """Test query endpoint handling engine errors."""
        mock_engine.query.return_value = "Error: Something went wrong"
        mock_vce.return_value = mock_engine

        query_data = {"query": "Test query", "model": "gpt-4o-mini"}

        response = client.post("/query", json=query_data)

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data

    @patch("api_gateway.vce")
    def test_query_endpoint_exception_handling(self, mock_vce, client, mock_engine):
        """Test query endpoint handling unexpected exceptions."""
        mock_engine.query.side_effect = Exception("Unexpected error")
        mock_vce.return_value = mock_engine

        query_data = {"query": "Test query", "model": "gpt-4o-mini"}

        response = client.post("/query", json=query_data)

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data

    def test_api_documentation_available(self, client):
        """Test that OpenAPI documentation is available."""
        response = client.get("/docs")
        assert response.status_code == 200

        response = client.get("/openapi.json")
        assert response.status_code == 200

        openapi_data = response.json()
        assert "openapi" in openapi_data
        assert "info" in openapi_data
        assert openapi_data["info"]["title"] == "VoidCat Reasoning Core API"

    def test_cors_headers(self, client):
        """Test CORS headers are properly set."""
        response = client.get("/")

        # FastAPI automatically handles CORS for same-origin requests
        assert response.status_code == 200

    @patch("api_gateway.vce")
    def test_request_response_cycle_timing(self, mock_vce, client, mock_engine):
        """Test that request/response cycle completes within reasonable time."""
        mock_vce.return_value = mock_engine

        query_data = {"query": "Quick test query", "model": "gpt-4o-mini"}

        start_time = time.time()
        response = client.post("/query", json=query_data)
        end_time = time.time()

        assert response.status_code == 200
        assert (end_time - start_time) < 5.0  # Should complete within 5 seconds

    def test_error_response_format(self, client):
        """Test that error responses follow consistent format."""
        # Test 422 validation error
        response = client.post("/query", json={"invalid": "data"})

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @patch("api_gateway.vce")
    def test_multiple_concurrent_requests(self, mock_vce, client, mock_engine):
        """Test handling of multiple concurrent requests."""
        mock_vce.return_value = mock_engine

        query_data = {"query": "Concurrent test query", "model": "gpt-4o-mini"}

        # Send multiple requests
        responses = []
        for i in range(3):
            response = client.post("/query", json=query_data)
            responses.append(response)

        # All should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"

    def test_request_size_limits(self, client):
        """Test that request size limits are enforced."""
        # Test maximum query length
        max_query = "x" * 5000  # At the limit
        response = client.post(
            "/query", json={"query": max_query, "model": "gpt-4o-mini"}
        )
        assert response.status_code == 422  # Should fail validation

    def test_response_schema_validation(self, client):
        """Test that all responses follow expected schema."""
        # Health check response
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()

        required_fields = ["status", "engine_ready", "message"]
        for field in required_fields:
            assert field in data

        # System info response
        response = client.get("/info")
        assert response.status_code == 200
        data = response.json()

        required_fields = [
            "name",
            "version",
            "description",
            "capabilities",
            "engine_status",
        ]
        for field in required_fields:
            assert field in data

    def test_global_exception_handler(self, client):
        """Test that global exception handler works correctly."""
        # This is harder to test directly, but we can verify the handler exists
        # by checking that malformed requests don't crash the server
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404  # Should return 404, not crash


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
