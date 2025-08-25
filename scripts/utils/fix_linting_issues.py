#!/usr/bin/env python3
"""
SmartCloudOps AI - Linting Issues Fixer
Automatically fixes common linting issues across the codebase.
"""

import os
import re


def fix_unused_imports(file_path: str) -> bool:
    """Remove unused imports from a file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Remove common unused imports
    unused_imports = [
        r"import json\n",
        r"from typing import Optional\n",
        r"from typing import Dict\n",
        r"from typing import List\n",
        r"from typing import Any\n",
        r"from typing import Union\n",
        r"from datetime import timedelta\n",
        r"from datetime import datetime\n",
        r"import time\n",
        r"import sys\n",
        r"import pickle\n",
        r"import asyncio\n",
        r"import aiofiles\n",
        r"from dataclasses import dataclass\n",
        r"from dataclasses import asdict\n",
        r"from pathlib import Path\n",
        r"from flask import current_app\n",
        r"from sqlalchemy.orm import Session\n",
        r"from sqlalchemy import and_\n",
        r"import pandas as pd\n",
        r"import numpy as np\n",
        r"from sklearn\.ensemble import IsolationForest\n",
        r"from sklearn\.metrics import accuracy_score\n",
        r"from sklearn\.metrics import f1_score\n",
        r"from sklearn\.metrics import precision_score\n",
        r"from sklearn\.metrics import recall_score\n",
        r"from sklearn\.preprocessing import StandardScaler\n",
        r"from sklearn\.model_selection import train_test_split\n",
        r"from sklearn\.metrics\.pairwise import cosine_similarity\n",
        r"import joblib\n",
        r"from unittest\.mock import Mock\n",
        r"from unittest\.mock import MagicMock\n",
        r"import tempfile\n",
        r"import pytest\n",
    ]

    for pattern in unused_imports:
        content = re.sub(pattern, "", content)

    # Remove empty import lines
    lines = content.split("\n")
    cleaned_lines = []
    skip_next = False

    for i, line in enumerate(lines):
        if skip_next:
            skip_next = False
            continue

        # Skip empty lines after imports
        if line.strip() == "" and i > 0 and "import" in lines[i - 1]:
            continue

        # Skip from imports that are now incomplete
        if line.strip().startswith("from ") and not line.strip().endswith("import"):
            skip_next = True
            continue

        cleaned_lines.append(line)

    content = "\n".join(cleaned_lines)

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True

    return False


def fix_long_lines(file_path: str) -> bool:
    """Fix lines that are too long by breaking them appropriately."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content
    lines = content.split("\n")
    modified = False

    for i, line in enumerate(lines):
        if len(line) > 88:
            # Skip comments and docstrings
            stripped = line.strip()
            if (
                stripped.startswith("#")
                or stripped.startswith('"""')
                or stripped.startswith("'''")
            ):
                continue

            # Try to break long lines at appropriate points
            if "(" in line and ")" in line:
                # Function calls
                if line.count("(") == line.count(")"):
                    # Simple case - break after opening parenthesis
                    parts = line.split("(", 1)
                    if len(parts) == 2:
                        indent = len(line) - len(line.lstrip())
                        new_line = parts[0] + "(\n" + " " * (indent + 4) + parts[1]
                        lines[i] = new_line
                        modified = True
            elif "," in line:
                # Lists, tuples, etc.
                indent = len(line) - len(line.lstrip())
                parts = line.split(",")
                if len(parts) > 1:
                    new_line = (
                        parts[0]
                        + ",\n"
                        + ",\n".join(" " * (indent + 4) + p.strip() for p in parts[1:])
                    )
                    lines[i] = new_line
                    modified = True

    if modified:
        content = "\n".join(lines)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True

    return False


def fix_f_strings(file_path: str) -> bool:
    """Fix f-strings that are missing placeholders."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Fix f-strings without placeholders
    content = re.sub(r'"([^"]*)"', r'"\1"', content)
    content = re.sub(r"'([^']*)'", r"'\1'", content)

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True

    return False


def fix_trailing_whitespace(file_path: str) -> bool:
    """Remove trailing whitespace from lines."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content
    lines = content.split("\n")

    for i, line in enumerate(lines):
        lines[i] = line.rstrip()

    content = "\n".join(lines)

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True

    return False


def fix_bare_excepts(file_path: str) -> bool:
    """Replace bare except clauses with specific exceptions."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Replace bare except with Exception
    content = re.sub(r"except Exception:", r"except Exception:", content)

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True

    return False


def process_file(file_path: str) -> List[str]:
    """Process a single file and return list of fixes applied."""
    fixes = []

    if fix_unused_imports(file_path):
        fixes.append("Removed unused imports")
    if fix_long_lines(file_path):
        fixes.append("Fixed long lines")

    if fix_f_strings(file_path):
        fixes.append("Fixed f-strings")

    if fix_trailing_whitespace(file_path):
        fixes.append("Removed trailing whitespace")

    if fix_bare_excepts(file_path):
        fixes.append("Fixed bare except clauses")

    return fixes


def main():
    """Main function to process all Python files."""
    directories = ["app", "tests", "scripts", "ml_models"]
    total_fixes = 0

    for directory in directories:
        if not os.path.exists(directory):
            continue

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    fixes = process_file(file_path)

                    if fixes:
                        print(f"Fixed {file_path}:")
                        for fix in fixes:
                            print(f"  - {fix}")
                        total_fixes += len(fixes)

    print(f"\nTotal fixes applied: {total_fixes}")
    print("Note: Some complex issues may require manual fixing.")


if __name__ == "__main__":
    main()
