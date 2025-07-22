# VoidCat Enhanced MCP Tools - Comprehensive Documentation

## Overview

The VoidCat Reasoning Core V2 enhanced MCP server provides a comprehensive suite of advanced tools that integrate seamlessly with Claude Desktop and other MCP clients. This document provides complete documentation for all available tools, their schemas, usage patterns, and integration capabilities.

## Tool Categories

### 1. Task Management Tools
Hierarchical task management with unlimited nesting, dependency tracking, and priority scoring.

#### `voidcat_task_create`
**Description**: Create new tasks with comprehensive metadata and dependency tracking.

**Schema**:
```json
{
  "type": "object",
  "properties": {
    "name": {"type": "string", "description": "Task name/title"},
    "description": {"type": "string", "description": "Detailed task description"},
    "priority": {"type": "integer", "minimum": 1, "maximum": 10, "description": "Task priority (1-10)"},
    "complexity": {"type": "integer", "minimum": 1, "maximum": 10, "description": "Task complexity (1-10)"},
    "estimated_hours": {"type": "number", "minimum": 0, "description": "Estimated completion time"},
    "parent_id": {"type": "string", "description": "Parent task ID for hierarchical organization"},
    "depends_on": {"type": "array", "items": {"type": "string"}, "description": "Array of task IDs this task depends on"},
    "tags": {"type": "array", "items": {"type": "string"}, "description": "Task categorization tags"}
  },
  "required": ["name", "description"]
}
```

**Usage Example**:
```json
{
  "name": "Implement authentication system",
  "description": "Build secure user authentication with JWT tokens",
  "priority": 8,
  "complexity": 7,
  "estimated_hours": 12,
  "tags": ["security", "backend", "authentication"]
}
```

#### `voidcat_task_list`
**Description**: List and filter tasks with hierarchical view and advanced filtering.

**Schema**:
```json
{
  "type": "object",
  "properties": {
    "project_id": {"type": "string", "description": "Filter by project ID"},
    "parent_id": {"type": "string", "description": "Filter by parent task"},
    "status": {"type": "string", "enum": ["pending", "in-progress", "completed", "blocked"], "description": "Filter by status"},
    "priority_min": {"type": "integer", "minimum": 1, "maximum": 10, "description": "Minimum priority filter"},
    "tags": {"type": "array", "items": {"type": "string"}, "description": "Filter by tags"},
    "include_completed": {"type": "boolean", "default": true, "description": "Include completed tasks"},
    "show_hierarchy": {"type": "boolean", "default": true, "description": "Show hierarchical structure"}
  }
}
```

#### `voidcat_task_update`
**Description**: Update task properties, status, and relationships.

**Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_id": {"type": "string", "description": "Task ID to update"},
    "name": {"type": "string", "description": "New task name"},
    "description": {"type": "string", "description": "New task description"},
    "status": {"type": "string", "enum": ["pending", "in-progress", "completed", "blocked"]},
    "priority": {"type": "integer", "minimum": 1, "maximum": 10},
    "complexity": {"type": "integer", "minimum": 1, "maximum": 10},
    "actual_hours": {"type": "number", "minimum": 0, "description": "Actual time spent"},
    "progress_notes": {"type": "string", "description": "Progress update notes"}
  },
  "required": ["task_id"]
}
```

### 2. Memory Management Tools
Persistent, categorized memory system with intelligent search and retrieval.

#### `voidcat_memory_store`
**Description**: Store memories with categorization, importance levels, and rich metadata.

**Schema**:
```json
{
  "type": "object",
  "properties": {
    "content": {"type": "string", "description": "Memory content/description"},
    "category": {
      "type": "string", 
      "enum": ["user_preferences", "conversation_history", "learned_heuristics", "project_context", "technical_knowledge"],
      "description": "Memory category"
    },
    "importance": {"type": "integer", "minimum": 1, "maximum": 10, "description": "Importance level (1-10)"},
    "tags": {"type": "array", "items": {"type": "string"}, "description": "Memory tags for organization"},
    "metadata": {"type": "object", "description": "Additional structured metadata"},
    "associations": {"type": "array", "items": {"type": "string"}, "description": "Related memory IDs"}
  },
  "required": ["content", "category"]
}
```

**Usage Example**:
```json
{
  "content": "User prefers detailed technical explanations with code examples",
  "category": "user_preferences",
  "importance": 8,
  "tags": ["communication", "technical", "preferences"],
  "metadata": {
    "preference_type": "communication_style",
    "applies_to": ["technical_discussions", "code_reviews"]
  }
}
```

#### `voidcat_memory_search`
**Description**: Advanced memory search with semantic matching, filtering, and relevance scoring.

**Schema**:
```json
{
  "type": "object",
  "properties": {
    "query": {"type": "string", "description": "Search query text"},
    "search_type": {"type": "string", "enum": ["semantic", "keyword", "hybrid"], "default": "hybrid"},
    "category": {"type": "string", "description": "Filter by memory category"},
    "tags": {"type": "array", "items": {"type": "string"}, "description": "Filter by tags"},
    "importance_min": {"type": "integer", "minimum": 1, "maximum": 10, "description": "Minimum importance level"},
    "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10, "description": "Maximum results"},
    "include_metadata": {"type": "boolean", "default": true, "description": "Include memory metadata"}
  },
  "required": ["query"]
}
```

#### `voidcat_preference_set`
**Description**: Set and manage user preferences with validation and persistence.

**Schema**:
```json
{
  "type": "object",
  "properties": {
    "preference_key": {"type": "string", "description": "Preference identifier"},
    "preference_value": {"description": "Preference value (any type)"},
    "category": {"type": "string", "default": "general", "description": "Preference category"},
    "description": {"type": "string", "description": "Preference description"},
    "validation_schema": {"type": "object", "description": "JSON schema for value validation"}
  },
  "required": ["preference_key", "preference_value"]
}
```

### 3. Code Analysis Tools
Advanced static analysis with security scanning and quality metrics.

#### `voidcat_code_analyze`
**Description**: Comprehensive code analysis including syntax, security, and quality assessment.

**Schema**:
```json
{
  "type": "object",
  "properties": {
    "file_path": {"type": "string", "description": "Path to file for analysis"},
    "code_content": {"type": "string", "description": "Direct code content (alternative to file_path)"},
    "language": {"type": "string", "enum": ["python", "javascript", "typescript", "java", "go", "rust"], "description": "Programming language"},
    "analysis_types": {
      "type": "array",
      "items": {"type": "string", "enum": ["syntax", "security", "quality", "complexity", "dependencies"]},
      "default": ["syntax", "security", "quality"],
      "description": "Types of analysis to perform"
    },
    "include_suggestions": {"type": "boolean", "default": true, "description": "Include improvement suggestions"},
    "security_level": {"type": "string", "enum": ["basic", "standard", "comprehensive"], "default": "standard"}
  }
}
```

**Analysis Capabilities**:
- **Syntax Analysis**: AST parsing, function/class detection, import tracking
- **Security Scanning**: Vulnerability detection (injection, secrets, XSS)
- **Quality Metrics**: Complexity analysis, code duplication, naming conventions
- **Dependency Analysis**: Import mapping, version tracking, security advisories

#### `voidcat_code_security_scan`
**Description**: Specialized security vulnerability scanning with detailed reporting.

**Schema**:
```json
{
  "type": "object",
  "properties": {
    "target": {"type": "string", "description": "File path or directory for scanning"},
    "scan_depth": {"type": "string", "enum": ["file", "directory", "recursive"], "default": "file"},
    "vulnerability_types": {
      "type": "array",
      "items": {"type": "string", "enum": ["injection", "secrets", "xss", "csrf", "insecure_dependencies"]},
      "description": "Types of vulnerabilities to scan for"
    },
    "severity_threshold": {"type": "string", "enum": ["low", "medium", "high", "critical"], "default": "medium"},
    "include_remediation": {"type": "boolean", "default": true, "description": "Include fix suggestions"}
  },
  "required": ["target"]
}
```

### 4. File Operations & Workspace Tools
Intelligent file management and workspace analysis capabilities.

#### `voidcat_file_search`
**Description**: Advanced file search with content analysis and intelligent filtering.

**Schema**:
```json
{
  "type": "object",
  "properties": {
    "query": {"type": "string", "description": "Search query (filename or content)"},
    "search_path": {"type": "string", "description": "Base directory for search"},
    "search_type": {"type": "string", "enum": ["filename", "content", "both"], "default": "both"},
    "file_types": {"type": "array", "items": {"type": "string"}, "description": "File extensions to include"},
    "exclude_patterns": {"type": "array", "items": {"type": "string"}, "description": "Patterns to exclude"},
    "max_results": {"type": "integer", "minimum": 1, "maximum": 1000, "default": 50},
    "include_hidden": {"type": "boolean", "default": false, "description": "Include hidden files"},
    "case_sensitive": {"type": "boolean", "default": false, "description": "Case sensitive search"}
  },
  "required": ["query"]
}
```

#### `voidcat_workspace_analyze`
**Description**: Comprehensive workspace analysis with project structure assessment.

**Schema**:
```json
{
  "type": "object",
  "properties": {
    "workspace_path": {"type": "string", "description": "Path to workspace/project directory"},
    "analysis_depth": {"type": "string", "enum": ["shallow", "standard", "deep"], "default": "standard"},
    "include_dependencies": {"type": "boolean", "default": true, "description": "Analyze project dependencies"},
    "detect_frameworks": {"type": "boolean", "default": true, "description": "Detect frameworks and libraries"},
    "identify_issues": {"type": "boolean", "default": true, "description": "Identify potential issues"},
    "generate_recommendations": {"type": "boolean", "default": true, "description": "Generate improvement recommendations"}
  },
  "required": ["workspace_path"]
}
```

**Analysis Features**:
- **Project Type Detection**: Node.js, Python, Java, Go, etc.
- **Framework Identification**: React, Django, Spring, etc.
- **Dependency Analysis**: Version tracking, security advisories
- **Code Organization**: Structure assessment, best practices
- **Issue Detection**: Common problems, optimization opportunities

#### `voidcat_bulk_operations`
**Description**: Safe bulk file operations with rollback capabilities.

**Schema**:
```json
{
  "type": "object",
  "properties": {
    "operation": {"type": "string", "enum": ["copy", "move", "rename", "delete"], "description": "Bulk operation type"},
    "source_pattern": {"type": "string", "description": "Source file pattern (glob)"},
    "destination": {"type": "string", "description": "Destination path or pattern"},
    "base_path": {"type": "string", "description": "Base directory for operations"},
    "preview_only": {"type": "boolean", "default": true, "description": "Preview changes without executing"},
    "create_backup": {"type": "boolean", "default": true, "description": "Create backup before operations"},
    "force_overwrite": {"type": "boolean", "default": false, "description": "Force overwrite existing files"},
    "safety_checks": {"type": "boolean", "default": true, "description": "Enable safety validations"}
  },
  "required": ["operation", "source_pattern"]
}
```

### 5. Enhanced MCP Features

#### Tool Discovery & Management
- **Dynamic Tool Registration**: Runtime tool addition and removal
- **Category-based Organization**: Logical grouping of related tools
- **Schema Validation**: Automatic validation of tool inputs and outputs
- **Version Management**: Tool versioning and compatibility tracking

#### Error Handling & Recovery
- **Graceful Degradation**: Continued operation despite individual tool failures
- **Detailed Error Messages**: Comprehensive error reporting with troubleshooting guidance
- **Automatic Retry Logic**: Intelligent retry mechanisms for transient failures
- **Error Logging**: Comprehensive error tracking and analysis

#### Performance & Monitoring
- **Request Tracking**: Detailed timing and performance metrics
- **Usage Analytics**: Tool usage patterns and optimization insights
- **Resource Monitoring**: Memory and CPU utilization tracking
- **Rate Limiting**: Configurable request throttling and quotas

## Integration with VoidCat Reasoning System

### Context Enhancement
All tools integrate with the VoidCat reasoning engine to provide:
- **Intelligent Suggestions**: AI-powered recommendations based on context
- **Automatic Categorization**: Smart tagging and organization
- **Relationship Detection**: Automatic association of related items
- **Learning Adaptation**: System learns from user patterns and preferences

### Cross-Component Data Sharing
- **Unified Data Model**: Consistent data structures across all tools
- **Real-time Synchronization**: Changes reflected immediately across components
- **Conflict Resolution**: Intelligent handling of data conflicts
- **Backup and Recovery**: Comprehensive data protection mechanisms

## Claude Desktop Integration

### MCP Protocol Compliance
- **Full MCP 2024-11-05 Compliance**: Complete adherence to latest MCP specification
- **Tool Schema Standards**: Properly formatted schemas with comprehensive validation
- **Error Response Formatting**: Claude-compatible error messages and handling
- **Performance Optimization**: Optimized for Claude's interaction patterns

### User Experience Enhancement
- **Intuitive Tool Descriptions**: Clear, actionable tool descriptions
- **Helpful Examples**: Comprehensive usage examples and patterns
- **Progressive Disclosure**: Simple interfaces with advanced options available
- **Contextual Help**: In-context assistance and guidance

## Advanced Usage Patterns

### Workflow Automation
```json
// Example: Automated project setup workflow
{
  "workflow": [
    {"tool": "voidcat_task_create", "params": {"name": "Setup Project", "priority": 9}},
    {"tool": "voidcat_workspace_analyze", "params": {"workspace_path": "./project"}},
    {"tool": "voidcat_code_analyze", "params": {"file_path": "./src/**/*.py"}},
    {"tool": "voidcat_memory_store", "params": {"content": "Project setup completed", "category": "project_context"}}
  ]
}
```

### Intelligent Search Patterns
```json
// Example: Multi-faceted search across memory and files
{
  "search_strategy": {
    "memory_search": {"query": "authentication patterns", "category": "technical_knowledge"},
    "file_search": {"query": "auth", "file_types": [".py", ".js"], "search_type": "content"},
    "code_analysis": {"analysis_types": ["security"], "target": "auth_modules"}
  }
}
```

### Performance Optimization
- **Caching Strategies**: Intelligent caching of frequently accessed data
- **Batch Operations**: Efficient handling of multiple related operations
- **Lazy Loading**: On-demand loading of resource-intensive components
- **Request Optimization**: Minimized network overhead and response times

## Security Considerations

### Access Control
- **Tool-level Permissions**: Granular control over tool access
- **Data Isolation**: Secure separation of different data types
- **Audit Logging**: Comprehensive logging of all operations
- **Encryption**: Secure storage and transmission of sensitive data

### Input Validation
- **Schema Enforcement**: Strict validation of all inputs
- **Sanitization**: Automatic sanitization of potentially dangerous inputs
- **Rate Limiting**: Protection against abuse and overuse
- **Error Boundary**: Controlled error handling to prevent information leakage

## Troubleshooting Guide

### Common Issues

#### Tool Not Found
- **Cause**: Tool not properly registered or MCP server not initialized
- **Solution**: Restart MCP server, verify tool registration
- **Prevention**: Use tool discovery to verify available tools

#### Invalid Parameters
- **Cause**: Parameters don't match tool schema
- **Solution**: Check tool documentation, validate parameter types
- **Prevention**: Use schema validation before sending requests

#### Performance Issues
- **Cause**: Large datasets, complex operations, or resource constraints
- **Solution**: Use pagination, filtering, or async operations
- **Prevention**: Monitor performance metrics, optimize queries

### Debug Mode
Enable detailed logging by setting environment variable:
```bash
VOIDCAT_DEBUG=true
```

### Support Resources
- **Error Codes**: Comprehensive error code reference
- **API Documentation**: Detailed API reference with examples
- **Community Forums**: User community and support channels
- **Issue Tracking**: Bug reports and feature requests

---

**Document Version**: 1.0.0  
**Last Updated**: July 19, 2025  
**Status**: Production Ready  
**Compatibility**: MCP Protocol 2024-11-05, Claude Desktop, VoidCat V2
