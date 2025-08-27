#!/usr/bin/env python3
"""
Comprehensive syntax error fixer for SmartCloudOps AI
Fixes all identified syntax error patterns systematically
"""

import os
import re
import glob
import ast

def fix_unterminated_strings(content):
    """Fix unterminated string literals at the beginning of files"""
    lines = content.split('\n')
    if not lines:
        return content
    
    # Fix case 1: File starts with unterminated string
    if lines[0].strip().startswith('"') and not lines[0].strip().startswith('"""'):
        # Find where the string should end
        for i, line in enumerate(lines):
            if i == 0:
                continue
            if line.strip().endswith('"') and not line.strip().endswith('"""'):
                # Replace with proper docstring
                lines[0] = lines[0].replace('"', '"""', 1)
                lines[i] = lines[i].replace('"', '"""', -1)
                break
    
    return '\n'.join(lines)

def fix_missing_colons(content):
    """Fix missing colons after function definitions"""
    # Pattern: def function_name(...) without colon
    content = re.sub(r'def\s+(\w+)\s*\([^)]*\)\s*\n\s*"""', r'def \1():\n    """', content)
    content = re.sub(r'def\s+(\w+)\s*\([^)]*\)\s*\n\s*(\w+)', r'def \1():\n    \2', content)
    
    # Pattern: class ClassName(...) without colon
    content = re.sub(r'class\s+(\w+)\s*\([^)]*\)\s*\n\s*"""', r'class \1:\n    """', content)
    
    return content

def fix_missing_parentheses(content):
    """Fix missing parentheses in function calls"""
    # Pattern: jsonify() without parentheses
    content = re.sub(r'jsonify\(\)', 'jsonify({})', content)
    
    # Pattern: function calls without parentheses
    content = re.sub(r'(\w+)\(\)\s*\n\s*(\w+)', r'\1()\n    \2', content)
    
    return content

def fix_dictionary_syntax(content):
    """Fix dictionary syntax errors"""
    # Pattern: "key": value, without opening {
    content = re.sub(r'(\s+)"([^"]+)":\s*([^,\n]+),?\n', r'\1{\n\1    "\2": \3,\n\1}', content)
    
    # Pattern: return {} with missing opening brace
    content = re.sub(r'return\s*\{\s*\n\s*"', r'return {\n        "', content)
    
    # Pattern: missing closing braces in dictionaries
    content = re.sub(r'(\s+)"([^"]+)":\s*([^,\n]+)\s*\n\s*(\w+)', r'\1"\2": \3,\n\1\4', content)
    
    return content

def fix_function_definitions(content):
    """Fix function definition syntax errors"""
    # Pattern: @abstractmethod without proper function definition
    content = re.sub(r'@abstractmethod\s*\n\s*def\s+(\w+)\s*\([^)]*\)\s*->\s*(\w+):\s*\n\s*"""([^"]*)"', 
                    r'@abstractmethod\n    def \1() -> \2:\n        """\3"""', content)
    
    return content

def fix_string_literals(content):
    """Fix unterminated string literals"""
    # Pattern: unterminated strings in assignments
    content = re.sub(r'(\w+)\s*=\s*"([^"]*)\s*\n', r'\1 = "\2"\n', content)
    
    # Pattern: unterminated docstrings
    content = re.sub(r'(\s+)"""([^"]*)\s*\n', r'\1"""\2"""\n', content)
    
    return content

def fix_import_statements(content):
    """Fix import statement syntax errors"""
    # Pattern: from module import without proper syntax
    content = re.sub(r'from\s+(\w+)\s+import\s*(\w+)\s*\n\s*(\w+)', r'from \1 import \2\n\3', content)
    
    return content

def fix_file(file_path):
    """Fix all syntax errors in a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all fixes
        content = fix_unterminated_strings(content)
        content = fix_missing_colons(content)
        content = fix_missing_parentheses(content)
        content = fix_dictionary_syntax(content)
        content = fix_function_definitions(content)
        content = fix_string_literals(content)
        content = fix_import_statements(content)
        
        # Additional specific fixes based on patterns found
        # Fix: unterminated strings in assignments
        content = re.sub(r'user_message\s*=\s*"([^"]*)\s*\n', r'user_message = "\1"\n', content)
        
        # Fix: missing closing parentheses in function calls
        content = re.sub(r'(\w+)\(([^)]*)\s*\n\s*(\w+)', r'\1(\2)\n        \3', content)
        
        # Fix: missing closing braces in return statements
        content = re.sub(r'return\s*\{\s*\n\s*"([^"]+)":\s*([^,\n]+)\s*\n\s*(\w+)', 
                        r'return {\n        "\1": \2,\n        \3', content)
        
        # Fix: unterminated docstrings in function definitions
        content = re.sub(r'def\s+(\w+)\s*\([^)]*\):\s*\n\s*"""([^"]*)\s*\n', 
                        r'def \1():\n    """\2"""\n', content)
        
        # Fix: missing colons in for loops
        content = re.sub(r'for\s+(\w+)\s+in\s+([^:]+)\s*\n', r'for \1 in \2:\n', content)
        
        # Fix: missing colons in if statements
        content = re.sub(r'if\s+([^:]+)\s*\n', r'if \1:\n', content)
        
        # Fix: missing colons in else statements
        content = re.sub(r'else\s*\n', r'else:\n', content)
        
        # Fix: missing colons in except statements
        content = re.sub(r'except\s+([^:]+)\s*\n', r'except \1:\n', content)
        
        # Fix: missing colons in try statements
        content = re.sub(r'try\s*\n', r'try:\n', content)
        
        # Fix: missing colons in finally statements
        content = re.sub(r'finally\s*\n', r'finally:\n', content)
        
        # Fix: missing colons in with statements
        content = re.sub(r'with\s+([^:]+)\s*\n', r'with \1:\n', content)
        
        # Fix: missing colons in while statements
        content = re.sub(r'while\s+([^:]+)\s*\n', r'while \1:\n', content)
        
        # Fix: missing colons in class definitions
        content = re.sub(r'class\s+(\w+)\s*\([^)]*\)\s*\n', r'class \1:\n', content)
        
        # Fix: missing colons in function definitions
        content = re.sub(r'def\s+(\w+)\s*\([^)]*\)\s*\n', r'def \1():\n', content)
        
        # Fix: missing colons in async function definitions
        content = re.sub(r'async\s+def\s+(\w+)\s*\([^)]*\)\s*\n', r'async def \1():\n', content)
        
        # Fix: missing colons in async for loops
        content = re.sub(r'async\s+for\s+(\w+)\s+in\s+([^:]+)\s*\n', r'async for \1 in \2:\n', content)
        
        # Fix: missing colons in async with statements
        content = re.sub(r'async\s+with\s+([^:]+)\s*\n', r'async with \1:\n', content)
        
        # Fix: missing colons in match statements
        content = re.sub(r'match\s+([^:]+)\s*\n', r'match \1:\n', content)
        
        # Fix: missing colons in case statements
        content = re.sub(r'case\s+([^:]+)\s*\n', r'case \1:\n', content)
        
        # Fix: missing colons in except statements without exception type
        content = re.sub(r'except\s*\n', r'except:\n', content)
        
        # Fix: missing colons in else statements in try-except
        content = re.sub(r'else\s*\n\s*(\w+)', r'else:\n    \1', content)
        
        # Fix: missing colons in finally statements in try-except
        content = re.sub(r'finally\s*\n\s*(\w+)', r'finally:\n    \1', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def validate_syntax(file_path):
    """Validate that a file has correct syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True
    except:
        return False

def main():
    """Main function to fix all Python files"""
    python_files = glob.glob('app/**/*.py', recursive=True)
    fixed_count = 0
    error_count = 0
    validated_count = 0
    
    print(f"Found {len(python_files)} Python files")
    print("Starting comprehensive syntax fix...")
    
    for file_path in python_files:
        try:
            if fix_file(file_path):
                fixed_count += 1
                print(f"✅ Fixed: {file_path}")
                
                # Validate the fix
                if validate_syntax(file_path):
                    validated_count += 1
                    print(f"✅ Validated: {file_path}")
                else:
                    print(f"⚠️  Still has syntax errors: {file_path}")
                    
        except Exception as e:
            error_count += 1
            print(f"❌ Error fixing {file_path}: {e}")
    
    print(f"\n📊 Summary:")
    print(f"✅ Files fixed: {fixed_count}")
    print(f"✅ Files validated: {validated_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📁 Total files processed: {len(python_files)}")
    
    # Final validation
    print("\n🔍 Final validation...")
    final_errors = []
    for file_path in python_files:
        if not validate_syntax(file_path):
            final_errors.append(file_path)
    
    print(f"📊 Final syntax errors: {len(final_errors)}")
    if final_errors:
        print("Files still with syntax errors:")
        for error_file in final_errors[:10]:  # Show first 10
            print(f"  - {error_file}")
        if len(final_errors) > 10:
            print(f"  ... and {len(final_errors) - 10} more")

if __name__ == "__main__":
    main()
