#!/usr/bin/env python3
"""
Track progress of syntax fixes
"""

import os
import json
from datetime import datetime

def test_file(filepath):
    """Test if a Python file has syntax errors."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        compile(source, filepath, 'exec')
        return True, "No errors"
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)

# Critical files to fix (from git status)
critical_files = [
    "/workspace/app/api/ai.py",  # ✅ FIXED
    "/workspace/app/api/performance.py",  # ✅ FIXED
    "/workspace/app/api/ml.py",  
    "/workspace/app/mlops/dataset_manager.py",
    "/workspace/app/mlops/experiment_tracker_minimal.py",
    "/workspace/app/mlops/model_monitor.py",
    "/workspace/app/mlops/model_registry.py",
    "/workspace/app/mlops/reinforcement_learning.py",
    "/workspace/app/mlops/training_pipeline.py",
    "/workspace/app/security/caching.py",
    "/workspace/app/security/config.py",
    "/workspace/app/security/input_validation.py",
    "/workspace/app/security/secrets_manager.py",
    "/workspace/app/services/remediation_service.py",
    "/workspace/app/services/security_validation.py",
]

print("=" * 60)
print("SYNTAX FIX PROGRESS TRACKER")
print("=" * 60)

fixed_count = 0
remaining_errors = []

for filepath in critical_files:
    if os.path.exists(filepath):
        is_ok, error_msg = test_file(filepath)
        rel_path = filepath.replace("/workspace/", "")
        if is_ok:
            print(f"✅ {rel_path}: FIXED")
            fixed_count += 1
        else:
            print(f"❌ {rel_path}: {error_msg}")
            remaining_errors.append((rel_path, error_msg))
    else:
        print(f"⚠️  {filepath}: File not found")

print("\n" + "=" * 60)
print(f"Progress: {fixed_count}/{len(critical_files)} files fixed")
print(f"Remaining: {len(remaining_errors)} files with errors")

if remaining_errors:
    print("\nFiles still needing fixes:")
    for filepath, error in remaining_errors:
        print(f"  - {filepath}: {error}")

# Save progress
progress_data = {
    "timestamp": datetime.now().isoformat(),
    "total_files": len(critical_files),
    "fixed_files": fixed_count,
    "remaining_files": len(remaining_errors),
    "details": remaining_errors
}

with open("/workspace/fix_progress.json", "w") as f:
    json.dump(progress_data, f, indent=2)

print("\n📊 Progress saved to /workspace/fix_progress.json")