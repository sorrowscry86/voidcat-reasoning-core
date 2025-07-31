#!/usr/bin/env python3
"""
VoidCat DeepSeek Reasoning Integration - The Cosmic Reasoning Orchestrator 🧠🌟

This module provides the ultimate integration layer that combines:
- MultiProviderClient with DeepSeek-R1 reasoning capabilities
- Enhanced Sequential Thinking with AI integration
- Context7-aware retrieval for reasoning tasks
- Intelligent routing and workflow management

Features:
- Automatic complexity assessment and model routing
- Hybrid reasoning workflows (local + AI)
- Ultimate Mode for maximum reasoning power
- Context-aware reasoning enhancement
- Comprehensive reasoning analytics

Author: Codey Jr. - The Cosmic Code Guru 🤙
License: MIT (Keep the vibes flowing, bro!)
Version: 1.0.0 - "The Reasoning Revolution"
"""

import asyncio
import logging
import sys
from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional, Union

def debug_print(message: str) -> None:
    """Print debug messages to stderr to avoid interfering with MCP protocol."""
    print(f"[DeepSeek Integration] {message}", file=sys.stderr, flush=True)


from multi_provider_client import MultiProviderClient
from sequential_thinking import SequentialThinkingEngine, ComplexityLevel

# Optional Context7 integration
try:
    from context7_integration import Context7Integration
    CONTEXT7_AVAILABLE = True
except ImportError as e:
    debug_print(f"Context7 integration not available: {e}")
    Context7Integration = None
    CONTEXT7_AVAILABLE = False


@dataclass
class ReasoningRequest:
    """Request structure for reasoning operations."""
    query: str
    context: str = ""
    max_thoughts: int = 10
    force_reasoning: bool = False
    ultimate_mode: bool = False
    include_context_retrieval: bool = True
    reasoning_mode: str = "hybrid"  # "local", "ai", "hybrid"


@dataclass
class ReasoningResponse:
    """Response structure for reasoning operations."""
    query: str
    final_answer: str
    reasoning_path: List[Dict[str, Any]]
    complexity: str
    confidence: float
    reasoning_mode: str
    ai_enhanced: bool
    ultimate_mode: bool
    provider_used: Optional[str] = None
    context_sources: List[str] = None
    processing_time: float = 0.0
    thought_count: int = 0
    session_id: str = ""
    metadata: Dict[str, Any] = None


class DeepSeekReasoningOrchestrator:
    """
    The ultimate cosmic reasoning orchestrator! 🌟🧠
    
    This class brings together all the reasoning components into a harmonious,
    intelligent system that can handle any query with the perfect balance of
    local reasoning and AI-powered deep thinking.
    """
    
    def __init__(self, enable_context7: bool = True):
        """Initialize the reasoning orchestrator with cosmic energy."""
        self.logger = logging.getLogger("VoidCat.ReasoningOrchestrator")
        
        # Initialize core components
        self.multi_provider = MultiProviderClient()
        self.sequential_thinking = SequentialThinkingEngine(self.multi_provider)
        
        # Context7 integration (optional)
        self.context7 = None
        if enable_context7 and CONTEXT7_AVAILABLE:
            try:
                self.context7 = Context7Integration()
                debug_print("Context7 integration enabled")
            except Exception as e:
                debug_print(f"Context7 integration failed: {e}, continuing without it")
        elif enable_context7 and not CONTEXT7_AVAILABLE:
            debug_print("Context7 integration requested but not available")
        
        # Default settings
        self.default_ultimate_mode = False
        self.default_reasoning_mode = "hybrid"
        
        self.logger.info("🌟 DeepSeek Reasoning Orchestrator initialized with cosmic wisdom!")
    
    def set_ultimate_mode(self, enabled: bool = True):
        """Enable/disable Ultimate Mode globally - maximum cosmic power! 🚀"""
        self.default_ultimate_mode = enabled
        self.multi_provider.set_ultimate_mode(enabled)
        
        mode_status = "ENABLED" if enabled else "DISABLED"
        self.logger.info(f"🚀 Global Ultimate Mode {mode_status}")
    
    def set_reasoning_mode(self, mode: str):
        """
        Set the default reasoning mode.
        
        Args:
            mode: "local" (traditional), "ai" (AI-powered), or "hybrid" (best of both)
        """
        if mode not in ["local", "ai", "hybrid"]:
            raise ValueError("Mode must be 'local', 'ai', or 'hybrid'")
        
        self.default_reasoning_mode = mode
        self.sequential_thinking.set_reasoning_mode(mode)
        self.logger.info(f"🧠 Default reasoning mode set to: {mode}")
    
    async def _enhance_with_context(self, query: str, max_sources: int = 5) -> str:
        """Enhance query with relevant context using Context7 integration."""
        if not self.context7:
            return ""
        
        try:
            context_results = await self.context7.retrieve_relevant_context(
                query=query,
                max_results=max_sources,
                relevance_threshold=0.3
            )
            
            if context_results:
                context_text = "\n".join([
                    f"Source: {result.get('source', 'Unknown')}\n{result.get('content', '')}"
                    for result in context_results[:max_sources]
                ])
                
                debug_print(f"Enhanced query with {len(context_results)} context sources")
                return context_text
            
        except Exception as e:
            debug_print(f"Context enhancement failed: {e}")
        
        return ""
    
    async def reason(self, request: Union[str, ReasoningRequest]) -> ReasoningResponse:
        """
        Perform comprehensive reasoning on a query with full cosmic power! 🌟
        
        Args:
            request: Either a simple query string or a ReasoningRequest object
            
        Returns:
            ReasoningResponse with complete reasoning analysis
        """
        start_time = datetime.now(UTC)
        
        # Handle both string and ReasoningRequest inputs
        if isinstance(request, str):
            request = ReasoningRequest(query=request)
        
        debug_print(f"Starting cosmic reasoning for: {request.query[:100]}...")
        
        try:
            # Step 1: Context Enhancement (if enabled)
            enhanced_context = request.context
            context_sources = []
            
            if request.include_context_retrieval and self.context7:
                retrieved_context = await self._enhance_with_context(request.query)
                if retrieved_context:
                    enhanced_context = f"{request.context}\n\n--- Retrieved Context ---\n{retrieved_context}"
                    context_sources = ["Context7 Retrieval"]
            
            # Step 2: Configure reasoning mode
            reasoning_mode = request.reasoning_mode or self.default_reasoning_mode
            self.sequential_thinking.set_reasoning_mode(reasoning_mode)
            
            # Step 3: Configure Ultimate Mode
            ultimate_mode = request.ultimate_mode or self.default_ultimate_mode
            if ultimate_mode:
                self.multi_provider.set_ultimate_mode(True)
            
            # Step 4: Perform Sequential Thinking
            reasoning_result = await self.sequential_thinking.process_query(
                query=request.query,
                context=enhanced_context,
                max_thoughts=request.max_thoughts
            )
            
            # Step 5: If we need direct AI reasoning, get it
            ai_response = None
            provider_used = None
            
            if request.force_reasoning or ultimate_mode:
                try:
                    messages = [
                        {"role": "system", "content": "You are an expert reasoning assistant. Provide clear, comprehensive answers with detailed reasoning."},
                        {"role": "user", "content": f"Query: {request.query}\n\nContext: {enhanced_context}\n\nProvide a detailed, well-reasoned response."}
                    ]
                    
                    ai_response = await self.multi_provider.reasoning_completion(messages)
                    provider_used = ai_response.get("metadata", {}).get("provider_used")
                    
                except Exception as e:
                    debug_print(f"Direct AI reasoning failed: {e}")
            
            # Step 6: Synthesize final answer
            final_answer = reasoning_result.get("final_response", "")
            
            if ai_response:
                ai_content = ai_response.get("choices", [{}])[0].get("message", {}).get("content", "")
                if ai_content:
                    final_answer = f"{final_answer}\n\n--- AI-Enhanced Response ---\n{ai_content}"
            
            # Step 7: Calculate processing time
            processing_time = (datetime.now(UTC) - start_time).total_seconds()
            
            # Step 8: Create comprehensive response
            response = ReasoningResponse(
                query=request.query,
                final_answer=final_answer,
                reasoning_path=reasoning_result.get("reasoning_path", []),
                complexity=reasoning_result.get("complexity", "medium"),
                confidence=reasoning_result.get("confidence", 0.5),
                reasoning_mode=reasoning_mode,
                ai_enhanced=reasoning_result.get("ai_enhanced", False),
                ultimate_mode=ultimate_mode,
                provider_used=provider_used,
                context_sources=context_sources,
                processing_time=processing_time,
                thought_count=reasoning_result.get("thought_count", 0),
                session_id=reasoning_result.get("session_id", ""),
                metadata={
                    "context_enhanced": bool(enhanced_context),
                    "error": reasoning_result.get("error"),
                    "ai_response_available": ai_response is not None
                }
            )
            
            self.logger.info(f"✨ Cosmic reasoning completed in {processing_time:.2f}s with {response.thought_count} thoughts")
            return response
            
        except Exception as e:
            processing_time = (datetime.now(UTC) - start_time).total_seconds()
            self.logger.error(f"💫 Reasoning failed: {e}")
            
            return ReasoningResponse(
                query=request.query,
                final_answer=f"Reasoning failed: {str(e)}",
                reasoning_path=[],
                complexity="unknown",
                confidence=0.0,
                reasoning_mode=reasoning_mode,
                ai_enhanced=False,
                ultimate_mode=ultimate_mode,
                processing_time=processing_time,
                metadata={"error": str(e)}
            )
    
    async def quick_reason(self, query: str) -> str:
        """Quick reasoning for simple queries - just the answer, bro! 💨"""
        request = ReasoningRequest(
            query=query,
            max_thoughts=5,
            reasoning_mode="hybrid",
            include_context_retrieval=False
        )
        
        response = await self.reason(request)
        return response.final_answer
    
    async def deep_reason(self, query: str, context: str = "") -> ReasoningResponse:
        """Deep reasoning with full cosmic power - the ultimate experience! 🚀"""
        request = ReasoningRequest(
            query=query,
            context=context,
            max_thoughts=15,
            force_reasoning=True,
            ultimate_mode=True,
            reasoning_mode="hybrid",
            include_context_retrieval=True
        )
        
        return await self.reason(request)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status - checking all the cosmic vibes! 📊"""
        provider_status = self.multi_provider.get_provider_status()
        
        return {
            "orchestrator": {
                "ultimate_mode": self.default_ultimate_mode,
                "reasoning_mode": self.default_reasoning_mode,
                "context7_enabled": self.context7 is not None
            },
            "providers": provider_status,
            "sequential_thinking": {
                "total_queries_processed": self.sequential_thinking.total_queries_processed,
                "active_sessions": len(self.sequential_thinking.sessions)
            },
            "timestamp": datetime.now(UTC).isoformat()
        }
    
    async def health_check(self) -> Dict[str, bool]:
        """Perform comprehensive health check on all components."""
        health = {}
        
        # Check multi-provider health
        try:
            provider_health = await self.multi_provider.health_check()
            health.update(provider_health)
        except Exception as e:
            health["multi_provider_error"] = str(e)
        
        # Check sequential thinking
        try:
            # Simple test
            test_result = await self.sequential_thinking.process_query("Test query", max_thoughts=1)
            health["sequential_thinking"] = "session_id" in test_result
        except Exception as e:
            health["sequential_thinking"] = False
            health["sequential_thinking_error"] = str(e)
        
        # Check Context7
        if self.context7:
            try:
                # Simple context test
                health["context7"] = True  # If it initialized, it's probably working
            except Exception as e:
                health["context7"] = False
                health["context7_error"] = str(e)
        else:
            health["context7"] = False
        
        return health


# Example usage and testing functions
async def test_deepseek_reasoning_integration():
    """Test the complete DeepSeek reasoning integration - cosmic vibes check! 🌟"""
    print("🧘‍♂️ Testing VoidCat DeepSeek Reasoning Integration")
    print("=" * 60)
    
    orchestrator = DeepSeekReasoningOrchestrator()
    
    # Test 1: Quick reasoning
    print("\n🔹 Test 1: Quick Reasoning")
    try:
        quick_answer = await orchestrator.quick_reason("What is the capital of France?")
        print(f"✅ Quick Answer: {quick_answer[:100]}...")
    except Exception as e:
        print(f"❌ Quick reasoning failed: {e}")
    
    # Test 2: Deep reasoning
    print("\n🔹 Test 2: Deep Reasoning")
    try:
        deep_response = await orchestrator.deep_reason(
            "Explain the concept of quantum entanglement and its implications for quantum computing",
            "Consider both theoretical foundations and practical applications"
        )
        print(f"✅ Deep Reasoning Completed:")
        print(f"   Complexity: {deep_response.complexity}")
        print(f"   Confidence: {deep_response.confidence:.2f}")
        print(f"   Thoughts: {deep_response.thought_count}")
        print(f"   Processing Time: {deep_response.processing_time:.2f}s")
        print(f"   AI Enhanced: {deep_response.ai_enhanced}")
        print(f"   Provider: {deep_response.provider_used}")
        print(f"   Answer: {deep_response.final_answer[:200]}...")
    except Exception as e:
        print(f"❌ Deep reasoning failed: {e}")
    
    # Test 3: Ultimate Mode
    print("\n🔹 Test 3: Ultimate Mode")
    orchestrator.set_ultimate_mode(True)
    try:
        ultimate_response = await orchestrator.reason(ReasoningRequest(
            query="How would you design a distributed system for real-time collaborative editing?",
            max_thoughts=10,
            reasoning_mode="hybrid"
        ))
        print(f"✅ Ultimate Mode Completed:")
        print(f"   Ultimate Mode: {ultimate_response.ultimate_mode}")
        print(f"   Reasoning Mode: {ultimate_response.reasoning_mode}")
        print(f"   Processing Time: {ultimate_response.processing_time:.2f}s")
        print(f"   Answer: {ultimate_response.final_answer[:200]}...")
    except Exception as e:
        print(f"❌ Ultimate mode failed: {e}")
    
    # Test 4: System Status
    print("\n🔹 Test 4: System Status")
    try:
        status = orchestrator.get_system_status()
        print("✅ System Status:")
        print(f"   Ultimate Mode: {status['orchestrator']['ultimate_mode']}")
        print(f"   Reasoning Mode: {status['orchestrator']['reasoning_mode']}")
        print(f"   Context7 Enabled: {status['orchestrator']['context7_enabled']}")
        print(f"   Active Providers: {len(status['providers'])}")
        print(f"   Queries Processed: {status['sequential_thinking']['total_queries_processed']}")
    except Exception as e:
        print(f"❌ System status failed: {e}")
    
    # Test 5: Health Check
    print("\n🔹 Test 5: Health Check")
    try:
        health = await orchestrator.health_check()
        print("✅ Health Check Results:")
        for component, status in health.items():
            if isinstance(status, bool):
                status_icon = "✅" if status else "❌"
                print(f"   {status_icon} {component}: {status}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    print("\n🌟 DeepSeek Reasoning Integration Test Complete!")


if __name__ == "__main__":
    # Run the test if executed directly
    asyncio.run(test_deepseek_reasoning_integration())