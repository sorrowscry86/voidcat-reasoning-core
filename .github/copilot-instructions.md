---
description: AI rules derived by SpecStory from the project AI interaction history
globs: *
---

## PROJECT RULES, CODING STANDARDS, WORKFLOW GUIDELINES, REFERENCES, DOCUMENTATION STRUCTURES, AND BEST PRACTICES

This file serves as the central source of truth for all project-related rules, coding standards, workflow guidelines, references, documentation structures, and best practices. The AI coding assistant must adhere to these guidelines at all times. This document is a living document and will evolve as the project progresses.

## UPDATED ARCHITECTURE OVERVIEW

The VoidCat Reasoning Core (VRE) now includes:

1. **Enhanced Engine**:
   - Unified enhanced pipeline in `enhanced_engine.py`.
   - Advanced RAG reasoning with Context7 integration.
   - Sequential Thinking for multi-branch reasoning.

2. **Integration Layer**:
   - Expanded MCP server capabilities in `mcp_server.py`.
   - Claude Desktop integration for enhanced diagnostics.

3. **Memory System**:
   - Intelligent caching with Redis-backed distributed cache.
   - Semantic similarity matching for query optimization.

4. **Local Model Integration**:
   - Complexity-based routing between local and cloud models.
   - Ollama integration for local model execution.

## UPDATED WORKFLOWS

### Build and Deployment

1. **Dockerized Deployment**:
   - Build the Docker image:
     ```powershell
     docker build -t voidcat-reasoning-core .
     ```
   - Run the container:
     ```powershell
     docker run --env-file .env voidcat-reasoning-core
     ```

2. **Environment Configuration**:
   - Set up `.env` file with required variables:
     ```ini
     OPENAI_API_KEY='your-super-secret-api-key'
     OPENROUTER_API_KEY='your_openrouter_api_key_here'
     DEEPSEEK_API_KEY='your_deepseek_api_key_here'
     ```

### Enhanced Testing

1. **Run Comprehensive Tests**:
   - Use `test_enhanced_system.py` for full pipeline validation.
   - Validate deployment with `deploy_enhanced.py`.

2. **Performance Monitoring**:
   - Track query metrics and system health using built-in diagnostics.

### Enhanced Deployment

1. **Dockerized Deployment**:
   - Updated Docker image with enhanced tools.
   - Use `deploy_enhanced.py` for deployment validation.

### Development and Global Installation (Experimental)

1.  **Package Structure:**
    - Follow the standard Python package structure.
    - Include `__init__.py`, `pyproject.toml`, and `MANIFEST.in` files.

2.  **pyproject.toml Configuration:**
    - Use `pyproject.toml` for build system configuration.
    - Include `[project.scripts]` section to define console scripts.
    - Correct any TOML syntax errors.

3.  **Installation:**
    - Install the package in development mode using `pip install -e .`.
    - Ensure the scripts directory is added to the PATH environment variable.

## UPDATED CONVENTIONS AND PATTERNS

1. **Tool Integration**:
   - Use `voidcat_query`, `voidcat_status`, and `voidcat_sequential_thinking` for reasoning tasks.
   - Leverage `voidcat_enhanced_query` for full pipeline execution.

2. **Testing**:
   - Follow the structure in `test_*` files for unit and integration tests.
   - Use `test_e2e_*` files for end-to-end testing.

3. **Documentation**:
   - Update `.github/copilot-instructions.md` and `README.md` for any major changes. **Always** update these files to reflect significant project changes.
   - Reference `ENHANCED_IMPLEMENTATION_SUMMARY.md` for detailed implementation notes.
   - See `VSVC_Testing.md` for VS Code Insiders testing details.

## UPDATED REFERENCES

- **Key Files**:
  - `engine.py`, `enhanced_engine.py`, `api_gateway.py`, `context7_integration.py`, `mcp_server.py`
  - `test_context_integration.py`, `test_engine_validation.py`, `test_e2e_complete_system.py`
- **Documentation**:
  - `README.md`, `.github/copilot-instructions.md`, `ENHANCED_IMPLEMENTATION_SUMMARY.md`, `VSVC_Testing.md`, `CHANGELOG.md`

## DEBUGGING

- Servers should log to `stderr`, not `stdout`, to avoid interfering with the MCP protocol.
- Add comprehensive try-except blocks to the MCP server startup code to catch any exceptions. Log these exceptions to stderr.

### Windows Asyncio Issues

- To fix Windows asyncio transport issues (Python 3.8+ ProactorEventLoop problems):
  ```python
  if sys.platform == 'win32':
      import asyncio
      asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
  ```

## WORKFLOW & RELEASE RULES

- **DO NOT** use `&&` in PowerShell commands.
- **Always** ensure all dependencies are included in the `requirements.txt` file.
- **Always** log to stderr, not stdout, when writing MCP servers.
- When configuring Claude Desktop, remove the following MCP servers: `playwright`, `filesystem`, `hyperbrowser`, `workspace`, `mermaid`, `github`, `websearch`, and `mcp`. The kept servers are: `memory`, `context7`, `MCP_DOCKER`, `voidcat-reasoning-core-v2`, `desktop-commander`, `agentic-tools`, `think-mcp`, `pylance-mcp`, `sqlite`, `postgres`, and `brave-search`.
- Look for and delete all "report" and unnecessary note and test files. Remove all test files.

## VOIDCAT REASONING CORE TOOLS

### Available Tools

1. **voidcat_query**
   - **Purpose**: Process intelligent queries using RAG-enhanced reasoning.
   - **Parameters**:
     - `query` (required): Your question or prompt.
     - `model` (optional): OpenAI model to use (default: gpt-4o-mini).

2. **voidcat_status**
   - **Purpose**: Check the health and status of the VoidCat reasoning engine.
   - **Parameters**: None.

3. **voidcat_sequential_thinking**
   - **Purpose**: Perform multi-branch structured reasoning.
   - **Parameters**:
     - `query` (required): The input query.
     - `max_thoughts` (optional): Maximum number of thoughts to process (default: 10).
     - `include_reasoning_trace` (optional): Whether to include the reasoning trace (default: True).

4. **voidcat_enhanced_query**
   - **Purpose**: Execute the full pipeline (Sequential Thinking + Context7 + RAG).
   - **Parameters**:
     - `query` (required): The input query.
     - `model` (optional): OpenAI model to use.

5. **voidcat_analyze_knowledge**
   - **Purpose**: Explore the knowledge base for insights.
   - **Parameters**: None.

6. **voidcat_configure_engine**
   - **Purpose**: Configure runtime behavior of the VoidCat engine.
   - **Parameters**: Configuration options as key-value pairs.

7. **voidcat_ultimate_enhanced_query** - The true Ultimate Mode
   - 85% performance improvement with parallel processing
   - Adaptive reasoning mode selection
   - Uses the actual `ultimate_enhanced_query` method

8. **voidcat_enhanced_query_with_sequential** - Sequential Thinking integration
   - Direct access to multi-branch reasoning
   - Configurable thought generation
   - Detailed reasoning trace display

9. **voidcat_enhanced_query_with_context7** - Context7 integration
   - Advanced context retrieval and analysis
   - Relevance scoring and source evaluation
   - Intelligent context aggregation

### New Tools

1. **voidcat_analyze_knowledge**:
   - Explore knowledge base insights with semantic analysis.

2. **voidcat_ultimate_enhanced_query**:
   - Adaptive reasoning with parallel processing.

3. **voidcat_enhanced_query_with_context7**:
   - Advanced context retrieval and relevance scoring.

## DEVELOPMENT AND GLOBAL INSTALLATION (EXPERIMENTAL) - ADDITIONAL RULES

1. **Error Handling:**
   - Add comprehensive try-except blocks to the MCP server startup code to catch any exceptions. Log these exceptions to stderr.
   ```python
   try:
       # server startup code here
   except Exception as e:
       print(f"Error starting server: {e}", file=sys.stderr)
   ```

2.  **Package Structure:**
    - Follow the standard Python package structure.
    - Include `__init__.py`, `pyproject.toml`, and `MANIFEST.in` files.

3.  **pyproject.toml Configuration:**
    - Use `pyproject.toml` for build system configuration.
    - Include `[project.scripts]` section to define console scripts.
    - Correct any TOML syntax errors.

4.  **Installation:**
    - Install the package in development mode using `pip install -e .`.
    - Ensure the scripts directory is added to the PATH environment variable.

## GLOBAL INSTALLATION

1. **Package Structure:**
   - Follow the standard Python package structure.
   - Include `__init__.py`, `pyproject.toml`, and `MANIFEST.in` files.

2. **pyproject.toml Configuration:**
   - Use `pyproject.toml` for build system configuration.
   - Include the `[project.scripts]` section to define console scripts.

3. **Installation:**
   - Install the package in development mode using `pip install -e .`.
   - Ensure the scripts directory is added to the PATH environment variable.

4. **Circular Import Fix:**
   - In `__init__.py`, avoid importing modules that might cause circular imports. To prevent circular imports, avoid importing modules that might cause circular imports. For example:
     ```python
     # __init__.py
     # Avoid: from . import engine # This might cause circular imports
     ```

5. **Error Handling:**
   - Add comprehensive try-except blocks to the MCP server startup code to catch any exceptions. Log these exceptions to stderr.

## POWERSHELL RULES

- **DO NOT** use `&&` in PowerShell commands. This is a persistent rule to avoid syntax errors.

## OPENROUTER FALLBACK

- To enable OpenRouter fallback, add the `OPENROUTER_API_KEY` to the `.env` file.
- The VoidCat engine uses a 3-tier API system: Deepseek API (primary), OpenAI API (secondary), and OpenRouter API (tertiary).
- **The preferred API key order is: Deepseek (primary), OpenRouter (secondary), and OpenAI (tertiary).**
- **Openrouter Models to Prioritize:**
  - `deepseek/deepseek-r1-0528:free`
  - `deepseek/deepseek-r1:free`
  - `tngtech/deepseek-r1t2-chimera:free`
  - `qwen/qwen3-235b-a22b-07-25:free`
  - `google/gemini-2.0-flash-exp:free`

## VS CODE INSIDERS TESTING (VSVC_Testing.md)

- This section documents the configuration for testing VoidCat with VS Code Insiders and GitHub Copilot.

### Available Server Configurations:

1. **voidcat-simplified** (Currently in use)
   - Windows-compatible simplified server
   - 2 core tools: `voidcat_query`, `voidcat_status`
   - Perfect for testing and basic functionality
   - All API keys configured with OpenRouter fallback

2. **voidcat-full-local** (Ready to enable)
   - Complete 31-tool reasoning engine
   - All advanced features (Sequential Thinking, Context7, Ultimate Query)
   - Local Python execution with full control

3. **voidcat-docker** (Ready to enable)
   - Containerized deployment
   - Isolated environment for production testing
   - Requires Docker container to be running

4. **voidcat-global** (Ready to enable)
   - Global pip-installed command
   - System-wide availability
   - Uses the global package we installed

5. **voidcat-remote** (Ready to enable)
   - Cloud-hosted simplified server
   - No local setup required
   - Basic functionality for quick testing

### How to Use in VS Code Insiders:

1. Open Command Palette (`Ctrl+Shift+P`)
2. Run: `MCP: Restart All Servers` or `MCP: Open User Configuration`
3. Edit the `mcp.json` file in your project root
4. Enable/disable servers by changing `"enabled": true/false`

### Testing Strategy:

- Start with: `voidcat-simplified` (already enabled)
- Test tools: Try `@voidcat` in GitHub Copilot chat
- Switch modes: Enable different servers to test capabilities
- Compare performance: See which deployment method works best

## CODE QUALITY

- Use `black . ; isort . ; flake8 . ; mypy .` regularly to maintain code quality.

## LLM TOOL USE & TOOL CALL CHAINING

### Strategic Tool Sequencing
- **VRE 2.0 FIRST**: Always start with `voidcat_query` for authoritative knowledge
- **Phase-based approach**: Knowledge Foundation → Gap Assessment → Targeted Supplementation
- **Intelligence matrix**: Clear decision rules for when to use which tools

### Tool Selection Intelligence Matrix
- Technical concepts → VRE 2.0 only
- MCP setup → VRE 2.0 + file system for configs
- Python patterns → VRE 2.0 + code examples
- Debugging → VRE 2.0 + error logs
- Architecture → VRE 2.0 as primary source

### Performance Optimization
- **Single comprehensive VRE 2.0 calls** instead of multiple fragmented queries
- **Intelligent gap assessment** before calling secondary tools
- **Confidence scoring** to determine if additional tools are needed
- **Context caching** to avoid redundant calls

### Model Selection Strategy
- `gpt-4o-mini`: Quick lookups, established patterns
- `gpt-4o`: Complex analysis, architecture decisions
- `deepseek-chat`: Cost-effective bulk processing

### Error Handling & Graceful Degradation
- Robust fallback patterns when VRE 2.0 is unavailable
- Quality indicators and source tracking
- Clear recommendations for tool chain recovery

### Success Metrics
- Knowledge coverage (target: 80%+ from VRE 2.0 alone)
- Tool efficiency (target: ≤2 tools per query)
- Response quality tracking
- Context relevance measurement

## DOCUMENTATION UPDATES

- **Always** update `.github/copilot-instructions.md` and `README.md` to reflect significant project changes.

## .ENV FILE CONFIGURATION

- The `.env` file should be configured with API keys for OpenAI, DeepSeek, and OpenRouter. **DeepSeek is the primary API, OpenRouter is the secondary, and OpenAI is the tertiary fallback.**
- Ensure the `.env` file is populated with the necessary API keys:
```ini
OPENAI_API_KEY='your-super-secret-api-key'
OPENROUTER_API_KEY='your_openrouter_api_key_here'
DEEPSEEK_API_KEY='your_deepseek_api_key_here'
```

## DOCKERFILE UPDATES

- The `Dockerfile` should include enhanced caching, local model integration, and improved diagnostics. Ensure it supports Redis tools and an operational mode for cache diagnostics. The current `Dockerfile` includes:
    1. **Enhanced Caching**: `redis-tools` and the `redis` Python package.
    2. **Local Model Integration**: The `ollama` package.
    3. **Improved Diagnostics**: A new operational mode (`cache`) for Redis diagnostics.
    4. **Flexible Entrypoint**: Supports multiple operational modes (`mcp`, `api`, `test`, `diagnostics`, `enhanced`, and `cache`).

## CHANGELOG UPDATES

- Move items from the "Unreleased" section of `CHANGELOG.md` to a new version entry when a release is planned. Verify that all recent updates (e.g., Dockerfile enhancements, new tools) are reflected. The `CHANGELOG.md` has been finalized with a new version entry for `2.1.0`.

## REPOSITORY MAINTENANCE

- Ensure all unnecessary files are removed and `.gitignore` is updated.
- Large files (e.g., `Brat Report.md`) exceeding GitHub's file size limit should be removed from the repository's history if unnecessary, or managed using Git Large File Storage (LFS).

## GIT RULES

- Large files (e.g., `Brat Report.md`) exceeding GitHub's file size limit must be removed from the repository's history. Use `git filter-repo` or `git filter-branch` to remove the file from all commits, followed by a force push.

### Steps to Rewrite History:
1. Use `git filter-repo` or `git filter-branch` to remove the file from all commits.
2. Force push the updated repository.

### Resolving Large File Issues (Brat Report.md):
- If encountering issues with large files, specifically `Brat Report.md`, the recommended approach is to rewrite the repository's history to remove the file completely.
- If `git filter-repo` is not available, use `git filter-branch` as an alternative. However, `git filter-repo` is the preferred and more reliable tool.
- Before rewriting history, ensure that all unstaged changes are stashed to avoid conflicts.
- Be prepared to install `git filter-repo` if it is not already available in the environment.
- If `git filter-repo` is refusing to rewrite the repository history because it is not operating on a fresh clone, clone the repository afresh and run the `git filter-repo` command on the fresh clone. This is safer and avoids potential issues.

## PATH ENVIRONMENT VARIABLE

- If a warning message indicates that the Python scripts directory (e.g., `'C:\Users\Wykeve\AppData\Roaming\Python\Python313\Scripts'`) is not on the PATH, add it to the PATH environment variable. This ensures that commands like `pip` can be run from any terminal location.

### Steps to Add to PATH:

1. Add the Python Scripts directory to the PATH environment variable.
2. Restart your terminal or system for the changes to take effect.

## FILE REMOVAL RULES

- Look for and delete all "report" and unnecessary note and test files. Remove all test files. This rule is persistent to reduce repository size and complexity.
- Remove all `.md` files related to "Claude", except for the following necessary files:
  1. `WINDOWS_SETUP_GUIDE.md`: Contains critical setup instructions for Windows integration, including Claude Desktop configuration.
  2. `VSCODE_INTEGRATION_PLAN.md`: Details the strategic enhancement plan for VS Code integration, including Claude Desktop optimization.
  3. `SECURITY_FIX_REPORT.md`: Highlights security fixes, including updates to Claude Desktop configuration files.

- Retain the following `.md` files as they are critical for project documentation, testing, and security:
  1. `README.md`: Core project documentation, including setup, features, and integration details.
  2. `README_ENHANCED.md`: Enhanced version documentation with advanced features like Sequential Thinking and Context7.
  3. `SECURITY_NOTICE.md`: Important security update regarding API key management.
  4. `ULTIMATE_TOOLS_RESTORATION.md`: Documentation of the operational status and usage of Ultimate Mode tools.