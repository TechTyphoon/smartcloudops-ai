#!/usr/bin/env python3
"""
Example Usage Script for ML Models Package
Demonstrates how to use the anomaly detection system
"""

import logging
import sys
import os
from datetime import datetime, timedelta

# Add the project root to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def basic_usage_example():
    """Demonstrate basic usage of the anomaly detector."""
    try:
        from ml_models import create_anomaly_detector, get_package_info
        
        # Get package information
        logger.info("=== Package Information ===")
        info = get_package_info()
        for key, value in info.items():
            logger.info(f"{key}: {value}")
        
        # Create detector
        logger.info("\n=== Creating Anomaly Detector ===")
        detector = create_anomaly_detector()
        logger.info("Detector created successfully")
        
        # Get system status
        logger.info("\n=== System Status ===")
        status = detector.get_system_status()
        logger.info(f"Initialized: {status.get('initialized', 'N/A')}")
        logger.info(f"Model exists: {status.get('model_exists', 'N/A')}")
        logger.info(f"Model path: {status.get('model_path', 'N/A')}")
        
        # Check if model is loaded
        if 'model_info' in status:
            logger.info(f"Model info: {status['model_info']}")
        else:
            logger.info("Model not yet loaded (needs training)")
        
        return True
        
    except Exception as e:
        logger.error(f"Error in basic usage example: {e}")
        return False

def production_detector_example():
    """Demonstrate production detector usage."""
    try:
        from ml_models import create_production_detector
        
        logger.info("\n=== Production Detector Example ===")
        detector = create_production_detector()
        logger.info("Production detector created successfully")
        
        # Example metrics
        test_metrics = {
            'cpu_usage_avg': 85.0,
            'cpu_usage_max': 95.0,
            'memory_usage_pct': 80.0,
            'disk_usage_pct': 75.0,
            'network_bytes_total': 1500.0,
            'request_rate': 25.0,
            'response_time_p95': 0.5
        }
        
        logger.info(f"Testing with metrics: {test_metrics}")
        
        # Detect anomalies
        result = detector.detect_anomalies_production(test_metrics)
        logger.info(f"Detection result: {result}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error in production detector example: {e}")
        return False

def quick_start_demo():
    """Show the quick start example."""
    try:
        from ml_models import get_quick_start_example
        
        logger.info("\n=== Quick Start Example ===")
        example = get_quick_start_example()
        logger.info(example)
        
        return True
        
    except Exception as e:
        logger.error(f"Error in quick start demo: {e}")
        return False

def health_check_example():
    """Demonstrate package health validation."""
    try:
        from ml_models import validate_package_health, get_usage_statistics
        
        logger.info("\n=== Package Health Check ===")
        health = validate_package_health()
        logger.info(f"Package healthy: {health['healthy']}")
        
        for check_name, check_result in health['checks'].items():
            logger.info(f"{check_name}: {check_result}")
        
        if health['warnings']:
            logger.info("Warnings:")
            for warning in health['warnings']:
                logger.info(f"  - {warning}")
        
        if health['errors']:
            logger.info("Errors:")
            for error in health['errors']:
                logger.error(f"  - {error}")
        
        logger.info("\n=== Usage Statistics ===")
        stats = get_usage_statistics()
        logger.info(f"Package version: {stats['package_version']}")
        logger.info(f"Available models: {len(stats['available_models'])}")
        logger.info(f"Config files: {len(stats['config_files'])}")
        logger.info(f"Data files: {len(stats['data_files'])}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error in health check example: {e}")
        return False

def main():
    """Run all examples."""
    logger.info("Starting ML Models Package Examples")
    logger.info("=" * 50)
    
    # Run examples
    examples = [
        ("Basic Usage", basic_usage_example),
        ("Production Detector", production_detector_example),
        ("Quick Start Demo", quick_start_demo),
        ("Health Check", health_check_example)
    ]
    
    results = {}
    for name, func in examples:
        logger.info(f"\nRunning {name} example...")
        try:
            results[name] = func()
        except Exception as e:
            logger.error(f"Failed to run {name}: {e}")
            results[name] = False
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("EXAMPLE EXECUTION SUMMARY")
    logger.info("=" * 50)
    for name, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        logger.info(f"{name}: {status}")
    
    return all(results.values())

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 