#!/usr/bin/env python3
"""Script to verify and list all Python syntax errors in the app directory."""

import ast
import os

def check_syntax_errors():
    """Check for syntax errors in all Python files under app/ directory."""
    errors = []
    file_count = 0
    
    for root, dirs, files in os.walk('app'):
        for file in files:
            if file.endswith('.py'):
                file_count += 1
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r') as f:
                        ast.parse(f.read())
                except SyntaxError as e:
                    errors.append(f'{filepath}:{e.lineno}: {e.msg}')
                except Exception as e:
                    errors.append(f'{filepath}: {str(e)}')
    
    print(f'Checked {file_count} Python files')
    print(f'Total syntax errors: {len(errors)}')
    
    if not errors:
        print('✅ SUCCESS! All syntax errors fixed!')
    else:
        print('\n❌ Still have errors to fix:\n')
        # Group errors by type
        docstring_errors = [e for e in errors if 'unterminated string literal' in e]
        bracket_errors = [e for e in errors if 'unmatched' in e or 'bracket' in e.lower()]
        other_errors = [e for e in errors if e not in docstring_errors and e not in bracket_errors]
        
        if docstring_errors:
            print(f'\nDocstring errors ({len(docstring_errors)}):')
            for error in docstring_errors[:10]:
                print(f'  {error}')
            if len(docstring_errors) > 10:
                print(f'  ... and {len(docstring_errors) - 10} more')
        
        if bracket_errors:
            print(f'\nBracket/Parenthesis errors ({len(bracket_errors)}):')
            for error in bracket_errors[:5]:
                print(f'  {error}')
            if len(bracket_errors) > 5:
                print(f'  ... and {len(bracket_errors) - 5} more')
        
        if other_errors:
            print(f'\nOther errors ({len(other_errors)}):')
            for error in other_errors[:5]:
                print(f'  {error}')
            if len(other_errors) > 5:
                print(f'  ... and {len(other_errors) - 5} more')
    
    return errors

if __name__ == '__main__':
    errors = check_syntax_errors()