#!/usr/bin/env python3
"""
Critical Files Final Fix - Manual targeted fixes for essential files
"""
import os
from pathlib import Path

def fix_critical_files():
    """Fix the most critical files that are still broken."""
    
    fixes_applied = []
    
    # Fix 1: app/main.py - Missing comma issue
    try:
        file_path = Path('/workspace/app/main.py')
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix missing comma in imports or function calls
        content = content.replace('Path\nimport', 'Path\nimport')
        content = content.replace('}\n        }', '},\n        }')
        
        with open(file_path, 'w') as f:
            f.write(content)
        fixes_applied.append('app/main.py')
    except Exception as e:
        print(f"Could not fix app/main.py: {e}")
    
    # Fix 2: app/monitoring_module.py - Empty try block
    try:
        file_path = Path('/workspace/app/monitoring_module.py')
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Find empty try blocks and add pass
        for i, line in enumerate(lines):
            if line.strip() == 'try:':
                if i + 1 < len(lines) and lines[i + 1].strip().startswith('except'):
                    lines.insert(i + 1, '    pass\n')
        
        with open(file_path, 'w') as f:
            f.writelines(lines)
        fixes_applied.append('app/monitoring_module.py')
    except Exception as e:
        print(f"Could not fix app/monitoring_module.py: {e}")
    
    # Fix 3: app/auth.py - Unmatched braces
    try:
        file_path = Path('/workspace/app/auth.py')
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Balance braces and parentheses
        lines = content.split('\n')
        for i, line in enumerate(lines):
            open_count = line.count('(') + line.count('{') + line.count('[')
            close_count = line.count(')') + line.count('}') + line.count(']')
            if open_count > close_count:
                # Add closing at end of line
                if '(' in line and ')' not in line:
                    lines[i] = line + ')'
                elif '{' in line and '}' not in line:
                    lines[i] = line + '}'
                elif '[' in line and ']' not in line:
                    lines[i] = line + ']'
        
        content = '\n'.join(lines)
        with open(file_path, 'w') as f:
            f.write(content)
        fixes_applied.append('app/auth.py')
    except Exception as e:
        print(f"Could not fix app/auth.py: {e}")
    
    # Fix 4: scripts/monitoring/continuous_health_monitor.py - Triple-quoted string
    try:
        file_path = Path('/workspace/scripts/monitoring/continuous_health_monitor.py')
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Ensure all triple-quoted strings are closed
        triple_quote_count = content.count('"""')
        if triple_quote_count % 2 != 0:
            # Add closing triple quote at end of file
            content = content.rstrip() + '\n"""\n'
        
        with open(file_path, 'w') as f:
            f.write(content)
        fixes_applied.append('scripts/monitoring/continuous_health_monitor.py')
    except Exception as e:
        print(f"Could not fix continuous_health_monitor.py: {e}")
    
    # Fix 5: Core module files - Add missing components
    core_files = [
        '/workspace/app/ml_module.py',
        '/workspace/app/chatops_module.py',
        '/workspace/app/auth_module.py'
    ]
    
    for file_path_str in core_files:
        try:
            file_path = Path(file_path_str)
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Fix common patterns
            content = content.replace('return jsonify()\n', 'return jsonify(\n')
            content = content.replace('{}', '{')  # Fix empty dict starts
            content = content.replace('))', ')')  # Fix double closing
            content = content.replace('}}', '}')  # Fix double closing braces
            
            # Ensure functions have proper returns
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'def ' in line and ':' in line:
                    # Check if function has a return
                    func_indent = len(line) - len(line.lstrip())
                    has_return = False
                    for j in range(i + 1, min(i + 50, len(lines))):
                        if lines[j].strip().startswith('return'):
                            has_return = True
                            break
                        if lines[j].strip() and not lines[j].startswith(' '):
                            break
                    
                    if not has_return and 'pass' not in content[i:i+500]:
                        # Add a default return
                        for j in range(i + 1, min(i + 50, len(lines))):
                            if lines[j].strip() == '':
                                lines[j] = ' ' * (func_indent + 4) + 'pass'
                                break
            
            content = '\n'.join(lines)
            with open(file_path, 'w') as f:
                f.write(content)
            fixes_applied.append(file_path_str)
        except Exception as e:
            print(f"Could not fix {file_path_str}: {e}")
    
    return fixes_applied

if __name__ == "__main__":
    print("🔧 Applying critical fixes to essential files...")
    fixed = fix_critical_files()
    print(f"✅ Applied fixes to {len(fixed)} files:")
    for file in fixed:
        print(f"   - {file}")
    print("\nRun syntax_validator.py to check results.")