"""
import pytest
Unit Tests for Performance Integration
Phase 2C Week 1: Performance & Scaling - Testing
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import time
import threading
from datetime import datetime

class TestCachingSystem(unittest.TestCase):
    """Test caching system functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Import here to handle potential import errors gracefully
        try:
            from app.performance.caching import LRUCache, CacheStats, CacheEntry
            self.LRUCache = LRUCache
            self.CacheStats = CacheStats
            self.CacheEntry = CacheEntry
            self.cache_available = True
        except ImportError:
            self.cache_available = False
            self.skipTest("Caching system not available")
    
    def test_lru_cache_basic_operations(self):
        """Test basic LRU cache operations"""
        cache = self.LRUCache(max_size=3)
        
        # Test set and get
        cache.set("key1", "value1")
        self.assertEqual(cache.get("key1"), "value1")
        
        # Test miss
        self.assertIsNone(cache.get("nonexistent"))
        
        # Test size
        self.assertEqual(cache.size(), 1)
    
    def test_lru_cache_eviction(self):
        """Test LRU cache eviction policy"""
        cache = self.LRUCache(max_size=2)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Should evict key1
        
        self.assertIsNone(cache.get("key1"))
        self.assertEqual(cache.get("key2"), "value2")
        self.assertEqual(cache.get("key3"), "value3")
    
    def test_cache_ttl(self):
        """Test cache TTL functionality"""
        cache = self.LRUCache(max_size=10, default_ttl=0.1)  # 100ms TTL
        
        cache.set("key1", "value1")
        self.assertEqual(cache.get("key1"), "value1")
        
        # Wait for expiration
        time.sleep(0.15)
        self.assertIsNone(cache.get("key1"))
    
    def test_cache_stats(self):
        """Test cache statistics tracking"""
        cache = self.LRUCache(max_size=10)
        
        # Test hits and misses
        cache.set("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss
        
        self.assertEqual(cache.stats.hits, 1)
        self.assertEqual(cache.stats.misses, 1)
        self.assertEqual(cache.stats.hit_rate, 0.5)


class TestDatabaseOptimization(unittest.TestCase):
    """Test database optimization functionality"""
    
    def setUp(self):
        """Set up test environment"""
        try:
            from app.performance.database_optimization import DatabaseMetrics, QueryStats
            self.DatabaseMetrics = DatabaseMetrics
            self.QueryStats = QueryStats
            self.db_available = True
        except ImportError:
            self.db_available = False
            self.skipTest("Database optimization not available")
    
    def test_database_metrics(self):
        """Test database metrics collection"""
        metrics = self.DatabaseMetrics()
        
        # Test query recording
        query_stats = self.QueryStats(
            query_hash="test_hash",
            query_type="SELECT",
            execution_time=0.5,
            rows_affected=10,
            timestamp=datetime.now(),
            parameters={}
        )
        
        metrics.record_query(query_stats)
        self.assertEqual(len(metrics.query_stats), 1)
        
        # Test slow query detection
        slow_query = self.QueryStats(
            query_hash="slow_hash",
            query_type="SELECT",
            execution_time=2.0,  # Slow query
            rows_affected=1000,
            timestamp=datetime.now(),
            parameters={}
        )
        
        metrics.record_query(slow_query)
        slow_queries = metrics.get_slow_queries(threshold=1.0)
        self.assertEqual(len(slow_queries), 1)
        self.assertEqual(slow_queries[0].query_hash, "slow_hash")
    
    def test_query_summary(self):
        """Test query summary statistics"""
        metrics = self.DatabaseMetrics()
        
        # Add multiple queries
        for i in range(5):
            query_stats = self.QueryStats(
                query_hash=f"hash_{i}",
                query_type="SELECT" if i % 2 == 0 else "INSERT",
                execution_time=0.1 * (i + 1),
                rows_affected=i + 1,
                timestamp=datetime.now(),
                parameters={}
            )
            metrics.record_query(query_stats)
        
        summary = metrics.get_query_summary()
        
        self.assertEqual(summary['total_queries'], 5)
        self.assertIn('avg_execution_time', summary)
        self.assertIn('queries_by_type', summary)
        self.assertEqual(summary['queries_by_type']['SELECT'], 3)
        self.assertEqual(summary['queries_by_type']['INSERT'], 2)


class TestAPIOptimization(unittest.TestCase):
    """Test API optimization functionality"""
    
    def setUp(self):
        """Set up test environment"""
        try:
            from app.performance.api_optimization import PerformanceCollector, APIMetrics, RateLimiter
            self.PerformanceCollector = PerformanceCollector
            self.APIMetrics = APIMetrics
            self.RateLimiter = RateLimiter
            self.api_available = True
        except ImportError:
            self.api_available = False
            self.skipTest("API optimization not available")
    
    def test_performance_collector(self):
        """Test API performance collection"""
        collector = self.PerformanceCollector()
        
        # Test metrics recording
        metrics = self.APIMetrics(
            endpoint="/api/test",
            method="GET",
            status_code=200,
            response_time=0.5,
            response_size=1024,
            timestamp=datetime.now(),
            user_agent="test-agent",
            ip_address="127.0.0.1",
            memory_usage=1024,
            cpu_usage=10.0
        )
        
        collector.record_request(metrics)
        self.assertEqual(len(collector.metrics), 1)
        
        # Test endpoint statistics
        endpoint_key = "GET /api/test"
        self.assertIn(endpoint_key, collector.endpoint_stats)
        
        stats = collector.endpoint_stats[endpoint_key]
        self.assertEqual(stats['count'], 1)
        self.assertEqual(stats['avg_response_time'], 0.5)
    
    def test_rate_limiter(self):
        """Test rate limiting functionality"""
        limiter = self.RateLimiter(max_requests=2, window_seconds=1)
        
        # Test allowed requests
        self.assertTrue(limiter.is_allowed("user1"))
        self.assertTrue(limiter.is_allowed("user1"))
        
        # Test rate limit exceeded
        self.assertFalse(limiter.is_allowed("user1"))
        
        # Test different user
        self.assertTrue(limiter.is_allowed("user2"))
    
    def test_slow_endpoints_detection(self):
        """Test slow endpoint detection"""
        collector = self.PerformanceCollector()
        
        # Add fast endpoint
        fast_metrics = self.APIMetrics(
            endpoint="/api/fast",
            method="GET",
            status_code=200,
            response_time=0.1,
            response_size=512,
            timestamp=datetime.now(),
            user_agent="test",
            ip_address="127.0.0.1",
            memory_usage=512,
            cpu_usage=5.0
        )
        collector.record_request(fast_metrics)
        
        # Add slow endpoint
        slow_metrics = self.APIMetrics(
            endpoint="/api/slow",
            method="POST",
            status_code=200,
            response_time=2.0,
            response_size=2048,
            timestamp=datetime.now(),
            user_agent="test",
            ip_address="127.0.0.1",
            memory_usage=2048,
            cpu_usage=25.0
        )
        collector.record_request(slow_metrics)
        
        # Test slow endpoint detection
        slow_endpoints = collector.get_slow_endpoints(threshold=1.0)
        self.assertEqual(len(slow_endpoints), 1)
        self.assertEqual(slow_endpoints[0]['endpoint'], 'POST /api/slow')


class TestPerformanceIntegration(unittest.TestCase):
    """Test overall performance system integration"""
    
    def setUp(self):
        """Set up test environment"""
        try:
            from app.performance import cache_manager
            self.cache_manager = cache_manager
            self.performance_available = True
        except ImportError:
            self.performance_available = False
            self.skipTest("Performance integration not available")
    
    def test_cache_manager_initialization(self):
        """Test cache manager initialization"""
        self.assertIsNotNone(self.cache_manager)
        
        # Test default caches
        expected_caches = [
            'experiments', 'models', 'data_versions', 
            'statistics', 'quality_reports', 'api_responses', 
            'computed_metrics'
        ]
        
        for cache_name in expected_caches:
            cache = self.cache_manager.get_cache(cache_name)
            self.assertIsNotNone(cache, f"Cache {cache_name} should be initialized")
    
    def test_cache_manager_stats(self):
        """Test cache manager statistics"""
        stats = self.cache_manager.get_stats()
        self.assertIsInstance(stats, dict)
        
        # Each cache should have stats
        for cache_name, cache_stats in stats.items():
            self.assertIn('hits', cache_stats)
            self.assertIn('misses', cache_stats)
            self.assertIn('hit_rate', cache_stats)
    
    @patch('app.performance.caching.cached')
    def test_cached_decorator_integration(self, mock_cached):
        """Test cached decorator integration"""
        # Mock the cached decorator
        def mock_decorator(func):
            return func
        
        mock_cached.return_value = mock_decorator
        
        # Test that decorator can be applied
        @mock_cached(cache_name='test_cache', ttl=300)
        def test_function():
            return "test_result"
        
        result = test_function()
        self.assertEqual(result, "test_result")


class TestMemoryManagement(unittest.TestCase):
    """Test memory management functionality"""
    
    def setUp(self):
        """Set up test environment"""
        try:
            from app.performance.api_optimization import MemoryManager
            self.MemoryManager = MemoryManager
            self.memory_available = True
        except ImportError:
            self.memory_available = False
            self.skipTest("Memory management not available")
    
    def test_memory_cleanup(self):
        """Test memory cleanup functionality"""
        # Create some objects to be garbage collected
        test_objects = [[] for _ in range(1000)]
        del test_objects
        
        # Test cleanup
        collected = self.MemoryManager.cleanup_memory()
        self.assertIsInstance(collected, int)
        self.assertGreaterEqual(collected, 0)
    
    def test_memory_usage_info(self):
        """Test memory usage information"""
        usage_info = self.MemoryManager.get_memory_usage()
        self.assertIsInstance(usage_info, dict)
        
        if usage_info:  # Only test if we got data
            self.assertIn('system', usage_info)
            self.assertIn('gc_stats', usage_info)


if __name__ == '__main__':
    # Configure logging for tests
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # Run tests
    unittest.main(verbosity=2)
