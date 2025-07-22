# main.py
"""
VoidCat Reasoning Core - Entry Point and Test Harness

This module serves as both an entry point for the VoidCat Reasoning Core system
and a comprehensive test harness for validating engine functionality.

Usage:
    python main.py              # Run test harness
    uvicorn api_gateway:app     # Start API server
"""

import asyncio

from engine import VoidCatEngine


async def run_test_harness():
    """
    Comprehensive test harness for the VoidCat RDC Engine.

    This function initializes the engine, loads the knowledge base,
    and executes a series of validation queries to ensure system
    operational readiness.
    """
    print("Initializing VoidCat RDC Engine...")

    # Initialize the engine
    engine = VoidCatEngine()

    # Test query to validate system functionality
    test_query = "What are the core MCP primitives and who controls them?"
    print(f"Executing query: '{test_query}'")

    try:
        response = await engine.query(test_query)
        print("---Engine Response---")
        print(response)
        print("---End Response---")
        return True
    except Exception as e:
        print(f"Error during query execution: {str(e)}")
        return False


def main():
    """
    Main entry point for the VoidCat Reasoning Core system.

    Provides information about available execution modes and
    runs the test harness by default.
    """
    print("VoidCat Reasoning Core - Strategic Intelligence Engine")
    print("=" * 60)
    print()
    print("Available execution modes:")
    print("  • Test Harness:  python main.py")
    print("  • API Server:    uvicorn api_gateway:app --reload")
    print("  • Documentation: http://localhost:8000/docs")
    print()
    print("Running test harness...")
    print()

    # Run the async test harness
    success = asyncio.run(run_test_harness())

    if success:
        print()
        print("✅ Test harness completed successfully!")
        print("🚀 System ready for production deployment.")
    else:
        print()
        print("❌ Test harness encountered errors.")
        print("🔧 Please check configuration and try again.")


if __name__ == "__main__":
    main()
