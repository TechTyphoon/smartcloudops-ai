#!/usr/bin/env python3
"""
Comprehensive Syntax Validator for Python Codebase
"""
import ast
import os
import sys
from pathlib import Path
from typing import List, Tuple

def check_python_syntax(file_path: Path) -> Tuple[bool, str]:
    """Check if a Python file has valid syntax."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True, ""
    except SyntaxError as e:
        return False, f"SyntaxError at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)

def validate_directory(directory: Path, exclude_dirs: List[str] = None) -> dict:
    """Validate all Python files in a directory."""
    if exclude_dirs is None:
        exclude_dirs = ['venv', '__pycache__', '.git', 'node_modules', '.pytest_cache']
    
    results = {
        'total_files': 0,
        'valid_files': 0,
        'invalid_files': 0,
        'errors': []
    }
    
    for py_file in directory.rglob('*.py'):
        # Skip excluded directories
        if any(excluded in py_file.parts for excluded in exclude_dirs):
            continue
            
        results['total_files'] += 1
        is_valid, error_msg = check_python_syntax(py_file)
        
        if is_valid:
            results['valid_files'] += 1
        else:
            results['invalid_files'] += 1
            results['errors'].append({
                'file': str(py_file.relative_to(directory)),
                'error': error_msg
            })
    
    return results

def main():
    """Main validation function."""
    workspace_dir = Path('/workspace')
    
    print("🔍 Running Comprehensive Syntax Validation...")
    print("=" * 60)
    
    # Validate main app directory
    app_results = validate_directory(workspace_dir / 'app')
    print(f"\n📁 App Directory:")
    print(f"   Total files: {app_results['total_files']}")
    print(f"   ✅ Valid: {app_results['valid_files']}")
    print(f"   ❌ Invalid: {app_results['invalid_files']}")
    
    if app_results['errors']:
        print("\n   Errors found:")
        for error in app_results['errors'][:10]:  # Show first 10 errors
            print(f"   - {error['file']}: {error['error']}")
    
    # Validate scripts directory
    scripts_results = validate_directory(workspace_dir / 'scripts')
    print(f"\n📁 Scripts Directory:")
    print(f"   Total files: {scripts_results['total_files']}")
    print(f"   ✅ Valid: {scripts_results['valid_files']}")
    print(f"   ❌ Invalid: {scripts_results['invalid_files']}")
    
    if scripts_results['errors']:
        print("\n   Errors found:")
        for error in scripts_results['errors'][:10]:
            print(f"   - {error['file']}: {error['error']}")
    
    # Validate tests directory
    tests_results = validate_directory(workspace_dir / 'tests')
    print(f"\n📁 Tests Directory:")
    print(f"   Total files: {tests_results['total_files']}")
    print(f"   ✅ Valid: {tests_results['valid_files']}")
    print(f"   ❌ Invalid: {tests_results['invalid_files']}")
    
    if tests_results['errors']:
        print("\n   Errors found:")
        for error in tests_results['errors'][:10]:
            print(f"   - {error['file']}: {error['error']}")
    
    # Calculate totals
    total_files = app_results['total_files'] + scripts_results['total_files'] + tests_results['total_files']
    total_valid = app_results['valid_files'] + scripts_results['valid_files'] + tests_results['valid_files']
    total_invalid = app_results['invalid_files'] + scripts_results['invalid_files'] + tests_results['invalid_files']
    
    print("\n" + "=" * 60)
    print("📊 FINAL SUMMARY:")
    print(f"   Total Python files checked: {total_files}")
    print(f"   ✅ Valid files: {total_valid}")
    print(f"   ❌ Invalid files: {total_invalid}")
    
    if total_invalid == 0:
        print("\n🎉 SUCCESS: All Python files have valid syntax!")
        return 0
    else:
        print(f"\n⚠️  {total_invalid} files still have syntax errors.")
        # Write detailed error report
        with open('/workspace/remaining_errors.txt', 'w') as f:
            f.write("Remaining Syntax Errors\n")
            f.write("=" * 60 + "\n\n")
            for error in app_results['errors']:
                f.write(f"File: app/{error['file']}\n")
                f.write(f"Error: {error['error']}\n\n")
            for error in scripts_results['errors']:
                f.write(f"File: scripts/{error['file']}\n")
                f.write(f"Error: {error['error']}\n\n")
            for error in tests_results['errors']:
                f.write(f"File: tests/{error['file']}\n")
                f.write(f"Error: {error['error']}\n\n")
        print("   Detailed error report saved to: remaining_errors.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())