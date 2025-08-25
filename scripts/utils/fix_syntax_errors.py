#!/usr/bin/env python3
"""
SmartCloudOps AI - Syntax Error Fixer
Fixes syntax errors introduced by the linting fix script.
"""

import os
import re
from typing import List


def fix_broken_f_strings(file_path: str) -> bool:
    """Fix broken f-strings that were incorrectly modified."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix common patterns that were broken
    fixes = [
        # Fix broken f-string patterns
        (rf'"([^f"]*)\{([^}]*)\}([^"]*)"', rf'ff"\1{\2}\3"'),
        (rf"'([^f']*)\{([^}]*)\}([^']*)'", rf"ff'\1{\2}\3'"),
        
        # Fix specific broken patterns
        (rf'f"Warning: \{key\} in \.env file is too short \("', rf'fff"Warning: {key} in .env file is too short ("'),
        (rf'f"Insufficient training data\. Need at least 100 samples, got \{len\("', r'ff"Insufficient training data. Need at least 100 samples, got {len("'),
        (r'"\{len\("', r'ff"{len("'),
        (r'"authentication": "All endpoints except /api/feedback/ \("', r'ff"authentication": "All endpoints except /api/feedback/ ("'),
        (r'"Executed remediation \{remediation\.id\}: \{remediation\.action_type\} \("', rf'fff"Executed remediation {remediation.id}: {remediation.action_type} ("'),
        (rf'f"Added experience: \{anomaly_info\.get\("', r'ff"Added experience: {anomaly_info.get("'),
        (r'"deploy_\{version_id\}_\{environment\}_\{datetime\.now\("', rf'fff"deploy_{version_id}_{environment}_{datetime.now("'),
        (r'"explanation": "Critical CPU usage at \{cpu_usage\}% \("', rf'f"explanation": f"Critical CPU usage at {cpu_usage}% ("'),
        (rf'f"   Anomalies detected: \{sum\("', r'ff"   Anomalies detected: {sum("'),
        (r'"  Memory Usage: \{real_metrics\[\'memory\'\]\[\'usage_percent\'\]\}% \("', rf'ff"  Memory Usage: {real_metrics[\'memory\'][\'usage_percent\']}% ("'),
        (rf'f"🏥 Health Status: \{sum\("', r'ff"🏥 Health Status: {sum("'),
        (r'"Flask endpoints failed: health=\{health_response\.status_code\},"', rf'fff"Flask endpoints failed: health={health_response.status_code},"'),
        (rf'f"✅ \{endpoint\} - \{result\[\'status_code\'\]\} \("', rf'ff"✅ {endpoint} - {result[\'status_code\']} ("'),
        (r'"   smartcloudops-main Up 45 minutes \("', r'ff"   smartcloudops-main Up 45 minutes ("'),
        (rf'f"Too many requests\. Limit: \{result\[\'limits\'\]\},"', rf'ff"Too many requests. Limit: {result[\'limits\']},"'),
        (r'f"Request: \{error_record\[\'request_info\'\]\.get\("', r'f"Request: {error_record[\'request_info\'].get("'),
    ]
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False


def fix_import_statements(file_path: str) -> bool:
    """Fix broken import statements."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix common import issues
    fixes = [
        # Fix broken imports
        (r'from sqlalchemy import Boolean', r'from sqlalchemy import Boolean'),
        (r'from prometheus_client import CollectorRegistry', r'from prometheus_client import CollectorRegistry'),
        (r'from app\.chatops\.ai_handler import FlexibleAIHandler,', r'from app.chatops.ai_handler import FlexibleAIHandler'),
        (r'from app\.security\.input_validation import sanitize_log_message,', r'from app.security.input_validation import sanitize_log_message'),
        (r'from ml_models\.anomaly_detector import AnomalyInferenceEngine,', r'from ml_models.anomaly_detector import AnomalyInferenceEngine'),
        (r'from app\.chatops\.utils import LogRetriever,', r'from app.chatops.utils import LogRetriever'),
        (r'from app\.chatops\.utils import SystemContextGatherer,', r'from app.chatops.utils import SystemContextGatherer'),
    ]
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False


def fix_indentation_issues(file_path: str) -> bool:
    """Fix indentation issues."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix common indentation issues
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Fix specific indentation issues
        if line.strip().startswith('auth_manager,'):
            # This should be properly indented
            fixed_lines.append('    auth_manager,')
        else:
            fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False


def process_file(file_path: str) -> List[str]:
    """Process a single file and return list of fixes applied."""
    fixes = []
    
    if fix_broken_f_strings(file_path):
        fixes.append("Fixed broken f-strings")
    
    if fix_import_statements(file_path):
        fixes.append("Fixed import statements")
    
    if fix_indentation_issues(file_path):
        fixes.append("Fixed indentation issues")
    
    return fixes


def main():
    """Main function to process all Python files."""
    directories = ['app', 'tests', 'scripts', 'ml_models']
    total_fixes = 0
    
    for directory in directories:
        if not os.path.exists(directory):
            continue
            
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    fixes = process_file(file_path)
                    
                    if fixes:
                        print(f"Fixed {file_path}:")
                        for fix in fixes:
                            print(ff"  - {fix}")
                        total_fixes += len(fixes)
    
    print(ff"\nTotal fixes applied: {total_fixes}")


if __name__ == "__main__":
    main()
