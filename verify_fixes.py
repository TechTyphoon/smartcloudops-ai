#!/usr/bin/env python3
"""
Verification script to check if all syntax errors are fixed
Run this after Opus makes changes to verify the fixes
"""

import ast
import os
from collections import defaultdict


def check_syntax():
    errors_by_file = defaultdict(list)
    file_count = 0

    for root, dirs, files in os.walk("app"):
        for file in files:
            if file.endswith(".py"):
                file_count += 1
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r") as f:
                        ast.parse(f.read())
                except SyntaxError as e:
                    errors_by_file[filepath].append(f"Line {e.lineno}: {e.msg}")

    total_errors = sum(len(errors) for errors in errors_by_file.values())

    print("=" * 60)
    print("SYNTAX ERROR VERIFICATION REPORT")
    print("=" * 60)
    print(f"Total Python files: {file_count}")
    print(f"Files with syntax errors: {len(errors_by_file)}")
    print(f"Total syntax errors: {total_errors}")
    print()

    if total_errors == 0:
        print("🎉 SUCCESS! All syntax errors have been fixed!")
        print("✅ Your codebase is ready for GitHub push!")
        return True
    else:
        print("❌ Still have syntax errors to fix:")
        print()
        for filepath, errors in sorted(errors_by_file.items()):
            print(f"📁 {filepath}:")
            for error in errors:
                print(f"   ❌ {error}")
            print()

        print(
            f"📊 SUMMARY: {total_errors} errors remaining across {len(errors_by_file)} files"
        )
        return False


if __name__ == "__main__":
    success = check_syntax()
    exit(0 if success else 1)
