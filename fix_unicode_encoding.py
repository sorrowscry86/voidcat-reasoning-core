#!/usr/bin/env python3
"""
Codey Jr's Unicode Encoding Fix - Apply UTF-8 encoding to all file operations
"""

import os
import re
from pathlib import Path

# Base directory
BASE_DIR = Path("d:/03_Development/Active_Projects/voidcat-reasoning-core")

def fix_file_operations(file_path):
    """Fix file operations in a Python file to use UTF-8 encoding."""
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = 0
        
        # Pattern 1: with open(file, "w", encoding="utf-8") -> with open(file, "w", encoding="utf-8")
        pattern1 = r'with open\(([^,]+),\s*["\']w["\']\)'
        replacement1 = r'with open(\1, "w", encoding="utf-8")'
        content, count1 = re.subn(pattern1, replacement1, content)
        changes_made += count1
        
        # Pattern 2: with open(file, "w", encoding="utf-8") -> with open(file, 'w', encoding='utf-8')
        pattern2 = r"with open\(([^,]+),\s*['\"]w['\"]\)"
        replacement2 = r"with open(\1, 'w', encoding='utf-8')"
        content, count2 = re.subn(pattern2, replacement2, content)
        changes_made += count2
        
        # Pattern 3: open(file, "w", encoding="utf-8") -> open(file, "w", encoding="utf-8")
        pattern3 = r'(?<!with\s)open\(([^,]+),\s*["\']w["\']\)'
        replacement3 = r'open(\1, "w", encoding="utf-8")'
        content, count3 = re.subn(pattern3, replacement3, content)
        changes_made += count3
        
        # Pattern 4: Path.write_text(content, encoding="utf-8") -> Path.write_text(content, encoding='utf-8')
        pattern4 = r'\.write_text\(([^,)]+)\)'
        replacement4 = r'.write_text(\1, encoding="utf-8")'
        content, count4 = re.subn(pattern4, replacement4, content)
        changes_made += count4
        
        # Only write back if changes were made
        if changes_made > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed {changes_made} file operations in: {file_path.name}")
            return changes_made
        else:
            return 0
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return 0

def main():
    print("🔧 Codey Jr's Unicode Encoding Fix")
    print("=" * 50)
    
    # Find all Python files
    python_files = list(BASE_DIR.glob("*.py"))
    
    total_changes = 0
    files_modified = 0
    
    print(f"\n🔍 Scanning {len(python_files)} Python files...")
    
    for py_file in python_files:
        changes = fix_file_operations(py_file)
        if changes > 0:
            total_changes += changes
            files_modified += 1
    
    print(f"\n📊 Summary:")
    print(f"✅ Files modified: {files_modified}")
    print(f"✅ Total fixes applied: {total_changes}")
    
    if total_changes > 0:
        print(f"\n🎉 Unicode encoding fixes applied!")
        print(f"All file operations should now use UTF-8 encoding properly.")
    else:
        print(f"\n✨ No fixes needed - all file operations already use proper encoding!")

if __name__ == "__main__":
    main()