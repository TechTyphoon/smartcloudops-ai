#!/usr/bin/env python3
"""
Unit tests for ML Models module
Tests anomaly detection, model training, and prediction functionality
"""

import os


class TestAnomalyDetector:
    """Test suite for AnomalyDetector functionality."""

    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        np.random.seed(42)
        n_samples = 1000

        # Generate normal data
        normal_data = np.random.normal(50, 10, (n_samples, 5))

        # Generate some anomalies
        anomaly_indices = np.random.choice(n_samples, 50, replace=False)
        normal_data[anomaly_indices] = np.random.normal(80, 5, (50, 5))

        return pd.DataFrame(
            normal_data,
            columns=[
                "cpu_usage",
                "memory_usage",
                "disk_usage",
                "network_io",
                "response_time",
            ],
        )

    @pytest.fixture
    def mock_config(self):
        """Create mock configuration for testing."""
        return {
            "MODEL_PATH": "/tmp/test_model.pkl",
            "ANOMALY_THRESHOLD": 0.7,
            "MIN_SAMPLES": 100,
            "RANDOM_STATE": 42,
        }

    @patch("ml_models.anomaly_detector.IsolationForest")
    def test_anomaly_detector_initialization(self, mock_isolation_forest, mock_config):
        """Test anomaly detector initialization."""
        detector = AnomalyDetector(mock_config)

        assert detector is not None
        assert hasattr(detector, "model")
        assert hasattr(detector, "config")
        assert detector.config == mock_config

    @patch("ml_models.anomaly_detector.IsolationForest")
    def test_model_training(self, mock_isolation_forest, sample_data, mock_config):
        """Test model training functionality."""
        # Setup mock
        mock_model = Mock()
        mock_model.fit.return_value = mock_model
        mock_isolation_forest.return_value = mock_model

        detector = AnomalyDetector(mock_config)

        # Train model
        result = detector.train_model(sample_data)

        assert result["success"] is True
        assert "training_time" in result
        assert "model_info" in result
        mock_model.fit.assert_called_once()

    @patch("ml_models.anomaly_detector.IsolationForest")
    def test_anomaly_prediction(self, mock_isolation_forest, sample_data, mock_config):
        """Test anomaly prediction functionality."""
        # Setup mock
        mock_model = Mock()
        mock_model.fit.return_value = mock_model
        mock_model.predict.return_value = np.array(
            [1, -1, 1, -1, 1]
        )  # Mix of normal and anomalies
        mock_model.decision_function.return_value = np.array(
            [0.1, -0.8, 0.2, -0.9, 0.1]
        )
        mock_isolation_forest.return_value = mock_model

        detector = AnomalyDetector(mock_config)

        # Train model first
        detector.train_model(sample_data)

        # Test prediction
        test_data = sample_data.iloc[:5]
        result = detector.predict_anomalies(test_data)

        assert result["success"] is True
        assert "predictions" in result
        assert "anomaly_scores" in result
        assert len(result["predictions"]) == 5
        assert len(result["anomaly_scores"]) == 5

    @patch("ml_models.anomaly_detector.IsolationForest")
    def test_model_save_and_load(self, mock_isolation_forest, sample_data, mock_config):
        """Test model save and load functionality."""
        # Setup mock
        mock_model = Mock()
        mock_model.fit.return_value = mock_model
        mock_isolation_forest.return_value = mock_model

        detector = AnomalyDetector(mock_config)

        # Train model
        detector.train_model(sample_data)

        # Test save
        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as tmp_file:
            save_result = detector.save_model(tmp_file.name)
            assert save_result["success"] is True

            # Test load
            new_detector = AnomalyDetector(mock_config)
            load_result = new_detector.load_model(tmp_file.name)
            assert load_result["success"] is True

            # Cleanup
            os.unlink(tmp_file.name)

    def test_data_preprocessing(self, sample_data, mock_config):
        """Test data preprocessing functionality."""
        detector = AnomalyDetector(mock_config)

        # Test preprocessing
        processed_data = detector.preprocess_data(sample_data)

        assert processed_data is not None
        assert not processed_data.isnull().any().any()  # No NaN values
        assert processed_data.shape[0] > 0
        assert processed_data.shape[1] > 0

    def test_feature_engineering(self, sample_data, mock_config):
        """Test feature engineering functionality."""
        detector = AnomalyDetector(mock_config)

        # Test feature engineering
        engineered_data = detector.engineer_features(sample_data)

        assert engineered_data is not None
        assert engineered_data.shape[0] == sample_data.shape[0]
        assert (
            engineered_data.shape[1] >= sample_data.shape[1]
        )  # Should have same or more features

    @patch("ml_models.anomaly_detector.IsolationForest")
    def test_model_evaluation(self, mock_isolation_forest, sample_data, mock_config):
        """Test model evaluation functionality."""
        # Setup mock
        mock_model = Mock()
        mock_model.fit.return_value = mock_model
        mock_model.predict.return_value = np.array([1, -1, 1, -1, 1])
        mock_isolation_forest.return_value = mock_model

        detector = AnomalyDetector(mock_config)

        # Train model
        detector.train_model(sample_data)

        # Test evaluation
        evaluation_result = detector.evaluate_model(sample_data)

        assert evaluation_result["success"] is True
        assert "metrics" in evaluation_result
        assert "confusion_matrix" in evaluation_result

    def test_anomaly_threshold_validation(self, mock_config):
        """Test anomaly threshold validation."""
        # Test valid threshold
        valid_config = mock_config.copy()
        valid_config["ANOMALY_THRESHOLD"] = 0.5
        detector = AnomalyDetector(valid_config)
        assert detector.config["ANOMALY_THRESHOLD"] == 0.5

        # Test invalid threshold (should be clamped)
        invalid_config = mock_config.copy()
        invalid_config["ANOMALY_THRESHOLD"] = 1.5  # > 1
        detector = AnomalyDetector(invalid_config)
        assert detector.config["ANOMALY_THRESHOLD"] <= 1.0

    def test_data_validation(self, mock_config):
        """Test data validation functionality."""
        detector = AnomalyDetector(mock_config)

        # Test valid data
        valid_data = pd.DataFrame(
            {"cpu_usage": [50, 60, 70], "memory_usage": [40, 50, 60]}
        )
        assert detector.validate_data(valid_data) is True

        # Test empty data
        empty_data = pd.DataFrame()
        assert detector.validate_data(empty_data) is False

        # Test data with NaN values
        nan_data = pd.DataFrame(
            {"cpu_usage": [50, np.nan, 70], "memory_usage": [40, 50, 60]}
        )
        assert detector.validate_data(nan_data) is False


class TestModelVersioning:
    """Test suite for model versioning functionality."""

    @pytest.fixture
    def mock_config(self):
        """Create mock configuration for versioning tests."""
        return {
            "MODEL_REGISTRY_PATH": "/tmp/model_registry",
            "VERSION_FORMAT": "v{major}.{minor}.{patch}",
            "MAX_VERSIONS": 5,
        }

    def test_version_creation(self, mock_config):
        """Test model version creation."""
        versioning = ModelVersioning(mock_config)

        # Test version creation
        version = versioning.create_version("1.0.0")
        assert version is not None
        assert "1.0.0" in version

    def test_version_comparison(self, mock_config):
        """Test version comparison functionality."""
        versioning = ModelVersioning(mock_config)

        # Test version comparison
        assert versioning.compare_versions("1.0.0", "1.0.1") < 0
        assert versioning.compare_versions("1.0.1", "1.0.0") > 0
        assert versioning.compare_versions("1.0.0", "1.0.0") == 0

    def test_version_cleanup(self, mock_config):
        """Test version cleanup functionality."""
        versioning = ModelVersioning(mock_config)

        # Test cleanup
        versions = ["v1.0.0", "v1.0.1", "v1.0.2", "v1.0.3", "v1.0.4", "v1.0.5"]
        cleaned_versions = versioning.cleanup_old_versions(versions)

        assert len(cleaned_versions) <= mock_config["MAX_VERSIONS"]


class TestMLModelsIntegration:
    """Integration tests for ML models with external dependencies."""

    @pytest.fixture
    def sample_data(self):
        """Create sample data for integration testing."""
        np.random.seed(42)
        return pd.DataFrame(
            {
                "cpu_usage": np.random.normal(50, 10, 100),
                "memory_usage": np.random.normal(60, 15, 100),
                "disk_usage": np.random.normal(40, 8, 100),
            }
        )

    @patch("ml_models.anomaly_detector.joblib")
    def test_full_ml_pipeline(self, mock_joblib, sample_data):
        """Test complete ML pipeline from training to prediction."""
        config = {
            "MODEL_PATH": "/tmp/test_model.pkl",
            "ANOMALY_THRESHOLD": 0.7,
            "MIN_SAMPLES": 50,
            "RANDOM_STATE": 42,
        }

        # Setup mocks
        mock_joblib.dump.return_value = None
        mock_joblib.load.return_value = Mock()

        detector = AnomalyDetector(config)

        # Test full pipeline
        train_result = detector.train_model(sample_data)
        assert train_result["success"] is True

        predict_result = detector.predict_anomalies(sample_data.iloc[:10])
        assert predict_result["success"] is True

        eval_result = detector.evaluate_model(sample_data)
        assert eval_result["success"] is True

    def test_model_persistence(self, sample_data):
        """Test model persistence across sessions."""
        config = {
            "MODEL_PATH": "/tmp/persistent_model.pkl",
            "ANOMALY_THRESHOLD": 0.7,
            "MIN_SAMPLES": 50,
            "RANDOM_STATE": 42,
        }

        # Create and train model
        detector1 = AnomalyDetector(config)
        detector1.train_model(sample_data)

        # Save model
        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as tmp_file:
            save_result = detector1.save_model(tmp_file.name)
            assert save_result["success"] is True

            # Load model in new instance
            detector2 = AnomalyDetector(config)
            load_result = detector2.load_model(tmp_file.name)
            assert load_result["success"] is True

            # Test that predictions are consistent
            test_data = sample_data.iloc[:5]
            pred1 = detector1.predict_anomalies(test_data)
            pred2 = detector2.predict_anomalies(test_data)

            assert pred1["success"] is True
            assert pred2["success"] is True

            # Cleanup
            os.unlink(tmp_file.name)


class TestMLModelsErrorHandling:
    """Test error handling in ML models."""

    def test_invalid_data_handling(self):
        """Test handling of invalid data."""
        config = {
            "MODEL_PATH": "/tmp/test_model.pkl",
            "ANOMALY_THRESHOLD": 0.7,
            "MIN_SAMPLES": 50,
            "RANDOM_STATE": 42,
        }

        detector = AnomalyDetector(config)

        # Test with None data
        result = detector.train_model(None)
        assert result["success"] is False
        assert "error" in result

        # Test with empty DataFrame
        result = detector.train_model(pd.DataFrame())
        assert result["success"] is False
        assert "error" in result

    def test_model_file_errors(self):
        """Test handling of model file errors."""
        config = {
            "MODEL_PATH": "/tmp/test_model.pkl",
            "ANOMALY_THRESHOLD": 0.7,
            "MIN_SAMPLES": 50,
            "RANDOM_STATE": 42,
        }

        detector = AnomalyDetector(config)

        # Test loading non-existent model
        result = detector.load_model("/non/existent/path.pkl")
        assert result["success"] is False
        assert "error" in result

    def test_configuration_errors(self):
        """Test handling of configuration errors."""
        # Test with missing required config
        try:
            detector = AnomalyDetector({})
            # Should handle gracefully or raise appropriate error
            assert detector is not None
        except Exception as e:
            # Should be a meaningful error
            assert "config" in str(e).lower() or "required" in str(e).lower()


class TestMLModelsPerformance:
    """Performance tests for ML models."""

    @pytest.fixture
    def large_sample_data(self):
        """Create large sample data for performance testing."""
        np.random.seed(42)
        n_samples = 10000
        return pd.DataFrame(
            {
                "cpu_usage": np.random.normal(50, 10, n_samples),
                "memory_usage": np.random.normal(60, 15, n_samples),
                "disk_usage": np.random.normal(40, 8, n_samples),
                "network_io": np.random.normal(30, 5, n_samples),
                "response_time": np.random.normal(100, 20, n_samples),
            }
        )

    @patch("ml_models.anomaly_detector.IsolationForest")
    def test_training_performance(self, mock_isolation_forest, large_sample_data):
        """Test model training performance."""

        config = {
            "MODEL_PATH": "/tmp/test_model.pkl",
            "ANOMALY_THRESHOLD": 0.7,
            "MIN_SAMPLES": 100,
            "RANDOM_STATE": 42,
        }

        # Setup mock
        mock_model = Mock()
        mock_model.fit.return_value = mock_model
        mock_isolation_forest.return_value = mock_model

        detector = AnomalyDetector(config)

        start_time = time.time()
        result = detector.train_model(large_sample_data)
        end_time = time.time()

        assert result["success"] is True
        assert (end_time - start_time) < 10.0  # Should train in under 10 seconds

    @patch("ml_models.anomaly_detector.IsolationForest")
    def test_prediction_performance(self, mock_isolation_forest, large_sample_data):
        """Test prediction performance."""

        config = {
            "MODEL_PATH": "/tmp/test_model.pkl",
            "ANOMALY_THRESHOLD": 0.7,
            "MIN_SAMPLES": 100,
            "RANDOM_STATE": 42,
        }

        # Setup mock
        mock_model = Mock()
        mock_model.fit.return_value = mock_model
        mock_model.predict.return_value = np.ones(1000)
        mock_model.decision_function.return_value = np.random.random(1000)
        mock_isolation_forest.return_value = mock_model

        detector = AnomalyDetector(config)
        detector.train_model(large_sample_data)

        test_data = large_sample_data.iloc[:1000]

        start_time = time.time()
        result = detector.predict_anomalies(test_data)
        end_time = time.time()

        assert result["success"] is True
        assert (end_time - start_time) < 1.0  # Should predict in under 1 second
