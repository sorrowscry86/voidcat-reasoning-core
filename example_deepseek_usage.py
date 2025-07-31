#!/usr/bin/env python3
"""
VoidCat DeepSeek-R1 Usage Examples - Cosmic Reasoning in Action! 🌟🧠

This script demonstrates practical usage of the enhanced VoidCat Reasoning Core
with DeepSeek-R1 integration. Perfect for learning and experimentation!

Author: Codey Jr. - The Example Master 🤙
License: MIT
Version: 1.0.0 - "The Practical Guide"
"""

import asyncio
import time
from deepseek_reasoning_integration import DeepSeekReasoningOrchestrator, ReasoningRequest


async def example_1_basic_usage():
    """Example 1: Basic usage patterns"""
    print("🔹 Example 1: Basic Usage Patterns")
    print("-" * 40)
    
    orchestrator = DeepSeekReasoningOrchestrator(enable_context7=False)
    
    # Quick reasoning for simple questions
    print("💨 Quick Reasoning:")
    start_time = time.time()
    answer = await orchestrator.quick_reason("What are the main benefits of using Python?")
    elapsed = time.time() - start_time
    print(f"   Time: {elapsed:.2f}s")
    print(f"   Answer: {answer[:200]}...")
    
    print("\n🧠 Deep Reasoning:")
    start_time = time.time()
    response = await orchestrator.deep_reason(
        "Compare Python and JavaScript for web development, considering performance, ecosystem, and learning curve"
    )
    elapsed = time.time() - start_time
    print(f"   Time: {elapsed:.2f}s")
    print(f"   Complexity: {response.complexity}")
    print(f"   Confidence: {response.confidence:.2f}")
    print(f"   Thoughts: {response.thought_count}")
    print(f"   Answer: {response.final_answer[:300]}...")


async def example_2_reasoning_modes():
    """Example 2: Different reasoning modes"""
    print("\n🔹 Example 2: Reasoning Modes Comparison")
    print("-" * 40)
    
    orchestrator = DeepSeekReasoningOrchestrator(enable_context7=False)
    query = "How would you design a caching system for a high-traffic web application?"
    
    modes = ["local", "hybrid", "ai"]
    
    for mode in modes:
        print(f"\n🧘‍♂️ {mode.upper()} Mode:")
        orchestrator.set_reasoning_mode(mode)
        
        start_time = time.time()
        response = await orchestrator.reason(ReasoningRequest(
            query=query,
            max_thoughts=5,
            reasoning_mode=mode
        ))
        elapsed = time.time() - start_time
        
        print(f"   Time: {elapsed:.2f}s")
        print(f"   AI Enhanced: {response.ai_enhanced}")
        print(f"   Thoughts: {response.thought_count}")
        print(f"   Answer: {response.final_answer[:200]}...")


async def example_3_ultimate_mode():
    """Example 3: Ultimate Mode demonstration"""
    print("\n🔹 Example 3: Ultimate Mode - Maximum Cosmic Power!")
    print("-" * 40)
    
    orchestrator = DeepSeekReasoningOrchestrator(enable_context7=False)
    
    # Regular mode
    print("🌟 Regular Mode:")
    response = await orchestrator.reason("Hello, how are you?")
    print(f"   Ultimate Mode: {response.ultimate_mode}")
    print(f"   Provider: {response.provider_used}")
    print(f"   Answer: {response.final_answer[:150]}...")
    
    # Ultimate mode
    print("\n🚀 ULTIMATE MODE ACTIVATED:")
    orchestrator.set_ultimate_mode(True)
    response = await orchestrator.reason("Hello, how are you?")
    print(f"   Ultimate Mode: {response.ultimate_mode}")
    print(f"   Provider: {response.provider_used}")
    print(f"   AI Enhanced: {response.ai_enhanced}")
    print(f"   Answer: {response.final_answer[:150]}...")
    
    # Reset for other examples
    orchestrator.set_ultimate_mode(False)


async def example_4_complex_reasoning():
    """Example 4: Complex reasoning scenarios"""
    print("\n🔹 Example 4: Complex Reasoning Scenarios")
    print("-" * 40)
    
    orchestrator = DeepSeekReasoningOrchestrator(enable_context7=False)
    
    complex_scenarios = [
        {
            "title": "System Design",
            "query": "Design a microservices architecture for an e-commerce platform. Consider scalability, data consistency, and fault tolerance.",
            "context": "The platform needs to handle 100k+ concurrent users with real-time inventory updates."
        },
        {
            "title": "Algorithm Optimization",
            "query": "Optimize a sorting algorithm for a dataset with mostly sorted data but occasional random elements.",
            "context": "The dataset size varies from 1K to 10M elements, and memory usage is a concern."
        },
        {
            "title": "Business Strategy",
            "query": "Analyze the pros and cons of implementing AI-powered customer service vs human agents.",
            "context": "Consider cost, customer satisfaction, scalability, and implementation complexity."
        }
    ]
    
    for i, scenario in enumerate(complex_scenarios, 1):
        print(f"\n🎯 Scenario {i}: {scenario['title']}")
        
        start_time = time.time()
        response = await orchestrator.reason(ReasoningRequest(
            query=scenario['query'],
            context=scenario['context'],
            max_thoughts=10,
            reasoning_mode="hybrid"
        ))
        elapsed = time.time() - start_time
        
        print(f"   Processing Time: {elapsed:.2f}s")
        print(f"   Complexity: {response.complexity}")
        print(f"   Confidence: {response.confidence:.2f}")
        print(f"   Reasoning Branches: {len(response.reasoning_path)}")
        print(f"   Total Thoughts: {response.thought_count}")
        print(f"   AI Enhanced: {response.ai_enhanced}")
        print(f"   Summary: {response.final_answer[:250]}...")


async def example_5_monitoring_and_diagnostics():
    """Example 5: System monitoring and diagnostics"""
    print("\n🔹 Example 5: System Monitoring & Diagnostics")
    print("-" * 40)
    
    orchestrator = DeepSeekReasoningOrchestrator(enable_context7=False)
    
    # Perform some reasoning to generate metrics
    await orchestrator.quick_reason("Test query for metrics")
    
    print("📊 System Status:")
    status = orchestrator.get_system_status()
    
    # Orchestrator status
    orch_status = status['orchestrator']
    print(f"   Ultimate Mode: {orch_status['ultimate_mode']}")
    print(f"   Reasoning Mode: {orch_status['reasoning_mode']}")
    print(f"   Context7 Enabled: {orch_status['context7_enabled']}")
    
    # Provider status
    print("\n🔌 Provider Performance:")
    for provider, info in status['providers'].items():
        metrics = info['metrics']
        print(f"   {provider}:")
        print(f"      Status: {info['status']}")
        print(f"      Success Rate: {metrics['success_rate']:.1f}%")
        print(f"      Total Requests: {metrics['total_requests']}")
        print(f"      Avg Response Time: {metrics['average_response_time']:.2f}s")
    
    # Health check
    print("\n🏥 Health Check:")
    health = await orchestrator.health_check()
    for component, is_healthy in health.items():
        if isinstance(is_healthy, bool):
            status_icon = "✅" if is_healthy else "❌"
            print(f"   {status_icon} {component}")


async def example_6_error_handling():
    """Example 6: Error handling and fallback strategies"""
    print("\n🔹 Example 6: Error Handling & Fallback Strategies")
    print("-" * 40)
    
    orchestrator = DeepSeekReasoningOrchestrator(enable_context7=False)
    
    # Simulate various scenarios
    test_cases = [
        "Normal query that should work fine",
        "A very complex query that might challenge the system with multiple layers of reasoning and analysis",
        "",  # Empty query
        "Query with special characters: !@#$%^&*()",
    ]
    
    for i, query in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {query[:50]}{'...' if len(query) > 50 else ''}")
        
        try:
            start_time = time.time()
            response = await orchestrator.reason(ReasoningRequest(
                query=query,
                max_thoughts=5,
                reasoning_mode="hybrid"
            ))
            elapsed = time.time() - start_time
            
            print(f"   ✅ Success in {elapsed:.2f}s")
            print(f"   Provider: {response.provider_used}")
            print(f"   Confidence: {response.confidence:.2f}")
            
            if response.metadata and response.metadata.get('error'):
                print(f"   ⚠️ Warning: {response.metadata['error']}")
            
        except Exception as e:
            print(f"   ❌ Failed: {str(e)}")
            
            # Demonstrate fallback strategy
            try:
                print("   🔄 Trying fallback approach...")
                fallback_response = await orchestrator.quick_reason(query or "What is AI?")
                print(f"   ✅ Fallback successful: {fallback_response[:100]}...")
            except Exception as fallback_error:
                print(f"   ❌ Fallback also failed: {fallback_error}")


async def example_7_performance_comparison():
    """Example 7: Performance comparison between approaches"""
    print("\n🔹 Example 7: Performance Comparison")
    print("-" * 40)
    
    orchestrator = DeepSeekReasoningOrchestrator(enable_context7=False)
    test_query = "Explain the concept of machine learning and its applications"
    
    approaches = [
        ("Quick Reasoning", lambda: orchestrator.quick_reason(test_query)),
        ("Standard Reasoning", lambda: orchestrator.reason(ReasoningRequest(query=test_query, max_thoughts=5))),
        ("Deep Reasoning", lambda: orchestrator.deep_reason(test_query)),
    ]
    
    print("🏁 Performance Race:")
    results = []
    
    for name, approach in approaches:
        print(f"\n⏱️ Testing {name}...")
        
        start_time = time.time()
        try:
            if name == "Quick Reasoning":
                result = await approach()
                elapsed = time.time() - start_time
                
                print(f"   Time: {elapsed:.2f}s")
                print(f"   Length: {len(result)} chars")
                print(f"   Speed: {len(result)/elapsed:.0f} chars/sec")
                results.append((name, elapsed, len(result)))
                
            else:
                result = await approach()
                elapsed = time.time() - start_time
                
                print(f"   Time: {elapsed:.2f}s")
                print(f"   Thoughts: {result.thought_count}")
                print(f"   Confidence: {result.confidence:.2f}")
                print(f"   Length: {len(result.final_answer)} chars")
                print(f"   Speed: {len(result.final_answer)/elapsed:.0f} chars/sec")
                results.append((name, elapsed, len(result.final_answer)))
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            results.append((name, float('inf'), 0))
    
    # Summary
    print("\n🏆 Performance Summary:")
    results.sort(key=lambda x: x[1])  # Sort by time
    for i, (name, time_taken, length) in enumerate(results, 1):
        if time_taken != float('inf'):
            print(f"   {i}. {name}: {time_taken:.2f}s ({length} chars)")
        else:
            print(f"   {i}. {name}: Failed")


async def main():
    """Run all examples"""
    print("🧘‍♂️ VoidCat DeepSeek-R1 Usage Examples")
    print("🌟 Exploring cosmic reasoning capabilities...")
    print("=" * 60)
    
    examples = [
        ("Basic Usage Patterns", example_1_basic_usage),
        ("Reasoning Modes", example_2_reasoning_modes),
        ("Ultimate Mode", example_3_ultimate_mode),
        ("Complex Reasoning", example_4_complex_reasoning),
        ("Monitoring & Diagnostics", example_5_monitoring_and_diagnostics),
        ("Error Handling", example_6_error_handling),
        ("Performance Comparison", example_7_performance_comparison),
    ]
    
    for example_name, example_func in examples:
        try:
            await example_func()
            print(f"\n✅ {example_name} completed successfully!")
        except Exception as e:
            print(f"\n❌ {example_name} failed: {e}")
        
        # Small pause between examples
        await asyncio.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("🎉 All examples completed!")
    print("🚀 Your cosmic reasoning system is ready to rock!")
    print("🧘‍♂️ May the reasoning force be with you!")


if __name__ == "__main__":
    # Run all examples
    asyncio.run(main())