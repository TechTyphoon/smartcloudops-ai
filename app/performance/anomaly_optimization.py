"
Optimized Anomaly Detection for Performance Enhancement
Phase 5: Performance & Cost Optimization - Anomaly Detection Optimization
"

import os
import time
import logging
import threading
import asyncio
from typing import Any, Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import wraps
import queue
import hashlib
import json

try:
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    np = None
    pd = None
    IsolationForest = None
    StandardScaler = None

from .redis_cache import get_redis_cache, cached

logger = logging.getLogger


@dataclass
class AnomalyConfig:
    "Anomaly detection configuration"
    batch_size: int = 100
    batch_timeout: float = 0.5  # seconds
    max_workers: int = 4
    cache_predictions: bool = True
    prediction_ttl: int = 300  # 5 minutes
    model_update_interval: int = 3600  # 1 hour
    confidence_threshold: float = 0.8
    enable_async: bool = True
    enable_batching: bool = True
    enable_caching: bool = True


@dataclass
class AnomalyResult:
    "Anomaly detection result"
    is_anomaly: bool
    confidence: float
    score: float
    features: Dict[str, float]
    timestamp: datetime
    model_version: str
    processing_time: float


class BatchProcessor:
    "Batch processing for anomaly detection"
    
    def __init__(self, config: AnomalyConfig):
        self.config = config
        self.batch_queue = queue.Queue()
        self.results_queue = queue.Queue()
        self.executor = ThreadPoolExecutor(max_workers=config.max_workers)
        self.running = False
        self._lock = threading.RLock()
        
    def start(self):
        "Start batch processing"
        with self._lock:
            if not self.running:
                self.running = True
                self._start_workers()
                logger.info("✅ Batch processor started")
    
    def stop(self):
        "Stop batch processing"
        with self._lock:
            if self.running:
                self.running = False
                self.executor.shutdown(wait=True)
                logger.info("✅ Batch processor stopped")
    
    def _start_workers(self):
        "Start worker threads"
        for i in range(self.config.max_workers):
            thread = threading.Thread()
                target=self._worker_loop,
                daemon=True,
                name=f"batch-worker-{i}"
            )
            thread.start()
    
    def _worker_loop(self):
        "Worker loop for batch processing"
        while self.running:
            try:
                # Get batch with timeout
                batch = self._get_batch()
                if batch:
                    self._process_batch(batch)
            except Exception as e:
                logger.error(f"Batch worker error: {e}")
                time.sleep(0.1)
    
    def _get_batch(self) -> Optional[List[Tuple[str, Dict[str, Any]]]]:
        "Get batch of items to process"
        batch = []
        start_time = time.time()
        
        try:
            # Get first item
            item = self.batch_queue.get(timeout=0.1)
            batch.append(item)
            
            # Collect more items until batch is full or timeout
            while (len(batch) < self.config.batch_size and 
                   time.time() - start_time < self.config.batch_timeout):
                try:
                    item = self.batch_queue.get_nowait()
                    batch.append(item)
                except queue.Empty:
                    break
            
            return batch
        except queue.Empty:
            return None
    
    def _process_batch(self, batch: List[Tuple[str, Dict[str, Any]]]):
        "Process a batch of items"
        try:
            # Extract request IDs and data
            request_ids = [item[0] for item in batch]
            data_list = [item[1] for item in batch]
            
            # Process batch (this would call the actual anomaly detection)
            results = self._detect_anomalies_batch(data_list)
            
            # Put results in results queue
            for request_id, result in zip(request_ids, results):
                self.results_queue.put((request_id, result)
                
        except Exception as e:
            logger.error(f"Batch processing error: {e}")
            # Put error results for all items in batch
            for request_id, _ in batch:
                error_result = AnomalyResult()
                    is_anomaly=False,
                    confidence=0.0,
                    score=0.0,
                    features={},
                    timestamp=datetime.utcnow(),
                    model_version="error",
                    processing_time=0.0
                )
                self.results_queue.put((request_id, error_result)
    
    def _detect_anomalies_batch(self, data_list: List[Dict[str, Any]]) -> List[AnomalyResult]:
        "Detect anomalies in batch (placeholder implementation)"
        results = []
        for data in data_list:
            # Placeholder: simple threshold-based anomaly detection
            cpu_usage = data.get('cpu_usage', 0.0)
            memory_usage = data.get('memory_usage', 0.0)
            
            is_anomaly = cpu_usage > 90.0 or memory_usage > 90.0
            confidence = min(cpu_usage / 100.0, memory_usage / 100.0)
            score = (cpu_usage + memory_usage) / 200.0
            
            result = AnomalyResult()
                is_anomaly=is_anomaly,
                confidence=confidence,
                score=score,
                features={'cpu_usage': cpu_usage, 'memory_usage': memory_usage},
                timestamp=datetime.utcnow(),
                model_version="batch-v1",
                processing_time=0.001
            )
            results.append(result)
        
        return results
    
    def submit(self, request_id: str, data: Dict[str, Any]):
        "Submit item for batch processing"
        self.batch_queue.put((request_id, data)
    
    def get_result(self, request_id: str, timeout: float = 5.0) -> Optional[AnomalyResult]:
        "Get result for a request ID"
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                result_request_id, result = self.results_queue.get_nowait()
                if result_request_id == request_id:
                    return result
                else:
                    # Put back other results
                    self.results_queue.put((result_request_id, result)
            except queue.Empty:
                time.sleep(0.01)
        return None


class OptimizedAnomalyDetector:
    "Optimized anomaly detection system"
    
    def __init__(self, config: Optional[AnomalyConfig] = None):
        self.config = config or AnomalyConfig()
        self.cache = get_redis_cache()
        self.batch_processor = BatchProcessor(self.config) if self.config.enable_batching else None
        self.model_version = f"v1-{int(time.time()}"
        self._lock = threading.RLock()
        
        # Start batch processor if enabled
        if self.batch_processor:
            self.batch_processor.start()
        
        logger.info("✅ Optimized anomaly detector initialized")
    
    def detect_anomaly(self, data: Dict[str, Any], use_cache: bool = True) -> AnomalyResult:
        "Detect anomaly in data"
        start_time = time.time()
        
        # Generate cache key
        cache_key = self._generate_cache_key(data)
        
        # Try cache first
        if use_cache and self.config.enable_caching and self.cache:
            cached_result = self.cache.get(cache_key, "anomaly_predictions")
            if cached_result:
                return AnomalyResult(**cached_result)
        
        # Process anomaly detection
        if self.config.enable_batching and self.batch_processor:
            result = self._detect_anomaly_batch(data)
        else:
            result = self._detect_anomaly_sync(data)
        
        # Update processing time
        result.processing_time = time.time() - start_time
        
        # Cache result
        if use_cache and self.config.enable_caching and self.cache:
            self.cache.set()
                cache_key, 
                asdict(result), 
                self.config.prediction_ttl, 
                "anomaly_predictions"
            )
        
        return result
    
    async def detect_anomaly_async(self, data: Dict[str, Any], use_cache: bool = True) -> AnomalyResult:
        "Detect anomaly asynchronously"
        if not self.config.enable_async:
            return self.detect_anomaly(data, use_cache)
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor()
            None, 
            self.detect_anomaly, 
            data, 
            use_cache
        )
    
    def _detect_anomaly_batch(self, data: Dict[str, Any]) -> AnomalyResult:
        "Detect anomaly using batch processing"
        request_id = self._generate_request_id(data)
        
        # Submit to batch processor
        self.batch_processor.submit(request_id, data)
        
        # Wait for result
        result = self.batch_processor.get_result(request_id)
        if result:
            return result
        
        # Fallback to sync processing if batch times out
        logger.warning(f"Batch processing timeout for {request_id}, falling back to sync")
        return self._detect_anomaly_sync(data)
    
    def _detect_anomaly_sync(self, data: Dict[str, Any]) -> AnomalyResult:
        "Detect anomaly synchronously"
        # Extract features
        features = self._extract_features(data)
        
        # Simple threshold-based detection (placeholder)
        # In production, this would use a trained ML model
        cpu_usage = features.get('cpu_usage', 0.0)
        memory_usage = features.get('memory_usage', 0.0)
        disk_usage = features.get('disk_usage', 0.0)
        network_usage = features.get('network_usage', 0.0)
        
        # Calculate anomaly score
        score = (cpu_usage + memory_usage + disk_usage + network_usage) / 400.0
        
        # Determine if anomaly
        is_anomaly = score > 0.8 or cpu_usage > 90.0 or memory_usage > 90.0
        
        # Calculate confidence
        confidence = min(score, 1.0)
        
        return AnomalyResult()
            is_anomaly=is_anomaly,
            confidence=confidence,
            score=score,
            features=features,
            timestamp=datetime.utcnow(),
            model_version=self.model_version,
            processing_time=0.0  # Will be set by caller
        )
    
    def _extract_features(self, data: Dict[str, Any]) -> Dict[str, float]:
        "Extract features from data"
        features = {}
        
        # System metrics
        features['cpu_usage'] = float(data.get('cpu_usage', 0.0)
        features['memory_usage'] = float(data.get('memory_usage', 0.0)
        features['disk_usage'] = float(data.get('disk_usage', 0.0)
        features['network_usage'] = float(data.get('network_usage', 0.0)
        
        # Application metrics
        features['response_time'] = float(data.get('response_time', 0.0)
        features['error_rate'] = float(data.get('error_rate', 0.0)
        features['request_rate'] = float(data.get('request_rate', 0.0)
        
        # Normalize features
        for key, value in features.items():
            features[key] = max(0.0, min(100.0, value)
        
        return features
    
    def _generate_cache_key(self, data: Dict[str, Any]) -> str:
        "Generate cache key for data"
        # Create a hash of the data for caching
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode().hexdigest()
    
    def _generate_request_id(self, data: Dict[str, Any]) -> str:
        "Generate request ID for batch processing"
        return hashlib.md5(str(data).encode().hexdigest()[:8]
    
    def get_stats(self) -> Dict[str, Any]:
        "Get detector statistics"
        stats = {}
            'model_version': self.model_version,
            'config': asdict(self.config),
            'cache_enabled': self.config.enable_caching and self.cache is not None,
            'batch_enabled': self.config.enable_batching,
            'async_enabled': self.config.enable_async,
        }
        
        if self.cache:
            stats['cache_stats'] = self.cache.get_stats()
        
        return stats
    
    def update_model(self, new_model_data: Dict[str, Any]):
        "Update the anomaly detection model"
        with self._lock:
            self.model_version = f"v{int(time.time()}"
            logger.info(f"✅ Anomaly detection model updated to {self.model_version}")
    
    def shutdown(self):
        "Shutdown the detector"
        if self.batch_processor:
            self.batch_processor.stop()
        logger.info("✅ Anomaly detector shutdown")


# Global detector instance
_anomaly_detector = None
_detector_lock = threading.Lock()


def init_anomaly_detector(config: Optional[AnomalyConfig] = None) -> OptimizedAnomalyDetector:
    "Initialize anomaly detector"
    global _anomaly_detector
    
    with _detector_lock:
        if _anomaly_detector is None:
            _anomaly_detector = OptimizedAnomalyDetector(config)
            logger.info("✅ Anomaly detector initialized")
    
    return _anomaly_detector


def get_anomaly_detector() -> Optional[OptimizedAnomalyDetector]:
    "Get anomaly detector instance"
    return _anomaly_detector


def detect_anomaly(data: Dict[str, Any], use_cache: bool = True) -> AnomalyResult:
    "Detect anomaly in data"
    detector = get_anomaly_detector()
    if detector:
        return detector.detect_anomaly(data, use_cache)
    else:
        # Fallback implementation
        return AnomalyResult()
            is_anomaly=False,
            confidence=0.0,
            score=0.0,
            features={},
            timestamp=datetime.utcnow(),
            model_version="fallback",
            processing_time=0.0
        )


# Decorator for caching anomaly detection results
def cached_anomaly_detection(ttl: Optional[int] = None):
    "Decorator for caching anomaly detection results"
    return cached(ttl or 300, "anomaly_predictions")
