#!/usr/bin/env python3
"""
Codey Jr's Codebase Cleanup - Phase 3: Code Deduplication
"""

import os
import shutil
from pathlib import Path

# Base directory
BASE_DIR = Path("d:/03_Development/Active_Projects/voidcat-reasoning-core")
ARCHIVE_DIR = BASE_DIR / "CLEANUP_ARCHIVE_2025"

# Core code files to keep
KEEP_CODE = {
    # Main engine files
    "enhanced_engine.py",            # Main engine
    "engine.py",                     # Keep as backup/simple version
    
    # MCP server (keep main one)
    "mcp_server.py",                 # Main MCP server
    
    # Core VoidCat modules
    "voidcat_task_models.py",
    "voidcat_persistence.py", 
    "voidcat_operations.py",
    "voidcat_memory_models.py",
    "voidcat_memory_storage.py",
    "voidcat_memory_integration.py",
    "voidcat_memory_retrieval.py",
    "voidcat_memory_search.py",
    "voidcat_context_integration.py",
    
    # API and utilities
    "api_gateway.py",
    "main.py",
    "voidcat_launcher.py",
    "launch_voidcat.bat",
    "launch_voidcat.sh",
    
    # Processing modules
    "hybrid_vectorizer.py",
    "multi_format_processor.py",
    "sequential_thinking.py",
    "context7_integration.py",
    
    # Configuration
    "conftest.py",
    "pyproject.toml",
    "requirements.txt",
    "setup.py",
    "pytest.ini",
}

# Code files to archive (duplicates/debug versions)
ARCHIVE_CODE = {
    # MCP server variations (keep main mcp_server.py)
    "mcp_server_clean.py",
    "mcp_server_simplified.py", 
    "mcp_server_simplified_fixed.py",
    "mcp_server_windows.py",
    "mcp_server_windows_integration.py",
    
    # MCP launcher variations
    "launch_clean_mcp.py",
    "launch_mcp_server.bat",
    "launch_mcp_server.py", 
    "launch_ultimate_mcp.py",
    
    # Debug/analysis scripts
    "analyze_performance.py",
    "benchmark_lightweight.py",
    "benchmark_voidcat.py",
    "check_environment.py",
    "debug_api_gateway.py",
    "debug_claude_env.py",
    "performance_analysis_report.py",
    
    # Demo/example files
    "demo_enhanced_memory.py",
    "diagnostics_widget.py",
    
    # Debug/fix scripts
    "fastmcp_debug.py",
    "fastmcp_debug_fixed.py", 
    "fastmcp_debug_simple.py",
    "fix_file.py",
    "quick_mcp_test.py",
    "quick_test.py",
    "quote_check.py",
    "syntax_check.py",
    "syntax_check_simple.py",
    
    # Security audit (keep one, archive duplicates)
    "security_audit_new.py",  # Keep security_audit.py
    
    # Docstring/validation scripts
    "docstring_check.py",
    
    # Deployment scripts (keep main launcher)
    "deploy_enhanced.py",
    
    # My cleanup scripts (archive after use)
    "cleanup_phase1.py",
    "cleanup_phase2.py",
    # "cleanup_phase3.py",  # Don't archive myself yet!
}

# Config files to archive (duplicates)
ARCHIVE_CONFIG = {
    # Claude Desktop configs (multiple versions)
    "claude_desktop_config_docker.json",
    "claude_desktop_config_ultimate_backup.json",
    "blackbox_mcp_settings_updated.json",
    
    # MCP configs
    "mcp.json",
    "mcp-toolkit-config.yml",
    "schema.json",
    "sequential-thinking.jsonld",
    
    # Package configs
    "package.json",  # Seems to be leftover from Node.js
    
    # Deployment configs
    "DEPLOYMENT_INFO.json",
    
    # Text files
    "cache_fix.txt",
    "https_enforcement.txt", 
    "rate_limiting.txt",
    "Albedo Supermemory.txt",
    
    # Markdown files
    "chart_demo.md",
    "chatlog.md",  # Huge file, archive it
    "project-export.md",  # Another huge file
}

def move_to_archive(filename, subdir="code_files"):
    """Move a file to the archive directory."""
    source = BASE_DIR / filename
    if source.exists():
        # Create subdirectory in archive
        archive_subdir = ARCHIVE_DIR / subdir
        archive_subdir.mkdir(exist_ok=True)
        
        destination = archive_subdir / filename
        try:
            shutil.move(str(source), str(destination))
            print(f"✅ Archived: {filename}")
            return True
        except Exception as e:
            print(f"❌ Failed to archive {filename}: {e}")
            return False
    else:
        print(f"⚠️ File not found: {filename}")
        return False

def main():
    print("🧹 Codey Jr's Code Deduplication - Phase 3")
    print("=" * 50)
    
    # Create archive directory
    ARCHIVE_DIR.mkdir(exist_ok=True)
    
    archived_count = 0
    
    # Archive duplicate code files
    print("\n🐍 Archiving duplicate/debug Python files...")
    for code_file in sorted(ARCHIVE_CODE):
        if move_to_archive(code_file, "code_files"):
            archived_count += 1
    
    # Archive config files
    print("\n⚙️ Archiving duplicate config files...")
    for config_file in sorted(ARCHIVE_CONFIG):
        if move_to_archive(config_file, "config_files"):
            archived_count += 1
    
    print(f"\n📊 Summary:")
    print(f"✅ Archived: {archived_count} files")
    print(f"🎯 Core code files kept: {len(KEEP_CODE)}")
    
    # List some key files we kept
    print(f"\n🎯 Key files kept:")
    key_files = [
        "mcp_server.py",
        "enhanced_engine.py", 
        "api_gateway.py",
        "voidcat_task_models.py",
        "voidcat_persistence.py",
        "main.py"
    ]
    
    for key_file in key_files:
        if (BASE_DIR / key_file).exists():
            print(f"  ✅ {key_file}")
        else:
            print(f"  ⚠️ {key_file} (not found)")
    
    print(f"\n🎉 Phase 3 cleanup complete!")
    print(f"Next: Test that core functionality still works")

if __name__ == "__main__":
    main()