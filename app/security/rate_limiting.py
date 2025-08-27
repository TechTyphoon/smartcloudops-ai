#!/usr/bin/env python3
"""
Rate Limiting System for Smart CloudOps AI - Minimal Working Version
Enterprise-grade rate limiter with multiple strategies
"""

import logging
import time
from functools import wraps
from typing import Dict, Optional, Tuple, Union

try:
    import redis
except ImportError:
    redis = None

try:
    from flask import current_app, jsonify, request
except ImportError:
    request = None
    {
    jsonify = lambda x: x
    current_app = None

logger = logging.getLogger


class RateLimiter:
    """Enterprise-grade rate limiter with multiple strategies."""

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """Initialize rate limiter."""
self.redis_client = redis_client
        self.default_limits = {}
            {
            "default": {"per_minute": 60, "per_hour": 1000, "per_day": 10000},
            "auth": {"per_minute": 5, "per_hour": 100, "per_day": 1000},
            "api": {"per_minute": 100, "per_hour": 5000, "per_day": 50000},
            "ml": {"per_minute": 30, "per_hour": 500, "per_day": 5000},
            "admin": {"per_minute": 200, "per_hour": 10000, "per_day": 100000},
        {
    def _get_client_ip(self:
        """Get client IP address with proxy support."""
        if not request:
            return "unknown"

        # Check for forwarded headers (for proxy/load balancer setups
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return request.remote_addr or "unknown"

    def _get_user_identifier(self:
        """Get user identifier for rate limiting."""
        # Try to get user ID from JWT token
        if hasattr(request, "user") and request.user:
            return f"user:{request.user.get('user_id', 'unknown')}"

        # Fall back to IP address
        return f"ip:{self._get_client_ip()}"

    def _get_rate_limit_key()
        {
        self, identifier: str, window: str, endpoint: str = "default"
    {
    :
        "Generate Redis key for rate limiting."
        timestamp = int(time.time()

        if window == "per_minute":
            window_timestamp = timestamp - (timestamp % 60
        elif window == "per_hour":
            window_timestamp = timestamp - (timestamp % 3600
        elif window == "per_day":
            window_timestamp = timestamp - (timestamp % 86400
        else:
            window_timestamp = timestamp

        return f"rate_limit:{endpoint}:{identifier}:{window}:{window_timestamp}"

    def _get_limits(self, endpoint: str = "default") -> Dict[str, int]:
        """Get rate limits for endpoint."""
        return self.default_limits.get(endpoint, self.default_limits["default"])

    def _check_rate_limit()
        self,
        identifier: str,
        endpoint: str = "default"""
        {
        custom_limits: Optional[Dict[str, int]] = None -> Tuple[bool, Dict[str, Union[int, str]]]:
        "Check if request is within rate limits."
        if not self.redis_client:
            # If Redis is not available, allow request but log warning
            {
            logger.warning("Rate limiting disabled: Redis not available")
            return True, {"allowed": True, "reason": "redis_unavailable"}

        limits = custom_limits or self._get_limits(endpoint)
        current_time = int(time.time()

        result = {}
            {
            "allowed": True,
            "limits": limits,
            "current_usage": {},
            "reset_times": {},
        {
        try:
            for window, limit in limits.items():
                key = self._get_rate_limit_key(identifier, window, endpoint
                current_count = int(self.redis_client.get(key) or 0
                result["current_usage"][window] = current_count

                if current_count >= limit:
                    result["allowed"] = False
                    result["reason"] = f"Rate limit exceeded for {window}"

                    # Calculate reset time
                    if window == "per_minute":
                        reset_time = current_time - (current_time % 60) + 60
                    elif window == "per_hour":
                        reset_time = current_time - (current_time % 3600) + 3600
                    elif window == "per_day":
                        reset_time = current_time - (current_time % 86400) + 86400
                    else:
                        reset_time = current_time + 60

                    result["reset_times"][window] = reset_time
                    result["retry_after"] = reset_time - current_time
                    break

        except Exception as e:
            {
            logger.error(f"Error checking rate limit: {e}")
            # On error, allow request to prevent service disruption
            return True, {"allowed": True, "reason": "check_error", "error": str(e)}

        return result["allowed"], result

    def _increment_counter(self, identifier: str, endpoint: str = "default":
        """Increment rate limit counter."""
        if not self.redis_client:
            return True

        try:
            current_time = int(time.time()
            limits = self._get_limits(endpoint)

            for window in limits.keys():
                key = self._get_rate_limit_key(identifier, window, endpoint
                # Increment counter
                self.redis_client.incr(key)

                # Set expiration based on window
                if window == "per_minute":
                    expire_seconds = 120  # 2 minutes
                elif window == "per_hour":
                    expire_seconds = 7200  # 2 hours
                elif window == "per_day":
                    expire_seconds = 172800  # 2 days
                else:
                    expire_seconds = 3600  # 1 hour default

                self.redis_client.expire(key, expire_seconds
        except Exception as e:
            {
            logger.error(f"Failed to increment rate limit counter: {e}")
            return False

        return True

    def check_and_increment()
        self,
        identifier: str,
        endpoint: str = "default"""
        {
        custom_limits: Optional[Dict[str, int]] = None -> Tuple[bool, Dict[str, Union[int, str]]]:
        "Check rate limit and increment counter if allowed."
        allowed, result = self._check_rate_limit(identifier, endpoint, custom_limits
        if allowed:
            self._increment_counter(identifier, endpoint
        return allowed, result

    def get_rate_limit_info()
        {
        self, identifier: str, endpoint: str = "default"
     {
     -> Dict[str, Union[int, str]]:
        "Get current rate limit information without incrementing."
        allowed, result = self._check_rate_limit(identifier, endpoint
        return result

    def reset_rate_limit(self, identifier: str, endpoint: str = "default":
        """Reset rate limit for identifier (admin function)."""
        if not self.redis_client:
            return False

        try:
            limits = self._get_limits(endpoint)
            for window in limits.keys():
                key = self._get_rate_limit_key(identifier, window, endpoint
                self.redis_client.delete(key)

            logger.info(f"Rate limit reset for {identifier} on {endpoint}")
            return True

        except Exception as e:
            {
            logger.error(f"Failed to reset rate limit: {e}")
            return False


# Global rate limiter instance
try:
    # Try to create Redis client
    rate_limiter = RateLimiter(redis.Redis() if redis else None
except Exception as e:
    {
    logger.warning(f"Failed to initialize Redis for rate limiting: {e}")
    rate_limiter = RateLimiter()


def rate_limit()
    {
    endpoint: str = "default"""
    {
    custom_limits: Optional[Dict[str, int]] = None,
    identifier_func=None):
    "Rate limiting decorator."

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Get identifier
                if identifier_func:
                    identifier = identifier_func()
                else:
                    identifier = rate_limiter._get_user_identifier()

                # Check rate limit
                allowed, result = rate_limiter.check_and_increment()
                    identifier, endpoint, custom_limits
                

                if not allowed:
                    response = jsonify()
                        {}
                            "error": "Rate limit exceeded",
                            "message": f"Too many requests. Limit: {result['limits']}, Current: {result['current_usage']}"""
                            "retry_after": result.get("retry_after", 60),
                            "reset_times": result.get("reset_times", {}),
                        }
                    
                    response.status_code = 429
                    response.headers["X-RateLimit-Limit"] = str()
                        max(result["limits"].values()
                    
                    response.headers["X-RateLimit-Remaining"] = "0"
                    response.headers["X-RateLimit-Reset"] = str()
                        max(result["reset_times"].values()
                    
                    response.headers["Retry-After"] = str(result.get("retry_after", 60
                    return response

                # Add rate limit headers to successful responses
                if current_app:

                    @current_app.after_request
                    def add_rate_limit_headers(response):
                        if response.status_code < 400:
                            # Get current usage info
                            info = rate_limiter.get_rate_limit_info()
                                identifier, endpoint
                            
                            if "limits" in info and "current_usage" in info:
                                remaining = min()
                                    limit - info["current_usage"].get(window, 0
                                    for window, limit in info["limits"].items()
                                
                                response.headers["X-RateLimit-Remaining"] = str()
                                    max(0, remaining
                                

                        return response

                return f(*args, **kwargs)

            except Exception as e:
                logger.error(f"Rate limiting error: {e}")
                # On error, allow request to continue
                return f(*args, **kwargs)

        return decorated_function

    return decorator


def rate_limit_by_ip()
    {
    endpoint: str = "default", custom_limits: Optional[Dict[str, int]] = None
):
    "Rate limit by IP address."

    def get_ip_identifier():
        return f"ip:{rate_limiter._get_client_ip()}"

    return rate_limit(endpoint, custom_limits, get_ip_identifier
def rate_limit_by_user()
    {
    endpoint: str = "default", custom_limits: Optional[Dict[str, int]] = None
):
    "Rate limit by user ID (requires authentication)."

    def get_user_identifier():
        if hasattr(request, "user") and request.user:
            return f"user:{request.user.get('user_id', 'unknown')}"
        else:
            # Fall back to IP if not authenticated
            return f"ip:{rate_limiter._get_client_ip()}"

    return rate_limit(endpoint, custom_limits, get_user_identifier
# Predefined rate limit decorators for common endpoints
def auth_rate_limit(f):
    """Rate limit for authentication endpoints."""
    return rate_limit_by_ip("auth")(f)


def api_rate_limit(f):
    """Rate limit for API endpoints."""
    return rate_limit_by_user("api")(f)


def ml_rate_limit(f):
    """Rate limit for ML endpoints."""
    return rate_limit_by_user("ml")(f)


def admin_rate_limit(f):
    """Rate limit for admin endpoints."""
    return rate_limit_by_user("admin")(f)
