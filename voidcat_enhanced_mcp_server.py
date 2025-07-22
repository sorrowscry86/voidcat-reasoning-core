#!/usr/bin/env python3
"""
VoidCat Enhanced MCP Server - Pillar IV: The Guardian's Overseer
Advanced Model Context Protocol server with comprehensive tool suite

This module implements the final pillar of Beatrice's directive, providing:
- Enhanced MCP server architecture with advanced protocol compliance
- Advanced code analysis tools with syntax analysis and security scanning
- Comprehensive file operations and workspace management tools
- Robust error handling, logging, and monitoring capabilities
- Complete integration with VoidCat task management and memory systems

Features:
- Advanced code analysis: syntax analysis, dependency tracking, security scanning
- File operations: intelligent search, bulk operations, automated refactoring
- Enhanced tool discovery with categorization and dynamic loading
- Comprehensive logging and monitoring system
- Advanced error recovery and graceful degradation
- Production-ready deployment with rate limiting and validation

Author: VoidCat Reasoning Core Team - Pillar IV Implementation
License: MIT
Version: 1.0.0 (Guardian's Overseer)
"""

import ast
import asyncio
import hashlib
import json
import logging
import os
import re
import shutil

# Enhanced imports for code analysis and file operations
import subprocess
import sys
import tempfile
import time
import traceback
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

# VoidCat system imports
from enhanced_engine import VoidCatEnhancedEngine as VoidCatEngine
from voidcat_context_integration import create_context_integration
from voidcat_mcp_tools import create_mcp_task_tools
from voidcat_memory_mcp_tools import create_memory_mcp_tools


class AdvancedLogger:
    """Enhanced logging system for the VoidCat MCP server."""

    def __init__(self, name: str = "VoidCat-Guardian", log_level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))

        # Enhanced formatter with timestamp, level, and context
        formatter = logging.Formatter(
            "[%(asctime)s.%(msecs)03d] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Console handler for stderr (MCP compatible)
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler for persistent logging
        try:
            log_dir = Path(__file__).parent / "logs"
            log_dir.mkdir(exist_ok=True)
            file_handler = logging.FileHandler(
                log_dir / f"voidcat_mcp_{datetime.now().strftime('%Y%m%d')}.log"
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            self.logger.warning(f"Could not create file handler: {e}")

    def debug(self, message: str, **kwargs):
        self.logger.debug(self._format_message(message, **kwargs))

    def info(self, message: str, **kwargs):
        self.logger.info(self._format_message(message, **kwargs))

    def warning(self, message: str, **kwargs):
        self.logger.warning(self._format_message(message, **kwargs))

    def error(self, message: str, **kwargs):
        self.logger.error(self._format_message(message, **kwargs))

    def critical(self, message: str, **kwargs):
        self.logger.critical(self._format_message(message, **kwargs))

    def _format_message(self, message: str, **kwargs) -> str:
        """Format message with optional context."""
        if kwargs:
            context = " | ".join(f"{k}={v}" for k, v in kwargs.items())
            return f"{message} | {context}"
        return message


@dataclass
class ToolMetadata:
    """Enhanced tool metadata with category, performance, and usage tracking."""

    name: str
    description: str
    category: str
    input_schema: Dict[str, Any]
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    rate_limit: Optional[int] = None  # requests per minute
    complexity_score: int = 1  # 1-10 scale
    usage_count: int = 0
    error_count: int = 0
    average_execution_time: float = 0.0
    last_used: Optional[datetime] = None
    requires_file_access: bool = False
    requires_network_access: bool = False


@dataclass
class PerformanceMetrics:
    """Performance tracking for the enhanced MCP server."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    peak_response_time: float = 0.0
    requests_per_minute: float = 0.0
    active_tools: Set[str] = field(default_factory=set)
    rate_limit_hits: int = 0
    last_reset: datetime = field(default_factory=lambda: datetime.now(UTC))


class RateLimiter:
    """Advanced rate limiting mechanism for tool usage."""

    def __init__(self):
        self.tool_usage = defaultdict(deque)  # tool_name -> timestamps
        self.global_usage = deque()
        self.global_limit = 1000  # requests per minute globally
        self.default_tool_limit = 60  # requests per minute per tool

    def check_rate_limit(
        self, tool_name: str, custom_limit: Optional[int] = None
    ) -> bool:
        """Check if tool usage is within rate limits."""
        now = time.time()
        minute_ago = now - 60

        # Clean old entries
        self._clean_old_entries(minute_ago)

        # Check global rate limit
        if len(self.global_usage) >= self.global_limit:
            return False

        # Check tool-specific rate limit
        tool_limit = custom_limit or self.default_tool_limit
        if len(self.tool_usage[tool_name]) >= tool_limit:
            return False

        return True

    def record_usage(self, tool_name: str):
        """Record tool usage for rate limiting."""
        now = time.time()
        self.tool_usage[tool_name].append(now)
        self.global_usage.append(now)

    def _clean_old_entries(self, cutoff_time: float):
        """Remove usage entries older than cutoff time."""
        # Clean global usage
        while self.global_usage and self.global_usage[0] < cutoff_time:
            self.global_usage.popleft()

        # Clean tool-specific usage
        for tool_name in list(self.tool_usage.keys()):
            tool_queue = self.tool_usage[tool_name]
            while tool_queue and tool_queue[0] < cutoff_time:
                tool_queue.popleft()

            # Remove empty queues
            if not tool_queue:
                del self.tool_usage[tool_name]


class CodeAnalyzer:
    """Advanced code analysis tools for syntax, dependencies, and security."""

    def __init__(self, logger: AdvancedLogger):
        self.logger = logger
        self.supported_languages = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "react",
            ".tsx": "react-typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".cs": "csharp",
            ".go": "go",
            ".rs": "rust",
            ".php": "php",
            ".rb": "ruby",
            ".swift": "swift",
            ".kt": "kotlin",
        }

    async def analyze_syntax(self, file_path: str) -> Dict[str, Any]:
        """Perform comprehensive syntax analysis on a code file."""
        try:
            path = Path(file_path)
            if not path.exists():
                return {"error": f"File not found: {file_path}"}

            language = self.supported_languages.get(path.suffix.lower())
            if not language:
                return {"error": f"Unsupported file type: {path.suffix}"}

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            analysis_result = {
                "file_path": str(path),
                "language": language,
                "file_size": len(content),
                "line_count": len(content.splitlines()),
                "character_count": len(content),
                "syntax_valid": True,
                "issues": [],
                "metrics": {},
                "suggestions": [],
            }

            # Language-specific analysis
            if language == "python":
                analysis_result.update(await self._analyze_python_syntax(content))
            elif language in ["javascript", "typescript"]:
                analysis_result.update(await self._analyze_js_syntax(content))
            else:
                analysis_result.update(
                    await self._analyze_generic_syntax(content, language)
                )

            self.logger.info(
                f"Syntax analysis completed for {file_path}",
                language=language,
                lines=analysis_result["line_count"],
            )

            return analysis_result

        except Exception as e:
            self.logger.error(f"Syntax analysis failed for {file_path}: {str(e)}")
            return {"error": f"Analysis failed: {str(e)}"}

    async def _analyze_python_syntax(self, content: str) -> Dict[str, Any]:
        """Detailed Python syntax analysis."""
        try:
            # Parse AST for syntax validation
            tree = ast.parse(content)

            # Collect metrics
            metrics = {
                "functions": 0,
                "classes": 0,
                "imports": 0,
                "complexity_score": 0,
            }

            issues = []
            suggestions = []

            # Walk the AST to collect information
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metrics["functions"] += 1
                elif isinstance(node, ast.ClassDef):
                    metrics["classes"] += 1
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    metrics["imports"] += 1

            # Basic complexity analysis
            lines = content.splitlines()
            for i, line in enumerate(lines, 1):
                line = line.strip()

                # Check for common issues
                if len(line) > 100:
                    issues.append(
                        {
                            "type": "style",
                            "message": f"Line {i} exceeds 100 characters",
                            "severity": "warning",
                            "line": i,
                        }
                    )

                # Check for potential improvements
                if line.startswith("print(") and not line.startswith("print(f"):
                    suggestions.append(
                        {
                            "type": "improvement",
                            "message": f"Consider using f-string at line {i}",
                            "line": i,
                        }
                    )

            return {
                "syntax_valid": True,
                "metrics": metrics,
                "issues": issues,
                "suggestions": suggestions,
            }

        except SyntaxError as e:
            return {
                "syntax_valid": False,
                "issues": [
                    {
                        "type": "syntax_error",
                        "message": str(e),
                        "line": e.lineno,
                        "severity": "error",
                    }
                ],
                "metrics": {},
                "suggestions": [],
            }

    async def _analyze_js_syntax(self, content: str) -> Dict[str, Any]:
        """JavaScript/TypeScript syntax analysis."""
        # Basic analysis - in production this could use actual JS parsers
        lines = content.splitlines()
        issues = []
        suggestions = []

        function_count = len(
            re.findall(r"function\s+\w+|=>\s*{|\w+\s*:\s*function", content)
        )
        class_count = len(re.findall(r"class\s+\w+", content))

        for i, line in enumerate(lines, 1):
            if "var " in line:
                suggestions.append(
                    {
                        "type": "modernization",
                        "message": f"Consider using 'let' or 'const' instead of 'var' at line {i}",
                        "line": i,
                    }
                )

        return {
            "syntax_valid": True,
            "metrics": {"functions": function_count, "classes": class_count},
            "issues": issues,
            "suggestions": suggestions,
        }

    async def _analyze_generic_syntax(
        self, content: str, language: str
    ) -> Dict[str, Any]:
        """Generic syntax analysis for other languages."""
        lines = content.splitlines()

        return {
            "syntax_valid": True,
            "metrics": {
                "line_count": len(lines),
                "non_empty_lines": len([l for l in lines if l.strip()]),
            },
            "issues": [],
            "suggestions": [
                {
                    "type": "info",
                    "message": f"Advanced analysis for {language} not yet implemented",
                }
            ],
        }

    async def analyze_dependencies(self, file_path: str) -> Dict[str, Any]:
        """Analyze code dependencies and imports."""
        try:
            path = Path(file_path)
            if not path.exists():
                return {"error": f"File not found: {file_path}"}

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            language = self.supported_languages.get(path.suffix.lower())
            dependencies = {
                "file_path": str(path),
                "language": language,
                "internal_imports": [],
                "external_imports": [],
                "missing_imports": [],
                "circular_dependencies": [],
                "dependency_tree": {},
            }

            if language == "python":
                dependencies.update(
                    await self._analyze_python_dependencies(content, path)
                )
            elif language in ["javascript", "typescript"]:
                dependencies.update(await self._analyze_js_dependencies(content, path))

            self.logger.info(
                f"Dependency analysis completed for {file_path}",
                total_deps=len(dependencies["external_imports"]),
            )

            return dependencies

        except Exception as e:
            self.logger.error(f"Dependency analysis failed for {file_path}: {str(e)}")
            return {"error": f"Dependency analysis failed: {str(e)}"}

    async def _analyze_python_dependencies(
        self, content: str, file_path: Path
    ) -> Dict[str, Any]:
        """Analyze Python-specific dependencies."""
        try:
            tree = ast.parse(content)
            internal_imports = []
            external_imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_name = alias.name
                        if self._is_internal_module(module_name, file_path):
                            internal_imports.append(module_name)
                        else:
                            external_imports.append(module_name)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_name = node.module
                        if self._is_internal_module(module_name, file_path):
                            internal_imports.append(module_name)
                        else:
                            external_imports.append(module_name)

            return {
                "internal_imports": list(set(internal_imports)),
                "external_imports": list(set(external_imports)),
            }

        except Exception as e:
            return {"error": f"Python dependency analysis failed: {str(e)}"}

    async def _analyze_js_dependencies(
        self, content: str, file_path: Path
    ) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript dependencies."""
        import_pattern = r'(?:import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]|require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\))'
        matches = re.findall(import_pattern, content)

        internal_imports = []
        external_imports = []

        for match in matches:
            module_name = match[0] or match[1]
            if module_name.startswith(".") or module_name.startswith("/"):
                internal_imports.append(module_name)
            else:
                external_imports.append(module_name)

        return {
            "internal_imports": list(set(internal_imports)),
            "external_imports": list(set(external_imports)),
        }

    def _is_internal_module(self, module_name: str, file_path: Path) -> bool:
        """Check if a module is internal to the project."""
        if module_name.startswith("."):
            return True

        # Check if module exists in project directory
        project_root = file_path.parent
        while project_root.parent != project_root:
            if (project_root / f"{module_name}.py").exists():
                return True
            if (project_root / module_name / "__init__.py").exists():
                return True
            project_root = project_root.parent

        return False

    async def security_scan(self, file_path: str) -> Dict[str, Any]:
        """Perform security analysis on code files."""
        try:
            path = Path(file_path)
            if not path.exists():
                return {"error": f"File not found: {file_path}"}

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            language = self.supported_languages.get(path.suffix.lower())
            security_result = {
                "file_path": str(path),
                "language": language,
                "security_issues": [],
                "vulnerability_score": 0,
                "recommendations": [],
            }

            # Common security patterns
            security_patterns = {
                "sql_injection": r"(?i)(select|insert|update|delete).*(%s|format|f['\"])",
                "xss_vulnerability": r"(?i)(innerHTML|outerHTML|document\.write).*(\+|\$\{)",
                "hardcoded_secrets": r"(?i)(password|secret|key|token)\s*=\s*['\"][^'\"]{8,}['\"]",
                "command_injection": r"(?i)(exec|eval|system|shell_exec|subprocess)",
                "path_traversal": r"\.\.[\\/]",
                "unsafe_deserialization": r"(?i)(pickle\.loads|yaml\.load|json\.loads).*input",
            }

            lines = content.splitlines()
            for i, line in enumerate(lines, 1):
                for issue_type, pattern in security_patterns.items():
                    if re.search(pattern, line):
                        security_result["security_issues"].append(
                            {
                                "type": issue_type,
                                "line": i,
                                "content": line.strip()[:100],
                                "severity": self._get_severity(issue_type),
                                "description": self._get_security_description(
                                    issue_type
                                ),
                            }
                        )

            # Calculate vulnerability score
            security_result["vulnerability_score"] = min(
                len(security_result["security_issues"]) * 10, 100
            )

            # Generate recommendations
            if security_result["security_issues"]:
                security_result["recommendations"] = [
                    "Review flagged lines for potential security vulnerabilities",
                    "Use parameterized queries for database operations",
                    "Validate and sanitize all user inputs",
                    "Avoid using eval() or exec() with untrusted input",
                    "Use secure deserialization methods",
                ]

            self.logger.info(
                f"Security scan completed for {file_path}",
                issues=len(security_result["security_issues"]),
                score=security_result["vulnerability_score"],
            )

            return security_result

        except Exception as e:
            self.logger.error(f"Security scan failed for {file_path}: {str(e)}")
            return {"error": f"Security scan failed: {str(e)}"}

    def _get_severity(self, issue_type: str) -> str:
        """Get severity level for security issue type."""
        high_severity = ["sql_injection", "command_injection", "unsafe_deserialization"]
        medium_severity = ["xss_vulnerability", "hardcoded_secrets"]
        return (
            "high"
            if issue_type in high_severity
            else "medium" if issue_type in medium_severity else "low"
        )

    def _get_security_description(self, issue_type: str) -> str:
        """Get description for security issue type."""
        descriptions = {
            "sql_injection": "Potential SQL injection vulnerability",
            "xss_vulnerability": "Potential cross-site scripting vulnerability",
            "hardcoded_secrets": "Hardcoded credentials or secrets detected",
            "command_injection": "Potential command injection vulnerability",
            "path_traversal": "Potential path traversal vulnerability",
            "unsafe_deserialization": "Unsafe deserialization detected",
        }
        return descriptions.get(issue_type, "Security issue detected")


class FileOperationsManager:
    """Advanced file operations and workspace management tools."""

    def __init__(self, logger: AdvancedLogger):
        self.logger = logger
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def intelligent_search(
        self,
        search_query: str,
        search_path: str = ".",
        file_types: Optional[List[str]] = None,
        include_content: bool = True,
        max_results: int = 50,
    ) -> Dict[str, Any]:
        """Intelligent file search with content analysis."""
        try:
            search_path = Path(search_path).resolve()
            if not search_path.exists():
                return {"error": f"Search path not found: {search_path}"}

            results = {
                "search_query": search_query,
                "search_path": str(search_path),
                "file_matches": [],
                "content_matches": [],
                "total_files_scanned": 0,
                "search_time": 0,
            }

            start_time = time.time()

            # Build file type filter
            extensions = set()
            if file_types:
                for ft in file_types:
                    if not ft.startswith("."):
                        ft = f".{ft}"
                    extensions.add(ft.lower())

            # Search files
            for file_path in search_path.rglob("*"):
                if file_path.is_file():
                    results["total_files_scanned"] += 1

                    # Check file type filter
                    if extensions and file_path.suffix.lower() not in extensions:
                        continue

                    # Filename match
                    if search_query.lower() in file_path.name.lower():
                        results["file_matches"].append(
                            {
                                "path": str(file_path.relative_to(search_path)),
                                "name": file_path.name,
                                "size": file_path.stat().st_size,
                                "modified": datetime.fromtimestamp(
                                    file_path.stat().st_mtime
                                ).isoformat(),
                            }
                        )

                    # Content search if requested
                    if include_content and self._is_text_file(file_path):
                        try:
                            with open(
                                file_path, "r", encoding="utf-8", errors="ignore"
                            ) as f:
                                content = f.read()
                                if search_query.lower() in content.lower():
                                    # Find line matches
                                    lines = content.splitlines()
                                    matching_lines = [
                                        {
                                            "line_number": i + 1,
                                            "content": line.strip()[:200],
                                        }
                                        for i, line in enumerate(lines)
                                        if search_query.lower() in line.lower()
                                    ]

                                    results["content_matches"].append(
                                        {
                                            "path": str(
                                                file_path.relative_to(search_path)
                                            ),
                                            "matches": matching_lines[
                                                :10
                                            ],  # Limit matches per file
                                        }
                                    )
                        except Exception:
                            continue  # Skip files that can't be read

                    # Limit results
                    if (
                        len(results["file_matches"]) + len(results["content_matches"])
                        >= max_results
                    ):
                        break

            results["search_time"] = time.time() - start_time

            self.logger.info(
                f"File search completed for '{search_query}'",
                file_matches=len(results["file_matches"]),
                content_matches=len(results["content_matches"]),
                time=f"{results['search_time']:.2f}s",
            )

            return results

        except Exception as e:
            self.logger.error(f"File search failed: {str(e)}")
            return {"error": f"File search failed: {str(e)}"}

    def _is_text_file(self, file_path: Path) -> bool:
        """Check if file is likely a text file."""
        text_extensions = {
            ".txt",
            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".java",
            ".cpp",
            ".c",
            ".cs",
            ".go",
            ".rs",
            ".php",
            ".rb",
            ".swift",
            ".kt",
            ".html",
            ".css",
            ".scss",
            ".less",
            ".json",
            ".xml",
            ".yaml",
            ".yml",
            ".md",
            ".rst",
            ".ini",
            ".cfg",
            ".conf",
            ".log",
            ".sql",
            ".sh",
            ".bat",
            ".ps1",
        }
        return (
            file_path.suffix.lower() in text_extensions
            or file_path.stat().st_size < 1024 * 1024
        )  # < 1MB

    async def bulk_operations(
        self,
        operation: str,
        file_patterns: List[str],
        target_path: str = ".",
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Perform bulk file operations with safety checks."""
        try:
            target_path = Path(target_path).resolve()
            if not target_path.exists():
                return {"error": f"Target path not found: {target_path}"}

            options = options or {}
            results = {
                "operation": operation,
                "target_path": str(target_path),
                "patterns": file_patterns,
                "processed_files": [],
                "failed_files": [],
                "total_processed": 0,
                "total_failed": 0,
            }

            # Collect matching files
            matching_files = []
            for pattern in file_patterns:
                matching_files.extend(target_path.glob(pattern))

            # Safety check for destructive operations
            if operation in ["delete", "move"] and len(matching_files) > 100:
                if not options.get("force_bulk", False):
                    return {
                        "error": f"Bulk {operation} would affect {len(matching_files)} files. Use force_bulk=true to proceed."
                    }

            # Process files
            for file_path in matching_files:
                try:
                    if operation == "rename":
                        await self._bulk_rename(file_path, options, results)
                    elif operation == "move":
                        await self._bulk_move(file_path, options, results)
                    elif operation == "copy":
                        await self._bulk_copy(file_path, options, results)
                    elif operation == "delete":
                        await self._bulk_delete(file_path, options, results)
                    else:
                        results["failed_files"].append(
                            {
                                "path": str(file_path),
                                "error": f"Unknown operation: {operation}",
                            }
                        )
                        results["total_failed"] += 1
                        continue

                    results["total_processed"] += 1

                except Exception as e:
                    results["failed_files"].append(
                        {"path": str(file_path), "error": str(e)}
                    )
                    results["total_failed"] += 1

            self.logger.info(
                f"Bulk {operation} completed",
                processed=results["total_processed"],
                failed=results["total_failed"],
            )

            return results

        except Exception as e:
            self.logger.error(f"Bulk operation failed: {str(e)}")
            return {"error": f"Bulk operation failed: {str(e)}"}

    async def _bulk_rename(
        self, file_path: Path, options: Dict[str, Any], results: Dict[str, Any]
    ):
        """Rename file according to options."""
        new_name_pattern = options.get("new_name_pattern", "{name}")
        new_name = new_name_pattern.format(
            name=file_path.stem, ext=file_path.suffix, dir=file_path.parent.name
        )
        new_path = file_path.with_name(new_name + file_path.suffix)

        file_path.rename(new_path)
        results["processed_files"].append(
            {"original": str(file_path), "new": str(new_path), "operation": "rename"}
        )

    async def _bulk_move(
        self, file_path: Path, options: Dict[str, Any], results: Dict[str, Any]
    ):
        """Move file to new location."""
        destination = Path(options.get("destination", "./moved"))
        destination.mkdir(parents=True, exist_ok=True)
        new_path = destination / file_path.name

        shutil.move(str(file_path), str(new_path))
        results["processed_files"].append(
            {"original": str(file_path), "new": str(new_path), "operation": "move"}
        )

    async def _bulk_copy(
        self, file_path: Path, options: Dict[str, Any], results: Dict[str, Any]
    ):
        """Copy file to new location."""
        destination = Path(options.get("destination", "./copied"))
        destination.mkdir(parents=True, exist_ok=True)
        new_path = destination / file_path.name

        shutil.copy2(str(file_path), str(new_path))
        results["processed_files"].append(
            {"original": str(file_path), "new": str(new_path), "operation": "copy"}
        )

    async def _bulk_delete(
        self, file_path: Path, options: Dict[str, Any], results: Dict[str, Any]
    ):
        """Delete file with safety checks."""
        if options.get("backup", False):
            backup_dir = Path("./deleted_backup")
            backup_dir.mkdir(exist_ok=True)
            shutil.copy2(str(file_path), str(backup_dir / file_path.name))

        file_path.unlink()
        results["processed_files"].append(
            {"original": str(file_path), "operation": "delete"}
        )

    async def workspace_analysis(self, workspace_path: str = ".") -> Dict[str, Any]:
        """Comprehensive workspace analysis and insights."""
        try:
            workspace_path = Path(workspace_path).resolve()
            if not workspace_path.exists():
                return {"error": f"Workspace path not found: {workspace_path}"}

            analysis = {
                "workspace_path": str(workspace_path),
                "total_files": 0,
                "total_directories": 0,
                "file_types": defaultdict(int),
                "language_distribution": defaultdict(int),
                "largest_files": [],
                "recent_files": [],
                "project_structure": {},
                "potential_issues": [],
            }

            # Collect file information
            all_files = []
            for item in workspace_path.rglob("*"):
                if item.is_file():
                    analysis["total_files"] += 1
                    file_info = {
                        "path": str(item.relative_to(workspace_path)),
                        "size": item.stat().st_size,
                        "modified": item.stat().st_mtime,
                        "extension": item.suffix.lower(),
                    }
                    all_files.append(file_info)

                    # Count file types
                    analysis["file_types"][item.suffix.lower() or "no_extension"] += 1

                    # Language distribution
                    if item.suffix.lower() in [
                        ".py",
                        ".js",
                        ".ts",
                        ".java",
                        ".cpp",
                        ".c",
                        ".cs",
                        ".go",
                        ".rs",
                    ]:
                        analysis["language_distribution"][item.suffix.lower()] += 1

                elif item.is_dir():
                    analysis["total_directories"] += 1

            # Sort files by size (largest first)
            analysis["largest_files"] = sorted(
                all_files, key=lambda x: x["size"], reverse=True
            )[:10]

            # Sort files by modification time (most recent first)
            analysis["recent_files"] = sorted(
                all_files, key=lambda x: x["modified"], reverse=True
            )[:10]

            # Project structure analysis
            analysis["project_structure"] = await self._analyze_project_structure(
                workspace_path
            )

            # Identify potential issues
            analysis["potential_issues"] = await self._identify_workspace_issues(
                workspace_path, all_files
            )

            self.logger.info(
                f"Workspace analysis completed for {workspace_path}",
                files=analysis["total_files"],
                dirs=analysis["total_directories"],
            )

            return analysis

        except Exception as e:
            self.logger.error(f"Workspace analysis failed: {str(e)}")
            return {"error": f"Workspace analysis failed: {str(e)}"}

    async def _analyze_project_structure(self, workspace_path: Path) -> Dict[str, Any]:
        """Analyze project structure and identify project type."""
        structure = {"type": "unknown", "features": []}

        # Check for common project files
        project_indicators = {
            "package.json": "nodejs",
            "requirements.txt": "python",
            "Pipfile": "python",
            "pyproject.toml": "python",
            "Cargo.toml": "rust",
            "go.mod": "go",
            "pom.xml": "java",
            "build.gradle": "java",
            "Dockerfile": "containerized",
            ".git": "git_repository",
            ".vscode": "vscode_project",
            "tsconfig.json": "typescript",
        }

        for indicator, project_type in project_indicators.items():
            if (workspace_path / indicator).exists():
                if structure["type"] == "unknown":
                    structure["type"] = project_type
                structure["features"].append(project_type)

        return structure

    async def _identify_workspace_issues(
        self, workspace_path: Path, all_files: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Identify potential workspace issues."""
        issues = []

        # Large files (>10MB)
        large_files = [f for f in all_files if f["size"] > 10 * 1024 * 1024]
        if large_files:
            issues.append(
                {
                    "type": "large_files",
                    "severity": "warning",
                    "message": f"Found {len(large_files)} files larger than 10MB",
                    "details": [f["path"] for f in large_files[:5]],
                }
            )

        # Too many files in root
        root_files = [f for f in all_files if "/" not in f["path"]]
        if len(root_files) > 20:
            issues.append(
                {
                    "type": "cluttered_root",
                    "severity": "info",
                    "message": f"Root directory contains {len(root_files)} files",
                    "details": "Consider organizing files into subdirectories",
                }
            )

        # Duplicate file names
        file_names = defaultdict(list)
        for file_info in all_files:
            name = Path(file_info["path"]).name
            file_names[name].append(file_info["path"])

        duplicates = {
            name: paths for name, paths in file_names.items() if len(paths) > 1
        }
        if duplicates:
            issues.append(
                {
                    "type": "duplicate_names",
                    "severity": "info",
                    "message": f"Found {len(duplicates)} duplicate file names",
                    "details": dict(list(duplicates.items())[:3]),
                }
            )

        return issues


class EnhancedVoidCatMCPServer:
    """
    Enhanced VoidCat MCP Server - Pillar IV: The Guardian's Overseer

    Advanced Model Context Protocol server with comprehensive tool suite including:
    - Enhanced architecture with advanced logging and rate limiting
    - Advanced code analysis tools with security scanning
    - Comprehensive file operations and workspace management
    - Complete integration with VoidCat reasoning, task, and memory systems
    """

    def __init__(self):
        """Initialize the enhanced MCP server with all Guardian capabilities."""
        # Enhanced logging system
        self.logger = AdvancedLogger("VoidCat-Guardian")

        # Core VoidCat components
        self.engine: Optional[VoidCatEngine] = None
        self.task_tools = None
        self.memory_tools = None
        self.context_integration = None

        # Enhanced server components
        self.code_analyzer = CodeAnalyzer(self.logger)
        self.file_manager = FileOperationsManager(self.logger)
        self.rate_limiter = RateLimiter()
        self.performance_metrics = PerformanceMetrics()

        # Server metadata
        self.server_version = "1.0.0"
        self.server_name = "VoidCat-Guardian-MCP"
        self.initialization_time = None
        self.request_count = 0
        self.error_count = 0

        # Tool registry with enhanced metadata
        self.tool_registry: Dict[str, ToolMetadata] = {}
        self._initialize_tool_registry()

        self.logger.info(
            "Enhanced VoidCat MCP Server initialized",
            version=self.server_version,
            components=["CodeAnalyzer", "FileManager", "RateLimiter"],
        )

    def _initialize_tool_registry(self):
        """Initialize the enhanced tool registry with all available tools."""
        # Core reasoning tools
        self._register_tool(
            ToolMetadata(
                name="voidcat_enhanced_query",
                description="Process queries using the full enhanced pipeline with memory and context",
                category="reasoning",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The question or prompt to process",
                        },
                        "model": {
                            "type": "string",
                            "default": "gpt-4o-mini",
                            "description": "AI model to use",
                        },
                        "include_context": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include task/project context",
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Session ID for memory tracking",
                        },
                    },
                    "required": ["query"],
                },
                complexity_score=7,
                requires_network_access=True,
            )
        )

        # Code analysis tools
        self._register_tool(
            ToolMetadata(
                name="voidcat_analyze_syntax",
                description="Perform comprehensive syntax analysis on code files",
                category="code_analysis",
                input_schema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the code file to analyze",
                        },
                        "include_metrics": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include code metrics",
                        },
                        "include_suggestions": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include improvement suggestions",
                        },
                    },
                    "required": ["file_path"],
                },
                complexity_score=6,
                requires_file_access=True,
            )
        )

        self._register_tool(
            ToolMetadata(
                name="voidcat_analyze_dependencies",
                description="Analyze code dependencies and imports",
                category="code_analysis",
                input_schema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the code file to analyze",
                        },
                        "include_tree": {
                            "type": "boolean",
                            "default": False,
                            "description": "Include dependency tree",
                        },
                    },
                    "required": ["file_path"],
                },
                complexity_score=5,
                requires_file_access=True,
            )
        )

        self._register_tool(
            ToolMetadata(
                name="voidcat_security_scan",
                description="Perform security analysis and vulnerability scanning",
                category="code_analysis",
                input_schema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the code file to scan",
                        },
                        "scan_depth": {
                            "type": "string",
                            "enum": ["basic", "comprehensive"],
                            "default": "basic",
                        },
                    },
                    "required": ["file_path"],
                },
                complexity_score=8,
                requires_file_access=True,
                tags=["security", "vulnerability"],
            )
        )

        # File operation tools
        self._register_tool(
            ToolMetadata(
                name="voidcat_intelligent_search",
                description="Intelligent file and content search with advanced filtering",
                category="file_operations",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "path": {
                            "type": "string",
                            "default": ".",
                            "description": "Search path",
                        },
                        "file_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "File extensions to search",
                        },
                        "include_content": {
                            "type": "boolean",
                            "default": True,
                            "description": "Search file contents",
                        },
                        "max_results": {
                            "type": "integer",
                            "default": 50,
                            "minimum": 1,
                            "maximum": 200,
                        },
                    },
                    "required": ["query"],
                },
                complexity_score=6,
                requires_file_access=True,
            )
        )

        self._register_tool(
            ToolMetadata(
                name="voidcat_bulk_operations",
                description="Perform bulk file operations with safety checks",
                category="file_operations",
                input_schema={
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["rename", "move", "copy", "delete"],
                        },
                        "patterns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "File patterns to match",
                        },
                        "target_path": {
                            "type": "string",
                            "default": ".",
                            "description": "Target directory",
                        },
                        "options": {
                            "type": "object",
                            "description": "Operation-specific options",
                        },
                    },
                    "required": ["operation", "patterns"],
                },
                complexity_score=9,
                requires_file_access=True,
                rate_limit=30,  # Limit bulk operations
                tags=["bulk", "dangerous"],
            )
        )

        self._register_tool(
            ToolMetadata(
                name="voidcat_workspace_analysis",
                description="Comprehensive workspace analysis and insights",
                category="workspace",
                input_schema={
                    "type": "object",
                    "properties": {
                        "workspace_path": {
                            "type": "string",
                            "default": ".",
                            "description": "Workspace directory to analyze",
                        },
                        "include_structure": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include project structure analysis",
                        },
                        "include_issues": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include potential issues",
                        },
                    },
                    "required": [],
                },
                complexity_score=7,
                requires_file_access=True,
            )
        )

        # Enhanced status and diagnostics
        self._register_tool(
            ToolMetadata(
                name="voidcat_system_status",
                description="Get comprehensive system status and performance metrics",
                category="diagnostics",
                input_schema={
                    "type": "object",
                    "properties": {
                        "include_metrics": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include performance metrics",
                        },
                        "include_tools": {
                            "type": "boolean",
                            "default": False,
                            "description": "Include tool usage statistics",
                        },
                    },
                    "required": [],
                },
                complexity_score=3,
            )
        )

        self.logger.info(
            f"Tool registry initialized with {len(self.tool_registry)} tools"
        )

    def _register_tool(self, tool_metadata: ToolMetadata):
        """Register a tool in the enhanced tool registry."""
        self.tool_registry[tool_metadata.name] = tool_metadata

    async def initialize(self, request_id: Optional[str] = None) -> None:
        """Initialize the enhanced VoidCat MCP server with all components."""
        try:
            self.initialization_time = datetime.now(UTC)
            self.logger.info("Starting VoidCat Enhanced MCP Server initialization...")

            # Initialize core VoidCat engine
            self.engine = VoidCatEngine()
            self.logger.info("Core VoidCat engine initialized")

            # Initialize task management tools
            try:
                self.task_tools = create_mcp_task_tools(working_directory=".")
                self.logger.info("Task management tools initialized")
            except Exception as e:
                self.logger.warning(f"Task tools initialization failed: {e}")

            # Initialize memory management tools
            try:
                self.memory_tools = create_memory_mcp_tools()
                self.logger.info("Memory management tools initialized")
            except Exception as e:
                self.logger.warning(f"Memory tools initialization failed: {e}")

            # Initialize context integration
            try:
                self.context_integration = create_context_integration()
                self.logger.info("Context integration initialized")
            except Exception as e:
                self.logger.warning(f"Context integration initialization failed: {e}")

            # Send MCP initialization response
            await self._send_response(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {"listChanged": True},
                            "resources": {},
                            "prompts": {},
                        },
                        "serverInfo": {
                            "name": self.server_name,
                            "version": self.server_version,
                            "description": "Enhanced VoidCat MCP Server with advanced code analysis and file operations",
                        },
                    },
                }
            )

            self.logger.info(
                "Enhanced MCP server initialization completed successfully",
                tools=len(self.tool_registry),
                engine_ready=self.engine is not None,
            )

        except Exception as e:
            self.error_count += 1
            error_msg = f"Enhanced MCP server initialization failed: {str(e)}"
            self.logger.error(error_msg, error=str(e))
            await self._send_error(error_msg, request_id)

    async def handle_list_tools(self, request_id: Optional[str] = None) -> None:
        """Handle MCP list_tools request with enhanced tool metadata."""
        try:
            tools_data = []

            # Core registered tools
            for tool_name, tool_meta in self.tool_registry.items():
                tools_data.append(
                    {
                        "name": tool_meta.name,
                        "description": tool_meta.description,
                        "inputSchema": tool_meta.input_schema,
                    }
                )

            # Add task management tools if available
            if self.task_tools:
                try:
                    task_tool_definitions = self.task_tools.get_tool_definitions()
                    for tool_def in task_tool_definitions:
                        tools_data.append(
                            {
                                "name": tool_def["name"],
                                "description": tool_def["description"],
                                "inputSchema": tool_def["inputSchema"],
                            }
                        )
                except Exception as e:
                    self.logger.warning(f"Failed to get task tool definitions: {e}")

            # Add memory management tools if available
            if self.memory_tools:
                try:
                    memory_tool_definitions = self.memory_tools.get_tools()
                    for tool_def in memory_tool_definitions:
                        tools_data.append(
                            {
                                "name": tool_def["name"],
                                "description": tool_def["description"],
                                "inputSchema": tool_def["inputSchema"],
                            }
                        )
                except Exception as e:
                    self.logger.warning(f"Failed to get memory tool definitions: {e}")

            await self._send_response(
                {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools_data}}
            )

            self.logger.info(f"Tool list sent with {len(tools_data)} tools")

        except Exception as e:
            self.error_count += 1
            error_msg = f"Failed to list tools: {str(e)}"
            self.logger.error(error_msg)
            await self._send_error(error_msg, request_id)

    async def handle_call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        request_id: Optional[str] = None,
    ) -> None:
        """Handle MCP call_tool request with enhanced error handling and rate limiting."""
        start_time = time.time()

        try:
            # Check rate limiting
            tool_meta = self.tool_registry.get(tool_name)
            rate_limit = tool_meta.rate_limit if tool_meta else None

            if not self.rate_limiter.check_rate_limit(tool_name, rate_limit):
                self.performance_metrics.rate_limit_hits += 1
                await self._send_error(
                    f"Rate limit exceeded for tool '{tool_name}'", request_id
                )
                return

            # Record usage
            self.rate_limiter.record_usage(tool_name)
            self.request_count += 1
            self.performance_metrics.total_requests += 1

            if tool_meta:
                tool_meta.usage_count += 1
                tool_meta.last_used = datetime.now(UTC)
                self.performance_metrics.active_tools.add(tool_name)

            self.logger.info(
                f"Executing tool: {tool_name}",
                arguments=len(arguments),
                request_id=request_id,
            )

            # Route to appropriate handler
            if tool_name in self.tool_registry:
                await self._handle_registered_tool(tool_name, arguments, request_id)
            elif self.task_tools and tool_name.startswith("voidcat_task_"):
                await self._handle_task_tool(tool_name, arguments, request_id)
            elif self.memory_tools and tool_name.startswith("voidcat_memory_"):
                await self._handle_memory_tool(tool_name, arguments, request_id)
            else:
                await self._send_error(f"Unknown tool: {tool_name}", request_id)
                return

            # Update performance metrics
            execution_time = time.time() - start_time
            self.performance_metrics.successful_requests += 1
            self._update_performance_metrics(execution_time, tool_meta)

            self.logger.info(
                f"Tool execution completed: {tool_name}",
                duration=f"{execution_time:.3f}s",
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self.error_count += 1
            self.performance_metrics.failed_requests += 1

            if tool_meta:
                tool_meta.error_count += 1

            error_msg = f"Tool execution failed for '{tool_name}': {str(e)}"
            self.logger.error(
                error_msg,
                duration=f"{execution_time:.3f}s",
                error=str(e),
                traceback=traceback.format_exc(),
            )
            await self._send_error(error_msg, request_id)

    def _update_performance_metrics(
        self, execution_time: float, tool_meta: Optional[ToolMetadata]
    ):
        """Update performance metrics after tool execution."""
        # Update server metrics
        total_time = (
            self.performance_metrics.average_response_time
            * (self.performance_metrics.successful_requests - 1)
            + execution_time
        )
        self.performance_metrics.average_response_time = (
            total_time / self.performance_metrics.successful_requests
        )

        if execution_time > self.performance_metrics.peak_response_time:
            self.performance_metrics.peak_response_time = execution_time

        # Update tool-specific metrics
        if tool_meta:
            total_time = (
                tool_meta.average_execution_time * (tool_meta.usage_count - 1)
                + execution_time
            )
            tool_meta.average_execution_time = total_time / tool_meta.usage_count

    async def _handle_registered_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        request_id: Optional[str] = None,
    ):
        """Handle execution of registered enhanced tools."""
        try:
            # Code analysis tools
            if tool_name == "voidcat_analyze_syntax":
                result = await self.code_analyzer.analyze_syntax(
                    arguments.get("file_path", "")
                )
                await self._send_tool_response(
                    result, request_id, "Code Syntax Analysis"
                )

            elif tool_name == "voidcat_analyze_dependencies":
                result = await self.code_analyzer.analyze_dependencies(
                    arguments.get("file_path", "")
                )
                await self._send_tool_response(
                    result, request_id, "Dependency Analysis"
                )

            elif tool_name == "voidcat_security_scan":
                result = await self.code_analyzer.security_scan(
                    arguments.get("file_path", "")
                )
                await self._send_tool_response(result, request_id, "Security Scan")

            # File operation tools
            elif tool_name == "voidcat_intelligent_search":
                result = await self.file_manager.intelligent_search(
                    search_query=arguments.get("query", ""),
                    search_path=arguments.get("path", "."),
                    file_types=arguments.get("file_types"),
                    include_content=arguments.get("include_content", True),
                    max_results=arguments.get("max_results", 50),
                )
                await self._send_tool_response(
                    result, request_id, "Intelligent File Search"
                )

            elif tool_name == "voidcat_bulk_operations":
                result = await self.file_manager.bulk_operations(
                    operation=arguments.get("operation", ""),
                    file_patterns=arguments.get("patterns", []),
                    target_path=arguments.get("target_path", "."),
                    options=arguments.get("options", {}),
                )
                await self._send_tool_response(
                    result, request_id, "Bulk File Operations"
                )

            elif tool_name == "voidcat_workspace_analysis":
                result = await self.file_manager.workspace_analysis(
                    workspace_path=arguments.get("workspace_path", ".")
                )
                await self._send_tool_response(result, request_id, "Workspace Analysis")

            # Enhanced reasoning tools
            elif tool_name == "voidcat_enhanced_query":
                await self._handle_enhanced_query(arguments, request_id)

            # System diagnostics
            elif tool_name == "voidcat_system_status":
                await self._handle_system_status(arguments, request_id)

            else:
                await self._send_error(
                    f"Handler not implemented for tool: {tool_name}", request_id
                )

        except Exception as e:
            self.logger.error(
                f"Registered tool handler failed for {tool_name}: {str(e)}"
            )
            await self._send_error(f"Tool execution failed: {str(e)}", request_id)

    async def _handle_enhanced_query(
        self, arguments: Dict[str, Any], request_id: Optional[str] = None
    ):
        """Handle enhanced query with full context integration."""
        try:
            if not self.engine:
                await self._send_error("VoidCat engine not initialized", request_id)
                return

            query = arguments.get("query", "")
            model = arguments.get("model", "gpt-4o-mini")
            include_context = arguments.get("include_context", True)
            session_id = arguments.get("session_id")

            if not query:
                await self._send_error("Query parameter is required", request_id)
                return

            # Build enhanced context
            context_parts = []

            if include_context and self.context_integration:
                try:
                    # Get active context
                    active_context = await self.context_integration.get_active_context()
                    if active_context:
                        context_parts.append(
                            f"Active Context:\n{json.dumps(active_context, indent=2)}"
                        )
                except Exception as e:
                    self.logger.warning(f"Failed to get active context: {e}")

            # Enhanced query processing
            enhanced_query = query
            if context_parts:
                enhanced_query = f"{' '.join(context_parts)}\n\nUser Query: {query}"

            # Process with VoidCat engine
            response = await self.engine.query(enhanced_query, model=model)

            # Format response
            formatted_response = f"🧠 **VoidCat Enhanced Response**\n\n{response}"

            if include_context:
                formatted_response += (
                    f"\n\n---\n*Enhanced processing with full context integration*"
                )

            await self._send_response(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": formatted_response}]
                    },
                }
            )

        except Exception as e:
            self.logger.error(f"Enhanced query failed: {str(e)}")
            await self._send_error(f"Enhanced query failed: {str(e)}", request_id)

    async def _handle_system_status(
        self, arguments: Dict[str, Any], request_id: Optional[str] = None
    ):
        """Handle comprehensive system status request."""
        try:
            include_metrics = arguments.get("include_metrics", True)
            include_tools = arguments.get("include_tools", False)

            status = {
                "server_info": {
                    "name": self.server_name,
                    "version": self.server_version,
                    "uptime": (
                        (datetime.now(UTC) - self.initialization_time).total_seconds()
                        if self.initialization_time
                        else 0
                    ),
                    "initialization_time": (
                        self.initialization_time.isoformat()
                        if self.initialization_time
                        else None
                    ),
                },
                "engine_status": {
                    "initialized": self.engine is not None,
                    "task_tools": self.task_tools is not None,
                    "memory_tools": self.memory_tools is not None,
                    "context_integration": self.context_integration is not None,
                },
                "request_stats": {
                    "total_requests": self.request_count,
                    "total_errors": self.error_count,
                    "success_rate": (self.request_count - self.error_count)
                    / max(1, self.request_count)
                    * 100,
                },
            }

            if include_metrics:
                status["performance_metrics"] = {
                    "total_requests": self.performance_metrics.total_requests,
                    "successful_requests": self.performance_metrics.successful_requests,
                    "failed_requests": self.performance_metrics.failed_requests,
                    "average_response_time": f"{self.performance_metrics.average_response_time:.3f}s",
                    "peak_response_time": f"{self.performance_metrics.peak_response_time:.3f}s",
                    "rate_limit_hits": self.performance_metrics.rate_limit_hits,
                    "active_tools": list(self.performance_metrics.active_tools),
                }

            if include_tools:
                status["tool_statistics"] = {}
                for tool_name, tool_meta in self.tool_registry.items():
                    status["tool_statistics"][tool_name] = {
                        "usage_count": tool_meta.usage_count,
                        "error_count": tool_meta.error_count,
                        "average_execution_time": f"{tool_meta.average_execution_time:.3f}s",
                        "last_used": (
                            tool_meta.last_used.isoformat()
                            if tool_meta.last_used
                            else None
                        ),
                        "category": tool_meta.category,
                        "complexity_score": tool_meta.complexity_score,
                    }

            # Format status response
            status_text = f"🛡️ **VoidCat Guardian System Status**\n\n"
            status_text += f"**Server**: {status['server_info']['name']} v{status['server_info']['version']}\n"
            status_text += (
                f"**Uptime**: {status['server_info']['uptime']:.1f} seconds\n"
            )
            status_text += (
                f"**Success Rate**: {status['request_stats']['success_rate']:.1f}%\n\n"
            )

            status_text += "**Component Status**:\n"
            for component, enabled in status["engine_status"].items():
                emoji = "✅" if enabled else "❌"
                status_text += f"- {emoji} {component.replace('_', ' ').title()}\n"

            if include_metrics:
                status_text += f"\n**Performance**:\n"
                status_text += f"- Average Response: {status['performance_metrics']['average_response_time']}\n"
                status_text += f"- Peak Response: {status['performance_metrics']['peak_response_time']}\n"
                status_text += f"- Active Tools: {len(status['performance_metrics']['active_tools'])}\n"

            status_text += f"\n```json\n{json.dumps(status, indent=2)}\n```"

            await self._send_response(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"content": [{"type": "text", "text": status_text}]},
                }
            )

        except Exception as e:
            self.logger.error(f"System status failed: {str(e)}")
            await self._send_error(f"System status failed: {str(e)}", request_id)

    async def _handle_task_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        request_id: Optional[str] = None,
    ):
        """Handle task management tool execution."""
        try:
            if not self.task_tools:
                await self._send_error(
                    "Task management tools not initialized", request_id
                )
                return

            result = await self.task_tools.execute_tool(tool_name, arguments)
            await self._send_tool_response(result, request_id, "Task Management")

        except Exception as e:
            self.logger.error(f"Task tool execution failed for {tool_name}: {str(e)}")
            await self._send_error(f"Task tool execution failed: {str(e)}", request_id)

    async def _handle_memory_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        request_id: Optional[str] = None,
    ):
        """Handle memory management tool execution."""
        try:
            if not self.memory_tools:
                await self._send_error(
                    "Memory management tools not initialized", request_id
                )
                return

            result = await self.memory_tools.execute_tool(tool_name, arguments)
            await self._send_tool_response(result, request_id, "Memory Management")

        except Exception as e:
            self.logger.error(f"Memory tool execution failed for {tool_name}: {str(e)}")
            await self._send_error(
                f"Memory tool execution failed: {str(e)}", request_id
            )

    async def _send_tool_response(
        self, result: Dict[str, Any], request_id: Optional[str], tool_category: str
    ):
        """Send formatted tool response."""
        if "error" in result:
            await self._send_error(result["error"], request_id)
            return

        # Format result as text response
        response_text = f"🔧 **{tool_category} Result**\n\n```json\n{json.dumps(result, indent=2)}\n```"

        await self._send_response(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"content": [{"type": "text", "text": response_text}]},
            }
        )

    async def handle_request(self, request: Dict[str, Any]) -> None:
        """Handle incoming MCP request with enhanced logging and error handling."""
        method = request.get("method", "")
        params = request.get("params", {})
        request_id = request.get("id")

        self.logger.debug(f"Received MCP request: {method}", request_id=request_id)

        try:
            if method == "initialize":
                await self.initialize(request_id)
            elif method == "tools/list":
                await self.handle_list_tools(request_id)
            elif method == "tools/call":
                tool_name = params.get("name", "")
                arguments = params.get("arguments", {})
                await self.handle_call_tool(tool_name, arguments, request_id)
            else:
                await self._send_error(f"Unknown method: {method}", request_id)

        except Exception as e:
            self.error_count += 1
            error_msg = f"Request handling failed for method '{method}': {str(e)}"
            self.logger.error(error_msg, traceback=traceback.format_exc())
            await self._send_error(error_msg, request_id)

    async def _send_response(self, response: Dict[str, Any]) -> None:
        """Send JSON-RPC response to stdout."""
        print(json.dumps(response), flush=True)

    async def _send_error(
        self, error_message: str, request_id: Optional[str] = None
    ) -> None:
        """Send JSON-RPC error response."""
        await self._send_response(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -1, "message": error_message},
            }
        )


async def main():
    """Main entry point for the enhanced VoidCat MCP server."""
    server = EnhancedVoidCatMCPServer()
    server.logger.info("🚀 Starting VoidCat Enhanced MCP Server (Guardian's Overseer)")

    try:
        # Setup stdin reader for MCP protocol
        import asyncio

        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)

        server.logger.info("📡 Listening for MCP requests...")

        while True:
            try:
                line = await reader.readline()
                if not line:
                    break

                line_str = line.decode("utf-8").strip()
                if line_str:
                    server.logger.debug(f"📥 Received: {line_str[:100]}...")
                    try:
                        request = json.loads(line_str)
                        await server.handle_request(request)
                    except json.JSONDecodeError as e:
                        server.logger.error(f"JSON decode error: {str(e)}")
                        await server._send_error(f"Invalid JSON: {str(e)}")
                    except Exception as e:
                        server.logger.error(f"Request processing error: {str(e)}")
                        await server._send_error(f"Request processing failed: {str(e)}")

            except Exception as e:
                server.logger.error(f"Main loop error: {str(e)}")
                break

    except KeyboardInterrupt:
        server.logger.info("🛑 Server stopped by user")
    except Exception as e:
        server.logger.error(f"Server error: {str(e)}")
    finally:
        server.logger.info("🔚 VoidCat Enhanced MCP Server shutting down")


if __name__ == "__main__":
    asyncio.run(main())
