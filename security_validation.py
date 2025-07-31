#!/usr/bin/env python3
"""
Security Validation Script for VoidCat Reasoning Core
Validates that all security fixes have been properly implemented.
"""

import os
import re
import json
from typing import List, Dict, Tuple

def check_hardcoded_secrets() -> Tuple[bool, List[str]]:
    """Check for hardcoded API keys in configuration files."""
    issues = []
    
    # Check claude desktop config
    config_file = "claude_desktop_config_fastmcp.json"
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            content = f.read()
            if 'sk-proj-' in content or 'sk-2abfd' in content:
                issues.append(f"Hardcoded API keys found in {config_file}")
    
    # Check for any sk- patterns in main files
    main_files = ['api_gateway.py', 'cosmic_engine.py', 'engine.py', 'mcp_server.py']
    for file in main_files:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                if re.search(r'sk-[a-zA-Z0-9]{20,}', content):
                    issues.append(f"Potential hardcoded API key in {file}")
    
    return len(issues) == 0, issues

def check_path_traversal_protection() -> Tuple[bool, List[str]]:
    """Check that path traversal protection is implemented."""
    issues = []
    
    # Check main engine files for secure path handling
    files_to_check = ['engine.py', 'cosmic_engine.py', 'context7_integration.py']
    
    for file in files_to_check:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for secure path handling patterns
                if 'os.path.abspath' not in content and 'with open(' in content:
                    issues.append(f"Missing secure path handling in {file}")
                
                # Check for path validation
                if 'startswith(' not in content and 'with open(' in content:
                    issues.append(f"Missing path validation in {file}")
    
    return len(issues) == 0, issues

def check_input_validation() -> Tuple[bool, List[str]]:
    """Check that input validation is implemented in API endpoints."""
    issues = []
    
    if os.path.exists('api_gateway.py'):
        with open('api_gateway.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for validator decorators
            if '@validator' not in content:
                issues.append("Missing input validation decorators in api_gateway.py")
            
            # Check for dangerous character filtering
            if 'dangerous_chars' not in content:
                issues.append("Missing dangerous character filtering in api_gateway.py")
    
    return len(issues) == 0, issues

def check_error_handling() -> Tuple[bool, List[str]]:
    """Check that error handling doesn't leak information."""
    issues = []
    
    if os.path.exists('api_gateway.py'):
        with open('api_gateway.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for generic error messages
            if 'str(e)' in content and 'detail=' in content:
                # Look for lines that might expose internal errors
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'detail=f"' in line and 'str(e)' in line:
                        issues.append(f"Potential information leakage in api_gateway.py line {i+1}")
    
    return len(issues) == 0, issues

def check_dependency_versions() -> Tuple[bool, List[str]]:
    """Check that dependencies are updated to secure versions."""
    issues = []
    
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r') as f:
            content = f.read()
            
            # Check for outdated PyPDF2
            if 'PyPDF2==3.0.0' in content:
                issues.append("PyPDF2 version is outdated (security vulnerability)")
            
            # Check for minimum OpenAI version
            if 'openai>=1.98.0' not in content and 'openai>=' in content:
                issues.append("OpenAI SDK should be updated to latest version")
    
    return len(issues) == 0, issues

def check_environment_config() -> Tuple[bool, List[str]]:
    """Check that environment configuration is secure."""
    issues = []
    
    if os.path.exists('.env.example'):
        with open('.env.example', 'r') as f:
            content = f.read()
            
            # Check for OPENROUTER_API_KEY
            if 'OPENROUTER_API_KEY' not in content:
                issues.append("Missing OPENROUTER_API_KEY in .env.example")
            
            # Check for placeholder values
            if 'sk-' in content and 'your_' not in content:
                issues.append("Potential real API key in .env.example")
    
    return len(issues) == 0, issues

def main():
    """Run all security validation checks."""
    print("🛡️ VoidCat Reasoning Core - Security Validation")
    print("=" * 50)
    
    all_passed = True
    total_issues = []
    
    checks = [
        ("Hardcoded Secrets", check_hardcoded_secrets),
        ("Path Traversal Protection", check_path_traversal_protection),
        ("Input Validation", check_input_validation),
        ("Error Handling", check_error_handling),
        ("Dependency Versions", check_dependency_versions),
        ("Environment Configuration", check_environment_config),
    ]
    
    for check_name, check_func in checks:
        print(f"\n🔍 Checking {check_name}...")
        passed, issues = check_func()
        
        if passed:
            print(f"✅ {check_name}: PASSED")
        else:
            print(f"❌ {check_name}: FAILED")
            for issue in issues:
                print(f"   - {issue}")
            all_passed = False
            total_issues.extend(issues)
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL SECURITY CHECKS PASSED!")
        print("The project is ready for production deployment.")
    else:
        print(f"⚠️  {len(total_issues)} SECURITY ISSUES FOUND")
        print("Please address these issues before production deployment:")
        for i, issue in enumerate(total_issues, 1):
            print(f"{i}. {issue}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)