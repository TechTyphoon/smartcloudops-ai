#!/usr/bin/env python3
"""
Targeted syntax fixer for the most common patterns
"""

import os
import re
import glob

def fix_common_patterns(file_path):
    """Fix the most common syntax error patterns"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix 1: Unterminated docstrings at line 2
        content = re.sub(r'^\s*"""\s*\n', '"""\n', content)
        
        # Fix 2: Blueprint with wrong name
        content = re.sub(r'Blueprint\("([^"]+)_bp = Blueprint"', r'Blueprint("\1"', content)
        
        # Fix 3: Missing colons in function definitions
        content = re.sub(r'def\s+(\w+)\s*\([^)]*\)\s*\n\s*"""', r'def \1():\n    """', content)
        
        # Fix 4: Missing colons in class definitions
        content = re.sub(r'class\s+(\w+)\s*\([^)]*\)\s*\n\s*"""', r'class \1:\n    """', content)
        
        # Fix 5: Missing colons in for loops
        content = re.sub(r'for\s+(\w+)\s+in\s+([^:]+)\s*\n', r'for \1 in \2:\n', content)
        
        # Fix 6: Missing colons in if statements
        content = re.sub(r'if\s+([^:]+)\s*\n', r'if \1:\n', content)
        
        # Fix 7: Missing colons in else statements
        content = re.sub(r'else\s*\n', r'else:\n', content)
        
        # Fix 8: Missing colons in except statements
        content = re.sub(r'except\s+([^:]+)\s*\n', r'except \1:\n', content)
        
        # Fix 9: Missing colons in try statements
        content = re.sub(r'try\s*\n', r'try:\n', content)
        
        # Fix 10: Missing colons in finally statements
        content = re.sub(r'finally\s*\n', r'finally:\n', content)
        
        # Fix 11: Missing colons in with statements
        content = re.sub(r'with\s+([^:]+)\s*\n', r'with \1:\n', content)
        
        # Fix 12: Missing colons in while statements
        content = re.sub(r'while\s+([^:]+)\s*\n', r'while \1:\n', content)
        
        # Fix 13: Missing colons in async function definitions
        content = re.sub(r'async\s+def\s+(\w+)\s*\([^)]*\)\s*\n', r'async def \1():\n', content)
        
        # Fix 14: Missing colons in async for loops
        content = re.sub(r'async\s+for\s+(\w+)\s+in\s+([^:]+)\s*\n', r'async for \1 in \2:\n', content)
        
        # Fix 15: Missing colons in async with statements
        content = re.sub(r'async\s+with\s+([^:]+)\s*\n', r'async with \1:\n', content)
        
        # Fix 16: Missing colons in match statements
        content = re.sub(r'match\s+([^:]+)\s*\n', r'match \1:\n', content)
        
        # Fix 17: Missing colons in case statements
        content = re.sub(r'case\s+([^:]+)\s*\n', r'case \1:\n', content)
        
        # Fix 18: Missing colons in except statements without exception type
        content = re.sub(r'except\s*\n', r'except:\n', content)
        
        # Fix 19: Missing colons in else statements in try-except
        content = re.sub(r'else\s*\n\s*(\w+)', r'else:\n    \1', content)
        
        # Fix 20: Missing colons in finally statements in try-except
        content = re.sub(r'finally\s*\n\s*(\w+)', r'finally:\n    \1', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Main function to fix common patterns"""
    # Get list of files that Black reported as having syntax errors
    problematic_files = [
        'app/api/anomalies_refactored.py',
        'app/api/ml.py',
        'app/api/mlops.py',
        'app/api/performance.py',
        'app/auth.py',
        'app/chatops/ai_handler.py',
        'app/chatops/gpt_handler.py',
        'app/chatops/utils.py',
        'app/security/config.py',
        'app/security/caching.py',
        'app/security/secrets_manager.py',
        'app/security/input_validation.py',
        'app/security/error_handling.py',
        'app/security/__init__.py',
        'app/security/rate_limiting.py',
        'app/services/mlops_service.py',
        'app/services/ml_service.py',
        'app/services/security_validation.py',
        'app/services/feedback_service.py',
        'app/services/ai_service.py',
        'app/services/remediation_service.py',
        'app/services/anomaly_service.py',
        'app/services/__init__.py',
        'app/auth.py',
        'app/database.py',
        'app/ml_module.py',
        'app/chatops_module.py',
        'app/auth_routes.py',
        'app/auth_module.py',
    ]
    
    fixed_count = 0
    
    print(f"Fixing {len(problematic_files)} problematic files...")
    
    for file_path in problematic_files:
        if os.path.exists(file_path):
            if fix_common_patterns(file_path):
                fixed_count += 1
                print(f"✅ Fixed: {file_path}")
    
    print(f"\n📊 Summary:")
    print(f"✅ Files fixed: {fixed_count}")
    print(f"📁 Total files processed: {len(problematic_files)}")

if __name__ == "__main__":
    main()
