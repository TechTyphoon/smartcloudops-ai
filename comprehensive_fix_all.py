#!/usr/bin/env python3
"""
Comprehensive syntax fixer for all 80 Python files with errors.
This script applies targeted fixes based on the specific patterns observed.
"""

import os
import re
import subprocess
from pathlib import Path
from datetime import datetime


def get_all_error_files():
    """Get list of all files with syntax errors"""
    files = []
    
    # Run a check to find all files with syntax errors
    for root, dirs, filenames in os.walk('.'):
        # Skip certain directories
        if any(skip in root for skip in ['venv', '.venv', 'smartcloudops-ai', 'syntax_backup']):
            continue
            
        for filename in filenames:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                result = subprocess.run(['python3', '-m', 'py_compile', filepath],
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    files.append(filepath)
                    
    return files


def fix_file_content(content, filepath):
    """Apply comprehensive fixes to file content"""
    
    # Fix 1: Move docstrings before imports
    lines = content.split('\n')
    
    # Find docstrings that appear after imports
    docstring_lines = []
    import_start = -1
    
    for i, line in enumerate(lines):
        if line.strip().startswith(('from ', 'import ')):
            if import_start == -1:
                import_start = i
        elif '"""' in line and i < 20:  # Look for docstrings in first 20 lines
            # Check if this is after an import
            if import_start >= 0 and i > import_start:
                # Find the complete docstring
                start = i
                end = i
                if line.count('"""') == 1:
                    # Multi-line docstring
                    for j in range(i + 1, len(lines)):
                        if '"""' in lines[j]:
                            end = j
                            break
                # Extract and remove docstring
                docstring_lines = lines[start:end + 1]
                for k in range(end, start - 1, -1):
                    lines.pop(k)
                break
    
    # Re-insert docstring at the beginning (after shebang if present)
    if docstring_lines:
        insert_pos = 1 if lines[0].startswith('#!') else 0
        for doc_line in reversed(docstring_lines):
            lines.insert(insert_pos, doc_line.lstrip())
    
    content = '\n'.join(lines)
    
    # Fix 2: Fix indented module docstrings
    content = re.sub(r'^    """', '"""', content, flags=re.MULTILINE)
    
    # Fix 3: Fix malformed object instantiations (Class() followed by arguments)
    content = re.sub(r'(\w+)\(\)\s*\n\s+(\w+=)', r'\1(\n    \2', content)
    
    # Fix 4: Fix malformed function calls (func() followed by arguments)
    content = re.sub(r'(\.\w+)\(\)\s*\n\s+(\w+=)', r'\1(\n    \2', content)
    
    # Fix 5: Fix malformed return statements
    content = re.sub(r'return\s+\(\)\s*\n\s+jsonify\(\)\s*\n\s+\{\}', 
                    'return jsonify({', content)
    content = re.sub(r'return\s+\(\)\s*\n\s+jsonify\(\)', 
                    'return jsonify(', content)
    
    # Fix 6: Fix unterminated strings
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Count quotes
        double_quotes = line.count('"')
        single_quotes = line.count("'")
        
        # Fix f-strings
        if 'f"' in line and double_quotes % 2 != 0 and not line.rstrip().endswith('\\'):
            line = line.rstrip() + '"'
        elif "f'" in line and single_quotes % 2 != 0 and not line.rstrip().endswith('\\'):
            line = line.rstrip() + "'"
            
        # Fix regular strings
        elif '"' in line and double_quotes % 2 != 0 and 'f"' not in line and 'r"' not in line:
            if not line.rstrip().endswith('\\'):
                line = line.rstrip() + '"'
        elif "'" in line and single_quotes % 2 != 0 and "f'" not in line and "r'" not in line:
            if not line.rstrip().endswith('\\'):
                line = line.rstrip() + "'"
        
        fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # Fix 7: Fix mismatched brackets/parentheses
    content = re.sub(r'\)\s*}\s*\)', ')}', content)
    content = re.sub(r'}\s*\)\s*,\s*\n\s+200\)', '}), 200', content)
    
    # Fix 8: Fix Path operations
    content = re.sub(r'Path\.parent', 'Path(__file__).parent', content)
    
    # Fix 9: Fix sys.path.insert issues
    content = re.sub(r'sys\.path\.insert, "[^"]+", "[^"]+"', 
                    'sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))', content)
    
    # Fix 10: Fix missing closing parentheses
    content = re.sub(r'(int\(os\.getenv\("[^"]+", \d+\))\s*$', r'\1)', content, flags=re.MULTILINE)
    
    # Fix 11: Add missing imports
    if 'from datetime import datetime' in content and 'timedelta' in content:
        if 'from datetime import' in content and 'timedelta' not in content:
            content = content.replace('from datetime import datetime',
                                    'from datetime import datetime, timedelta')
    
    # Fix 12: Fix logging.basicConfig
    content = re.sub(r'logging\.basicConfig\(\)\s*\n\s+level=', 
                    'logging.basicConfig(\n    level=', content)
    
    # Fix 13: Fix empty function bodies
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        fixed_lines.append(line)
        
        # Check if this is a function/class definition
        if (line.strip().startswith(('def ', 'class ')) and 
            line.strip().endswith(':') and 
            i + 1 < len(lines)):
            
            next_line = lines[i + 1] if i + 1 < len(lines) else ''
            
            # Check if the next line is another definition or empty
            if (not next_line.strip() or 
                next_line.strip().startswith(('def ', 'class ', '@')) or
                (i + 2 < len(lines) and lines[i + 2].strip().startswith(('def ', 'class ')))):
                
                # Add pass statement
                indent = len(line) - len(line.lstrip()) + 4
                fixed_lines.append(' ' * indent + 'pass')
    
    content = '\n'.join(fixed_lines)
    
    # Fix 14: Remove unmatched closing brackets/parentheses
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Skip standalone closing brackets/parentheses
        if line.strip() in [')', '}', '),', '},', '})']:
            # Check context
            if i > 0:
                prev_line = lines[i - 1].strip()
                # If previous line ends properly, this is likely an error
                if (prev_line.endswith((',', ')', '}', ':', '"', "'")) or
                    prev_line.startswith('return ') or
                    prev_line.startswith('except')):
                    
                    # Check if next line starts a new block
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if (next_line.startswith(('def ', 'class ', 'except', 'return', 
                                                 'if ', 'elif ', 'else:', 'try:', 
                                                 'finally:', 'with ')) or
                            next_line == '' or
                            next_line.startswith('@')):
                            continue  # Skip this line
        
        fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # Fix 15: Fix specific patterns for different file types
    if 'app/api/' in filepath:
        # Fix dictionary assignment issues
        content = re.sub(r'(\w+)\["(\w+)"\]\s*=\s*=\s*', r'\1["\2"] = ', content)
        
    if 'scripts/' in filepath:
        # Fix regex patterns
        content = re.sub(r'r"([^"]+)\["\f', r'r"\1["', content)
        
    return content


def main():
    """Main execution"""
    print("🔍 Finding all files with syntax errors...")
    error_files = get_all_error_files()
    
    print(f"📊 Found {len(error_files)} files with syntax errors")
    
    # Create backup directory
    backup_dir = f"syntax_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    fixed_count = 0
    still_error_count = 0
    
    for filepath in error_files:
        print(f"\n🔧 Fixing: {filepath}")
        
        # Create backup
        backup_path = Path(backup_dir) / Path(filepath).relative_to('.')
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Read original content
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Backup original
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Apply fixes
            fixed_content = fix_file_content(content, filepath)
            
            # Write fixed content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            # Verify fix
            result = subprocess.run(['python3', '-m', 'py_compile', filepath],
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"  ✅ Fixed successfully!")
                fixed_count += 1
            else:
                print(f"  ⚠️  Still has errors: {result.stderr.split(':', 1)[0] if result.stderr else 'Unknown'}")
                still_error_count += 1
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            still_error_count += 1
    
    print(f"\n" + "="*60)
    print(f"📊 FINAL RESULTS:")
    print(f"  ✅ Successfully fixed: {fixed_count} files")
    print(f"  ❌ Still have errors: {still_error_count} files")
    print(f"  💾 Backups saved to: {backup_dir}")
    print("="*60)
    
    # List files that still have errors
    if still_error_count > 0:
        print("\n⚠️  Files that still need manual fixing:")
        for filepath in error_files:
            result = subprocess.run(['python3', '-m', 'py_compile', filepath],
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print(f"  - {filepath}")
    
    return fixed_count, still_error_count


if __name__ == "__main__":
    fixed, errors = main()
    exit(0 if errors == 0 else 1)