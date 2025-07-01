---
description: AI rules derived by SpecStory from the project AI interaction history
globs: *
---

## PROJECT RULES, CODING STANDARDS, WORKFLOW GUIDELINES, REFERENCES, DOCUMENTATION STRUCTURES, AND BEST PRACTICES

This file serves as the central source of truth for all project-related rules, coding standards, workflow guidelines, references, documentation structures, and best practices. The AI coding assistant must adhere to these guidelines at all times. This document is a living document and will evolve as the project progresses.

## HEADERS

(This section is intentionally left blank in this initial version but will be populated as the project evolves).

## TECH STACK

(This section is intentionally left blank in this initial version but will be populated as the project evolves).

## PROJECT DOCUMENTATION & CONTEXT SYSTEM

(This section is intentionally left blank in this initial version but will be populated as the project evolves).

## CODING STANDARDS

(This section is intentionally left blank in this initial version but will be populated as the project evolves).

## WORKFLOW & RELEASE RULES

(This section is intentionally left blank in this initial version but will be populated as the project evolves).

## DEBUGGING

(This section is intentionally left blank in this initial version but will be populated as the project evolves).

## TESTING

Before executing any code, always ensure that:

1.  The virtual environment is active.
2.  The necessary dependencies (httpx, python-dotenv, scikit-learn, numpy) are installed.
3.  The test harness is executed using the command: `python main.py`

## REFERENCES

(This section is intentionally left blank in this initial version but will be populated as the project evolves).

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

### Integration Instructions

1. **Configuration File**:
   - Ensure the `mcp_server.py` file is correctly referenced in the configuration.
   - Example:
     ```json
     {
         "mcpServers": {
             "voidcat-reasoning-core": {
                 "command": "python",
                 "args": ["P:\\voidcat-reasoning-core\\mcp_server.py"],
                 "env": {
                     "OPENAI_API_KEY": "your-openai-api-key-here",
                     "PYTHONPATH": "P:\\voidcat-reasoning-core"
                 }
             }
         }
     }
     ```

2. **Environment Variables**:
   - Set the `OPENAI_API_KEY` and other required variables in the `.env` file or system environment.

3. **Testing**:
   - Run the MCP server manually to verify functionality:
     ```bash
     python "P:\\voidcat-reasoning-core\\mcp_server.py"
     ```
   - Test individual tools using the MCP client.