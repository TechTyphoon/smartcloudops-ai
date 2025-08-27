#!/usr/bin/env python3
"""
Fix Truncated Strings Script
Fixes truncated string literals that were broken during automated formatting
"""

import os
import re
import sys
from pathlib import Path


def fix_truncated_strings():
    """Fix truncated strings in all Python files."""""
    project_root = Path("/home/reddy/Desktop/CloudOps")
    app_dir = project_root / "app"
    
    # Common string truncation patterns and their fixes
    fixes = [
        # app/chatops/ai_handler.py
        {
            'file': 'app/chatops/ai_handler.py',
            'old': '"**Anomaly Detection Rep',
            'new': '"**Anomaly Detection Report**: 🔍 Analysis Complete\\n\\n**Current Status**:\\n- No anomalies detected in the last 24 hours\\n- Model confidence: 96.8%\\n- False positive rate: 2.1%\\n\\n**Monitored Metrics**:\\n- CPU utilization patterns\\n- Memory consumption trends\\n- Disk I/O performance\\n- Network traffic analysis\\n- Application response times\\n\\n**Recommendations**:\\n1. Continue monitoring for pattern changes\\n2. Review historical data for trends\\n3. Consider model retraining in 7 days"'
        },
        # app/main.py
        {
            'file': 'app/main.py', 
            'old': '"AI-powered DevOps platform with anomal',
            'new': '"AI-powered DevOps platform with anomaly detection and automated remediation"'
        },
        # app/api/ml.py
        {
            'file': 'app/api/ml.py',
            'old': 'f"Insufficient training data. Need at least 100 sa',
            'new': 'f"Insufficient training data. Need at least 100 samples, got {len(input_data)}"'
        },
        # app/api/anomalies.py
        {
            'file': 'app/api/anomalies.py',
            'old': 'f"{len(created_anomalies)} anomalies created succe',
            'new': 'f"{len(created_anomalies)} anomalies created successfully"'
        },
        # app/api/remediation.py
        {
            'file': 'app/api/remediation.py',
            'old': 'f"{len(created_actions)} remediation actions creat',
            'new': 'f"{len(created_actions)} remediation actions created successfully"'
        }
    ]
    
    # Apply fixes
    fixed_files = []
    
    for fix in fixes:
        file_path = project_root / fix['file']
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if fix['old'] in content:
                    content = content.replace(fix['old'], fix['new'])
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    fixed_files.append(str(file_path))
                    print(f"✅ Fixed truncated string in {fix['file']}")
                
            except Exception as e:
                print(f"❌ Error fixing {fix['file']}: {e}")
    
    # Generic fix for remaining truncated strings
    generic_fixes_applied = 0
    
    for py_file in app_dir.rglob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix common truncation patterns
            # Pattern: strings ending with incomplete words followed by quote
            patterns = [
                (r'"([^"]*\w)\s*"(\s*\+|\s*,|\s*\))', r'"\1"'),  # Remove trailing spaces before quote
                (r'f"([^"]*)\s+"', r'f"\1"'),  # Fix f-strings with trailing spaces
            ]
            
            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)
            
            # Fix obvious truncations (strings ending abruptly)
            lines = content.split('\n')
            fixed_lines = []
            
            for i, line in enumerate(lines):
                # Look for obviously truncated strings
                if (line.strip().endswith('"') and 
                    len(line.strip()) > 50 and
                    line.count('"') % 2 == 0 and
                    not line.strip().endswith('",') and
                    not line.strip().endswith('")') and
                    not line.strip().endswith('")')):
                    
                    # This might be a truncated string, add proper ending
                    if '"message"' in line or '"description"' in line:
                        line = line.rstrip() + '"'
                
                fixed_lines.append(line)
            
            content = '\n'.join(fixed_lines)
            
            if content != original_content:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                generic_fixes_applied += 1
                print(f"✅ Applied generic fixes to {py_file.name}")
                
        except Exception as e:
            print(f"❌ Error processing {py_file}: {e}")
    
    print(f"\n🎉 Truncated string fixes completed!")
    print(f"📁 Specific fixes: {len(fixed_files)} files")
    print(f"🔧 Generic fixes: {generic_fixes_applied} files")


if __name__ == "__main__":
    fix_truncated_strings()
