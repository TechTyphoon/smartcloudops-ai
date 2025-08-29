#!/usr/bin/env python3
"""
Improved script to fix specific syntax errors identified by Black
"""

import os
import re
import glob

def fix_file(file_path):
    """Fix specific syntax errors in a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        fixed = False
        
        # Fix 1: Unterminated string literals at start of file
        if content.startswith('"') and not content.startswith('"""'):
            lines = content.split('\n')
            if lines[0].startswith('"'):
                # Find where the string ends
                string_end = -1
                for i, line in enumerate(lines):
                    if line.strip().endswith('"') and i > 0:
                        string_end = i
                        break
                
                if string_end > 0:
                    # Replace with proper docstring
                    lines[0] = lines[0].replace('"', '"""', 1)
                    lines[string_end] = lines[string_end].replace('"', '"""', -1)
                    content = '\n'.join(lines)
                    fixed = True
        
        # Fix 2: Missing parentheses in function calls
        # Pattern: jsonify() without parentheses
        content = re.sub(r'jsonify\(\)', 'jsonify({})', content)
        
        # Fix 3: Dictionary syntax errors - missing opening braces
        # Pattern: "key": value, without opening {
        content = re.sub(r'(\s+)"([^"]+)":\s*([^,\n]+),?\n', rf'\1{\n\1    "\2": \3,\n\1}', content)
        
        # Fix 4: Fix specific patterns found in the errors
        # Fix: "status": "healthy" if redis_cache._redis_client else "unavailable",
        content = re.sub(
            r'"status":\s*"([^"]+)"\s+if\s+([^:]+)\s+else\s+"([^"]+)"',
            r'"status": "\\1" if \\2 else "\\3"',
            content
        )
        
        # Fix 5: Fix unterminated docstrings
        content = re.sub(r'(\s+)"""\s*\n', r'\1"""\n', content)
        
        # Fix 6: Fix missing closing parentheses in function definitions
        content = re.sub(r'def\s+(\w+)\s*\([^)]*\):\s*\n\s*"""([^"]*)"', r'def \1():\n    """\2"""', content)
        
        # Fix 7: Fix specific error patterns
        # Fix: analysis_result["anomaly_detected"] = False
        content = re.sub(r'(\w+)\["([^"]+)"\]\s*=\s*(\w+)', r'\1["\\2"] = \\3', content)
        
        # Fix 8: Fix for loops with missing colons
        content = re.sub(r'for\s+(\w+)\s+in\s+([^:]+)\s*\n', r'for \1 in \2:\n', content)
        
        # Fix 9: Fix version strings
        content = re.sub(r'__version__\s*=\s*\("([^"]+)"\)', r'__version__ = "\\1"', content)
        
        # Fix 10: Fix missing closing quotes in docstrings
        content = re.sub(r'(\s+)"""([^"]*)\n', r'\1"""\\2"""\n', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Main function to fix all Python files"""
    python_files = glob.glob('app/**/*.py', recursive=True)
    fixed_count = 0
    error_count = 0
    
    print(f"Found {len(python_files)} Python files")
    
    for file_path in python_files:
        try:
            if fix_file(file_path):
                fixed_count += 1
                print(f"✅ Fixed: {file_path}")
        except Exception as e:
            error_count += 1
            print(f"❌ Error fixing {file_path}: {e}")
    
    print(f"\n📊 Summary:")
    print(f"✅ Files fixed: {fixed_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📁 Total files processed: {len(python_files)}")

if __name__ == "__main__":
    main()
