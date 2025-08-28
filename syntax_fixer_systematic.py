#!/usr/bin/env python3
"""
Systematic Syntax Error Fixer
This script will fix syntax errors while preserving functionality
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import Tuple, Dict, List

class SyntaxFixer:
    def __init__(self):
        self.backup_dir = Path("/workspace/syntax_backup_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        self.fix_log = []
        self.test_results = {}
        
    def create_backup(self, filepath: str) -> bool:
        """Create backup of file before modification."""
        try:
            rel_path = Path(filepath).relative_to("/workspace")
            backup_path = self.backup_dir / rel_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(filepath, backup_path)
            print(f"✅ Backed up: {rel_path}")
            return True
        except Exception as e:
            print(f"❌ Backup failed for {filepath}: {e}")
            return False
    
    def test_syntax(self, filepath: str) -> Tuple[bool, str]:
        """Test if a Python file has syntax errors."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            compile(source, filepath, 'exec')
            return True, "No syntax errors"
        except SyntaxError as e:
            return False, f"Line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, str(e)
    
    def fix_unterminated_string(self, filepath: str, line_no: int) -> bool:
        """Fix unterminated string literal at specific line."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if line_no <= len(lines):
                line = lines[line_no - 1]
                
                # Check for quadruple quotes (common error)
                if '""""' in line:
                    lines[line_no - 1] = line.replace('""""', '"""')
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    return True
                
                # Check for unterminated f-string
                if line.strip().startswith('f"') or line.strip().startswith("f'"):
                    # Count quotes
                    if line.count('"') % 2 == 1 or line.count("'") % 2 == 1:
                        # Add closing quote
                        lines[line_no - 1] = line.rstrip() + '"\n' if '"' in line else line.rstrip() + "'\n"
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.writelines(lines)
                        return True
                
                # Check for regular unterminated string
                for quote in ['"', "'"]:
                    if line.strip().startswith(quote) and line.count(quote) == 1:
                        lines[line_no - 1] = line.rstrip() + quote + '\n'
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.writelines(lines)
                        return True
            
            return False
        except Exception as e:
            print(f"Error fixing unterminated string: {e}")
            return False
    
    def fix_unmatched_bracket(self, filepath: str, line_no: int, error_msg: str) -> bool:
        """Fix unmatched bracket/parenthesis errors."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Check if we have closing bracket without opening
            if "closing parenthesis '}' does not match opening parenthesis '('" in error_msg:
                # Need to add opening brace
                # Search backwards for function/method call
                for i in range(line_no - 1, max(0, line_no - 10), -1):
                    if '(' in lines[i] and '{' not in lines[i]:
                        # This might be where we need the opening brace
                        # Check if it looks like a dict should start here
                        if lines[i].rstrip().endswith('(') or ', {' not in lines[i]:
                            lines[i] = lines[i].rstrip()[:-1] + '({\n'
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.writelines(lines)
                            return True
            
            return False
        except Exception as e:
            print(f"Error fixing unmatched bracket: {e}")
            return False
    
    def fix_unexpected_indent(self, filepath: str, line_no: int) -> bool:
        """Fix unexpected indentation errors."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Common issue: file starts with indentation
            if line_no <= 5:  # Error in first few lines
                # Remove leading indentation from first actual code line
                for i in range(min(10, len(lines))):
                    if lines[i].strip() and not lines[i].startswith('#') and not lines[i].startswith('"""'):
                        if lines[i].startswith(' ') or lines[i].startswith('\t'):
                            lines[i] = lines[i].lstrip()
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.writelines(lines)
                            return True
                        break
            
            return False
        except Exception as e:
            print(f"Error fixing indentation: {e}")
            return False
    
    def log_fix(self, filepath: str, error_before: str, error_after: str, fixed: bool):
        """Log the fix attempt."""
        self.fix_log.append({
            'file': filepath,
            'error_before': error_before,
            'error_after': error_after,
            'fixed': fixed,
            'timestamp': datetime.now().isoformat()
        })
    
    def save_log(self):
        """Save fix log to file."""
        log_file = Path("/workspace/syntax_fix_log.json")
        with open(log_file, 'w') as f:
            json.dump(self.fix_log, f, indent=2)
        print(f"📝 Fix log saved to {log_file}")

# Create fixer instance
fixer = SyntaxFixer()

# Priority 1: Modified files that need immediate fixing
critical_files = [
    ("/workspace/app/api/ai.py", 177, "cannot assign to subscript"),
    ("/workspace/app/api/performance.py", 166, "closing parenthesis"),
    ("/workspace/app/mlops/dataset_manager.py", 3, "unterminated string literal"),
    ("/workspace/app/mlops/model_monitor.py", 337, "closing parenthesis"),
    ("/workspace/app/security/config.py", 281, "closing parenthesis"),
    ("/workspace/app/security/caching.py", 4, "unterminated string literal"),
    ("/workspace/app/security/input_validation.py", 4, "unterminated string literal"),
    ("/workspace/app/security/secrets_manager.py", 3, "unterminated string literal"),
    ("/workspace/app/services/remediation_service.py", 2, "unexpected indent"),
    ("/workspace/app/services/security_validation.py", 27, "unmatched ']'"),
]

print("=" * 60)
print("SYSTEMATIC SYNTAX ERROR FIXER")
print("=" * 60)
print(f"\n📁 Creating backup directory: {fixer.backup_dir}")
fixer.backup_dir.mkdir(parents=True, exist_ok=True)

print("\n" + "=" * 60)
print("PHASE 1: Backing up critical files")
print("=" * 60)

for filepath, _, _ in critical_files:
    if os.path.exists(filepath):
        fixer.create_backup(filepath)

print("\n✅ Backup complete. Starting fixes...")
print("\nFix log will be saved to /workspace/syntax_fix_log.json")
print("You can restore files from:", fixer.backup_dir)