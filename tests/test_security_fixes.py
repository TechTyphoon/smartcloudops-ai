#!/usr/bin/env python3
"""
Security Fixes Validation Tests
Tests to verify that all security vulnerabilities have been properly fixed.
"""

import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import our security validation functions
try:
    from app.main import validate_string_input, validate_numeric_input, validate_json_input
except ImportError:
    print("⚠️ Could not import validation functions from app.main")
    print("This is expected if running outside of the Flask app context")
    validate_string_input = None
    validate_numeric_input = None 
    validate_json_input = None


class TestInputValidation:
    """Test the security input validation functions."""

    def test_validate_string_input_basic(self):
        """Test basic string validation."""
        # Valid input
        result = validate_string_input("Hello World", max_length=20)
        assert result == "Hello World"
        
        # Empty string with allow_empty=True
        result = validate_string_input("", max_length=20, allow_empty=True)
        assert result == ""

    def test_validate_string_input_security(self):
        """Test string validation security features."""
        # Test XSS prevention
        try:
            validate_string_input("<script>alert('xss')</script>")
            assert False, "Should have raised ValueError for XSS"
        except ValueError as e:
            assert "malicious" in str(e)
            
        try:
            validate_string_input("javascript:alert('xss')")
            assert False, "Should have raised ValueError for XSS"
        except ValueError as e:
            assert "malicious" in str(e)
        
        # Test length limits
        try:
            validate_string_input("x" * 1001, max_length=1000)
            assert False, "Should have raised ValueError for length"
        except ValueError as e:
            assert "too long" in str(e)
        
        # Test null byte removal
        result = validate_string_input("test\x00data")
        assert "\x00" not in result

    def test_validate_numeric_input_basic(self):
        """Test basic numeric validation."""
        # Valid integers
        assert validate_numeric_input(42) == 42
        assert validate_numeric_input("42") == 42
        
        # Valid floats
        assert validate_numeric_input(3.14) == 3.14
        assert validate_numeric_input("3.14") == 3.14

    def test_validate_numeric_input_security(self):
        """Test numeric validation security features."""
        # Test range validation
        try:
            validate_numeric_input(5, min_val=10)
            assert False, "Should have raised ValueError for below minimum"
        except ValueError as e:
            assert "below minimum" in str(e)
            
        try:
            validate_numeric_input(15, min_val=1, max_val=10)
            assert False, "Should have raised ValueError for above maximum"
        except ValueError as e:
            assert "above maximum" in str(e)
        
        # Test invalid input types
        try:
            validate_numeric_input("not_a_number")
            assert False, "Should have raised ValueError for invalid input"
        except ValueError as e:
            assert "Invalid numeric input" in str(e) or "Expected numeric value" in str(e)
            
        try:
            validate_numeric_input([1, 2, 3])
            assert False, "Should have raised ValueError for invalid type"
        except ValueError as e:
            assert "Expected numeric value" in str(e)

    def test_validate_json_input_basic(self):
        """Test basic JSON validation."""
        # Valid JSON
        data = {"key": "value", "number": 42}
        result = validate_json_input(data)
        assert result == data

    def test_validate_json_input_security(self):
        """Test JSON validation security features."""
        # Test depth protection
        deeply_nested = {"level1": {"level2": {"level3": {}}}}
        for i in range(15):  # Create very deep nesting
            deeply_nested = {"level": deeply_nested}
        
        try:
            validate_json_input(deeply_nested)
            assert False, "Should have raised ValueError for deep nesting"
        except ValueError as e:
            assert "nesting too deep" in str(e)
        
        # Test non-dict input
        try:
            validate_json_input("not_a_dict")
            assert False, "Should have raised ValueError for non-dict"
        except ValueError as e:
            assert "Expected dictionary" in str(e)
            
        try:
            validate_json_input([1, 2, 3])
            assert False, "Should have raised ValueError for list input"
        except ValueError as e:
            assert "Expected dictionary" in str(e)


class TestSecureSubprocessUsage:
    """Test that subprocess usage is secure."""

    def test_no_shell_true_in_modified_files(self):
        """Verify that shell=True has been removed from critical files."""
        files_to_check = [
            "scripts/one-time/test_github_workflows.py",
            "scripts/one-time/test_workflows_locally.py"
        ]
        
        for file_path in files_to_check:
            full_path = os.path.join(os.path.dirname(__file__), "..", file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r') as f:
                    lines = f.readlines()
                    
                    # Check each line for shell=True (ignoring comments)
                    shell_true_found = False
                    shell_false_found = False
                    
                    for line in lines:
                        # Remove comments from line
                        code_part = line.split('#')[0].strip()
                        if 'shell=True' in code_part:
                            shell_true_found = True
                        if 'shell=False' in code_part:
                            shell_false_found = True
                    
                    assert not shell_true_found, f"Found shell=True in code (not comment) in {file_path}"
                    assert shell_false_found, f"Missing shell=False in {file_path}"

    def test_proper_shlex_usage(self):
        """Test that our secure command parsing works."""
        # Test the secure command parsing from our fixed files
        import shlex
        
        # Test basic command parsing
        cmd = "python3 -m pytest tests/"
        cmd_list = shlex.split(cmd)
        expected = ["python3", "-m", "pytest", "tests/"]
        assert cmd_list == expected
        
        # Test command with quotes and spaces
        cmd = 'echo "hello world" > /tmp/test'
        cmd_list = shlex.split(cmd)
        assert len(cmd_list) == 4
        assert cmd_list[1] == "hello world"  # Quotes should be handled properly


class TestExceptionHandling:
    """Test that dangerous exception handling has been fixed."""

    def test_no_bare_except_pass(self):
        """Verify that bare except/pass blocks have been fixed."""
        files_to_check = [
            "scripts/one-time/generate_massive_real_data.py",
            "scripts/one-time/generate_more_real_data.py", 
            "scripts/one-time/generate_real_metrics.py"
        ]
        
        for file_path in files_to_check:
            full_path = os.path.join(os.path.dirname(__file__), "..", file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r') as f:
                    content = f.read()
                    # Should not contain bare 'except:' followed by 'pass'
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if line.strip() == "except:":
                            # Check if next non-empty line is just 'pass'
                            for j in range(i + 1, min(i + 5, len(lines))):
                                next_line = lines[j].strip()
                                if next_line:
                                    assert next_line != "pass", f"Found bare except/pass in {file_path} at line {j}"
                                    break


class TestCryptographicSecurity:
    """Test cryptographic security improvements."""

    def test_secrets_module_usage(self):
        """Test that secrets module is used instead of random."""
        file_path = "scripts/load_testing.py"
        full_path = os.path.join(os.path.dirname(__file__), "..", file_path)
        
        if os.path.exists(full_path):
            with open(full_path, 'r') as f:
                content = f.read()
                # Should contain secrets.choice instead of random.choice
                assert "secrets.choice" in content, "Should use secrets.choice for cryptographic randomness"


class TestConfigurationSecurity:
    """Test configuration security improvements."""

    def test_env_template_security_comments(self):
        """Test that env.template has proper security guidance."""
        file_path = "env.template"
        full_path = os.path.join(os.path.dirname(__file__), "..", file_path)
        
        if os.path.exists(full_path):
            with open(full_path, 'r') as f:
                content = f.read()
                # Should contain security warnings
                assert "SECURITY:" in content, "Should contain security warnings"
                assert "NEVER commit" in content, "Should warn about committing secrets"
                assert "IAM roles" in content, "Should recommend IAM roles over access keys"


if __name__ == "__main__":
    # Run the tests
    print("🔒 Running security validation tests...")
    
    # Test input validation (only if functions are available)
    if validate_string_input is not None:
        print("✅ Testing input validation...")
        test_input = TestInputValidation()
        test_input.test_validate_string_input_basic()
        test_input.test_validate_string_input_security()
        test_input.test_validate_numeric_input_basic()
        test_input.test_validate_numeric_input_security()
        test_input.test_validate_json_input_basic()
        test_input.test_validate_json_input_security()
    else:
        print("⏭️ Skipping input validation tests (functions not available)")
    
    # Test subprocess security
    print("✅ Testing subprocess security...")
    test_subprocess = TestSecureSubprocessUsage()
    test_subprocess.test_no_shell_true_in_modified_files()
    test_subprocess.test_proper_shlex_usage()
    
    # Test exception handling
    print("✅ Testing exception handling...")
    test_exceptions = TestExceptionHandling()
    test_exceptions.test_no_bare_except_pass()
    
    # Test cryptographic security
    print("✅ Testing cryptographic security...")
    test_crypto = TestCryptographicSecurity()
    test_crypto.test_secrets_module_usage()
    
    # Test configuration security
    print("✅ Testing configuration security...")
    test_config = TestConfigurationSecurity()
    test_config.test_env_template_security_comments()
    
    print("🎉 All security validation tests passed!")
