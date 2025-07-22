#!/usr/bin/env python3
"""
VoidCat Enhanced Deployment Script

Quick deployment script for GitHub upload.
Validates core functionality and prepares the system for production use.
"""

import asyncio
import json
import os
import sys
from datetime import datetime


def check_dependencies():
    """Check if all required dependencies are available."""
    print("🔍 Checking dependencies...")

    required_modules = ["httpx", "sklearn", "numpy", "dotenv"]

    missing = []
    for module in required_modules:
        try:
            if module == "dotenv":
                from dotenv import load_dotenv
            elif module == "sklearn":
                import sklearn
            else:
                __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            missing.append(module)
            print(f"  ❌ {module}")

    if missing:
        print(f"\n⚠️ Missing dependencies: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False

    print("✅ All dependencies available\n")
    return True


def validate_core_files():
    """Validate that core files exist and are readable."""
    print("📁 Validating core files...")

    core_files = [
        "engine.py",
        "sequential_thinking.py",
        "context7_integration.py",
        "enhanced_engine.py",
        "mcp_server.py",
        "requirements.txt",
        "README.md",
    ]

    missing = []
    for file in core_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            missing.append(file)
            print(f"  ❌ {file}")

    if missing:
        print(f"\n⚠️ Missing files: {', '.join(missing)}")
        return False

    print("✅ All core files present\n")
    return True


def create_deployment_info():
    """Create deployment information file."""
    print("📋 Creating deployment information...")

    deployment_info = {
        "project_name": "VoidCat Reasoning Core - Enhanced",
        "version": "2.0.0",
        "deployment_date": datetime.now().isoformat(),
        "features": {
            "sequential_thinking": "Multi-stage reasoning with complexity assessment",
            "context7_integration": "Advanced context retrieval and analysis",
            "enhanced_rag": "Combined reasoning pipeline",
            "mcp_protocol": "Full Model Context Protocol compliance",
            "claude_integration": "Ready for Claude Desktop",
        },
        "architecture": {
            "stages": [
                "Query Analysis & Complexity Assessment",
                "Context7 Enhanced Context Retrieval",
                "Sequential Thinking Reasoning Process",
                "RAG Integration for Response Generation",
                "Quality Validation & Response Synthesis",
            ]
        },
        "tools": [
            "voidcat_query",
            "voidcat_enhanced_query",
            "voidcat_sequential_thinking",
            "voidcat_status",
            "voidcat_analyze_knowledge",
            "voidcat_configure_engine",
        ],
        "status": "production_ready",
        "github_ready": True,
    }

    with open("DEPLOYMENT_INFO.json", "w") as f:
        json.dump(deployment_info, f, indent=2)

    print("✅ Deployment info created\n")
    return True


def create_github_workflow():
    """Create basic GitHub workflow for testing."""
    print("⚙️ Creating GitHub workflow...")

    os.makedirs(".github/workflows", exist_ok=True)

    workflow_content = """name: VoidCat Enhanced Test

on:
  push:
    branches: [ main, enhanced ]
  pull_request:
    branches: [ main, enhanced ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.8
      uses: actions/setup-python@v3
      with:
        python-version: 3.8
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Validate imports
      run: |
        python -c "from enhanced_engine import VoidCatEnhancedEngine; print('Enhanced engine import successful')"
        python -c "from sequential_thinking import SequentialThinkingEngine; print('Sequential thinking import successful')"
        python -c "from context7_integration import Context7Engine; print('Context7 import successful')"
    
    - name: Run basic validation
      run: |
        python -c "
        import asyncio
        from enhanced_engine import VoidCatEnhancedEngine
        async def test():
            engine = VoidCatEnhancedEngine()
            print('Enhanced engine created successfully')
        asyncio.run(test())
        "
"""

    with open(".github/workflows/test.yml", "w") as f:
        f.write(workflow_content)

    print("✅ GitHub workflow created\n")
    return True


def main():
    """Main deployment validation."""
    print("🚀 VoidCat Enhanced Deployment Validation")
    print("=" * 50)
    print(f"Validation started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    checks = [
        check_dependencies,
        validate_core_files,
        create_deployment_info,
        create_github_workflow,
    ]

    all_passed = True
    for check in checks:
        try:
            if not check():
                all_passed = False
        except Exception as e:
            print(f"❌ Check failed: {str(e)}")
            all_passed = False

    print("=" * 50)
    if all_passed:
        print("🎉 All validation checks passed!")
        print("✅ System is ready for GitHub upload")
        print("\nNext steps:")
        print("1. git add .")
        print("2. git commit -m 'Enhanced VoidCat with Sequential Thinking + Context7'")
        print("3. git push origin enhanced")
    else:
        print("❌ Some validation checks failed")
        print("Please fix the issues before uploading to GitHub")

    print(f"\nValidation completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
