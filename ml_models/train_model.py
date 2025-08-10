#!/usr/bin/env python3
"""
Training Script for Anomaly Detection Model
Trains and validates the ML anomaly detection model
"""

import logging
import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ml_models import AnomalyDetector

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main training function."""
    try:
        logger.info("Starting anomaly detection model training...")

        # Initialize anomaly detector
        detector = AnomalyDetector()

        # Train model
        logger.info("Training model...")
        results = detector.train_model()

        # Display results
        logger.info("Training completed!")
        logger.info(f"Status: {results['status']}")

        if results["status"] == "success":
            logger.info(f"F1 Score: {results['f1_score']:.3f}")
            logger.info(f"Precision: {results['precision']:.3f}")
            logger.info(f"Recall: {results['recall']:.3f}")
            logger.info(f"Data shape: {results['data_shape']}")
            logger.info(f"Feature count: {results['feature_count']}")

            # Test inference
            logger.info("Testing inference...")
            test_metrics = {
                "cpu_usage_avg": 45.2,
                "cpu_usage_max": 78.9,
                "memory_usage_pct": 65.3,
                "disk_usage_pct": 42.1,
                "network_bytes_total": 1250.5,
                "request_rate": 15.2,
                "response_time_p95": 0.23,
            }

            result = detector.detect_anomaly(test_metrics)
            logger.info(f"Inference test result: {result}")

        elif results["status"] == "skipped":
            logger.info(f"Reason: {results['reason']}")

        else:
            logger.error(f"Training failed: {results['reason']}")
            return 1

        return 0

    except Exception as e:
        logger.error(f"Error in training script: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
