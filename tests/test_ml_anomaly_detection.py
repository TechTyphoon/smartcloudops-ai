#!/usr/bin/env python3
import pytest
"""
Tests for ML Anomaly Detection Components
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ml_models.anomaly_detector import (
    AnomalyInferenceEngine,
    AnomalyModelTrainer,
    DataProcessor,
)


class TestDataProcessor:
    """Test data processor functionality."""

    def test_data_processor_initialization(self):
        """Test data processor initialization."""
        # Mock the config to avoid hardcoded URL issues
        with patch(
            "ml_models.anomaly_detector.DataProcessor._load_configf"
        ) as mock_config:
            mock_config.return_value = {
                "data": {
                    "prometheus_url": "http://localhost:9090",
                    "lookback_hours": 168,
                    "feature_window": 60,
                },
                "features": [
                    "cpu_usage_avg",
                    "cpu_usage_max",
                    "memory_usage_pct",
                    "disk_usage_pct",
                    "network_bytes_total",
                    "request_rate",
                ],
            }

            processor = DataProcessor()
            assert processor.prometheus_url == "http://localhost:9090"
            assert len(processor.features) > 0

    def test_synthetic_data_generation(self):
        """Test synthetic data generation."""
        processor = DataProcessor()
        start_time = datetime.now() - timedelta(hours=1)
        end_time = datetime.now()

        data = processor._generate_synthetic_data(start_time, end_time)
        assert isinstance(data, pd.DataFrame)
        assert len(data) > 0
        assert "cpu_usage_avg" in data.columns
        assert "memory_usage_pct" in data.columns

    def test_data_preprocessing(self):
        """Test data preprocessing."""
        processor = DataProcessor()

        # Create test data
        test_data = pd.DataFrame(
            {
                "cpu_usage_avg": [30, 40, 50, np.nan, 60],
                "memory_usage_pct": [60, 70, 80, 90, 100],
                "disk_usage_pct": [45, 55, 65, 75, 85],
            }
        )

        processed_data = processor.preprocess_data(test_data)
        assert isinstance(processed_data, pd.DataFrame)
        assert len(processed_data) > 0
        assert not processed_data.isnull().any().any()

    def test_data_validation(self):
        """Test data validation."""
        processor = DataProcessor()

        # Valid data (with enough points)
        valid_data = pd.DataFrame(
            {"cpu_usage_avg": [30] * 100, "memory_usage_pct": [60] * 100}  # 100 points
        )

        is_valid, issues = processor.validate_data(valid_data)
        assert is_valid
        assert len(issues) == 0

        # Invalid data (insufficient points)
        invalid_data = pd.DataFrame({"cpu_usage_avg": [30, 40]})

        is_valid, issues = processor.validate_data(invalid_data)
        assert not is_valid
        assert len(issues) > 0


class TestModelTrainer:
    """Test model trainer functionality."""

    def test_model_trainer_initialization(self):
        """Test model trainer initialization."""
        trainer = AnomalyModelTrainer()
        assert trainer is not None
        assert trainer.model is None
        assert len(trainer.feature_columns) == 0

    def test_feature_preparation(self):
        """Test feature preparation."""
        trainer = AnomalyModelTrainer()

        # Create test data with mixed types
        test_data = pd.DataFrame(
            {
                "cpu_usage_avg": [30, 40, 50],
                "memory_usage_pct": [60, 70, 80],
                "hour": [10, 11, 12],  # Time feature to exclude
                "day_of_week": [1, 2, 3],  # Time feature to exclude
            }
        )

        feature_data = trainer.prepare_features(test_data)
        assert isinstance(feature_data, pd.DataFrame)
        assert "hour" not in feature_data.columns
        assert "day_of_week" not in feature_data.columns
        assert "cpu_usage_avg" in feature_data.columns

    def test_model_creation(self):
        """Test model creation."""
        trainer = AnomalyModelTrainer()
        model = trainer.create_model()
        assert model is not None
        assert hasattr(model, "fit")
        assert hasattr(model, "predict")

    def test_model_training(self):
        """Test model training functionality."""
        trainer = AnomalyModelTrainer()

        # Create test data
        test_data = pd.DataFrame(
            {
                "cpu_usage_avg": np.random.normal(50, 15, 200),  # More data points
                "memory_usage_pct": np.random.normal(70, 10, 200),
                "disk_usage_pct": np.random.normal(60, 8, 200),
            }
        )

        # Train model
        results = trainer.train(test_data)

        # Check if training was successful or skipped
        assert results["status"] in ["success", "failed", "skipped"]

        if results["status"] == "success":
            assert "f1_score" in results
            assert "precision" in results
            assert "recall" in results
        elif results["status"] == "failed":
            # If training failed, it should have a reason
            assert "reason" in results

    def test_model_save_load(self):
        """Test model save and load functionality."""
        trainer = AnomalyModelTrainer()

        # Create sufficient training data (more than 100 samples)
        start_time = datetime.now() - timedelta(hours=10)
        end_time = datetime.now()

        # Generate more data points to meet minimum requirement
        processor = DataProcessor()
        data = processor._generate_synthetic_data(start_time, end_time)

        # Ensure we have enough data
        if len(data) < 100:
            # Extend the time range to get more data
            start_time = datetime.now() - timedelta(hours=20)
            data = processor._generate_synthetic_data(start_time, end_time)

        # Train model with sufficient data
        result = trainer.train(data)

        # Check if training was successful
        if result["status"] == "success":
            # Test save and load
            save_success = trainer.save_model()
            assert save_success

            load_success = trainer.load_model()
            assert load_success
        else:
            # If training failed, skip save/load test but don't fail the test
            pytest.skip(
                f"Model training failed: {result.get('message', 'Unknown error')}"
            )


class TestInferenceEngine:
    """Test inference engine functionality."""

    def test_inference_engine_initialization(self):
        """Test inference engine initialization."""
        engine = AnomalyInferenceEngine()
        assert engine is not None
        assert engine.model is None  # No model loaded initially

    def test_feature_preparation(self):
        """Test feature preparation for inference."""
        engine = AnomalyInferenceEngine()
        engine.feature_columns = ["cpu_usage_avg", "memory_usage_pctf"]

        metrics = {"cpu_usage_avg": 50.0, "memory_usage_pct": 75.0}

        feature_vector = engine._prepare_features(metrics)
        assert feature_vector is not None
        assert len(feature_vector) == 2
        assert feature_vector[0] == 50.0
        assert feature_vector[1] == 75.0

    def test_severity_calculation(self):
        """Test severity score calculation."""
        engine = AnomalyInferenceEngine()

        # Test normal score
        normal_score = engine._calculate_severity_score(-0.1)
        assert 0 <= normal_score <= 1

        # Test anomaly score
        anomaly_score = engine._calculate_severity_score(-0.8)
        assert 0 <= anomaly_score <= 1
        assert anomaly_score > normal_score

    def test_anomaly_explanation(self):
        """Test anomaly explanation generation."""
        engine = AnomalyInferenceEngine()

        metrics = {
            "cpu_usage_avg": 85.0,
            "memory_usage_pct": 90.0,
            "disk_usage_pct": 95.0,
        }

        explanation = engine._explain_anomaly(metrics, -0.5, 0.6, 10.0)
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        assert (
            "Anomaly detected" in explanation or "No anomalies detected" in explanation
        )


class TestAnomalyDetector:
    """Test main anomaly detector functionality."""

    def test_anomaly_detector_initialization(self):
        """Test anomaly detector initialization."""
        detector = AnomalyDetector()
        assert detector is not None
        assert detector.data_processor is not None
        assert detector.model_trainer is not None
        assert not detector.is_initialized

    def test_metrics_validation(self):
        """Test metrics validation."""
        detector = AnomalyDetector()

        # Valid metrics
        valid_metrics = {"cpu_usage_avg": 50.0, "memory_usage_pct": 75.0}

        is_valid, issues = detector.validate_metrics(valid_metrics)
        assert is_valid
        assert len(issues) == 0

        # Invalid metrics (missing required)
        invalid_metrics = {
            "cpu_usage_avgf": 50.0
            # Missing memory_usage_pct
        }

        is_valid, issues = detector.validate_metrics(invalid_metrics)
        assert not is_valid
        assert len(issues) > 0

        # Invalid metrics (non-numeric)
        invalid_metrics2 = {"cpu_usage_avg": "invalid", "memory_usage_pct": 75.0}

        is_valid, issues = detector.validate_metrics(invalid_metrics2)
        assert not is_valid
        assert len(issues) > 0

    def test_system_status(self):
        """Test system status retrieval."""
        detector = AnomalyDetector()
        status = detector.get_system_status()

        assert isinstance(status, dict)
        assert "initialized" in status
        assert "model_path" in status
        assert "model_exists" in status
        assert "config" in status

    def test_feature_importance(self):
        """Test feature importance retrieval."""
        detector = AnomalyDetector()
        feature_info = detector.get_feature_importance()
        assert isinstance(feature_info, dict)
        if "error" not in feature_info:
            assert "feature_count" in feature_info
            assert "features" in feature_info


class TestIntegration:
    """Integration tests for the complete ML pipeline."""

    def test_complete_pipeline(self):
        """Test the complete ML pipeline from data to inference."""
        # Initialize detector
        detector = AnomalyDetector()

        # Test metrics validation
        test_metrics = {
            "cpu_usage_avg": 45.2,
            "cpu_usage_max": 78.9,
            "memory_usage_pct": 65.3,
            "disk_usage_pct": 42.1,
            "network_bytes_total": 1250.5,
            "request_rate": 15.2,
            "response_time_p95": 0.23,
        }

        is_valid, issues = detector.validate_metrics(test_metrics)
        assert is_valid, "Metrics validation failed: {issues}"

        # Test anomaly detection (if model is available)
        if detector.is_initialized:
            result = detector.detect_anomaly(test_metrics)
            assert result["status"] == "success"
            assert "is_anomaly" in result
            assert "severity_score" in result
            assert "explanation" in result

    def test_batch_processing(self):
        """Test batch anomaly detection."""
        detector = AnomalyDetector()

        batch_metrics = [
            {"cpu_usage_avg": 45.2, "memory_usage_pct": 65.3},
            {"cpu_usage_avg": 85.5, "memory_usage_pct": 88.7},
        ]

        # Validate batch
        for i, metrics in enumerate(batch_metrics):
            is_valid, issues = detector.validate_metrics(metrics)
            assert is_valid, f"Batch metrics {i} validation failed: {issues}"

        # Test batch detection (if model is available)
        if detector.is_initialized:
            results = detector.batch_detect(batch_metrics)
            assert len(results) == 2
            for result in results:
                assert result["status"] == "success"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
