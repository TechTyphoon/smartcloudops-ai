#!/usr/bin/env python3
"""
Advanced Fix Script - Targeted fixes for specific syntax errors
"""
import ast
import os
import re
from pathlib import Path
from typing import List, Tuple, Optional

class AdvancedPythonFixer:
    def __init__(self):
        self.fixed_count = 0
        self.error_files = []
    
    def get_syntax_error(self, file_path: Path) -> Optional[Tuple[int, str]]:
        """Get the first syntax error in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            ast.parse(content)
            return None
        except SyntaxError as e:
            return (e.lineno, e.msg)
        except Exception:
            return None
    
    def fix_unmatched_parentheses(self, content: str, line_num: int) -> str:
        """Fix unmatched parentheses, brackets, or braces."""
        lines = content.split('\n')
        if line_num <= len(lines):
            line = lines[line_num - 1]
            
            # Count opening and closing brackets
            open_count = line.count('(') + line.count('[') + line.count('{')
            close_count = line.count(')') + line.count(']') + line.count('}')
            
            # Fix common patterns
            if '{}' in line and '({' not in line:
                # Replace {} with { at start of dict/set
                line = line.replace('{}', '{')
            elif '))' in line and open_count < close_count:
                # Remove extra closing parenthesis
                line = line.replace('))', ')')
            elif '}}' in line and open_count < close_count:
                # Remove extra closing brace
                line = line.replace('}}', '}')
            
            lines[line_num - 1] = line
        
        return '\n'.join(lines)
    
    def fix_invalid_syntax(self, content: str, line_num: int) -> str:
        """Fix various invalid syntax issues."""
        lines = content.split('\n')
        if line_num <= len(lines):
            line = lines[line_num - 1]
            
            # Fix missing commas in dict/list
            if '{' in line or '[' in line:
                # Add comma after dict/list items
                line = re.sub(r'(["\'])\s*\n', r'\1,\n', line)
                line = re.sub(r'(\d+)\s*\n', r'\1,\n', line)
                line = re.sub(r'(True|False|None)\s*\n', r'\1,\n', line)
            
            # Fix assignment in conditional
            if '=' in line and ('if ' in line or 'elif ' in line):
                # Replace = with == in conditionals
                line = re.sub(r'(\s+)=(\s+)', r'\1==\2', line)
            
            # Fix missing colons
            if line.strip().startswith(('def ', 'class ', 'if ', 'elif ', 'else', 'for ', 'while ', 'try', 'except', 'finally', 'with ')):
                if not line.rstrip().endswith(':'):
                    line = line.rstrip() + ':'
            
            lines[line_num - 1] = line
        
        return '\n'.join(lines)
    
    def fix_unexpected_indent(self, content: str, line_num: int) -> str:
        """Fix unexpected indentation issues."""
        lines = content.split('\n')
        if line_num <= len(lines):
            # Check if it's a docstring issue
            if '"""' in lines[line_num - 1]:
                # Move docstring to proper position
                docstring_start = line_num - 1
                docstring_end = docstring_start
                
                # Find end of docstring
                for i in range(docstring_start + 1, len(lines)):
                    if '"""' in lines[i]:
                        docstring_end = i
                        break
                
                # Extract docstring
                docstring = []
                for i in range(docstring_start, docstring_end + 1):
                    docstring.append(lines[i].lstrip())
                
                # Remove old docstring
                for i in range(docstring_end, docstring_start - 1, -1):
                    lines.pop(i)
                
                # Find proper position (after shebang, before imports)
                insert_pos = 0
                if lines[0].startswith('#!/usr/bin/env'):
                    insert_pos = 1
                
                # Insert docstring
                for i, doc_line in enumerate(docstring):
                    lines.insert(insert_pos + i, doc_line)
            else:
                # General indent fix - remove excessive indentation
                lines[line_num - 1] = lines[line_num - 1].lstrip()
        
        return '\n'.join(lines)
    
    def fix_unterminated_string(self, content: str, line_num: int) -> str:
        """Fix unterminated string literals."""
        lines = content.split('\n')
        if line_num <= len(lines):
            line = lines[line_num - 1]
            
            # Count quotes
            single_quotes = line.count("'") - line.count("\\'")
            double_quotes = line.count('"') - line.count('\\"')
            
            # Fix unterminated strings
            if single_quotes % 2 != 0:
                line = line + "'"
            if double_quotes % 2 != 0:
                line = line + '"'
            
            # Fix f-strings
            if 'f"' in line or "f'" in line:
                # Ensure f-strings are properly closed
                line = re.sub(r'(f["\'][^"\']*)\n', r'\1"\n', line)
            
            lines[line_num - 1] = line
        
        return '\n'.join(lines)
    
    def fix_file(self, file_path: Path) -> bool:
        """Fix all syntax errors in a file."""
        max_attempts = 10
        attempt = 0
        
        while attempt < max_attempts:
            error = self.get_syntax_error(file_path)
            if not error:
                return True  # No errors
            
            line_num, msg = error
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Apply appropriate fix based on error message
                if 'unmatched' in msg or 'does not match' in msg:
                    content = self.fix_unmatched_parentheses(content, line_num)
                elif 'invalid syntax' in msg:
                    content = self.fix_invalid_syntax(content, line_num)
                elif 'unexpected indent' in msg:
                    content = self.fix_unexpected_indent(content, line_num)
                elif 'unterminated' in msg:
                    content = self.fix_unterminated_string(content, line_num)
                elif 'was never closed' in msg:
                    # Add closing parenthesis/bracket/brace
                    lines = content.split('\n')
                    if line_num <= len(lines):
                        # Find what needs closing
                        line = lines[line_num - 1]
                        if '(' in line and ')' not in line:
                            lines[line_num - 1] = line + ')'
                        elif '[' in line and ']' not in line:
                            lines[line_num - 1] = line + ']'
                        elif '{' in line and '}' not in line:
                            lines[line_num - 1] = line + '}'
                        content = '\n'.join(lines)
                
                # Write back if changed
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.fixed_count += 1
                else:
                    # Couldn't fix, record error
                    self.error_files.append((file_path, line_num, msg))
                    return False
                
            except Exception as e:
                self.error_files.append((file_path, 0, str(e)))
                return False
            
            attempt += 1
        
        return False
    
    def fix_all_files(self, directory: Path):
        """Fix all Python files in directory."""
        for py_file in directory.rglob('*.py'):
            # Skip excluded directories
            if any(excluded in str(py_file) for excluded in ['venv', '__pycache__', '.git', 'node_modules']):
                continue
            
            # Check if file has errors
            if self.get_syntax_error(py_file):
                print(f"Fixing: {py_file.relative_to(directory)}")
                self.fix_file(py_file)

def main():
    """Main function."""
    workspace_dir = Path('/workspace')
    
    print("🛠️  Advanced Python Fixer")
    print("=" * 60)
    
    fixer = AdvancedPythonFixer()
    
    # Fix app directory
    print("\n📁 Fixing App Directory...")
    fixer.fix_all_files(workspace_dir / 'app')
    
    # Fix scripts directory
    print("\n📁 Fixing Scripts Directory...")
    fixer.fix_all_files(workspace_dir / 'scripts')
    
    # Fix tests directory
    print("\n📁 Fixing Tests Directory...")
    fixer.fix_all_files(workspace_dir / 'tests')
    
    print("\n" + "=" * 60)
    print(f"✅ Fixed {fixer.fixed_count} files")
    
    if fixer.error_files:
        print(f"\n⚠️  Could not fix {len(fixer.error_files)} files:")
        for file, line, msg in fixer.error_files[:10]:
            print(f"   - {file.relative_to(workspace_dir)} (line {line}): {msg}")

if __name__ == "__main__":
    main()