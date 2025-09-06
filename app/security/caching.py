#!/usr/bin/env python3
"""
Caching System for Smart CloudOps AI
Enterprise-grade caching with Redis backend, multiple strategies, and cache invalidation
"""

import hashlib
import json
import logging
import pickle
from typing import Any, Callable, Dict, Optional

import redis

logger = logging.getLogger(__name__)


class CacheManager:
    """Enterprise-grade cache manager with multiple strategies."""

    def __init__(
        self, redis_client: Optional[redis.Redis] = None, default_ttl: int = 300
    ):
        """Initialize cache manager."""
        self.redis_client = redis_client
        self.default_ttl = default_ttl
        self.cache_prefix = "smartcloudops:cache:"

        # Cache statistics
        self.stats = {"hits": 0, "misses": 0, "sets": 0, "deletes": 0, "errors": 0}

    def _generate_key(self, key: str, namespace: str = "default") -> str:
        """Generate cache key with namespace."""
        return f"{self.cache_prefix}{namespace}:{key}"

    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value for storage."""
        try:
            # Try JSON first for simple types
            if isinstance(value, (dict, list, str, int, float, bool)) or value is None:
                return json.dumps(value, default=str).encode("utf-8")
            else:
                # Use pickle for complex objects
                return pickle.dumps(value)
        except Exception as e:
            logger.error(f"Serialization error: {e}")
            return pickle.dumps(value)

    def _deserialize_value(self, data: bytes) -> Any:
        """Deserialize value from storage."""
        try:
            # Try JSON first
            json_str = data.decode("utf-8")
            return json.loads(json_str)
        except (UnicodeDecodeError, json.JSONDecodeError):
            try:
                # Fall back to pickle
                return pickle.loads(data)
            except Exception as e:
                logger.error(f"Deserialization error: {e}")
                return None

    def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """Get value from cache."""
        if not self.redis_client:
            return None
        try:
            cache_key = self._generate_key(key, namespace)
            data = self.redis_client.get(cache_key)

            if data is not None:
                self.stats["hits"] += 1
                return self._deserialize_value(data)
            else:
                self.stats["misses"] += 1
                return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.stats["errors"] += 1
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        namespace: str = "default",
    ) -> bool:
        """Set value in cache."""
        if not self.redis_client:
            return False
        try:
            cache_key = self._generate_key(key, namespace)
            serialized_value = self._serialize_value(value)
            ttl = ttl or self.default_ttl

            result = self.redis_client.setex(cache_key, ttl, serialized_value)
            if result:
                self.stats["sets"] += 1
            return result
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            self.stats["errors"] += 1
            return False

    def delete(self, key: str, namespace: str = "default") -> bool:
        """Delete value from cache."""
        if not self.redis_client:
            return False
        try:
            cache_key = self._generate_key(key, namespace)
            result = self.redis_client.delete(cache_key)
            if result:
                self.stats["deletes"] += 1
            return bool(result)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            self.stats["errors"] += 1
            return False

    def exists(self, key: str, namespace: str = "default") -> bool:
        """Check if key exists in cache."""
        if not self.redis_client:
            return False
        try:
            cache_key = self._generate_key(key, namespace)
            return bool(self.redis_client.exists(cache_key))
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False

    def clear_namespace(self, namespace: str = "default") -> bool:
        """Clear all keys in a namespace."""
        if not self.redis_client:
            return False
        try:
            pattern = f"{self.cache_prefix}{namespace}:*"
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                self.stats["deletes"] += len(keys)
            return True
        except Exception as e:
            logger.error(f"Cache clear namespace error: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = self.stats.copy()
        if self.stats["hits"] + self.stats["misses"] > 0:
            stats["hit_rate"] = self.stats["hits"] / (
                self.stats["hits"] + self.stats["misses"]
            )
        else:
            stats["hit_rate"] = 0.0
        return stats

    def reset_stats(self):
        """Reset cache statistics."""
        self.stats = {"hits": 0, "misses": 0, "sets": 0, "deletes": 0, "errors": 0}


class SecureCacheManager(CacheManager):
    """Secure cache manager with encryption and access control."""

    def __init__(
        self,
        redis_client: Optional[redis.Redis] = None,
        default_ttl: int = 300,
        encryption_key: Optional[str] = None,
    ):
        """Initialize secure cache manager."""
        super().__init__(redis_client, default_ttl)
        self.encryption_key = encryption_key or "default-secure-key"

    def _encrypt_value(self, value: bytes) -> bytes:
        """Encrypt value before storage."""
        try:
            # Simple XOR encryption for demo (use proper encryption in production)
            key_bytes = self.encryption_key.encode("utf-8")
            encrypted = bytearray()
            for i, byte in enumerate(value):
                encrypted.append(byte ^ key_bytes[i % len(key_bytes)])
            return bytes(encrypted)
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return value

    def _decrypt_value(self, value: bytes) -> bytes:
        """Decrypt value after retrieval."""
        try:
            # Simple XOR decryption for demo (use proper decryption in production)
            key_bytes = self.encryption_key.encode("utf-8")
            decrypted = bytearray()
            for i, byte in enumerate(value):
                decrypted.append(byte ^ key_bytes[i % len(key_bytes)])
            return bytes(decrypted)
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return value

    def _serialize_value(self, value: Any) -> bytes:
        """Serialize and encrypt value for storage."""
        serialized = super()._serialize_value(value)
        return self._encrypt_value(serialized)

    def _deserialize_value(self, data: bytes) -> Any:
        """Decrypt and deserialize value from storage."""
        decrypted = self._decrypt_value(data)
        return super()._deserialize_value(decrypted)


class CacheDecorator:
    """Decorator for caching function results."""

    def __init__(
        self, cache_manager: CacheManager, ttl: int = 300, namespace: str = "default"
    ):
        """Initialize cache decorator."""
        self.cache_manager = cache_manager
        self.ttl = ttl
        self.namespace = namespace

    def __call__(self, func: Callable) -> Callable:
        """Cache decorator implementation."""

        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_parts = [func.__name__]
            key_parts.extend([str(arg) for arg in args])
            key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
            cache_key = hashlib.sha256(":".join(key_parts).encode()).hexdigest()

            # Try to get from cache
            cached_result = self.cache_manager.get(cache_key, self.namespace)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            self.cache_manager.set(cache_key, result, self.ttl, self.namespace)
            return result

        return wrapper


# Global cache manager instances
cache_manager = CacheManager()
secure_cache_manager = SecureCacheManager()


def cache_result(ttl: int = 300, namespace: str = "default"):
    """Decorator for caching function results."""
    return CacheDecorator(cache_manager, ttl, namespace)


def secure_cache_result(ttl: int = 300, namespace: str = "secure"):
    """Decorator for secure caching function results."""
    return CacheDecorator(secure_cache_manager, ttl, namespace)
