#!/usr/bin/env python3
"""
VoidCat Reasoning Core - Environment Check Script

This script verifies that the environment is properly set up for the VoidCat Reasoning Core:
1. Checks Python version
2. Verifies required dependencies
3. Validates environment variables
4. Checks knowledge source directory

Usage:
    python check_environment.py
"""

import importlib
import os
import platform
import sys
from pathlib import Path


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")


def print_result(check_name, success, message=""):
    """Print a formatted check result."""
    status = "✅ PASSED" if success else "❌ FAILED"
    print(f"{status} | {check_name}")
    if message:
        print(f"       {message}")


def check_python_version():
    """Check if Python version is compatible."""
    current_version = sys.version_info
    required_version = (3, 11)  # Minimum required version
    recommended_version = (3, 13)  # Recommended version

    is_compatible = current_version >= required_version
    is_recommended = current_version >= recommended_version

    message = f"Current: {platform.python_version()}, Required: {required_version[0]}.{required_version[1]}+"
    if is_compatible and not is_recommended:
        message += f" (Recommended: {recommended_version[0]}.{recommended_version[1]}+)"

    print_result("Python Version", is_compatible, message)
    return is_compatible


def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        "httpx",
        "fastapi",
        "uvicorn",
        "pydantic",
        "scikit-learn",
        "numpy",
        "python-dotenv",
        "openai",
    ]

    optional_packages = ["pytest", "black", "isort", "flake8", "mypy", "PyPDF2"]

    print("Checking required packages:")
    all_required_installed = True
    for package in required_packages:
        try:
            importlib.import_module(package.replace("-", "_"))
            print_result(package, True, "Installed")
        except ImportError:
            print_result(package, False, "Not installed")
            all_required_installed = False

    print("\nChecking optional packages:")
    for package in optional_packages:
        try:
            importlib.import_module(package.replace("-", "_"))
            print_result(package, True, "Installed")
        except ImportError:
            print_result(package, False, "Not installed (optional)")

    return all_required_installed


def check_environment_variables():
    """Check if required environment variables are set."""
    required_vars = ["OPENAI_API_KEY"]
    optional_vars = ["DEEPSEEK_API_KEY"]

    print("Checking environment variables:")
    all_required_set = True
    for var in required_vars:
        value = os.getenv(var)
        is_set = value is not None and value.strip() != ""
        print_result(var, is_set, "Set" if is_set else "Not set")
        if not is_set:
            all_required_set = False

    print("\nChecking optional environment variables:")
    for var in optional_vars:
        value = os.getenv(var)
        is_set = value is not None and value.strip() != ""
        print_result(var, is_set, "Set" if is_set else "Not set (optional)")

    return all_required_set


def check_knowledge_source():
    """Check if knowledge source directory exists and contains documents."""
    knowledge_dir = Path("knowledge_source")

    # Check if directory exists
    dir_exists = knowledge_dir.exists() and knowledge_dir.is_dir()
    print_result(
        "Knowledge Directory",
        dir_exists,
        f"Path: {knowledge_dir.absolute()}" if dir_exists else "Directory not found",
    )

    if dir_exists:
        # Check for markdown files
        markdown_files = list(knowledge_dir.glob("**/*.md"))
        has_markdown = len(markdown_files) > 0
        print_result(
            "Markdown Documents",
            has_markdown,
            (
                f"Found {len(markdown_files)} markdown files"
                if has_markdown
                else "No markdown files found"
            ),
        )

        # Check for other document types
        other_files = list(knowledge_dir.glob("**/*.*"))
        other_files = [
            f for f in other_files if f.suffix.lower() not in [".md", ".git"]
        ]
        has_other = len(other_files) > 0
        print_result(
            "Other Documents",
            has_other,
            (
                f"Found {len(other_files)} other files"
                if has_other
                else "No other files found"
            ),
        )

        return dir_exists and (has_markdown or has_other)

    return False


def check_project_structure():
    """Check if the project structure is correct."""
    required_files = [
        "engine.py",
        "enhanced_engine.py",
        "api_gateway.py",
        "sequential_thinking.py",
        "context7_integration.py",
        "mcp_server.py",
        "main.py",
    ]

    print("Checking project structure:")
    all_files_exist = True
    for file in required_files:
        file_path = Path(file)
        exists = file_path.exists() and file_path.is_file()
        print_result(file, exists, "Found" if exists else "Missing")
        if not exists:
            all_files_exist = False

    return all_files_exist


def main():
    """Main function to run all checks."""
    print_header("VoidCat Reasoning Core - Environment Check")

    # Run all checks
    python_ok = check_python_version()
    deps_ok = check_dependencies()
    env_ok = check_environment_variables()
    knowledge_ok = check_knowledge_source()
    structure_ok = check_project_structure()

    # Print summary
    print_header("Environment Check Summary")
    print_result("Python Version", python_ok)
    print_result("Dependencies", deps_ok)
    print_result("Environment Variables", env_ok)
    print_result("Knowledge Source", knowledge_ok)
    print_result("Project Structure", structure_ok)

    all_ok = python_ok and deps_ok and env_ok and knowledge_ok and structure_ok
    print(
        "\nOverall Environment Status:", "✅ READY" if all_ok else "❌ NEEDS ATTENTION"
    )

    if not all_ok:
        print("\nRecommended actions:")
        if not python_ok:
            print("- Install Python 3.11+ (3.13+ recommended)")
        if not deps_ok:
            print("- Install missing required dependencies:")
            print(
                "  pip install httpx fastapi uvicorn pydantic scikit-learn numpy python-dotenv openai"
            )
        if not env_ok:
            print("- Set required environment variables:")
            print("  - Create a .env file with OPENAI_API_KEY=your_api_key")
            print("  - Or set environment variables directly in your shell")
        if not knowledge_ok:
            print("- Create knowledge_source directory and add markdown documents")
        if not structure_ok:
            print("- Ensure all required project files are present")
    else:
        print("\nEnvironment is properly set up for VoidCat Reasoning Core!")


if __name__ == "__main__":
    main()
