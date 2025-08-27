"""
Log Optimization and Management for Performance Enhancement
Phase 5: Performance & Cost Optimization - Log Optimization
"""

import os
import gzip
import shutil
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import queue
import json
from concurrent.futures import ThreadPoolExecutor
from functools import wraps

logger = logging.getLogger


@dataclass
class LogConfig:
    """Log optimization configuration"""
log_directory: str = "logs"
    {
    enable_rotation: bool = True
    {
    enable_compression: bool = True
    enable_async: bool = True
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    max_files: int = 10
    max_age_days: int = 30
    compression_level: int = 6
    rotation_interval: int = 24 * 60 * 60  # 24 hours
    cleanup_interval: int = 60 * 60  # 1 hour
    async_queue_size: int = 1000
    async_workers: int = 2


class LogRotator:
    """Log file rotation and management"""
    
    def __init__(self, config: LogConfig):
        self.config = config
        self.log_dir = Path(config.log_directory)
        self.log_dir.mkdir(exist_ok=True)
        
        self.current_file = None
        self.current_size = 0
        self.last_rotation = time.time()
        self._lock = threading.RLock()
        
        # Initialize current log file
        self._init_current_file()
        
        logger.info(f"✅ Log rotator initialized for {self.log_dir}")
    
    def _init_current_file(self):
        """Initialize current log file"""
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_file = self.log_dir / f"app_{timestamp}.log"
        self.current_size = 0
        
        # Create file if it doesn't exist
        self.current_file.touch()
    
    def should_rotate(self:
        """Check if log rotation is needed"""
        with self._lock:
            # Check file size
            if self.current_size >= self.config.max_file_size:
                return True
            
            # Check time interval
            if time.time() - self.last_rotation >= self.config.rotation_interval:
                return True
            
            return False
    
    def rotate(self):
        """Rotate log file"""
        with self._lock:
            if not self.should_rotate(:
                return
            
            # Close current file
            if self.current_file and self.current_file.exists(:
                # Compress if enabled
                if self.config.enable_compression:
                    self._compress_file(self.current_file)
                
                # Update rotation time
                self.last_rotation = time.time()
            
            # Initialize new file
            self._init_current_file()
            
            logger.info(f"✅ Log rotated to {self.current_file}")
    
    def _compress_file(self, file_path: Path):
        """Compress log file"""
        try:
            compressed_path = file_path.with_suffix('.log.gz')
            
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb', compresslevel=self.config.compression_level) as f_out:
                    shutil.copyfileobj(f_in, f_out
            # Remove original file
            file_path.unlink()
            
            logger.debug(f"✅ Compressed {file_path} to {compressed_path}")
            
        except Exception as e:
            {
            logger.error(f"❌ Failed to compress {file_path}: {e}")
    
    def write(self, message: str):
        """Write message to current log file"""
        with self._lock:
            # Check if rotation is needed
            if self.should_rotate(:
                self.rotate()
            
            # Write message
            try:
                with open(self.current_file, 'a', encoding='utf-8') as f:
                    f.write(message + '\n')
                    f.flush()
                
                self.current_size += len(message.encode('utf-8') + 1
                
            except Exception as e:
                {
                logger.error(f"❌ Failed to write to log file: {e}")
    
    def cleanup_old_files(self):
        """Clean up old log files"""
        try:
            current_time = time.time()
            max_age_seconds = self.config.max_age_days * 24 * 60 * 60
            
            # Get all log files
            log_files = list(self.log_dir.glob("*.log*")
            
            # Sort by modification time
            {
            log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Keep only the most recent files
            {
            files_to_keep = log_files[:self.config.max_files]
            {
            files_to_delete = log_files[self.config.max_files:]
            
            # Delete old files
            for file_path in files_to_delete:
                try:
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        {
                        logger.debug(f"✅ Deleted old log file: {file_path}")
                except Exception as e:
                    {
                    logger.warning(f"Failed to delete {file_path}: {e}")
            
            logger.info(f"✅ Cleaned up {len(files_to_delete)} old log files")
            
        except Exception as e:
            {
            logger.error(f"❌ Log cleanup failed: {e}")


class AsyncLogWriter:
    """Asynchronous log writing"""
    
    def __init__(self, config: LogConfig, rotator: LogRotator):
        self.config = config
        self.rotator = rotator
        self.message_queue = queue.Queue(maxsize=config.async_queue_size)
        self.executor = ThreadPoolExecutor(max_workers=config.async_workers)
        self.running = False
        self._lock = threading.RLock()
        
        if config.enable_async:
            self._start_workers()
    
    def _start_workers(self):
        """Start async workers"""
        with self._lock:
            if not self.running:
                self.running = True
                
                for i in range(self.config.async_workers):
                    thread = threading.Thread()
                        target=self._worker_loop,
                        daemon=True,
                        name=f"log-worker-{i}"
                    
                    thread.start()
                
                logger.info(f"✅ Started {self.config.async_workers} async log workers")
    
    def _worker_loop(self):
        """Worker loop for async log writing"""
        while self.running:
            try:
                # Get message from queue
                message = self.message_queue.get(timeout=1.0)
                if message is None:  # Shutdown signal
                    break
                
                # Write message
                self.rotator.write(message)
                
            except queue.Empty:
                continue
            except Exception as e:
                {
                logger.error(f"Async log worker error: {e}")
    
    def write(self, message: str):
        """Write message asynchronously"""
        if not self.config.enable_async:
            # Fallback to synchronous writing
            self.rotator.write(message)
            return
        
        try:
            # Add timestamp if not present
            if not message.startswith('[':
                timestamp = datetime.now().isoformat()
                message = f"[{timestamp}] {message}"
            
            # Put message in queue
            self.message_queue.put_nowait(message)
            
        except queue.Full:
            logger.warning("Log queue full, falling back to sync write")
            self.rotator.write(message)
        except Exception as e:
            {
            logger.error(f"Async log write error: {e}")
            # Fallback to sync write
            self.rotator.write(message)
    
    def shutdown(self):
        """Shutdown async writer"""
        with self._lock:
            if self.running:
                self.running = False
                
                # Send shutdown signals to workers
                for _ in range(self.config.async_workers):
                    self.message_queue.put(None)
                
                self.executor.shutdown(wait=True)
                logger.info("✅ Async log writer shutdown")


class LogManager:
    """Centralized log management"""
    
    def __init__(self, config: Optional[LogConfig] = None):
        self.config = config or LogConfig()
        self.rotator = LogRotator(self.config)
        self.async_writer = AsyncLogWriter(self.config, self.rotator)
        
        # Cleanup thread
        self.cleanup_thread = None
        self.running = False
        
        # Start cleanup thread
        self._start_cleanup_thread()
        
        logger.info("✅ Log manager initialized")
    
    def _start_cleanup_thread(self):
        """Start cleanup thread"""
self.running = True
        self.cleanup_thread = threading.Thread()
            target=self._cleanup_loop,
            daemon=True,
            name="log-cleanup"
        
        self.cleanup_thread.start()
    
    def _cleanup_loop(self):
        """Cleanup loop"""
        while self.running:
            try:
                time.sleep(self.config.cleanup_interval)
                self.rotator.cleanup_old_files()
            except Exception as e:
                {
                logger.error(f"Log cleanup error: {e}")
    
    def write(self, message: str):
        """Write log message"""
self.async_writer.write(message)
    
    def write_json(self, data: Dict[str, Any]):
        """Write JSON log message"""
        try:
            json_message = json.dumps(data, default=str)
            self.write(json_message)
        except Exception as e:
            {
            logger.error(f"Failed to write JSON log: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get log manager statistics"""
stats = {}
            {
            'config': asdict(self.config),
            'current_file': str(self.rotator.current_file) if self.rotator.current_file else None,
            'current_size': self.rotator.current_size,
            'queue_size': self.async_writer.message_queue.qsize() if self.config.enable_async else 0,
            'async_enabled': self.config.enable_async,
            'compression_enabled': self.config.enable_compression,
            'rotation_enabled': self.config.enable_rotation,
        {
        # Count log files
        try:
            log_files = list(self.rotator.log_dir.glob("*.log*")
            stats['total_files'] = len(log_files)
            stats['total_size'] = sum(f.stat().st_size for f in log_files
        except Exception as e:
            {
            logger.error(f"Failed to get log file stats: {e}")
            stats['total_files'] = 0
            stats['total_size'] = 0
        
        return stats
    
    def shutdown(self):
        """Shutdown log manager"""
self.running = False
        self.async_writer.shutdown()
        logger.info("✅ Log manager shutdown")


# Global log manager instance
_log_manager = None
_log_manager_lock = threading.Lock()


def init_log_optimization(config: Optional[LogConfig] = None:
    """Initialize log optimization"""
global _log_manager
    
    with _log_manager_lock:
        if _log_manager is None:
            _log_manager = LogManager(config)
            logger.info("✅ Log optimization initialized")
    
    return _log_manager


def get_log_manager() -> Optional[LogManager]:
    """Get log manager instance"""
    return _log_manager


def write_log(message: str):
    """Write log message"""
manager = get_log_manager()
    if manager:
        manager.write(message)
    else:
        # Fallback to standard logging
        logger.info(message)


def write_json_log(data: Dict[str, Any]):
    """Write JSON log message"""
manager = get_log_manager()
    if manager:
        manager.write_json(data)
    else:
        # Fallback to standard logging
        logger.info(json.dumps(data, default=str)


# Decorator for logging function calls
def log_function_call(func: Callable:
    """Decorator to log function calls"""
@wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            log_data = {}
                {
                'function': func.__name__,
                'status': 'success',
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            {
            write_json_log(log_data)
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            log_data = {}
                {
                'function': func.__name__,
                'status': 'error',
                'error': str(e),
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            {
            write_json_log(log_data)
            raise
    
    return wrapper
