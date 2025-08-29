#!/usr/bin/env python3
"""
Fix the common docstring issue with extra quotes causing unterminated string literals
"""

import os
import re
import subprocess
from pathlib import Path


def fix_docstring_quotes(filepath):
    """Fix the 4-quote docstring issue in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Fix pattern: """" -> """
        content = re.sub(r'""""', '"""', content)
        
        # Fix pattern where there might be text between quotes
        # Replace """<text>"""" with """<text>"""
        content = re.sub(r'"""([^"]+)""""', r'"""\1"""', content)
        
        # Fix cases where docstring appears after class/function definition
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Check if this line has the """Authentication and authorization manager.""" pattern
            if line.strip() == '"""Authentication and authorization manager."""':
                # This should be removed as it's likely a duplicate
                continue
            fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False


def main():
    """Main execution"""
    print("🔍 Finding all Python files with docstring issues...")
    
    fixed_count = 0
    
    # Get all Python files
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        if any(skip in root for skip in ['venv', '.venv', 'smartcloudops-ai', 'syntax_backup']):
            continue
            
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                
                # Check if file has syntax error
                result = subprocess.run(['python3', '-m', 'py_compile', filepath],
                                      capture_output=True, text=True)
                
                if result.returncode != 0 and 'unterminated string literal' in result.stderr:
                    print(f"🔧 Fixing docstrings in: {filepath}")
                    
                    if fix_docstring_quotes(filepath):
                        # Verify the fix
                        result = subprocess.run(['python3', '-m', 'py_compile', filepath],
                                              capture_output=True, text=True)
                        if result.returncode == 0:
                            print(f"  ✅ Fixed!")
                            fixed_count += 1
                        else:
                            print(f"  ⚠️  Still has errors")
    
    print(f"\n📊 Fixed {fixed_count} files with docstring issues")


if __name__ == "__main__":
    main()