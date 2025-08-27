#!/usr/bin/env python3
"""
Comprehensive Syntax Fixes Script
Fixes common syntax errors introduced during automated formatting
"""

import os
import re
import sys
from pathlib import Path


def fix_syntax_errors():
    """Fix common syntax errors in all Python files."""""
    project_root = Path("/home/reddy/Desktop/CloudOps")
    app_dir = project_root / "app"
    
    fixes_applied = 0
    files_processed = 0
    
    # Common syntax error patterns and their fixes
    patterns = [
        # Blueprint definitions missing commas
        (r'Blueprint\("(\w+)"\s+__name__,', r'Blueprint("\1", __name__,'),
        
        # Missing commas in function parameters 
        (r'(\w+):\s*str\s*=\s*"([^"]*)"(\s+)(\w+)', r'\1: str = "\2",\3\4'),
        
        # Missing closing quotes and commas
        (r'(".*?)"(\s+)(\w+)', r'"\1",\2\3'),
        
        # Fix ContextVar definitions
        (r'ContextVar\("([^"]*)"(\s+)default=', r'ContextVar("\1",\2default='),
        
        # Fix function definitions missing colons
        (r'def (\w+)\(([^)]*)\)(\s*):(\s*)(\w+)', r'def \1(\2):\4return \5'),
        
        # Fix missing commas in boto3 client calls
        (r'boto3\.client\("(\w+)"(\s+)region_name=', r'boto3.client("\1",\2region_name='),
        
        # Fix missing commas in Gauge definitions
        (r'Gauge\("([^"]*)"(\s+)"([^"]*)"(\s+)registry=', r'Gauge("\1",\2"\3",\4registry='),
        
        # Fix missing commas in dictionary items
        (r'(\w+):\s*(\w+)(\s+)(\w+):', r'\1: \2,\3\4:'),
        
        # Fix list syntax errors
        (r'\[(\s*)\](\s*),(\s*)(\w+)', r'[\1],\3\4'),
        
        # Fix function parameters with missing commas
        (r'(\w+):\s*bool\s*=\s*(True|False)(\s+)(\w+)', r'\1: bool = \2,\3\4'),
        
        # Fix open() calls missing commas
        (r'open\(([^,]+),\s*"([^"]*)"(\s+)as\s+', r'open(\1, "\2") as '),
        
        # Fix severity checks
        (r'\.get\("(\w+)"(\s+)not\s+in\s+', r'.get("\1") not in '),
        
        # Fix default parameters
        (r'(\w+):\s*str\s*=\s*"([^"]*)"(\s*)\):', r'\1: str = "\2"\3):'),
        
        # Fix hasattr calls
        (r'hasattr\(([^,]+),\s*"([^"]*)"(\s*):', r'hasattr(\1, "\2"):'),
        
        # Fix if conditions
        (r'if\s+(\w+):\s*(\w+)', r'if \1:\n        \2'),
        
        # Fix missing commas in timedelta
        (r'timedelta\(hours=\d+\)(\s+)(\w+)', r'timedelta(hours=1)\n    \2'),
        
        # Fix missing commas in lists
        (r'"([^"]*)"(\s+)"([^"]*)"', r'"\1",\2"\3"'),
        
        # Fix model registry default path
        (r'"(ml_models/\w+)"(\s*)(\w+)', r'"\1",\2\3'),
        
        # Fix return values
        (r'return\s+(\w+)(\s+)(\w+)', r'return \1\n        \3'),
    ]
    
    for py_file in app_dir.rglob("*.py"):
        files_processed += 1
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply regex patterns
            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)
            
            # Manual fixes for specific known issues
            specific_fixes = [
                # Fix Blueprint definitions
                ('Blueprint("auth" __name__', 'Blueprint("auth", __name__'),
                ('Blueprint("ml" __name__', 'Blueprint("ml", __name__'),
                ('Blueprint("ai" __name__', 'Blueprint("ai", __name__'),
                ('Blueprint("chatops" __name__', 'Blueprint("chatops", __name__'),
                ('Blueprint("monitoring" __name__', 'Blueprint("monitoring", __name__'),
                ('Blueprint("remediation" __name__', 'Blueprint("remediation", __name__'),
                ('Blueprint("anomalies" __name__', 'Blueprint("anomalies", __name__'),
                ('Blueprint("feedback" __name__', 'Blueprint("feedback", __name__'),
                
                # Fix parameter missing commas
                ('algorithm="HS256":', 'algorithm="HS256"):'),
                ('default=True)', 'default=True'),
                ('], ', '],'),
                
                # Fix missing closing parentheses  
                ('with open(env_path, "r" as f:', 'with open(env_path, "r") as f:'),
                ('if database_url:', 'if database_url is not None:'),
                ('def health():', '@app.route("/health")\ndef health():'),
                
                # Fix specific syntax issues
                ('self.client = None', 'self.client = None'),
                ('result = func(*args, **kwargs)', 'result = func(*args, **kwargs)'),
                ('self.similarity_matrix = None', 'self.similarity_matrix = None'),
                ('except ImportError as e:', 'except ImportError as e:'),
                ('return True', 'return True'),
                
                # Fix missing quotes in path parameters
                ('"ml_models/datasets":', '"ml_models/datasets"):'),
                ('"mlops/data":', '"mlops/data"):'),
                ('"ml_models/monitoring" model_registry=None):', '"ml_models/monitoring", model_registry=None):'),
                ('0), [0, 50, 80, 100]', '0), [0, 50, 80, 100])'),
                
                # Fix tags and other list issues
                ('"smartcloudops" "overview"', '"smartcloudops", "overview"'),
                ('"ml_models/reproducibility":', '"ml_models/reproducibility"):'),
                ('"correlation_id" default=None)', '"correlation_id", default=None)'),
                ('"ml_models/experiments":', '"ml_models/experiments"):'),
                
                # Fix various missing commas and syntax
                ('if anomaly_info.get("severity" not in', 'if anomaly_info.get("severity") not in'),
                ('model_registry=None,', 'model_registry=None,'),
                ('def metrics_endpoint():', 'def metrics_endpoint():'),
                ('"ml_models/registry":', '"ml_models/registry"):'),
                ('boto3.client("ssm" region_name=', 'boto3.client("ssm", region_name='),
                ('is_active = Column(Boolean, default=True)', 'is_active = Column(Boolean, default=True)'),
                ('if hasattr(self.config, "MAX_ACTIONS_PER_HOUR":', 'if hasattr(self.config, "MAX_ACTIONS_PER_HOUR"):'),
                ('self.admin_emails = self._load_admin_emails()', 'self.admin_emails = self._load_admin_emails()'),
                
                # Fix more specific issues
                ('JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)', 'JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)'),
                ('service_version: str = "3.3.0"', 'service_version: str = "3.3.0"'),
                ('"active_users_total" "Number of active users" registry=registry', '"active_users_total", "Number of active users", registry=registry'),
                ('self.secrets_client = None', 'self.secrets_client = None'),
                ('"default" -> str:', '"default") -> str:'),
                ('"ssm" region_name=os.getenv("AWS_REGION" "ap-south-1"', '"ssm", region_name=os.getenv("AWS_REGION", "ap-south-1")'),
                ('include_traceback: bool = True,', 'include_traceback: bool = True,'),
                ('if forwarded_for:', 'if forwarded_for:'),
                ('def record_request(', 'def record_request('),
                ('if not isinstance(value, str):', 'if not isinstance(value, str):'),
            ]
            
            for old, new in specific_fixes:
                if old in content:
                    content = content.replace(old, new)
            
            # Line-by-line fixes for complex issues
            lines = content.split('\n')
            fixed_lines = []
            
            for i, line in enumerate(lines):
                fixed_line = line
                
                # Fix missing commas in function calls
                if re.search(r'\w+\([^)]*"[^"]*"\s+[^)]+\)', line):
                    fixed_line = re.sub(r'("[^"]*")(\s+)([^,\s)][^)]*\))', r'\1,\2\3', line)
                
                # Fix obvious syntax issues
                if line.strip().endswith('":') and not line.strip().startswith('#'):
                    fixed_line = line.replace('":', '"):')
                
                fixed_lines.append(fixed_line)
            
            content = '\n'.join(fixed_lines)
            
            if content != original_content:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixes_applied += 1
                print(f"✅ Fixed syntax errors in {py_file.name}")
                
        except Exception as e:
            print(f"❌ Error processing {py_file}: {e}")
    
    print(f"\n🎉 Syntax error fixes completed!")
    print(f"📁 Files processed: {files_processed}")
    print(f"🔧 Files fixed: {fixes_applied}")


if __name__ == "__main__":
    fix_syntax_errors()