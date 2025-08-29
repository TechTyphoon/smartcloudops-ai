#!/usr/bin/env python3
"""
Comprehensive Fix Script for Remaining Python Syntax Errors
"""
import os
import re
from pathlib import Path
from typing import List, Tuple

def fix_file(file_path: Path) -> bool:
    """Fix common syntax issues in a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix pattern 1: Docstring placement after imports
        # Match pattern: from/import lines followed by indented docstring
        pattern1 = r'^(from .+|import .+)\n\s+"""'
        if re.search(pattern1, content, re.MULTILINE):
            # Move docstring to top after shebang
            lines = content.split('\n')
            new_lines = []
            docstring_lines = []
            in_docstring = False
            docstring_found = False
            
            for i, line in enumerate(lines):
                if i == 0 and line.startswith('#!/usr/bin/env'):
                    new_lines.append(line)
                    continue
                    
                # Detect indented docstring
                if re.match(r'^\s+"""', line) and not docstring_found:
                    in_docstring = True
                    docstring_found = True
                    docstring_lines.append(line.lstrip())
                    continue
                elif in_docstring:
                    docstring_lines.append(line.lstrip())
                    if '"""' in line:
                        in_docstring = False
                    continue
                else:
                    new_lines.append(line)
            
            # Insert docstring after shebang if found
            if docstring_lines:
                if new_lines[0].startswith('#!/usr/bin/env'):
                    new_lines = [new_lines[0]] + docstring_lines + new_lines[1:]
                else:
                    new_lines = docstring_lines + new_lines
                    
            content = '\n'.join(new_lines)
        
        # Fix pattern 2: Malformed docstrings with extra quotes
        content = re.sub(r'""""\n', '"""\n', content)
        content = re.sub(r'\n""""', '\n"""', content)
        
        # Fix pattern 3: Unmatched parentheses in function calls
        # Fix dict/list creation with wrong syntax
        content = re.sub(r'(\w+)\s*=\s*(\w+)\(\)\n\s+', r'\1 = \2(\n    ', content)
        content = re.sub(r'(return\s+\w+)\(\)\n\s+\{', r'\1({\n    ', content)
        
        # Fix pattern 4: Missing f in f-strings
        lines = content.split('\n')
        for i, line in enumerate(lines):
            # Check for strings with curly braces that look like f-strings
            if re.search(r'["\'][^"\f']*\{[^}]+\}[^"\']*["\']', line):
                # Check if it's not already an f-string
                if not re.search(r'f["\']', line):
                    # Add f prefix to strings with interpolation
                    lines[i] = re.sub(r'([^f])(["\'][^"\f']*\{[^}]+\}[^"\']*["\'])', r'\1f\2', line)
        content = '\n'.join(lines)
        
        # Fix pattern 5: logger = logging.getLogger without __name__
        content = re.sub(r'logger\s*=\s*logging\.getLogger\s*$', 
                        r'logger = logging.getLogger(__name__)', 
                        content, flags=re.MULTILINE)
        
        # Fix pattern 6: Missing commas in dict/list literals
        # Fix: },\n            {}\n  to },\n            {\n
        content = re.sub(rf'},\n(\s+)\{\}\n', r'},\n\1{\n', content)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main fix function."""
    workspace_dir = Path('/workspace')
    
    print("🔧 Running Comprehensive Fix Script...")
    print("=" * 60)
    
    fixed_files = []
    
    # Process all Python files
    for py_file in workspace_dir.rglob('*.py'):
        # Skip virtual environments and cache
        if any(excluded in str(py_file) for excluded in ['venv', '__pycache__', '.git', 'node_modules']):
            continue
            
        if fix_file(py_file):
            fixed_files.append(py_file)
    
    print(f"\n✅ Fixed {len(fixed_files)} files:")
    for file in fixed_files[:20]:  # Show first 20
        print(f"   - {file.relative_to(workspace_dir)}")
    
    if len(fixed_files) > 20:
        print(f"   ... and {len(fixed_files) - 20} more files")
    
    print("\n" + "=" * 60)
    print("Fix script completed!")

if __name__ == "__main__":
    main()