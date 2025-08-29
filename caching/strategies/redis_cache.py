"""
Redis-based Distributed Caching System
Phase 3 Week 4: Advanced Caching Strategies - Redis Integration
"""

import redis
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

logger = logging.getLogger(__name__)


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
            raise ValueError(f"Unsupported deserialization method: {method}")


class RedisCache:
    """Advanced Redis caching implementation"""
    
    def __init__(self, 
                 host: str = 'localhost',
                 port: int = 6379,
                 db: int = 0,
                 password: Optional[str] = None,
                 connection_pool_size: int = 10,
                 default_ttl: int = 3600,
                 key_prefix: str = "smartcloudops:",
                 compression_threshold: int = 1024,
                 max_connections: int = 20):
        
        self.host = host
        self.port = port
        self.db = db
        self.default_ttl = default_ttl
        self.key_prefix = key_prefix
        self.compression_threshold = compression_threshold
        
        # Create connection pool
        self.connection_pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password,
            max_connections=max_connections,
            retry_on_timeout=True,
            socket_keepalive=True,
            socket_keepalive_options={}
        )
        
        # Redis client
        self.client = redis.Redis(connection_pool=self.connection_pool, decode_responses=False)
        
        # Cache statistics
        self.stats = CacheStats(
    self.stats_lock = threading.Lock()
        
        # Serializer
        self.serializer = CacheSerializer(
    # Test connection
        self._test_connection()
    
    def _test_connection(self):
        """Test Redis connection"""
        try:
            self.client.ping()
            logger.info(f"Connected to Redis at {self.host}:{self.port}")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def _generate_key(self, key: str) -> str:
        """Generate prefixed cache key"""
        return f"{self.key_prefix}{key}"
    
    def _should_compress(self, data: bytes) -> bool:
        """Determine if data should be compressed"""
        return len(data) > self.compression_threshold
    
    def _update_stats(self, operation: str):
        """Update cache statistics"""
        with self.stats_lock:
            if operation == "hit":
                self.stats.hits += 1
            elif operation == "miss":
                self.stats.misses += 1
            elif operation == "set":
                self.stats.sets += 1
            elif operation == "delete":
                self.stats.deletes += 1
            elif operation == "error":
                self.stats.errors += 1
            
            self.stats.total_requests += 1
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        try:
            redis_key = self._generate_key(key)
            
            # Get data from Redis
            data = self.client.get(redis_key)
            
            if data is None:
                self._update_stats("miss")
                return default
            
            # Get metadata
            metadata_key = f"{redis_key}:meta"
            metadata_data = self.client.get(metadata_key)
            
            # Deserialize metadata
            if metadata_data:
                try:
                    metadata = json.loads(metadata_data.decode('utf-8'))
                    compressed = metadata.get('compressed', False)
                    serializer = metadata.get('serializer', 'json')
                    
                    # Update access info
                    metadata['access_count'] = metadata.get('access_count', 0) + 1
                    metadata['last_access'] = datetime.now().isoformat()
                    
                    # Update metadata in Redis
                    self.client.set(metadata_key, json.dumps(metadata))
                    
                except json.JSONDecodeError:
                    compressed = False
                    serializer = 'json'
            else:
                compressed = False
                serializer = 'json'
            
            # Deserialize value
            value = self.serializer.deserialize(data, serializer, compressed)
            
            self._update_stats("hit")
            return value
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            self._update_stats("error")
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, 
            serializer: str = "json", force_compression: bool = False) -> bool:
        """Set value in cache"""
        try:
            redis_key = self._generate_key(key)
            
            # Use default TTL if not specified
            if ttl is None:
                ttl = self.default_ttl
            
            # Serialize value
            serialized_data = self.serializer.serialize(value, serializer)
            
            # Determine compression
            should_compress = force_compression or self._should_compress(serialized_data)
            if should_compress:
                serialized_data = gzip.compress(serialized_data)
            
            # Create metadata
            metadata = {
                'timestamp': datetime.now().isoformat(),
                'ttl': ttl,
                'compressed': should_compress,
                'serializer': serializer,
                'access_count': 0,
                'size_bytes': len(serialized_data)
            }
            
            # Set data and metadata in Redis
            pipe = self.client.pipeline()
            pipe.setex(redis_key, ttl, serialized_data)
            pipe.setex(f"{redis_key}:meta", ttl + 300, json.dumps(metadata))  # Metadata TTL slightly longer
            pipe.execute()
            
            self._update_stats("set")
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            self._update_stats("error")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            redis_key = self._generate_key(key)
            
            # Delete data and metadata
            pipe = self.client.pipeline()
            pipe.delete(redis_key)
            pipe.delete(f"{redis_key}:meta")
            result = pipe.execute()
            
            deleted = sum(result) > 0
            if deleted:
                self._update_stats("delete")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            self._update_stats("error")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            redis_key = self._generate_key(key)
            return bool(self.client.exists(redis_key))
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for key"""
        try:
            redis_key = self._generate_key(key)
            return bool(self.client.expire(redis_key, ttl))
        except Exception as e:
            logger.error(f"Cache expire error for key {key}: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """Get time to live for key"""
        try:
            redis_key = self._generate_key(key)
            return self.client.ttl(redis_key)
        except Exception as e:
            logger.error(f"Cache TTL error for key {key}: {e}")
            return -1
    
    def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern"""
        try:
            redis_pattern = self._generate_key(pattern)
            keys = self.client.keys(redis_pattern)
            
            # Remove prefix from keys
            prefix_len = len(self.key_prefix)
            return [key.decode('utf-8')[prefix_len:] for key in keys if not key.endswith(b':meta')]
            
        except Exception as e:
            logger.error(f"Cache keys error: {e}")
            return []
    
    def flush(self, pattern: Optional[str] = None) -> int:
        """Flush cache entries"""
        try:
            if pattern:
                keys = self.keys(pattern)
                if keys:
                    redis_keys = [self._generate_key(key) for key in keys]
                    # Also delete metadata keys
                    meta_keys = [f"{key}:meta" for key in redis_keys]
                    all_keys = redis_keys + meta_keys
                    
                    return self.client.delete(*all_keys)
                return 0
            else:
                # Flush entire database
                return self.client.flushdb()
                
        except Exception as e:
            logger.error(f"Cache flush error: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.stats_lock:
            stats = self.stats.to_dict()
        
        # Add Redis-specific stats
        try:
            info = self.client.info()
            redis_stats = {
                'used_memory': info.get('used_memory', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'connected_clients': info.get('connected_clients', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0)
            }
            
            stats['redis'] = redis_stats
        except Exception as e:
            logger.error(f"Error getting Redis stats: {e}")
        
        return stats
    
    def get_size_info(self) -> Dict[str, Any]:
        """Get cache size information"""
        try:
            keys = self.keys()
            total_keys = len(keys)
            
            # Sample some keys to estimate sizes
            sample_size = min(100, total_keys)
            sample_keys = keys[:sample_size] if keys else []
            
            total_size = 0
            metadata_info = []
            
            for key in sample_keys:
                try:
                    redis_key = self._generate_key(key)
                    metadata_key = f"{redis_key}:meta"
                    
                    metadata_data = self.client.get(metadata_key)
                    if metadata_data:
                        metadata = json.loads(metadata_data.decode('utf-8'))
                        size_bytes = metadata.get('size_bytes', 0)
                        total_size += size_bytes
                        
                        metadata_info.append({
                            'key': key,
                            'size_bytes': size_bytes,
                            'compressed': metadata.get('compressed', False),
                            'access_count': metadata.get('access_count', 0),
                            'timestamp': metadata.get('timestamp')
                        })
                except Exception:
                    continue
            
            # Estimate total size
            if sample_size > 0:
                avg_size = total_size / sample_size
                estimated_total_size = avg_size * total_keys
            else:
                estimated_total_size = 0
            
            return {
                'total_keys': total_keys,
                'sampled_keys': sample_size,
                'estimated_total_size_bytes': estimated_total_size,
                'estimated_total_size_mb': estimated_total_size / (1024 * 1024),
                'sample_metadata': metadata_info[:10]  # Top 10 for display
            }
            
        except Exception as e:
            logger.error(f"Error getting cache size info: {e}")
            return {}
    
    def warm_cache(self, keys: List[str], fetch_func: Callable[[str], Any], 
                   batch_size: int = 10, ttl: Optional[int] = None):
        """Warm cache with data"""
        total_keys = len(keys)
        loaded = 0
        
        logger.info(f"Warming cache with {total_keys} keys")
        
        for i in range(0, total_keys, batch_size):
            batch = keys[i:i + batch_size]
            
            for key in batch:
                try:
                    if not self.exists(key):
                        value = fetch_func(key)
                        if value is not None:
                            self.set(key, value, ttl=ttl)
                            loaded += 1
                except Exception as e:
                    logger.error(f"Error warming cache for key {key}: {e}")
            
            # Progress logging
            if (i + batch_size) % 100 == 0:
                logger.info(f"Cache warming progress: {min(i + batch_size, total_keys)}/{total_keys}")
        
        logger.info(f"Cache warming completed: {loaded}/{total_keys} keys loaded")
        return loaded
    
    @contextmanager
    def lock(self, key: str, timeout: int = 10, blocking_timeout: int = 10):
        """Distributed lock using Redis"""
        lock_key = f"lock:{key}"
        lock = self.client.lock(lock_key, timeout=timeout, blocking_timeout=blocking_timeout)
        
        try:
            acquired = lock.acquire()
            if not acquired:
                raise TimeoutError(f"Could not acquire lock for key: {key}")
            yield lock
        finally:
            if lock.owned():
                lock.release()
    
    def close(self):
        """Close Redis connection"""
        try:
            self.connection_pool.disconnect()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")


class CacheDecorator:
    """Decorators for caching function results"""
    
    def __init__(self, cache: RedisCache):
        self.cache = cache
    
    def cached(self, ttl: Optional[int] = None, key_prefix: str = "", 
               serializer: str = "json", include_args: bool = True):
        """Decorator to cache function results"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                if include_args:
                    key_parts = [func.__name__]
                    if key_prefix:
                        key_parts.insert(0, key_prefix)
                    
                    # Add arguments to key
                    if args:
                        key_parts.extend([str(arg) for arg in args])
                    if kwargs:
                        key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
                    
                    cache_key = ":".join(key_parts)
                else:
                    cache_key = f"{key_prefix}:{func.__name__}" if key_prefix else func.__name__
                
                # Hash long keys
                if len(cache_key) > 250:
                    cache_key = hashlib.md5(cache_key.encode()).hexdigest()
                
                # Try to get from cache
                result = self.cache.get(cache_key)
                if result is not None:
                    return result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                self.cache.set(cache_key, result, ttl=ttl, serializer=serializer)
                
                return result
            
            return wrapper
        return decorator
    
    def cache_invalidate(self, key_pattern: str):
        """Decorator to invalidate cache on function execution"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                
                # Invalidate cache
                deleted = self.cache.flush(key_pattern)
                if deleted > 0:
                    logger.info(f"Invalidated {deleted} cache entries matching pattern: {key_pattern}")
                
                return result
            
            return wrapper
        return decorator


# Global Redis cache instance
try:
    redis_cache = RedisCache(
    cache_decorator = CacheDecorator(redis_cache)
except Exception as e:
    logger.warning(f"Redis cache not available: {e}")
    redis_cache = None
    cache_decorator = None


def get_redis_cache() -> Optional[RedisCache]:
    """Get Redis cache instance"""
    return redis_cache


def cached(ttl: Optional[int] = None, key_prefix: str = "", 
          serializer: str = "json", include_args: bool = True):
    """Decorator to cache function results"""
    if cache_decorator:
        return cache_decorator.cached(ttl=ttl, key_prefix=key_prefix, 
                                    serializer=serializer, include_args=include_args)
    else:
        # No-op decorator if Redis not available
        def decorator(func: Callable) -> Callable:
            return func
        return decorator


def cache_invalidate(key_pattern: str):
    """Decorator to invalidate cache on function execution"""
    if cache_decorator:
        return cache_decorator.cache_invalidate(key_pattern)
    else:
        # No-op decorator if Redis not available
        def decorator(func: Callable) -> Callable:
            return func
        return decorator
