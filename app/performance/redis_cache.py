"""
Redis Cache Integration for Performance Optimization
Phase 5: Performance & Cost Optimization - Redis Caching Layer
"""

import os
import json
import pickle
import gzip
import time
import logging
import threading
from typing import Any, Optional, Dict, List, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from functools import wraps
import hashlib
from contextlib import contextmanager

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger(__name__)


@dataclass
class RedisCacheConfig:
    """Redis cache configuration"""
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    db: int = 0
    max_connections: int = 50
    socket_timeout: float = 5.0
    socket_connect_timeout: float = 5.0
    retry_on_timeout: bool = True
    health_check_interval: int = 30
    default_ttl: int = 3600
    compression_threshold: int = 1024  # Compress if larger than 1KB
    enable_compression: bool = True
    enable_serialization: bool = True


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    timestamp: datetime
    ttl: Optional[int]
    access_count: int = 0
    last_access: Optional[datetime] = None
    compressed: bool = False
    serializer: str = "json"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat(),
            'last_access': self.last_access.isoformat() if self.last_access else None,
            'value': None  # Don't serialize the actual value in metadata
        }


@dataclass
class CacheStats:
    """Cache performance statistics"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    errors: int = 0
    total_requests: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate"""
        if self.total_requests == 0:
            return 0.0
        return (self.hits / self.total_requests) * 100
    
    @property
    def miss_rate(self) -> float:
        """Calculate cache miss rate"""
        return 100.0 - self.hit_rate
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            'hit_rate': self.hit_rate,
            'miss_rate': self.miss_rate
        }


class CacheSerializer:
    """Handle different serialization methods"""
    
    @staticmethod
    def serialize(value: Any, method: str = "json", compress: bool = False) -> bytes:
        """Serialize value using specified method"""
        if method == "json":
            serialized = json.dumps(value, default=str).encode('utf-8')
        elif method == "pickle":
            serialized = pickle.dumps(value)
        else:
            raise ValueError(f"Unsupported serialization method: {method}")
        
        if compress:
            serialized = gzip.compress(serialized)
        
        return serialized
    
    @staticmethod
    def deserialize(data: bytes, method: str = "json", compressed: bool = False) -> Any:
        """Deserialize data using specified method"""
        if compressed:
            data = gzip.decompress(data)
        
        if method == "json":
            return json.loads(data.decode('utf-8'))
        elif method == "pickle":
            return pickle.loads(data)
        else:
            raise ValueError(f"Unsupported serialization method: {method}")


class RedisCache:
    """Redis-based distributed caching system"""
    
    def __init__(self, config: Optional[RedisCacheConfig] = None):
        self.config = config or RedisCacheConfig()
        self.stats = CacheStats()
        self._lock = threading.RLock()
        self._redis_client = None
        self._health_check_thread = None
        self._running = False
        
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available, using fallback cache")
            return
        
        self._init_redis_client()
        self._start_health_check()
    
    def _init_redis_client(self):
        """Initialize Redis client"""
        try:
            self._redis_client = redis.Redis(
                host=self.config.host,
                port=self.config.port,
                password=self.config.password,
                db=self.config.db,
                socket_timeout=self.config.socket_timeout,
                socket_connect_timeout=self.config.socket_connect_timeout,
                retry_on_timeout=self.config.retry_on_timeout,
                decode_responses=False,  # We handle serialization ourselves
                health_check_interval=self.config.health_check_interval
            )
            
            # Test connection
            self._redis_client.ping()
            logger.info(f"✅ Redis cache connected to {self.config.host}:{self.config.port}")
            
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            self._redis_client = None
    
    def _start_health_check(self):
        """Start health check thread"""
        if not self._redis_client:
            return
        
        self._running = True
        self._health_check_thread = threading.Thread(
            target=self._health_check_loop,
            daemon=True,
            name="redis-health-check"
        )
        self._health_check_thread.start()
    
    def _health_check_loop(self):
        """Health check loop"""
        while self._running:
            try:
                time.sleep(self.config.health_check_interval)
                if self._redis_client:
                    self._redis_client.ping()
            except Exception as e:
                logger.warning(f"Redis health check failed: {e}")
    
    def _get_cache_key(self, key: str, namespace: str = "default") -> str:
        """Generate cache key with namespace"""
        return f"{namespace}:{key}"
    
    def _should_compress(self, data: bytes) -> bool:
        """Determine if data should be compressed"""
        return (self.config.enable_compression and 
                len(data) > self.config.compression_threshold)
    
    def _serialize_value(self, value: Any) -> tuple[bytes, bool, str]:
        """Serialize value and determine compression"""
        if not self.config.enable_serialization:
            if isinstance(value, str):
                data = value.encode('utf-8')
            elif isinstance(value, bytes):
                data = value
            else:
                data = str(value).encode('utf-8')
            return data, False, "raw"
        
        # Try JSON first, fallback to pickle
        try:
            data = CacheSerializer.serialize(value, "json")
            serializer = "json"
        except (TypeError, ValueError):
            data = CacheSerializer.serialize(value, "pickle")
            serializer = "pickle"
        
        # Determine compression
        compressed = self._should_compress(data)
        if compressed:
            data = gzip.compress(data)
        
        return data, compressed, serializer
    
    def _deserialize_value(self, data: bytes, compressed: bool, serializer: str) -> Any:
        """Deserialize value"""
        if not self.config.enable_serialization:
            return data.decode('utf-8') if serializer == "raw" else data
        
        if compressed:
            data = gzip.decompress(data)
        
        return CacheSerializer.deserialize(data, serializer)
    
    def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """Get value from cache"""
        if not self._redis_client:
            return None
        
        cache_key = self._get_cache_key(key, namespace)
        
        try:
            with self._lock:
                self.stats.total_requests += 1
                
                # Get value and metadata
                value_data = self._redis_client.get(f"{cache_key}:value")
                meta_data = self._redis_client.get(f"{cache_key}:meta")
                
                if value_data is None:
                    self.stats.misses += 1
                    return None
                
                # Parse metadata
                if meta_data:
                    meta = json.loads(meta_data.decode('utf-8'))
                    compressed = meta.get('compressed', False)
                    serializer = meta.get('serializer', 'json')
                else:
                    compressed = False
                    serializer = 'json'
                
                # Deserialize value
                value = self._deserialize_value(value_data, compressed, serializer)
                
                # Update access metadata
                self._update_access_metadata(cache_key, meta)
                
                self.stats.hits += 1
                return value
                
        except Exception as e:
            logger.error(f"Cache get error for key {cache_key}: {e}")
            self.stats.errors += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, 
            namespace: str = "default") -> bool:
        """Set value in cache"""
        if not self._redis_client:
            return False
        
        cache_key = self._get_cache_key(key, namespace)
        ttl = ttl or self.config.default_ttl
        
        try:
            with self._lock:
                # Serialize value
                value_data, compressed, serializer = self._serialize_value(value)
                
                # Create metadata
                meta = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'ttl': ttl,
                    'compressed': compressed,
                    'serializer': serializer,
                    'access_count': 0,
                    'last_access': datetime.utcnow().isoformat()
                }
                meta_data = json.dumps(meta).encode('utf-8')
                
                # Store value and metadata
                pipe = self._redis_client.pipeline()
                pipe.setex(f"{cache_key}:value", ttl, value_data)
                pipe.setex(f"{cache_key}:meta", ttl, meta_data)
                pipe.execute()
                
                self.stats.sets += 1
                return True
                
        except Exception as e:
            logger.error(f"Cache set error for key {cache_key}: {e}")
            self.stats.errors += 1
            return False
    
    def delete(self, key: str, namespace: str = "default") -> bool:
        """Delete value from cache"""
        if not self._redis_client:
            return False
        
        cache_key = self._get_cache_key(key, namespace)
        
        try:
            with self._lock:
                pipe = self._redis_client.pipeline()
                pipe.delete(f"{cache_key}:value")
                pipe.delete(f"{cache_key}:meta")
                pipe.execute()
                
                self.stats.deletes += 1
                return True
                
        except Exception as e:
            logger.error(f"Cache delete error for key {cache_key}: {e}")
            self.stats.errors += 1
            return False
    
    def exists(self, key: str, namespace: str = "default") -> bool:
        """Check if key exists in cache"""
        if not self._redis_client:
            return False
        
        cache_key = self._get_cache_key(key, namespace)
        return bool(self._redis_client.exists(f"{cache_key}:value"))
    
    def ttl(self, key: str, namespace: str = "default") -> int:
        """Get remaining TTL for key"""
        if not self._redis_client:
            return -1
        
        cache_key = self._get_cache_key(key, namespace)
        return self._redis_client.ttl(f"{cache_key}:value")
    
    def _update_access_metadata(self, cache_key: str, meta: Dict[str, Any]):
        """Update access metadata"""
        if not meta:
            return
        
        meta['access_count'] = meta.get('access_count', 0) + 1
        meta['last_access'] = datetime.utcnow().isoformat()
        
        try:
            meta_data = json.dumps(meta).encode('utf-8')
            ttl = meta.get('ttl', self.config.default_ttl)
            self._redis_client.setex(f"{cache_key}:meta", ttl, meta_data)
        except Exception as e:
            logger.warning(f"Failed to update access metadata: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = self.stats.to_dict()
        stats['redis_connected'] = self._redis_client is not None
        stats['config'] = asdict(self.config)
        return stats
    
    def clear(self, namespace: str = "default") -> bool:
        """Clear all keys in namespace"""
        if not self._redis_client:
            return False
        
        try:
            pattern = f"{namespace}:*"
            keys = self._redis_client.keys(pattern)
            if keys:
                self._redis_client.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Cache clear error for namespace {namespace}: {e}")
            return False
    
    def close(self):
        """Close Redis connection"""
        self._running = False
        if self._redis_client:
            self._redis_client.close()


class CacheDecorator:
    """Decorator for caching function results"""
    
    def __init__(self, cache: RedisCache):
        self.cache = cache
    
    def __call__(self, ttl: Optional[int] = None, namespace: str = "default"):
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key from function name and arguments
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
                
                # Try to get from cache
                cached_result = self.cache.get(cache_key, namespace)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                self.cache.set(cache_key, result, ttl, namespace)
                return result
            
            return wrapper
        return decorator


# Global cache instance
_redis_cache = None
_redis_cache_lock = threading.Lock()


def init_redis_cache(config: Optional[RedisCacheConfig] = None) -> RedisCache:
    """Initialize Redis cache"""
    global _redis_cache
    
    with _redis_cache_lock:
        if _redis_cache is None:
            _redis_cache = RedisCache(config)
            logger.info("✅ Redis cache initialized")
    
    return _redis_cache


def get_redis_cache() -> Optional[RedisCache]:
    """Get Redis cache instance"""
    return _redis_cache


def cached(ttl: Optional[int] = None, namespace: str = "default"):
    """Cache decorator"""
    cache = get_redis_cache()
    if cache:
        return CacheDecorator(cache)(ttl, namespace)
    else:
        # Fallback decorator that does nothing
        def decorator(func):
            return func
        return decorator
