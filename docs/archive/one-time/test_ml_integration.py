#!/usr/bin/env python3
"""
Test ML model integration with the Flask application
"""

import os
import random
import sys
import time
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(__file__))

from ml_models import AnomalyDetector


def test_ml_pipeline():
    """Test the complete ML anomaly detection pipeline."""
    print("🧪 Testing ML Anomaly Detection Pipeline")
    print("=" * 50)

    try:
        # Initialize anomaly detector
        print("1. Initializing anomaly detector...")
        detector = AnomalyDetector()
        print("✅ Anomaly detector initialized")

        # Check system status
        print("\n2. Checking system status...")
        status = detector.get_system_status()
        print(f"✅ System status: {status['initialized']}")
        print(f"   Model exists: {status['model_exists']}")

        # Test anomaly detection
        print("\n3. Testing anomaly detection...")
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
        print(f"✅ Anomaly detection result:")
        print(f"   Status: {result['status']}")
        print(f"   Is anomaly: {result['is_anomaly']}")
        print(f"   Severity score: {result['severity_score']:.3f}")
        print(f"   Explanation: {result['explanation']}")

        # Test batch detection
        print("\n4. Testing batch anomaly detection...")
        batch_metrics = [
            test_metrics,
            {
                "cpu_usage_avg": 85.5,
                "cpu_usage_max": 95.2,
                "memory_usage_pct": 88.7,
                "disk_usage_pct": 75.3,
                "network_bytes_total": 2500.8,
                "request_rate": 45.6,
                "response_time_p95": 1.25,
            },
        ]

        batch_results = detector.batch_detect(batch_metrics)
        print(f"✅ Batch detection results:")
        for i, result in enumerate(batch_results):
            print(
                f"   Sample {i+1}: Anomaly={result['is_anomaly']}, Severity={result['severity_score']:.3f}"
            )

        # Test model retraining
        print("\n5. Testing model retraining...")
        train_result = detector.retrain_model()
        print(f"✅ Training result:")
        print(f"   Status: {train_result['status']}")
        if train_result["status"] == "success":
            print(f"   F1 Score: {train_result['f1_score']:.3f}")
            print(f"   Precision: {train_result['precision']:.3f}")
            print(f"   Recall: {train_result['recall']:.3f}")

        # Test feature importance
        print("\n6. Testing feature information...")
        feature_info = detector.get_feature_importance()
        print(f"✅ Feature information:")
        print(f"   Feature count: {feature_info['feature_count']}")
        print(f"   Features: {feature_info['features'][:5]}...")  # Show first 5

        print("\n🎉 All ML tests passed successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_model_quality():
    """Test model quality metrics."""
    print("\n🔍 Testing Model Quality")
    print("=" * 30)

    try:
        detector = AnomalyDetector()

        # Test with normal metrics
        normal_metrics = {
            "cpu_usage_avg": 25.0,
            "cpu_usage_max": 35.0,
            "memory_usage_pct": 45.0,
            "disk_usage_pct": 30.0,
            "network_bytes_total": 500.0,
            "request_rate": 5.0,
            "response_time_p95": 0.1,
        }

        normal_result = detector.detect_anomaly(normal_metrics)
        print(f"✅ Normal metrics test:")
        print(f"   Is anomaly: {normal_result['is_anomaly']}")
        print(f"   Severity: {normal_result['severity_score']:.3f}")

        # Test with anomalous metrics
        anomalous_metrics = {
            "cpu_usage_avg": 95.0,
            "cpu_usage_max": 98.0,
            "memory_usage_pct": 95.0,
            "disk_usage_pct": 95.0,
            "network_bytes_total": 5000.0,
            "request_rate": 100.0,
            "response_time_p95": 5.0,
        }

        anomalous_result = detector.detect_anomaly(anomalous_metrics)
        print(f"✅ Anomalous metrics test:")
        print(f"   Is anomaly: {anomalous_result['is_anomaly']}")
        print(f"   Severity: {anomalous_result['severity_score']:.3f}")

        return True

    except Exception as e:
        print(f"❌ Quality test failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Smart CloudOps AI - ML Integration Test")
    print("=" * 50)

    # Run tests
    success1 = test_ml_pipeline()
    success2 = test_model_quality()

    if success1 and success2:
        print("\n🎉 All tests passed! ML integration is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)
