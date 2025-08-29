#!/usr/bin/env python3
"""
Script to fix common syntax errors in Python files
"""

import os
import re
import glob

def fix_file(file_path):
    """Fix common syntax errors in a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix 1: Unterminated string literals at start of file
        if content.startswith('"') and not content.startswith('"""'):
            # Find the end of the string
            lines = content.split('\n')
            if lines[0].startswith('"'):
                # Replace with proper docstring
                lines[0] = lines[0].replace('"', '"""', 1)
                # Find where the string ends
                for i, line in enumerate(lines[1:], 1):
                    if line.strip().endswith('"'):
                        lines[i] = line.replace('"', '"""', 1)
                        break
                content = '\n'.join(lines)
        
        # Fix 2: Fix Blueprint initialization
        content = re.sub(r'(\w+_bp = Blueprint)\s*$', r'\1("\1", __name__)', content, flags=re.MULTILINE)
        
        # Fix 3: Fix empty dictionary assignments
        content = re.sub(rf'(\w+) = \{\}\s*$', r'\1 = {', content, flags=re.MULTILINE)
        
        # Fix 4: Fix function definitions with missing parentheses
        content = re.sub(r'def (\w+)\(:', r'def \1():', content)
        
        # Fix 5: Fix docstrings
        content = re.sub(r'^\s*"([^"]*)"\s*$', r'    """\1"""', content, flags=re.MULTILINE)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Main function to fix syntax errors"""
    # Get all Python files in the app directory
    python_files = glob.glob('app/**/*.py', recursive=True)
    
    fixed_count = 0
    total_files = len(python_files)
    
    print(f"Found {total_files} Python files to check...")
    
    for file_path in python_files:
        if fix_file(file_path):
            fixed_count += 1
            print(f"✅ Fixed: {file_path}")
    
    print(f"\nFixed {fixed_count} out of {total_files} files")

if __name__ == "__main__":
    main()
