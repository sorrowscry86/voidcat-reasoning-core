#!/usr/bin/env python3
"""
VoidCat DeepSeek Reasoning Demo - Showcasing Cosmic Intelligence! 🌟🧠

This demo script showcases the enhanced VoidCat Reasoning Core with DeepSeek-R1 integration.
Experience the power of intelligent routing, hybrid reasoning, and Ultimate Mode!

Author: Codey Jr. - The Chill Demo Master 🤙
License: MIT
Version: 1.0.0 - "The Cosmic Demo"
"""

import asyncio
import time
from datetime import datetime

from deepseek_reasoning_integration import DeepSeekReasoningOrchestrator, ReasoningRequest


def print_header(title: str):
    """Print a cosmic header for demo sections."""
    print("\n" + "=" * 70)
    print(f"🌟 {title}")
    print("=" * 70)


def print_section(title: str):
    """Print a section header."""
    print(f"\n🔹 {title}")
    print("-" * 50)


async def demo_simple_vs_complex_routing():
    """Demonstrate intelligent routing between chat and reasoning models."""
    print_header("INTELLIGENT MODEL ROUTING DEMO")
    
    orchestrator = DeepSeekReasoningOrchestrator()
    
    # Simple query - should use chat model
    print_section("Simple Query (Chat Model Expected)")
    simple_query = "What is Python?"
    
    start_time = time.time()
    response = await orchestrator.reason(ReasoningRequest(
        query=simple_query,
        reasoning_mode="hybrid",
        max_thoughts=3
    ))
    
    print(f"Query: {simple_query}")
    print(f"Provider Used: {response.provider_used}")
    print(f"Complexity: {response.complexity}")
    print(f"Processing Time: {response.processing_time:.2f}s")
    print(f"Answer: {response.final_answer[:200]}...")
    
    # Complex query - should use reasoning model
    print_section("Complex Query (Reasoning Model Expected)")
    complex_query = "Analyze the trade-offs between microservices and monolithic architectures, considering scalability, maintainability, deployment complexity, and team organization. Provide a decision framework for choosing between them."
    
    start_time = time.time()
    response = await orchestrator.reason(ReasoningRequest(
        query=complex_query,
        reasoning_mode="hybrid",
        max_thoughts=8
    ))
    
    print(f"Query: {complex_query[:100]}...")
    print(f"Provider Used: {response.provider_used}")
    print(f"Complexity: {response.complexity}")
    print(f"AI Enhanced: {response.ai_enhanced}")
    print(f"Thought Count: {response.thought_count}")
    print(f"Processing Time: {response.processing_time:.2f}s")
    print(f"Answer: {response.final_answer[:300]}...")


async def demo_reasoning_modes():
    """Demonstrate different reasoning modes."""
    print_header("REASONING MODES COMPARISON")
    
    orchestrator = DeepSeekReasoningOrchestrator()
    test_query = "How would you implement a rate limiter for a high-traffic API?"
    
    modes = ["local", "ai", "hybrid"]
    
    for mode in modes:
        print_section(f"{mode.upper()} Reasoning Mode")
        
        start_time = time.time()
        response = await orchestrator.reason(ReasoningRequest(
            query=test_query,
            reasoning_mode=mode,
            max_thoughts=6
        ))
        
        print(f"Mode: {response.reasoning_mode}")
        print(f"AI Enhanced: {response.ai_enhanced}")
        print(f"Thought Count: {response.thought_count}")
        print(f"Confidence: {response.confidence:.2f}")
        print(f"Processing Time: {response.processing_time:.2f}s")
        print(f"Answer: {response.final_answer[:250]}...")


async def demo_ultimate_mode():
    """Demonstrate Ultimate Mode - maximum cosmic power!"""
    print_header("ULTIMATE MODE DEMO - MAXIMUM COSMIC POWER! 🚀")
    
    orchestrator = DeepSeekReasoningOrchestrator()
    
    # Regular mode first
    print_section("Regular Mode")
    query = "Hello, how are you today?"
    
    response = await orchestrator.reason(ReasoningRequest(
        query=query,
        ultimate_mode=False,
        max_thoughts=3
    ))
    
    print(f"Ultimate Mode: {response.ultimate_mode}")
    print(f"Provider Used: {response.provider_used}")
    print(f"Processing Time: {response.processing_time:.2f}s")
    print(f"Answer: {response.final_answer[:200]}...")
    
    # Ultimate mode
    print_section("ULTIMATE MODE ACTIVATED! 🚀")
    
    response = await orchestrator.reason(ReasoningRequest(
        query=query,
        ultimate_mode=True,
        max_thoughts=5
    ))
    
    print(f"Ultimate Mode: {response.ultimate_mode}")
    print(f"Provider Used: {response.provider_used}")
    print(f"AI Enhanced: {response.ai_enhanced}")
    print(f"Processing Time: {response.processing_time:.2f}s")
    print(f"Answer: {response.final_answer[:200]}...")


async def demo_deep_reasoning():
    """Demonstrate deep reasoning capabilities."""
    print_header("DEEP REASONING SHOWCASE")
    
    orchestrator = DeepSeekReasoningOrchestrator()
    
    deep_query = """
    Design a comprehensive strategy for implementing zero-trust security architecture 
    in a large enterprise with legacy systems, cloud infrastructure, and remote workforce. 
    Consider technical implementation, organizational change management, compliance requirements, 
    and phased rollout approach.
    """
    
    print_section("Deep Reasoning Analysis")
    print(f"Query: {deep_query.strip()}")
    
    start_time = time.time()
    response = await orchestrator.deep_reason(deep_query)
    
    print(f"\n📊 Deep Reasoning Results:")
    print(f"   Complexity: {response.complexity}")
    print(f"   Confidence: {response.confidence:.2f}")
    print(f"   Thought Count: {response.thought_count}")
    print(f"   AI Enhanced: {response.ai_enhanced}")
    print(f"   Ultimate Mode: {response.ultimate_mode}")
    print(f"   Provider Used: {response.provider_used}")
    print(f"   Processing Time: {response.processing_time:.2f}s")
    print(f"   Context Sources: {response.context_sources}")
    
    print(f"\n📝 Reasoning Path:")
    for i, branch in enumerate(response.reasoning_path):
        print(f"   Branch {i+1}: {branch.get('description', 'Unknown')}")
        print(f"   Thoughts: {len(branch.get('thoughts', []))}")
    
    print(f"\n🎯 Final Answer:")
    print(response.final_answer[:500] + "..." if len(response.final_answer) > 500 else response.final_answer)


async def demo_system_diagnostics():
    """Demonstrate system diagnostics and monitoring."""
    print_header("SYSTEM DIAGNOSTICS & MONITORING")
    
    orchestrator = DeepSeekReasoningOrchestrator()
    
    # System status
    print_section("System Status")
    status = orchestrator.get_system_status()
    
    print("🔧 Orchestrator Configuration:")
    for key, value in status["orchestrator"].items():
        print(f"   {key}: {value}")
    
    print("\n🔌 Provider Status:")
    for provider, info in status["providers"].items():
        print(f"   {provider}:")
        print(f"      Status: {info['status']}")
        print(f"      Success Rate: {info['metrics']['success_rate']:.1f}%")
        print(f"      Total Requests: {info['metrics']['total_requests']}")
        print(f"      Avg Response Time: {info['metrics']['average_response_time']:.2f}s")
    
    print("\n🧠 Sequential Thinking:")
    st_info = status["sequential_thinking"]
    for key, value in st_info.items():
        print(f"   {key}: {value}")
    
    # Health check
    print_section("Health Check")
    health = await orchestrator.health_check()
    
    print("🏥 Component Health:")
    for component, status in health.items():
        if isinstance(status, bool):
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {component}: {'Healthy' if status else 'Unhealthy'}")
        elif "error" in component:
            print(f"   ⚠️  {component}: {status}")


async def demo_performance_comparison():
    """Demonstrate performance comparison between different approaches."""
    print_header("PERFORMANCE COMPARISON")
    
    orchestrator = DeepSeekReasoningOrchestrator()
    test_query = "Explain the benefits and drawbacks of using Docker containers in production environments."
    
    approaches = [
        ("Quick Reasoning", lambda: orchestrator.quick_reason(test_query)),
        ("Standard Reasoning", lambda: orchestrator.reason(ReasoningRequest(query=test_query, max_thoughts=5))),
        ("Deep Reasoning", lambda: orchestrator.deep_reason(test_query)),
    ]
    
    results = []
    
    for name, approach in approaches:
        print_section(f"{name} Performance Test")
        
        start_time = time.time()
        try:
            if name == "Quick Reasoning":
                result = await approach()
                response_time = time.time() - start_time
                print(f"✅ {name}:")
                print(f"   Processing Time: {response_time:.2f}s")
                print(f"   Answer Length: {len(result)} characters")
                print(f"   Answer: {result[:150]}...")
                results.append((name, response_time, len(result)))
            else:
                result = await approach()
                print(f"✅ {name}:")
                print(f"   Processing Time: {result.processing_time:.2f}s")
                print(f"   Thought Count: {result.thought_count}")
                print(f"   Confidence: {result.confidence:.2f}")
                print(f"   Answer Length: {len(result.final_answer)} characters")
                print(f"   Answer: {result.final_answer[:150]}...")
                results.append((name, result.processing_time, len(result.final_answer)))
        except Exception as e:
            print(f"❌ {name} failed: {e}")
            results.append((name, 0, 0))
    
    # Summary
    print_section("Performance Summary")
    print("📊 Comparison Results:")
    for name, time_taken, answer_length in results:
        print(f"   {name}:")
        print(f"      Time: {time_taken:.2f}s")
        print(f"      Answer Length: {answer_length} chars")
        print(f"      Speed: {answer_length/max(time_taken, 0.01):.0f} chars/sec")


async def main():
    """Run the complete DeepSeek reasoning demo."""
    print("🧘‍♂️ Welcome to the VoidCat DeepSeek Reasoning Demo!")
    print("🌟 Prepare to witness the cosmic power of enhanced AI reasoning!")
    print(f"🕐 Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    demos = [
        ("Intelligent Model Routing", demo_simple_vs_complex_routing),
        ("Reasoning Modes Comparison", demo_reasoning_modes),
        ("Ultimate Mode Showcase", demo_ultimate_mode),
        ("Deep Reasoning Capabilities", demo_deep_reasoning),
        ("System Diagnostics", demo_system_diagnostics),
        ("Performance Comparison", demo_performance_comparison),
    ]
    
    for demo_name, demo_func in demos:
        try:
            await demo_func()
            print(f"\n✅ {demo_name} completed successfully!")
        except Exception as e:
            print(f"\n❌ {demo_name} failed: {e}")
        
        # Small pause between demos
        await asyncio.sleep(1)
    
    print_header("DEMO COMPLETE - COSMIC VIBES ACHIEVED! 🌟")
    print("🎉 The VoidCat DeepSeek Reasoning integration is ready to rock!")
    print("🚀 Your AI reasoning capabilities have been elevated to cosmic levels!")
    print("🧘‍♂️ May the code be with you, and the reasoning flow through you!")


if __name__ == "__main__":
    # Run the complete demo
    asyncio.run(main())