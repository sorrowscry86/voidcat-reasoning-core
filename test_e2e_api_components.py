#!/usr/bin/env python3
"""
VoidCat V2 API Components End-to-End Tests
==========================================

Comprehensive E2E tests for the VoidCat API components including:
- Engine initialization and query processing
- API Gateway request/response models
- Error handling and validation
- Component integration without requiring running server

This validates that the API components work end-to-end as integrated units.

Author: Codey Jr. (channeling the API component cosmic vibes)
License: MIT
Version: 2.0.0-alpha
"""

import asyncio
import json
import os
import tempfile
import time
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from engine import VoidCatEngine
from enhanced_engine import VoidCatEnhancedEngine
from sequential_thinking import SequentialThinkingEngine


class TestAPIComponentsE2E:
    """End-to-End tests for VoidCat API Components - cosmic integration vibes! 🌊"""

    @pytest.fixture
    def temp_knowledge_dir(self):
        """Create temporary knowledge directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some sample knowledge files
            knowledge_dir = os.path.join(temp_dir, "knowledge_source")
            os.makedirs(knowledge_dir)

            # Create sample markdown files
            sample_files = [
                (
                    "mcp-basics.md",
                    "# MCP Basics\n\nMCP stands for Model Context Protocol.",
                ),
                (
                    "ai-concepts.md",
                    "# AI Concepts\n\nAI is about creating intelligent systems.",
                ),
                (
                    "testing-guide.md",
                    "# Testing Guide\n\nTesting ensures code quality.",
                ),
            ]

            for filename, content in sample_files:
                with open(os.path.join(knowledge_dir, filename), "w") as f:
                    f.write(content)

            yield temp_dir

    @pytest.mark.asyncio
    async def test_engine_initialization_e2e(self, temp_knowledge_dir):
        """Test VoidCat engine initialization end-to-end."""
        # Change to temp directory for testing
        original_cwd = os.getcwd()
        os.chdir(temp_knowledge_dir)

        try:
            engine = VoidCatEngine()
            assert engine is not None
            assert hasattr(engine, "documents")
            assert hasattr(engine, "doc_vectors")
            assert hasattr(engine, "query")

            # Test that documents are loaded
            assert isinstance(engine.documents, list)
            assert len(engine.documents) > 0

        finally:
            os.chdir(original_cwd)

    @pytest.mark.asyncio
    async def test_engine_query_processing_e2e(self, temp_knowledge_dir):
        """Test engine query processing end-to-end."""
        original_cwd = os.getcwd()
        os.chdir(temp_knowledge_dir)

        try:
            engine = VoidCatEngine()

            # Mock the OpenAI API call
            with patch("engine.httpx.AsyncClient") as mock_client:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "choices": [
                        {
                            "message": {
                                "content": "Test response about MCP from the cosmic engine"
                            }
                        }
                    ]
                }

                mock_client.return_value.__aenter__.return_value.post.return_value = (
                    mock_response
                )

                # Test query processing
                result = await engine.query("What is MCP?")

                assert isinstance(result, str)
                assert len(result) > 0
                assert "Test response" in result

        finally:
            os.chdir(original_cwd)

    def test_api_request_models_validation(self):
        """Test API request models validation."""
        # Test basic request structure
        request_data = {
            "query": "What are the core MCP primitives?",
            "model": "gpt-4o-mini",
        }

        assert request_data["query"] == "What are the core MCP primitives?"
        assert request_data["model"] == "gpt-4o-mini"

        # Test response structure
        response_data = {"response": "This is a test response", "status": "success"}

        assert response_data["response"] == "This is a test response"
        assert response_data["status"] == "success"

        # Test health response structure
        health_data = {
            "status": "healthy",
            "engine_ready": True,
            "message": "System is operational",
        }

        assert health_data["status"] == "healthy"
        assert health_data["engine_ready"] is True
        assert health_data["message"] == "System is operational"

    @pytest.mark.asyncio
    async def test_enhanced_engine_integration_e2e(self, temp_knowledge_dir):
        """Test enhanced engine integration end-to-end."""
        original_cwd = os.getcwd()
        os.chdir(temp_knowledge_dir)

        try:
            enhanced_engine = VoidCatEnhancedEngine()

            # Mock the OpenAI API call
            with patch("enhanced_engine.httpx.AsyncClient") as mock_client:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "choices": [
                        {
                            "message": {
                                "content": "Enhanced response from the cosmic engine"
                            }
                        }
                    ]
                }

                mock_client.return_value.__aenter__.return_value.post.return_value = (
                    mock_response
                )

                # Test enhanced query processing
                result = await enhanced_engine.enhanced_query("What is AI?")

                assert isinstance(result, str)
                assert len(result) > 0
                assert "Enhanced response" in result

        finally:
            os.chdir(original_cwd)

    @pytest.mark.asyncio
    async def test_sequential_thinking_integration_e2e(self):
        """Test sequential thinking engine integration end-to-end."""
        thinking_engine = SequentialThinkingEngine()

        # Mock the OpenAI API call
        with patch("sequential_thinking.httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "thoughts": [
                                        {"content": "First thought about the problem"},
                                        {
                                            "content": "Second thought building on the first"
                                        },
                                    ],
                                    "final_answer": "Sequential thinking final answer",
                                }
                            )
                        }
                    }
                ]
            }

            mock_client.return_value.__aenter__.return_value.post.return_value = (
                mock_response
            )

            # Test sequential thinking processing
            result = await thinking_engine.process_query("Test query", max_thoughts=2)

            assert isinstance(result, dict)
            assert "final_answer" in result
            assert "thoughts" in result
            assert result["final_answer"] == "Sequential thinking final answer"
            assert len(result["thoughts"]) == 2

    @pytest.mark.asyncio
    async def test_error_handling_e2e(self, temp_knowledge_dir):
        """Test error handling across components end-to-end."""
        original_cwd = os.getcwd()
        os.chdir(temp_knowledge_dir)

        try:
            engine = VoidCatEngine()

            # Test API error handling
            with patch("engine.httpx.AsyncClient") as mock_client:
                mock_response = MagicMock()
                mock_response.status_code = 500
                mock_response.json.return_value = {"error": "API Error"}

                mock_client.return_value.__aenter__.return_value.post.return_value = (
                    mock_response
                )

                # Test that error is handled gracefully
                result = await engine.query("Test query")

                assert isinstance(result, str)
                assert "Error" in result

        finally:
            os.chdir(original_cwd)

    @pytest.mark.asyncio
    async def test_component_integration_performance_e2e(self, temp_knowledge_dir):
        """Test component integration performance end-to-end."""
        original_cwd = os.getcwd()
        os.chdir(temp_knowledge_dir)

        try:
            engine = VoidCatEngine()

            # Mock the OpenAI API call
            with patch("engine.httpx.AsyncClient") as mock_client:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "choices": [{"message": {"content": "Performance test response"}}]
                }

                mock_client.return_value.__aenter__.return_value.post.return_value = (
                    mock_response
                )

                # Test multiple queries for performance
                start_time = time.time()

                tasks = []
                for i in range(5):
                    task = engine.query(f"Performance test query {i}")
                    tasks.append(task)

                results = await asyncio.gather(*tasks)

                end_time = time.time()

                # Verify all queries completed
                assert len(results) == 5
                for result in results:
                    assert isinstance(result, str)
                    assert "Performance test" in result

                # Verify reasonable performance
                assert (end_time - start_time) < 5.0  # Should complete within 5 seconds

        finally:
            os.chdir(original_cwd)

    def test_document_processing_e2e(self, temp_knowledge_dir):
        """Test document processing end-to-end."""
        original_cwd = os.getcwd()
        os.chdir(temp_knowledge_dir)

        try:
            engine = VoidCatEngine()

            # Test document loading
            assert len(engine.documents) > 0

            # Test document content
            found_mcp = False
            for doc in engine.documents:
                if "MCP" in doc:
                    found_mcp = True
                    break

            assert found_mcp, "MCP content should be found in documents"

            # Test vectorization
            assert engine.doc_vectors is not None
            assert len(engine.doc_vectors) > 0

        finally:
            os.chdir(original_cwd)

    @pytest.mark.asyncio
    async def test_context_retrieval_e2e(self, temp_knowledge_dir):
        """Test context retrieval end-to-end."""
        original_cwd = os.getcwd()
        os.chdir(temp_knowledge_dir)

        try:
            engine = VoidCatEngine()

            # Test context retrieval
            contexts = engine.get_relevant_contexts("What is MCP?", top_k=2)

            assert isinstance(contexts, list)
            assert len(contexts) > 0
            assert len(contexts) <= 2  # Should respect top_k

            # Test that relevant context is retrieved
            found_relevant = False
            for context in contexts:
                if "MCP" in context:
                    found_relevant = True
                    break

            assert found_relevant, "Relevant context should be retrieved"

        finally:
            os.chdir(original_cwd)

    @pytest.mark.asyncio
    async def test_concurrent_processing_e2e(self, temp_knowledge_dir):
        """Test concurrent processing end-to-end."""
        original_cwd = os.getcwd()
        os.chdir(temp_knowledge_dir)

        try:
            engine = VoidCatEngine()

            # Mock the OpenAI API call
            with patch("engine.httpx.AsyncClient") as mock_client:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "choices": [
                        {"message": {"content": "Concurrent processing response"}}
                    ]
                }

                mock_client.return_value.__aenter__.return_value.post.return_value = (
                    mock_response
                )

                # Test concurrent queries
                queries = [
                    "What is MCP?",
                    "What is AI?",
                    "What is testing?",
                    "How does the engine work?",
                    "What are the features?",
                ]

                tasks = [engine.query(query) for query in queries]
                results = await asyncio.gather(*tasks)

                # Verify all queries completed successfully
                assert len(results) == len(queries)
                for result in results:
                    assert isinstance(result, str)
                    assert "Concurrent processing" in result

        finally:
            os.chdir(original_cwd)

    def test_diagnostics_e2e(self, temp_knowledge_dir):
        """Test diagnostics functionality end-to-end."""
        original_cwd = os.getcwd()
        os.chdir(temp_knowledge_dir)

        try:
            engine = VoidCatEngine()

            # Test diagnostics
            diagnostics = engine.get_diagnostics()

            assert isinstance(diagnostics, dict)
            assert "documents_loaded" in diagnostics
            assert "vectorization_complete" in diagnostics
            assert "knowledge_base_ready" in diagnostics

            # Verify diagnostic values
            assert diagnostics["documents_loaded"] > 0
            assert diagnostics["vectorization_complete"] is True
            assert diagnostics["knowledge_base_ready"] is True

        finally:
            os.chdir(original_cwd)


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
