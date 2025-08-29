#!/usr/bin/env python3
"""
Comprehensive Syntax Error Fixer for SmartCloudOps.AI
This script systematically fixes all syntax errors in the codebase.
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
import ast
import subprocess

class SyntaxErrorFixer:
    def __init__(self):
        self.fixed_files = []
        self.failed_files = []
        self.backup_dir = f"syntax_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def create_backup(self, file_path):
        """Create backup of file before fixing"""
        backup_path = Path(self.backup_dir) / Path(file_path).relative_to('.')
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup_path)
        
    def verify_syntax(self, file_path):
        """Verify if a Python file has valid syntax"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                compile(f.read(), file_path, 'exec')
            return True
        except SyntaxError as e:
            return False
            
    def fix_file(self, file_path):
        """Fix syntax errors in a single file"""
        print(f"🔧 Fixing: {file_path}")
        
        # Create backup
        self.create_backup(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # Fix common patterns
            content = self.fix_indentation_errors(content)
            content = self.fix_docstring_placement(content)
            content = self.fix_missing_parentheses(content)
            content = self.fix_unterminated_strings(content)
            content = self.fix_import_statements(content)
            content = self.fix_function_calls(content)
            content = self.fix_path_operations(content)
            content = self.fix_logging_statements(content)
            content = self.fix_missing_colons(content)
            content = self.fix_dictionary_errors(content)
            
            # Write fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            # Verify the fix
            if self.verify_syntax(file_path):
                self.fixed_files.append(file_path)
                print(f"✅ Fixed: {file_path}")
                return True
            else:
                # Restore original if verification fails
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                self.failed_files.append(file_path)
                print(f"❌ Failed to fix: {file_path}")
                return False
                
        except Exception as e:
            print(f"❌ Error fixing {file_path}: {e}")
            self.failed_files.append(file_path)
            return False
            
    def fix_indentation_errors(self, content):
        """Fix indentation errors in docstrings and code blocks"""
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Fix indented module docstrings
            if i < 10 and line.strip().startswith('"""') and line.startswith('    '):
                fixed_lines.append(line.lstrip())
            # Fix incorrectly indented logging.basicConfig
            elif 'logging.basicConfig(' in line and line.startswith('logging.basicConfig('):
                # Ensure proper formatting for logging.basicConfig
                if i + 1 < len(lines) and lines[i + 1].strip().startswith('level='):
                    fixed_lines.append('logging.basicConfig(')
            elif i > 0 and 'level=' in line and 'logging.basicConfig' in lines[i-1]:
                fixed_lines.append('    ' + line.strip())
            else:
                fixed_lines.append(line)
                
        return '\n'.join(fixed_lines)
        
    def fix_docstring_placement(self, content):
        """Fix docstrings that appear after imports"""
        lines = content.split('\n')
        
        # Check if docstring is misplaced (after imports)
        import_line = -1
        docstring_start = -1
        
        for i, line in enumerate(lines):
            if line.strip().startswith('from ') or line.strip().startswith('import '):
                import_line = i
            if '"""' in line and docstring_start == -1:
                docstring_start = i
                break
                
        if import_line >= 0 and docstring_start > import_line:
            # Find docstring end
            docstring_end = docstring_start
            for i in range(docstring_start + 1, len(lines)):
                if '"""' in lines[i]:
                    docstring_end = i
                    break
                    
            # Move docstring before imports
            docstring_lines = lines[docstring_start:docstring_end + 1]
            # Remove docstring from current position
            for i in range(docstring_end, docstring_start - 1, -1):
                lines.pop(i)
            
            # Find first import
            first_import = -1
            for i, line in enumerate(lines):
                if line.strip().startswith('from ') or line.strip().startswith('import '):
                    first_import = i
                    break
                    
            # Insert docstring before first import
            if first_import >= 0:
                for doc_line in reversed(docstring_lines):
                    lines.insert(first_import, doc_line)
                    
        return '\n'.join(lines)
        
    def fix_missing_parentheses(self, content):
        """Fix missing parentheses in function calls and definitions"""
        # Fix Path.parent -> Path(__file__).parent
        content = re.sub(r'Path\.parent', r'Path(__file__).parent', content)
        
        # Fix create_app without parentheses
        content = re.sub(r'app = create_app\s*$', r'app = create_app()', content, flags=re.MULTILINE)
        
        # Fix main without parentheses at the end
        content = re.sub(r'if __name__ == "__main__":\s*main\s*$', 
                         r'if __name__ == "__main__":\n    main()', 
                         content, flags=re.MULTILINE)
        
        # Fix missing closing parentheses for int(os.getenv())
        content = re.sub(r'port = int\(os\.getenv\("PORT", 5000\)\s*$', 
                         r'port = int(os.getenv("PORT", 5000))', 
                         content, flags=re.MULTILINE)
        
        # Fix missing closing parentheses in conditionals
        content = re.sub(r'if _check_performance_available\(:$', 
                         r'if _check_performance_available():', 
                         content, flags=re.MULTILINE)
        
        return content
        
    def fix_unterminated_strings(self, content):
        """Fix unterminated string literals and f-strings"""
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Fix f-strings that are split across lines
            if 'f"' in line and line.count('"') % 2 != 0:
                # Check if it's a continuation
                if '(' in line and ')' not in line:
                    # Likely a function call split across lines
                    line = line.rstrip() + '")'
            
            # Fix unterminated strings in prints/logs
            if line.strip().startswith('print(') or 'logger.' in line:
                # Count quotes
                single_quotes = line.count("'")
                double_quotes = line.count('"')
                
                # Fix unmatched quotes
                if single_quotes % 2 != 0:
                    line = line.rstrip() + "'"
                elif double_quotes % 2 != 0:
                    line = line.rstrip() + '"'
                    
            fixed_lines.append(line)
            
        return '\n'.join(fixed_lines)
        
    def fix_import_statements(self, content):
        """Fix split import statements"""
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Fix split imports
            if 'from app.performance.api_optimization import (' in line:
                if i + 1 < len(lines) and 'shutdown_performance_monitoring' in lines[i + 1]:
                    fixed_lines.append('                from app.performance.api_optimization import shutdown_performance_monitoring')
                    i += 2
                    continue
                    
            fixed_lines.append(line)
            i += 1
            
        return '\n'.join(fixed_lines)
        
    def fix_function_calls(self, content):
        """Fix function calls split across lines"""
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Fix logger.info() split across lines
            if 'logger.info()' in line and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line.startswith('f"'):
                    fixed_lines.append(line.replace('logger.info()', f'logger.info({next_line})'))
                    i += 2
                    continue
                    
            # Fix sys.path.insert with missing parenthesis
            if 'sys.path.insert(0, str(current_dir)' in line and ')' not in line:
                line = line.rstrip() + ')'
                
            fixed_lines.append(line)
            i += 1
            
        return '\n'.join(fixed_lines)
        
    def fix_path_operations(self, content):
        """Fix Path operations"""
        # Fix Path.parent to Path(__file__).parent
        content = re.sub(r'current_dir = Path\.parent', 
                         r'current_dir = Path(__file__).parent', 
                         content)
        return content
        
    def fix_logging_statements(self, content):
        """Fix logging.basicConfig and logger statements"""
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Fix logging.basicConfig() without arguments
            if line.strip() == 'logging.basicConfig()':
                # Check if next lines contain the config
                if i + 1 < len(lines) and 'level=' in lines[i + 1]:
                    # Merge the configuration
                    config_lines = []
                    j = i + 1
                    while j < len(lines) and (lines[j].strip().startswith('level=') or 
                                              lines[j].strip().startswith('format=') or 
                                              lines[j].strip().startswith('handlers=')):
                        config_lines.append(lines[j].strip())
                        j += 1
                        
                    if config_lines:
                        config_str = ', '.join(config_lines)
                        # Remove the trailing parenthesis and bracket if they exist
                        config_str = config_str.rstrip(')')
                        fixed_lines.append(f'logging.basicConfig({config_str})')
                        i = j
                        continue
                        
            fixed_lines.append(line)
            i += 1
            
        return '\n'.join(fixed_lines)
        
    def fix_missing_colons(self, content):
        """Fix missing colons in conditionals and function definitions"""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Fix if statements without colons
            if re.match(r'^\s*if .+\)\s*$', line) and ':' not in line:
                line = line.rstrip() + ':'
            # Fix function definitions without colons
            elif re.match(r'^\s*def .+\)\s*$', line) and ':' not in line:
                line = line.rstrip() + ':'
                
            fixed_lines.append(line)
            
        return '\n'.join(fixed_lines)
        
    def fix_dictionary_errors(self, content):
        """Fix dictionary and tuple syntax errors"""
        # Fix mismatched brackets/parentheses in dictionaries
        content = re.sub(r'}\)', '}', content)
        content = re.sub(r'\(}', '}', content)
        
        return content
        
    def fix_all_files(self, file_list):
        """Fix all files in the list"""
        print(f"🚀 Starting to fix {len(file_list)} files...")
        print(f"📁 Creating backup in: {self.backup_dir}")
        
        for file_path in file_list:
            if os.path.exists(file_path):
                self.fix_file(file_path)
                
        print(f"\n📊 Summary:")
        print(f"✅ Successfully fixed: {len(self.fixed_files)} files")
        print(f"❌ Failed to fix: {len(self.failed_files)} files")
        
        return self.fixed_files, self.failed_files


def main():
    """Main execution function"""
    # List of all files with syntax errors
    files_to_fix = [
        "app/main.py",
        "app/auth.py",
        "app/auth_routes.py",
        "app/auth_module.py",
        
        # API files
        "app/api/ai.py",
        "app/api/anomalies_refactored.py",
        "app/api/mlops.py",
        "app/api/performance.py",
        
        # ChatOps
        "app/chatops/ai_handler.py",
        "app/chatops/gpt_handler.py",
        "app/chatops/utils.py",
        "app/chatops_module.py",
        
        # Services
        "app/services/ml_service.py",
        "app/services/mlops_service.py",
        "app/services/ai_service.py",
        "app/services/anomaly_service.py",
        "app/services/feedback_service.py",
        "app/services/remediation_service.py",
        "app/services/security_validation.py",
        
        # MLOps
        "app/mlops/autonomous_ops.py",
        "app/mlops/data_pipeline.py",
        "app/mlops/data_pipeline_enhanced.py",
        "app/mlops/dataset_manager.py",
        "app/mlops/experiment_tracker.py",
        "app/mlops/experiment_tracker_minimal.py",
        "app/mlops/knowledge_base.py",
        "app/mlops/model_monitor.py",
        "app/mlops/model_registry.py",
        "app/mlops/model_registry_minimal.py",
        "app/mlops/reinforcement_learning.py",
        "app/mlops/reproducibility.py",
        "app/mlops/training_pipeline.py",
        
        # Observability
        "app/observability/__init__.py",
        "app/observability/dashboards.py",
        "app/observability/enhanced_logging.py",
        "app/observability/logging_config.py",
        "app/observability/metrics.py",
        "app/observability/middleware.py",
        "app/observability/opentelemetry_config.py",
        "app/observability/slos.py",
        "app/observability/tracing.py",
        
        # Performance
        "app/performance/__init__.py",
        "app/performance/anomaly_optimization.py",
        "app/performance/api_optimization.py",
        "app/performance/caching.py",
        "app/performance/database_optimization.py",
        "app/performance/log_optimization.py",
        "app/performance/redis_cache.py",
        
        # Security
        "app/security/caching.py",
        "app/security/config.py",
        "app/security/error_handling.py",
        "app/security/input_validation.py",
        "app/security/rate_limiting.py",
        "app/security/secrets_manager.py",
        
        # Remediation
        "app/remediation/__init__.py",
        "app/remediation/actions.py",
        "app/remediation/engine.py",
        "app/remediation/notifications.py",
        "app/remediation/safety.py",
        
        # Other app files
        "app/ml_module.py",
        "app/monitoring/metrics.py",
        "app/analytics/real_time_dashboard.py",
        
        # ML Models
        "ml_models/model_versioning.py",
        
        # Scripts
        "scripts/monitoring/continuous_health_monitor.py",
        "scripts/monitoring/real_system_monitor.py",
        "scripts/monitoring/uptime_monitor.py",
        "scripts/security/validate_secrets.py",
        "scripts/testing/health_check.py",
        "scripts/testing/production_validation.py",
        
        # Tests
        "tests/test_integration.py",
        "tests/test_ml_anomaly_detection.py",
        "tests/test_chatops.py",
        "tests/test_remediation.py",
        "tests/test_ml_endpoints.py",
        "tests/test_ai_handler.py",
        "tests/test_gpt_integration.py",
        "tests/backend/test_chatops.py",
        "tests/unit/test_ml_models.py",
        "tests/unit/test_remediation_engine.py",
        "tests/integration/test_api_endpoints.py",
    ]
    
    fixer = SyntaxErrorFixer()
    fixed, failed = fixer.fix_all_files(files_to_fix)
    
    # Create a detailed report
    with open("syntax_fix_report.json", "w") as f:
        import json
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_files": len(files_to_fix),
            "fixed_files": fixed,
            "failed_files": failed,
            "backup_location": fixer.backup_dir
        }, f, indent=2)
        
    print(f"\n📄 Report saved to: syntax_fix_report.json")
    print(f"💾 Backups saved to: {fixer.backup_dir}")
    
    # Verify all fixes
    print("\n🔍 Verifying all Python files...")
    verification_failed = []
    for file_path in fixed:
        result = subprocess.run(['python3', '-m', 'py_compile', file_path], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            verification_failed.append(file_path)
            
    if verification_failed:
        print(f"⚠️  {len(verification_failed)} files still have syntax errors after fixing")
        for file in verification_failed:
            print(f"  - {file}")
    else:
        print("✅ All fixed files have valid syntax!")
        
    return len(failed) == 0 and len(verification_failed) == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)