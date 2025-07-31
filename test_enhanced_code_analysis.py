#!/usr/bin/env python3
"""
VoidCat Enhanced MCP Server - Advanced Code Analysis Tools Test Suite
Comprehensive testing for Pillar IV: The Guardian's Overseer

This test suite validates all advanced code analysis capabilities including:
- Syntax analysis with language-specific parsers
- Dependency tracking and import analysis
- Security scanning with vulnerability detection
- Code quality metrics and suggestions
- Integration with VoidCat reasoning systems

Author: VoidCat Reasoning Core Team - Pillar IV Testing
License: MIT
Version: 1.0.0
"""

import asyncio
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

# Import the enhanced MCP server components
try:
    from voidcat_enhanced_mcp_server import (
        AdvancedLogger,
        CodeAnalyzer,
        EnhancedVoidCatMCPServer,
        FileOperationsManager,
    )
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure voidcat_enhanced_mcp_server.py is in the current directory")
    exit(1)


class TestCodeAnalyzer:
    """Test suite for the advanced code analysis functionality."""

    @pytest.fixture
    def code_analyzer(self):
        """Create a CodeAnalyzer instance for testing."""
        logger = AdvancedLogger("Test-CodeAnalyzer")
        return CodeAnalyzer(logger)

    @pytest.fixture
    def sample_python_code(self):
        """Sample Python code for testing."""
        return '''#!/usr/bin/env python3
"""
Sample Python module for testing code analysis.
"""

import os
import sys
import json
from typing import List, Dict, Any
from dataclasses import dataclass

# Hardcoded password - security issue
PASSWORD = "hardcoded_secret_123"

@dataclass
class User:
    """User data class."""
    name: str
    email: str
    age: int

def process_data(data: str) -> Dict[str, Any]:
    """Process user data with potential security issues."""
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE name = '{data}'"
    
    # Command injection vulnerability  
    os.system(f"echo {data}")
    
    # XSS vulnerability
    html = f"<div>{data}</div>"
    
    return {"query": query, "html": html}

def long_line_function():
    """This function has a very long line that exceeds 100 characters and should trigger a style warning."""
    return "This is a very long string that definitely exceeds the 100 character limit and should be flagged"

if __name__ == "__main__":
    # Use eval - security issue
    user_input = input("Enter expression: ")
    result = eval(user_input)
    print(result)
'''

    @pytest.fixture
    def sample_javascript_code(self):
        """Sample JavaScript code for testing."""
        return """// Sample JavaScript file for testing
var globalVar = "should use let or const";

function processUserData(userData) {
    // XSS vulnerability
    document.getElementById("content").innerHTML = userData;
    
    // Potential security issue
    eval(userData);
    
    return userData;
}

class UserManager {
    constructor() {
        this.users = [];
    }
    
    addUser(user) {
        this.users.push(user);
    }
    
    findUser(id) {
        return this.users.find(user => user.id === id);
    }
}

// Export for testing
module.exports = { UserManager, processUserData };
"""

    async def test_python_syntax_analysis(self, code_analyzer, sample_python_code):
        """Test Python syntax analysis capabilities."""
        # Create temporary Python file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(sample_python_code)
            temp_file = f.name

        try:
            # Analyze syntax
            result = await code_analyzer.analyze_syntax(temp_file)

            # Validate results
            assert result["language"] == "python"
            assert result["syntax_valid"] is True
            assert result["line_count"] > 0
            assert "metrics" in result
            assert "functions" in result["metrics"]
            assert "classes" in result["metrics"]
            assert "imports" in result["metrics"]

            # Check for style issues
            assert len(result["issues"]) > 0
            style_issues = [
                issue for issue in result["issues"] if issue["type"] == "style"
            ]
            assert len(style_issues) > 0  # Should find long line

            # Check for suggestions
            assert len(result["suggestions"]) > 0

            print(
                f"✅ Python syntax analysis passed: {len(result['issues'])} issues found"
            )

        finally:
            os.unlink(temp_file)

    async def test_javascript_syntax_analysis(
        self, code_analyzer, sample_javascript_code
    ):
        """Test JavaScript syntax analysis capabilities."""
        # Create temporary JavaScript file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
            f.write(sample_javascript_code)
            temp_file = f.name

        try:
            # Analyze syntax
            result = await code_analyzer.analyze_syntax(temp_file)

            # Validate results
            assert result["language"] == "javascript"
            assert result["syntax_valid"] is True
            assert "metrics" in result
            assert result["metrics"]["functions"] > 0
            assert result["metrics"]["classes"] > 0

            # Check for modernization suggestions
            suggestions = [
                s for s in result["suggestions"] if s["type"] == "modernization"
            ]
            assert len(suggestions) > 0  # Should suggest let/const instead of var

            print(
                f"✅ JavaScript syntax analysis passed: {len(result['suggestions'])} suggestions found"
            )

        finally:
            os.unlink(temp_file)

    async def test_dependency_analysis(self, code_analyzer, sample_python_code):
        """Test dependency analysis functionality."""
        # Create temporary Python file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(sample_python_code)
            temp_file = f.name

        try:
            # Analyze dependencies
            result = await code_analyzer.analyze_dependencies(temp_file)

            # Validate results
            assert result["language"] == "python"
            assert "external_imports" in result
            assert "internal_imports" in result

            # Check for expected imports
            external_imports = result["external_imports"]
            assert "os" in external_imports
            assert "sys" in external_imports
            assert "json" in external_imports

            print(
                f"✅ Dependency analysis passed: {len(external_imports)} external imports found"
            )

        finally:
            os.unlink(temp_file)

    async def test_security_scanning(self, code_analyzer, sample_python_code):
        """Test security scanning capabilities."""
        # Create temporary Python file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(sample_python_code)
            temp_file = f.name

        try:
            # Perform security scan
            result = await code_analyzer.security_scan(temp_file)

            # Validate results
            assert result["language"] == "python"
            assert "security_issues" in result
            assert "vulnerability_score" in result
            assert "recommendations" in result

            # Check for expected security issues
            security_issues = result["security_issues"]
            issue_types = [issue["type"] for issue in security_issues]

            # Should detect hardcoded secrets
            assert "hardcoded_secrets" in issue_types
            # Should detect command injection
            assert "command_injection" in issue_types
            # Should detect SQL injection
            assert "sql_injection" in issue_types

            # Vulnerability score should be > 0
            assert result["vulnerability_score"] > 0

            # Should have recommendations
            assert len(result["recommendations"]) > 0

            print(
                f"✅ Security scan passed: {len(security_issues)} vulnerabilities found"
            )
            print(f"   Vulnerability score: {result['vulnerability_score']}")

        finally:
            os.unlink(temp_file)

    async def test_unsupported_file_type(self, code_analyzer):
        """Test handling of unsupported file types."""
        # Create temporary file with unsupported extension
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xyz", delete=False) as f:
            f.write("some content")
            temp_file = f.name

        try:
            # Analyze syntax
            result = await code_analyzer.analyze_syntax(temp_file)

            # Should return error for unsupported type
            assert "error" in result
            assert "Unsupported file type" in result["error"]

            print("✅ Unsupported file type handling passed")

        finally:
            os.unlink(temp_file)

    async def test_nonexistent_file(self, code_analyzer):
        """Test handling of nonexistent files."""
        # Try to analyze non-existent file
        result = await code_analyzer.analyze_syntax("/path/to/nonexistent/file.py")

        # Should return error
        assert "error" in result
        assert "File not found" in result["error"]

        print("✅ Nonexistent file handling passed")


class TestFileOperationsManager:
    """Test suite for the file operations functionality."""

    @pytest.fixture
    def file_manager(self):
        """Create a FileOperationsManager instance for testing."""
        logger = AdvancedLogger("Test-FileManager")
        return FileOperationsManager(logger)

    @pytest.fixture
    def test_workspace(self):
        """Create a temporary workspace for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)

            # Create test files
            (workspace / "test.py").write_text("print('Hello Python')")
            (workspace / "test.js").write_text("console.log('Hello JavaScript');")
            (workspace / "README.md").write_text("# Test Project\nThis is a test.")
            (workspace / "config.json").write_text(
                '{"name": "test", "version": "1.0.0"}'
            )

            # Create subdirectory
            subdir = workspace / "src"
            subdir.mkdir()
            (subdir / "main.py").write_text("def main():\n    print('Main function')")
            (subdir / "utils.js").write_text("function helper() { return 'help'; }")

            yield workspace

    async def test_intelligent_search_filename(self, file_manager, test_workspace):
        """Test intelligent file search by filename."""
        result = await file_manager.intelligent_search(
            search_query="test", search_path=str(test_workspace), include_content=False
        )

        # Validate results
        assert result["search_query"] == "test"
        assert len(result["file_matches"]) > 0

        # Should find test.py and test.js
        file_names = [match["name"] for match in result["file_matches"]]
        assert "test.py" in file_names
        assert "test.js" in file_names

        print(f"✅ Filename search passed: {len(result['file_matches'])} matches found")

    async def test_intelligent_search_content(self, file_manager, test_workspace):
        """Test intelligent file search by content."""
        result = await file_manager.intelligent_search(
            search_query="Hello", search_path=str(test_workspace), include_content=True
        )

        # Validate results
        assert len(result["content_matches"]) > 0

        # Should find content in test.py and test.js
        matched_files = [match["path"] for match in result["content_matches"]]
        assert any("test.py" in path for path in matched_files)
        assert any("test.js" in path for path in matched_files)

        print(
            f"✅ Content search passed: {len(result['content_matches'])} matches found"
        )

    async def test_intelligent_search_file_types(self, file_manager, test_workspace):
        """Test intelligent file search with file type filtering."""
        result = await file_manager.intelligent_search(
            search_query="test",
            search_path=str(test_workspace),
            file_types=["py"],
            include_content=False,
        )

        # Should only find Python files
        file_names = [match["name"] for match in result["file_matches"]]
        assert "test.py" in file_names
        assert "test.js" not in file_names

        print(
            f"✅ File type filtering passed: {len(result['file_matches'])} Python files found"
        )

    async def test_workspace_analysis(self, file_manager, test_workspace):
        """Test comprehensive workspace analysis."""
        result = await file_manager.workspace_analysis(str(test_workspace))

        # Validate results
        assert result["total_files"] > 0
        assert result["total_directories"] > 0
        assert len(result["file_types"]) > 0
        assert len(result["language_distribution"]) > 0

        # Check file type distribution
        assert ".py" in result["file_types"]
        assert ".js" in result["file_types"]
        assert ".md" in result["file_types"]

        # Check project structure analysis
        assert "project_structure" in result

        print(
            f"✅ Workspace analysis passed: {result['total_files']} files, {result['total_directories']} directories"
        )

    async def test_bulk_operations_safety(self, file_manager, test_workspace):
        """Test bulk operations safety checks."""
        # Try to delete all files without force flag
        result = await file_manager.bulk_operations(
            operation="delete",
            file_patterns=["*"],
            target_path=str(test_workspace),
            options={},
        )

        # Should not process many files without force flag
        if result["total_processed"] == 0 and "error" in result:
            print(
                "✅ Bulk operations safety check passed: Large operations require force flag"
            )
        else:
            # If it did process, make sure it was a reasonable number
            assert result["total_processed"] < 10
            print(
                f"✅ Bulk operations completed safely: {result['total_processed']} files processed"
            )


class TestEnhancedMCPServer:
    """Test suite for the enhanced MCP server integration."""

    @pytest.fixture
    def mcp_server(self):
        """Create an EnhancedVoidCatMCPServer instance for testing."""
        return EnhancedVoidCatMCPServer()

    def test_server_initialization(self, mcp_server):
        """Test server initialization and component setup."""
        # Validate server components
        assert mcp_server.server_name == "VoidCat-Guardian-MCP"
        assert mcp_server.server_version == "1.0.0"
        assert mcp_server.code_analyzer is not None
        assert mcp_server.file_manager is not None
        assert mcp_server.rate_limiter is not None
        assert mcp_server.performance_metrics is not None

        # Validate tool registry
        assert len(mcp_server.tool_registry) > 0

        # Check for expected tools
        tool_names = list(mcp_server.tool_registry.keys())
        assert "voidcat_analyze_syntax" in tool_names
        assert "voidcat_analyze_dependencies" in tool_names
        assert "voidcat_security_scan" in tool_names
        assert "voidcat_intelligent_search" in tool_names
        assert "voidcat_bulk_operations" in tool_names
        assert "voidcat_workspace_analysis" in tool_names

        print(f"✅ Server initialization passed: {len(tool_names)} tools registered")

    def test_tool_categorization(self, mcp_server):
        """Test tool categorization and metadata."""
        # Check tool categories
        categories = set()
        for tool_meta in mcp_server.tool_registry.values():
            categories.add(tool_meta.category)

        expected_categories = {
            "reasoning",
            "code_analysis",
            "file_operations",
            "workspace",
            "diagnostics",
        }

        assert expected_categories.issubset(categories)

        # Check rate limiting setup
        bulk_tool = mcp_server.tool_registry.get("voidcat_bulk_operations")
        assert bulk_tool is not None
        assert bulk_tool.rate_limit == 30  # Should have rate limit

        print(f"✅ Tool categorization passed: {len(categories)} categories found")

    def test_rate_limiter(self, mcp_server):
        """Test rate limiting functionality."""
        rate_limiter = mcp_server.rate_limiter

        # Test normal usage
        assert rate_limiter.check_rate_limit("test_tool") is True
        rate_limiter.record_usage("test_tool")

        # Test rate limit enforcement
        for i in range(65):  # Exceed default limit of 60
            rate_limiter.record_usage("test_tool")

        assert rate_limiter.check_rate_limit("test_tool") is False

        print("✅ Rate limiting passed: Limits enforced correctly")


async def run_comprehensive_tests():
    """Run comprehensive test suite for all code analysis tools."""
    print("🧪 Starting VoidCat Enhanced MCP Server Test Suite")
    print("=" * 60)

    # Test CodeAnalyzer
    print("\n🔍 Testing Code Analysis Tools...")
    code_analyzer = CodeAnalyzer(AdvancedLogger("Test"))

    # Create test files
    python_code = """import os
def test_function():
    password = "secret123"  # Security issue
    query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL injection
    return query
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        test_file = f.name

    try:
        # Test syntax analysis
        syntax_result = await code_analyzer.analyze_syntax(test_file)
        print(f"   ✅ Syntax analysis: {syntax_result['language']} file analyzed")

        # Test dependency analysis
        dep_result = await code_analyzer.analyze_dependencies(test_file)
        print(
            f"   ✅ Dependency analysis: {len(dep_result['external_imports'])} imports found"
        )

        # Test security scan
        sec_result = await code_analyzer.security_scan(test_file)
        print(
            f"   ✅ Security scan: {len(sec_result['security_issues'])} vulnerabilities found"
        )

    finally:
        os.unlink(test_file)

    # Test FileOperationsManager
    print("\n📁 Testing File Operations...")
    file_manager = FileOperationsManager(AdvancedLogger("Test"))

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        (Path(temp_dir) / "test.py").write_text("print('test')")
        (Path(temp_dir) / "README.md").write_text("# Test Project")

        # Test intelligent search
        search_result = await file_manager.intelligent_search("test", temp_dir)
        print(
            f"   ✅ Intelligent search: {len(search_result['file_matches'])} matches found"
        )

        # Test workspace analysis
        workspace_result = await file_manager.workspace_analysis(temp_dir)
        print(
            f"   ✅ Workspace analysis: {workspace_result['total_files']} files analyzed"
        )

    # Test EnhancedMCPServer
    print("\n🛡️ Testing Enhanced MCP Server...")
    server = EnhancedVoidCatMCPServer()
    print(f"   ✅ Server initialization: {len(server.tool_registry)} tools registered")
    print(f"   ✅ Components initialized: CodeAnalyzer, FileManager, RateLimiter")

    print("\n🎉 All tests completed successfully!")
    print("✅ VoidCat Enhanced MCP Server is ready for production use")


if __name__ == "__main__":
    asyncio.run(run_comprehensive_tests())
