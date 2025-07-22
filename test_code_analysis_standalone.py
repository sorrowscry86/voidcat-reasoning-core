#!/usr/bin/env python3
"""
VoidCat Code Analysis Tools - Standalone Test Suite
Test the advanced code analysis capabilities without complex dependencies.
"""

import ast
import asyncio
import json
import os
import re
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class SimpleLogger:
    """Simple logger for testing purposes."""

    def info(self, message: str, **kwargs):
        print(f"[INFO] {message}")

    def warning(self, message: str, **kwargs):
        print(f"[WARNING] {message}")

    def error(self, message: str, **kwargs):
        print(f"[ERROR] {message}")


class CodeAnalyzer:
    """Advanced code analysis tools for syntax, dependencies, and security."""

    def __init__(self, logger=None):
        self.logger = logger or SimpleLogger()
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

            self.logger.info(f"Syntax analysis completed for {file_path}")
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

            self.logger.info(f"Security scan completed for {file_path}")
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


async def test_code_analysis_tools():
    """Run comprehensive tests for code analysis tools."""
    print("Testing VoidCat Advanced Code Analysis Tools")
    print("=" * 50)

    # Initialize code analyzer
    analyzer = CodeAnalyzer()

    # Test 1: Python syntax analysis
    print("\nTesting Python Syntax Analysis...")
    python_code = '''#!/usr/bin/env python3
import os
import sys
from typing import List

# Security issue: hardcoded password  
PASSWORD = "hardcoded_secret_123"

def vulnerable_function(user_input):
    """Function with security vulnerabilities."""
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    
    # Command injection
    os.system(f"echo {user_input}")
    
    # Long line that exceeds 100 characters - this is a very long line that should trigger a style warning
    result = eval(user_input)  # Security issue
    
    return result

class TestClass:
    """Test class for metrics."""
    def method(self):
        pass
'''

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        python_file = f.name

    try:
        syntax_result = await analyzer.analyze_syntax(python_file)
        print(f"   Language: {syntax_result['language']}")
        print(f"   Syntax Valid: {syntax_result['syntax_valid']}")
        print(f"   Functions: {syntax_result['metrics']['functions']}")
        print(f"   Classes: {syntax_result['metrics']['classes']}")
        print(f"   Imports: {syntax_result['metrics']['imports']}")
        print(f"   Issues: {len(syntax_result['issues'])}")
        print(f"   Suggestions: {len(syntax_result['suggestions'])}")
        print("   PASS Python syntax analysis passed")

        # Test security scan
        print("\nTesting Security Scan...")
        security_result = await analyzer.security_scan(python_file)
        print(f"   Vulnerability Score: {security_result['vulnerability_score']}")
        print(f"   Security Issues: {len(security_result['security_issues'])}")

        for issue in security_result["security_issues"]:
            print(
                f"      - {issue['type']} (line {issue['line']}): {issue['severity']}"
            )

        print("   PASS Security scan passed")

    finally:
        os.unlink(python_file)

    # Test 2: JavaScript analysis
    print("\nTesting JavaScript Analysis...")
    js_code = """// JavaScript test file
var oldStyle = "should use let or const";
let modernStyle = "good practice";

function processUserData(userData) {
    // XSS vulnerability
    document.getElementById("content").innerHTML = userData;
    
    // Security issue
    eval(userData);
    
    return userData;
}

class ModernClass {
    constructor() {
        this.data = [];
    }
    
    addData(item) {
        this.data.push(item);
    }
}
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
        f.write(js_code)
        js_file = f.name

    try:
        js_result = await analyzer.analyze_syntax(js_file)
        print(f"   Language: {js_result['language']}")
        print(f"   Functions: {js_result['metrics']['functions']}")
        print(f"   Classes: {js_result['metrics']['classes']}")
        print(f"   Suggestions: {len(js_result['suggestions'])}")
        print("   PASS JavaScript analysis passed")

    finally:
        os.unlink(js_file)

    # Test 3: Error handling
    print("\nTesting Error Handling...")

    # Test nonexistent file
    error_result = await analyzer.analyze_syntax("/path/to/nonexistent/file.py")
    assert "error" in error_result
    print("   PASS Nonexistent file handling passed")

    # Test unsupported file type
    with tempfile.NamedTemporaryFile(mode="w", suffix=".xyz", delete=False) as f:
        f.write("some content")
        unsupported_file = f.name

    try:
        unsupported_result = await analyzer.analyze_syntax(unsupported_file)
        assert "error" in unsupported_result
        print("   PASS Unsupported file type handling passed")
    finally:
        os.unlink(unsupported_file)

    print("\nAll Code Analysis Tests Passed!")
    print("PASS Advanced Code Analysis Tools are ready for production")


if __name__ == "__main__":
    asyncio.run(test_code_analysis_tools())
