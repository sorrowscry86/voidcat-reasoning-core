# -*- coding: utf-8 -*-
"""
Security Audit Script for VoidCat Reasoning Core

This script performs basic security checks on Python files to identify
potential security vulnerabilities and insecure coding practices.
"""

import os
import re


def check_file_for_issues(file_path):
    """Check a Python file for potential security issues."""
    issues = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return [f"Could not read file: {str(e)}"]

    # Check for hardcoded secrets
    secret_patterns = [
        r'api_key\s*=\s*["\'][^"\']*["\']',
        r'password\s*=\s*["\'][^"\']*["\']',
        r'secret\s*=\s*["\'][^"\']*["\']',
        r'token\s*=\s*["\'][^"\']*["\']',
    ]

    for pattern in secret_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            if "os.getenv" not in match.group(0) and "environment" not in match.group(
                0
            ):
                issues.append(f"Potential hardcoded secret: {match.group(0)}")

    # Check for path traversal vulnerabilities
    if "open(" in content and ".." in content:
        issues.append(
            "Potential path traversal vulnerability with open() and relative paths"
        )

    # Check for pickle usage (insecure deserialization)
    if "pickle.load" in content:
        issues.append("Insecure deserialization using pickle.load()")

    # Check for command injection
    if "os.system(" in content or "subprocess.call(" in content:
        issues.append(
            "Potential command injection vulnerability with os.system() or subprocess.call()"
        )

    # Check for SQL injection
    if "execute(" in content and "%s" in content:
        issues.append(
            "Potential SQL injection vulnerability with execute() and string formatting"
        )

    # Check for CORS misconfiguration
    if "CORSMiddleware" in content and 'allow_origins=["*"]' in content:
        issues.append('Insecure CORS configuration with allow_origins=["*"]')

    # Check for missing input validation
    if "request." in content and not re.search(
        r"validate|sanitize|clean", content, re.IGNORECASE
    ):
        issues.append("Potential missing input validation for request data")

    return issues


def main():
    """Main function to run security audit."""
    base_dir = "d:/03_Development/Active_Projects/voidcat-reasoning-core"
    python_files = []

    for root, dirs, files in os.walk(base_dir):
        # Skip virtual environment directories
        if ".venv" in root:
            continue

        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    all_issues = {}
    for file_path in python_files:
        issues = check_file_for_issues(file_path)
        if issues:
            all_issues[file_path] = issues

    if all_issues:
        print("Security issues found:")
        for file_path, issues in all_issues.items():
            print(f"\nFile: {file_path}")
            for issue in issues:
                print(f"  - {issue}")
    else:
        print("No security issues found.")


if __name__ == "__main__":
    main()
