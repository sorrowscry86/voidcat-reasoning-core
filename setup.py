#!/usr/bin/env python3
"""
VoidCat Reasoning Core MCP Server
Global installation setup for Python packaging
"""

import os

from setuptools import find_packages, setup

# Read version from __init__.py or set manually
VERSION = "1.0.0"


# Read long description from README
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "VoidCat Reasoning Core - Advanced MCP Server with 31 AI tools"


# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8") as f:
            return [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]
    return []


setup(
    name="voidcat-reasoning-core",
    version=VERSION,
    author="SorrowsCry86",
    author_email="contact@voidcat.ai",
    description="Advanced MCP Server with 31 AI reasoning tools including RAG, sequential thinking, and knowledge management",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/sorrowscry86/voidcat-reasoning-core",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.11",
    install_requires=read_requirements(),
    extras_require={
        "dev": ["pytest", "black", "flake8", "mypy"],
        "docker": ["docker"],
    },
    entry_points={
        "console_scripts": [
            "voidcat-mcp=voidcat_reasoning_core.mcp_server:main",
            "voidcat-mcp-server=voidcat_reasoning_core.mcp_server:main",
            "voidcat-reasoning=voidcat_reasoning_core.mcp_server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "voidcat_reasoning_core": [
            "knowledge_source/**/*",
            "indexes/**/*",
            "*.json",
            "*.yaml",
            "*.yml",
        ],
    },
    keywords=[
        "mcp",
        "model-context-protocol",
        "ai",
        "reasoning",
        "rag",
        "llm",
        "claude",
        "openai",
        "artificial-intelligence",
        "knowledge-management",
    ],
    project_urls={
        "Bug Reports": "https://github.com/sorrowscry86/voidcat-reasoning-core/issues",
        "Source": "https://github.com/sorrowscry86/voidcat-reasoning-core",
        "Documentation": "https://github.com/sorrowscry86/voidcat-reasoning-core/blob/master/README.md",
    },
)
