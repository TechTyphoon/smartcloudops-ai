#!/usr/bin/env python3
"""
Rate Limiting System for Smart CloudOps AI
Enterprise-grade rate limiting with Redis backend and multiple strategies
"""

import time
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, List, Optional, Tuple, Union
from flask import request, jsonify, current_app
import redis

logger = logging.getLogger(__name__)


class RateLimiter:
    """Enterprise-grade rate limiter with multiple strategies."""

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """Initialize rate limiter."""
        self.redis_client = redis_client
        self.default_limits = {
            "default": {"per_minute": 100, "per_hour": 1000, "per_day": 10000},
            "auth": {"per_minute": 5, "per_hour": 20, "per_day": 100},
            "api": {"per_minute": 200, "per_hour": 2000, "per_day": 20000},
            "ml": {"per_minute": 50, "per_hour": 500, "per_day": 5000},
            "admin": {"per_minute": 500, "per_hour": 5000, "per_day": 50000},
        }

    def _get_client_ip(self) -> str:
        """Get client IP address with proxy support."""
        # Check for forwarded headers (for proxy/load balancer setups)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return request.remote_addr or "unknown"

    def _get_user_identifier(self) -> str:
        """Get user identifier for rate limiting."""
        # Try to get user ID from JWT token
        if hasattr(request, "user") and request.user:
            return f"user:{request.user.get('user_id', 'unknown')}"

        # Fall back to IP address
        return f"ip:{self._get_client_ip()}"

    def _get_rate_limit_key(
        self, identifier: str, window: str, endpoint: str = "default"
    ) -> str:
        """Generate Redis key for rate limiting."""
        timestamp = int(time.time())

        if window == "minute":
            window_timestamp = timestamp - (timestamp % 60)
        elif window == "hour":
            window_timestamp = timestamp - (timestamp % 3600)
        elif window == "day":
            window_timestamp = timestamp - (timestamp % 86400)
        else:
            window_timestamp = timestamp

        return f"rate_limit:{endpoint}:{identifier}:{window}:{window_timestamp}"

    def _get_limits(self, endpoint: str = "default") -> Dict[str, int]:
        """Get rate limits for endpoint."""
        return self.default_limits.get(endpoint, self.default_limits["default"])

    def _check_rate_limit(
        self,
        identifier: str,
        endpoint: str = "default",
        custom_limits: Optional[Dict[str, int]] = None,
    ) -> Tuple[bool, Dict[str, Union[int, int, str]]]:
        """Check if request is within rate limits."""
        if not self.redis_client:
            # If Redis is not available, allow request but log warning
            logger.warning("Rate limiting disabled: Redis not available")
            return True, {"allowed": True, "reason": "redis_unavailable"}

        limits = custom_limits or self._get_limits(endpoint)
        current_time = int(time.time())

        result = {
            "allowed": True,
            "identifier": identifier,
            "endpoint": endpoint,
            "limits": limits,
            "current_usage": {},
            "reset_times": {},
        }

        try:
            for window, limit in limits.items():
                key = self._get_rate_limit_key(identifier, window, endpoint)

                # Get current count
                current_count = self.redis_client.get(key)
                current_count = int(current_count) if current_count else 0

                result["current_usage"][window] = current_count

                # Check if limit exceeded
                if current_count >= limit:
                    result["allowed"] = False
                    result["reason"] = f"rate_limit_exceeded_{window}"

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

                    return False, result

        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # Allow request if rate limiting fails
            return True, {
                "allowed": True,
                "reason": "rate_limit_error",
                "error": str(e),
            }

        return True, result

    def _increment_counter(self, identifier: str, endpoint: str = "default") -> bool:
        """Increment rate limit counter."""
        if not self.redis_client:
            return True

        try:
            current_time = int(time.time())
            limits = self._get_limits(endpoint)

            for window, limit in limits.items():
                key = self._get_rate_limit_key(identifier, window, endpoint)

                # Set expiration based on window
                if window == "per_minute":
                    expire_seconds = 120  # 2 minutes
                elif window == "per_hour":
                    expire_seconds = 7200  # 2 hours
                elif window == "per_day":
                    expire_seconds = 172800  # 2 days
                else:
                    expire_seconds = 120

                # Increment counter with expiration
                pipe = self.redis_client.pipeline()
                pipe.incr(key)
                pipe.expire(key, expire_seconds)
                pipe.execute()

        except Exception as e:
            logger.error(f"Failed to increment rate limit counter: {e}")
            return False

        return True

    def check_and_increment(
        self,
        identifier: str,
        endpoint: str = "default",
        custom_limits: Optional[Dict[str, int]] = None,
    ) -> Tuple[bool, Dict[str, Union[int, int, str]]]:
        """Check rate limit and increment counter if allowed."""
        allowed, result = self._check_rate_limit(identifier, endpoint, custom_limits)

        if allowed:
            self._increment_counter(identifier, endpoint)

        return allowed, result

    def get_rate_limit_info(
        self, identifier: str, endpoint: str = "default"
    ) -> Dict[str, Union[int, int, str]]:
        """Get current rate limit information without incrementing."""
        allowed, result = self._check_rate_limit(identifier, endpoint)
        return result

    def reset_rate_limit(self, identifier: str, endpoint: str = "default") -> bool:
        """Reset rate limit for identifier (admin function)."""
        if not self.redis_client:
            return False

        try:
            limits = self._get_limits(endpoint)
            current_time = int(time.time())

            for window in limits.keys():
                key = self._get_rate_limit_key(identifier, window, endpoint)
                self.redis_client.delete(key)

            logger.info(f"Rate limit reset for {identifier} on {endpoint}")
            return True

        except Exception as e:
            logger.error(f"Failed to reset rate limit: {e}")
            return False


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(
    endpoint: str = "default",
    custom_limits: Optional[Dict[str, int]] = None,
    identifier_func: Optional[callable] = None,
):
    """
    Decorator for rate limiting Flask endpoints.

    Args:
        endpoint: Rate limit endpoint category
        custom_limits: Custom rate limits (overrides default)
        identifier_func: Custom function to get identifier
    """

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
                allowed, result = rate_limiter.check_and_increment(
                    identifier, endpoint, custom_limits
                )

                if not allowed:
                    # Add rate limit headers
                    response = jsonify(
                        {
                            "error": "Rate limit exceeded",
                            "message": f"Too many requests. Limit: {result['limits']}, Current: {result['current_usage']}",
                            "retry_after": result.get("retry_after", 60),
                            "reset_times": result.get("reset_times", {}),
                        }
                    )

                    response.status_code = 429
                    response.headers["X-RateLimit-Limit"] = str(
                        max(result["limits"].values())
                    )
                    response.headers["X-RateLimit-Remaining"] = "0"
                    response.headers["X-RateLimit-Reset"] = str(
                        max(result["reset_times"].values())
                    )
                    response.headers["Retry-After"] = str(result.get("retry_after", 60))

                    return response

                # Add rate limit headers to successful response
                @current_app.after_request
                def add_rate_limit_headers(response):
                    if response.status_code < 400:
                        # Get current usage info
                        info = rate_limiter.get_rate_limit_info(identifier, endpoint)
                        current_usage = info.get("current_usage", {})
                        limits = info.get("limits", {})

                        if current_usage and limits:
                            # Use the most restrictive limit
                            max_limit = max(limits.values())
                            max_usage = max(current_usage.values())
                            remaining = max(0, max_limit - max_usage)

                            response.headers["X-RateLimit-Limit"] = str(max_limit)
                            response.headers["X-RateLimit-Remaining"] = str(remaining)
                            response.headers["X-RateLimit-Reset"] = str(
                                int(time.time()) + 60
                            )

                    return response

                return f(*args, **kwargs)

            except Exception as e:
                logger.error(f"Rate limiting error: {e}")
                # Allow request if rate limiting fails
                return f(*args, **kwargs)

        return decorated_function

    return decorator


def rate_limit_by_ip(
    endpoint: str = "default", custom_limits: Optional[Dict[str, int]] = None
):
    """Rate limit by IP address."""

    def get_ip_identifier():
        return f"ip:{rate_limiter._get_client_ip()}"

    return rate_limit(endpoint, custom_limits, get_ip_identifier)


def rate_limit_by_user(
    endpoint: str = "default", custom_limits: Optional[Dict[str, int]] = None
):
    """Rate limit by user ID (requires authentication)."""

    def get_user_identifier():
        if hasattr(request, "user") and request.user:
            return f"user:{request.user.get('user_id', 'unknown')}"
        else:
            # Fall back to IP if not authenticated
            return f"ip:{rate_limiter._get_client_ip()}"

    return rate_limit(endpoint, custom_limits, get_user_identifier)


def rate_limit_by_role(
    endpoint: str = "default", custom_limits: Optional[Dict[str, int]] = None
):
    """Rate limit by user role (requires authentication)."""

    def get_role_identifier():
        if hasattr(request, "user") and request.user:
            role = request.user.get("role", "viewer")
            return f"role:{role}"
        else:
            return f"ip:{rate_limiter._get_client_ip()}"

    return rate_limit(endpoint, custom_limits, get_role_identifier)


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
    return rate_limit_by_role("admin")(f)


def strict_rate_limit(f):
    """Strict rate limit for sensitive endpoints."""
    custom_limits = {"per_minute": 10, "per_hour": 100, "per_day": 1000}
    return rate_limit_by_ip("default", custom_limits)(f)


# Rate limit monitoring and analytics
class RateLimitMonitor:
    """Monitor and analyze rate limiting patterns."""

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client

    def get_rate_limit_stats(self, hours: int = 24) -> Dict[str, any]:
        """Get rate limiting statistics."""
        if not self.redis_client:
            return {"error": "Redis not available"}

        try:
            current_time = int(time.time())
            start_time = current_time - (hours * 3600)

            # Get all rate limit keys
            pattern = "rate_limit:*"
            keys = self.redis_client.keys(pattern)

            stats = {
                "total_requests": 0,
                "rate_limited_requests": 0,
                "endpoints": {},
                "identifiers": {},
                "time_periods": {
                    "hour": {"requests": 0, "limited": 0},
                    "day": {"requests": 0, "limited": 0},
                },
            }

            for key in keys:
                # Parse key: rate_limit:endpoint:identifier:window:timestamp
                parts = key.decode().split(":")
                if len(parts) >= 5:
                    endpoint = parts[1]
                    identifier = parts[2]
                    window = parts[3]
                    timestamp = int(parts[4])

                    if timestamp >= start_time:
                        count = int(self.redis_client.get(key) or 0)

                        # Update stats
                        stats["total_requests"] += count

                        if endpoint not in stats["endpoints"]:
                            stats["endpoints"][endpoint] = {"requests": 0, "limited": 0}
                        stats["endpoints"][endpoint]["requests"] += count

                        if identifier not in stats["identifiers"]:
                            stats["identifiers"][identifier] = {
                                "requests": 0,
                                "limited": 0,
                            }
                        stats["identifiers"][identifier]["requests"] += count

                        if window in stats["time_periods"]:
                            stats["time_periods"][window]["requests"] += count

            return stats

        except Exception as e:
            logger.error(f"Failed to get rate limit stats: {e}")
            return {"error": str(e)}

    def get_top_offenders(self, limit: int = 10) -> List[Dict[str, any]]:
        """Get top rate limit offenders."""
        if not self.redis_client:
            return []

        try:
            pattern = "rate_limit:*"
            keys = self.redis_client.keys(pattern)

            offender_counts = {}

            for key in keys:
                parts = key.decode().split(":")
                if len(parts) >= 3:
                    identifier = parts[2]
                    count = int(self.redis_client.get(key) or 0)

                    if identifier not in offender_counts:
                        offender_counts[identifier] = 0
                    offender_counts[identifier] += count

            # Sort by count and return top offenders
            sorted_offenders = sorted(
                offender_counts.items(), key=lambda x: x[1], reverse=True
            )

            return [
                {"identifier": identifier, "total_requests": count}
                for identifier, count in sorted_offenders[:limit]
            ]

        except Exception as e:
            logger.error(f"Failed to get top offenders: {e}")
            return []


# Global monitor instance
rate_limit_monitor = RateLimitMonitor()
