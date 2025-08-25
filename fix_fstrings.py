#!/usr/bin/env python3
"""
Quick script to fix malformed f-strings across the codebase
Fixes patterns like: "string""f" -> "string"
"""

import os
import re
from pathlib import Path

def fix_fstring_pattern(content):
    """Fix malformed f-string patterns."""
    # Pattern 1: "text""f" -> "text"
    content = re.sub(r'"""([^"]+)""f"', r'"""\1"""', content)
    content = re.sub(r'"([^"]+)"f"', r'"\1"', content)
    
    # Pattern 2: Various corrupted f-strings
    content = re.sub(r'"([^"]+)f"', r'"\1"', content)
    
    return content

def process_file(file_path):
    """Process a single Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        fixed_content = fix_fstring_pattern(original_content)
        
        if fixed_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"✅ Fixed f-strings in {file_path}")
            return True
        return False
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Fix f-strings in all Python files in the app directory."""
    app_dir = Path("app")
    fixed_count = 0
    
    for py_file in app_dir.rglob("*.py"):
        if process_file(py_file):
            fixed_count += 1
    
    print(f"\n📊 Fixed f-strings in {fixed_count} files")

if __name__ == "__main__":
    main()
