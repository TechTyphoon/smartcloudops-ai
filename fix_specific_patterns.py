#!/usr/bin/env python3
"""
Targeted syntax error fixes for SmartCloudOps.AI files
Based on observed patterns in the codebase.
"""

import re
import os
import shutil
from pathlib import Path
from datetime import datetime


class TargetedSyntaxFixer:
    def __init__(self):
        self.backup_dir = f"syntax_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def create_backup(self, file_path):
        """Create backup of file before fixing"""
        backup_path = Path(self.backup_dir) / Path(file_path).relative_to('.')
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup_path)
        print(f"  📁 Backed up to: {backup_path}")
        
    def fix_file(self, file_path):
        """Apply targeted fixes to a file"""
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False
            
        print(f"\n🔧 Fixing: {file_path}")
        self.create_backup(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original = content
            
            # Apply specific fixes based on file
            if file_path == 'app/auth.py':
                content = self.fix_auth_py(content)
            elif file_path == 'app/auth_routes.py':
                content = self.fix_auth_routes_py(content)
            elif file_path == 'app/auth_module.py':
                content = self.fix_auth_module_py(content)
            elif file_path.startswith('app/api/'):
                content = self.fix_api_files(content)
            elif file_path.startswith('app/chatops/'):
                content = self.fix_chatops_files(content)
            elif file_path.startswith('app/services/'):
                content = self.fix_services_files(content)
            elif file_path.startswith('app/mlops/'):
                content = self.fix_mlops_files(content)
            elif file_path.startswith('app/observability/'):
                content = self.fix_observability_files(content)
            elif file_path.startswith('app/performance/'):
                content = self.fix_performance_files(content)
            elif file_path.startswith('app/security/'):
                content = self.fix_security_files(content)
            elif file_path.startswith('app/remediation/'):
                content = self.fix_remediation_files(content)
            elif file_path.startswith('scripts/'):
                content = self.fix_script_files(content)
            elif file_path.startswith('tests/'):
                content = self.fix_test_files(content)
            else:
                content = self.apply_general_fixes(content)
            
            # Write fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  ✅ Written fixed content")
            return True
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
            
    def fix_auth_py(self, content):
        """Fix remaining issues in app/auth.py"""
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Fix the unmatched brace issue at line 297
            if i >= 295 and i <= 300:
                # Look for patterns like standalone } or )
                if line.strip() == '}' or line.strip() == ')':
                    # Skip standalone braces/parens that are likely errors
                    i += 1
                    continue
                    
            fixed_lines.append(line)
            i += 1
            
        return '\n'.join(fixed_lines)
        
    def fix_auth_routes_py(self, content):
        """Fix app/auth_routes.py"""
        # Fix indented docstring
        content = re.sub(r'^    """', '"""', content, flags=re.MULTILINE)
        return content
        
    def fix_auth_module_py(self, content):
        """Fix app/auth_module.py"""
        # Fix indented docstring
        content = re.sub(r'^    """', '"""', content, flags=re.MULTILINE)
        # Fix missing closing brackets
        content = re.sub(r'(\{"[^"]+": "[^"]+"),?\s*$', r'\1}', content, flags=re.MULTILINE)
        return content
        
    def fix_api_files(self, content):
        """Fix common issues in API files"""
        # Fix indented docstrings
        content = re.sub(r'^    """', '"""', content, flags=re.MULTILINE)
        
        # Fix malformed dictionary assignments
        content = re.sub(r'(\w+)\["(\w+)"\]\s*=\s*=\s*', r'\1["\2"] = ', content)
        
        # Fix mismatched parentheses/brackets
        content = re.sub(r'\)\s*}\s*\)', ')}', content)
        
        return content
        
    def fix_chatops_files(self, content):
        """Fix common issues in chatops files"""
        # Fix indented docstrings
        content = re.sub(r'^    """', '"""', content, flags=re.MULTILINE)
        
        # Fix empty function bodies
        lines = content.split('\n')
        fixed_lines = []
        for i, line in enumerate(lines):
            fixed_lines.append(line)
            # If we find a function definition without a body
            if line.strip().endswith(':') and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line and not next_line.startswith(' ') and next_line != 'pass':
                    # Add pass statement
                    indent = len(line) - len(line.lstrip()) + 4
                    fixed_lines.append(' ' * indent + 'pass')
                    
        return '\n'.join(fixed_lines)
        
    def fix_services_files(self, content):
        """Fix common issues in services files"""
        # Fix indented docstrings
        content = re.sub(r'^    """', '"""', content, flags=re.MULTILINE)
        
        # Fix indentation issues
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Fix lines that start with unexpected indentation
            if line.startswith('        ') and not any(line.strip().startswith(x) for x in ['def ', 'class ', 'if ', 'elif ', 'else:', 'try:', 'except', 'finally:', 'with ', 'for ', 'while ', 'return ', 'pass', 'continue', 'break', '#', '"""']):
                # Likely an indentation error
                line = line[4:]  # Remove 4 spaces
            fixed_lines.append(line)
            
        return '\n'.join(fixed_lines)
        
    def fix_mlops_files(self, content):
        """Fix common issues in MLOps files"""
        # Fix indented docstrings
        content = re.sub(r'^    """', '"""', content, flags=re.MULTILINE)
        
        # Fix unterminated strings
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Count quotes
            if line.count('"') % 2 != 0 and not line.strip().endswith('\\'):
                # Unterminated string - add closing quote
                line = line.rstrip() + '"'
            fixed_lines.append(line)
            
        return '\n'.join(fixed_lines)
        
    def fix_observability_files(self, content):
        """Fix common issues in observability files"""
        # Fix indented docstrings
        content = re.sub(r'^    """', '"""', content, flags=re.MULTILINE)
        
        # Fix empty class/function bodies
        content = self.add_pass_statements(content)
        
        return content
        
    def fix_performance_files(self, content):
        """Fix common issues in performance files"""
        # Fix indented docstrings
        content = re.sub(r'^    """', '"""', content, flags=re.MULTILINE)
        
        # Fix dictionary/tuple mismatches
        content = re.sub(r'\(([^)]+)\s*:\s*([^)]+)\)', r'{\1: \2}', content)
        
        return content
        
    def fix_security_files(self, content):
        """Fix common issues in security files"""
        # Fix indented docstrings
        content = re.sub(r'^    """', '"""', content, flags=re.MULTILINE)
        
        # Fix unterminated strings in configs
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Fix lines with unterminated strings
            if '"' in line and line.count('"') % 2 != 0:
                line = line.rstrip() + '"'
            fixed_lines.append(line)
            
        return '\n'.join(fixed_lines)
        
    def fix_remediation_files(self, content):
        """Fix common issues in remediation files"""
        # Fix indented docstrings
        content = re.sub(r'^    """', '"""', content, flags=re.MULTILINE)
        
        # Add pass statements for empty functions
        content = self.add_pass_statements(content)
        
        return content
        
    def fix_script_files(self, content):
        """Fix common issues in script files"""
        # Fix unterminated f-strings
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Fix f-strings
            if 'f"' in line or "f'" in line:
                # Count quotes
                double_quotes = line.count('"')
                single_quotes = line.count("'")
                
                if 'f"' in line and double_quotes % 2 != 0:
                    line = line.rstrip() + '"'
                elif "f'" in line and single_quotes % 2 != 0:
                    line = line.rstrip() + "'"
                    
            # Fix regex patterns
            if 'r"' in line or "r'" in line:
                # Fix unterminated regex
                if line.count('"') % 2 != 0:
                    line = line.rstrip() + '"'
                elif line.count("'") % 2 != 0:
                    line = line.rstrip() + "'"
                    
            fixed_lines.append(line)
            
        return '\n'.join(fixed_lines)
        
    def fix_test_files(self, content):
        """Fix common issues in test files"""
        # Fix indented docstrings
        content = re.sub(r'^    """', '"""', content, flags=re.MULTILINE)
        
        # Fix import issues
        content = re.sub(r'from\s+\.\.\s+import', 'from .. import', content)
        
        return content
        
    def apply_general_fixes(self, content):
        """Apply general fixes that work for most files"""
        # Fix indented module docstrings
        lines = content.split('\n')
        if len(lines) > 2:
            for i in range(min(10, len(lines))):
                if lines[i].strip().startswith('"""') and lines[i].startswith('    '):
                    lines[i] = lines[i].lstrip()
                    
        content = '\n'.join(lines)
        
        # Fix common patterns
        content = re.sub(r'(\w+)\s*=\s*\(\)\s*$', r'\1 = ()', content, flags=re.MULTILINE)
        content = re.sub(r'return\s*\(\)\s*$', 'return', content, flags=re.MULTILINE)
        
        return content
        
    def add_pass_statements(self, content):
        """Add pass statements to empty function/class bodies"""
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            fixed_lines.append(line)
            
            # Check if this is a function or class definition
            if (line.strip().startswith('def ') or line.strip().startswith('class ')) and line.strip().endswith(':'):
                # Check if next line is empty or another definition
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if not next_line.strip() or next_line.strip().startswith('def ') or next_line.strip().startswith('class '):
                        # Add pass statement
                        indent = len(line) - len(line.lstrip()) + 4
                        fixed_lines.append(' ' * indent + 'pass')
                        
        return '\n'.join(fixed_lines)


def main():
    """Main execution"""
    # First, let's finish fixing app/auth.py
    fixer = TargetedSyntaxFixer()
    
    # Complete the auth.py fix
    print("Completing app/auth.py fix...")
    
    # Read the current state
    with open('app/auth.py', 'r') as f:
        content = f.read()
    
    # Find and remove unmatched braces/parentheses
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Skip standalone unmatched braces/parentheses
        if line.strip() in [')', '}', '},', '),']:
            # Check if this is truly unmatched by looking at context
            if i > 0 and i < len(lines) - 1:
                prev_line = lines[i-1].strip()
                next_line = lines[i+1].strip() if i+1 < len(lines) else ''
                
                # If previous line ends properly and next line starts a new block, skip this line
                if (prev_line.endswith(',') or prev_line.endswith(')') or prev_line.endswith('}')) and \
                   (next_line.startswith('def ') or next_line.startswith('class ') or 
                    next_line.startswith('except') or next_line.startswith('return')):
                    continue  # Skip this line
                    
        fixed_lines.append(line)
    
    # Write back
    with open('app/auth.py', 'w') as f:
        f.write('\n'.join(fixed_lines))
    
    print("✅ Completed app/auth.py additional fixes")
    
    # Now continue with other files
    files_to_fix = [
        'app/auth_routes.py',
        'app/auth_module.py',
        'app/api/ai.py',
        'app/api/anomalies_refactored.py',
        'app/api/mlops.py',
        'app/api/performance.py',
        'app/chatops/ai_handler.py',
        'app/chatops/gpt_handler.py',
        'app/chatops/utils.py',
        'app/chatops_module.py',
    ]
    
    for file_path in files_to_fix:
        fixer.fix_file(file_path)
    
    print("\n🔍 Verifying fixes...")
    import subprocess
    
    success_count = 0
    for file_path in ['app/main.py', 'app/auth.py'] + files_to_fix:
        if os.path.exists(file_path):
            result = subprocess.run(['python3', '-m', 'py_compile', file_path], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✅ {file_path}")
                success_count += 1
            else:
                print(f"  ❌ {file_path}: {result.stderr.split(':', 1)[0] if result.stderr else 'Unknown error'}")
    
    print(f"\n📊 Fixed {success_count} out of {len(files_to_fix) + 2} files")
    

if __name__ == "__main__":
    main()