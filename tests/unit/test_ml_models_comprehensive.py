"""
Comprehensive unit tests for ML Models
Complete test coverage for anomaly detection and ML functionality
"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple

from ml_models.anomaly_detector import AnomalyDetector
from ml_models.model_versioning import ModelVersioning


class TestAnomalyDetector:
    """Test suite for AnomalyDetector class."""

    @pytest.fixture
    def sample_data(self) -> np.ndarray:
        """Generate sample data for testing."""
        np.random.seed(42)
        # Generate normal data with some outliers
        normal_data = np.random.normal(0, 1, 1000)
        outliers = np.random.normal(5, 0.5, 50)  # Outliers
        return np.concatenate([normal_data, outliers])

    @pytest.fixture
    def anomaly_detector(self) -> AnomalyDetector:
        """Create AnomalyDetector instance for testing."""
        return AnomalyDetector(model_type='isolation_forest')

    @pytest.fixture
    def mock_model(self):
        """Mock ML model for testing."""
        mock = Mock()
        mock.predict.return_value = np.array([1, -1, 1, -1, 1])  # Mix of normal and anomalies
        mock.predict_proba.return_value = np.array([[0.8, 0.2], [0.3, 0.7], [0.9, 0.1]])
        mock.score_samples.return_value = np.array([-0.5, -2.0, -0.3, -1.8, -0.4])
        return mock

    def test_init_default_parameters(self):
        """Test AnomalyDetector initialization with default parameters."""
        detector = AnomalyDetector()
        
        assert detector.model_type == 'isolation_forest'
        assert detector.model is None
        assert detector.is_trained is False
        assert detector.training_data is None
        assert detector.feature_names is None

    def test_init_custom_parameters(self):
        """Test AnomalyDetector initialization with custom parameters."""
        detector = AnomalyDetector(
            model_type='one_class_svm',
            contamination=0.1,
            random_state=42
        )
        
        assert detector.model_type == 'one_class_svm'
        assert detector.contamination == 0.1
        assert detector.random_state == 42

    def test_init_invalid_model_type(self):
        """Test AnomalyDetector initialization with invalid model type."""
        with pytest.raises(ValueError, match="Unsupported model type"):
            AnomalyDetector(model_type='invalid_model')

    @patch('ml_models.anomaly_detector.IsolationForest')
    def test_create_model_isolation_forest(self, mock_isolation_forest, anomaly_detector):
        """Test model creation for Isolation Forest."""
        mock_model = Mock()
        mock_isolation_forest.return_value = mock_model
        
        model = anomaly_detector._create_model()
        
        assert model == mock_model
        mock_isolation_forest.assert_called_once_with(
            contamination=0.05,
            random_state=42,
            n_estimators=100
        )

    @patch('ml_models.anomaly_detector.OneClassSVM')
    def test_create_model_one_class_svm(self, mock_one_class_svm):
        """Test model creation for One-Class SVM."""
        detector = AnomalyDetector(model_type='one_class_svm')
        mock_model = Mock()
        mock_one_class_svm.return_value = mock_model
        
        model = detector._create_model()
        
        assert model == mock_model
        mock_one_class_svm.assert_called_once_with(
            kernel='rbf',
            nu=0.05,
            gamma='scale'
        )

    @patch('ml_models.anomaly_detector.LocalOutlierFactor')
    def test_create_model_local_outlier_factor(self, mock_lof):
        """Test model creation for Local Outlier Factor."""
        detector = AnomalyDetector(model_type='local_outlier_factor')
        mock_model = Mock()
        mock_lof.return_value = mock_model
        
        model = detector._create_model()
        
        assert model == mock_model
        mock_lof.assert_called_once_with(
            contamination=0.05,
            n_neighbors=20,
            algorithm='auto'
        )

    def test_preprocess_data_valid_input(self, anomaly_detector, sample_data):
        """Test data preprocessing with valid input."""
        # Convert to DataFrame for testing
        df = pd.DataFrame(sample_data, columns=['value'])
        
        processed_data, feature_names = anomaly_detector._preprocess_data(df)
        
        assert isinstance(processed_data, np.ndarray)
        assert len(processed_data) == len(df)
        assert feature_names == ['value']
        assert not np.isnan(processed_data).any()

    def test_preprocess_data_with_missing_values(self, anomaly_detector):
        """Test data preprocessing with missing values."""
        df = pd.DataFrame({
            'value': [1, 2, np.nan, 4, 5],
            'feature': [1.1, 2.2, 3.3, np.nan, 5.5]
        })
        
        processed_data, feature_names = anomaly_detector._preprocess_data(df)
        
        assert isinstance(processed_data, np.ndarray)
        assert not np.isnan(processed_data).any()
        assert len(feature_names) == 2

    def test_preprocess_data_empty_dataframe(self, anomaly_detector):
        """Test data preprocessing with empty DataFrame."""
        df = pd.DataFrame()
        
        with pytest.raises(ValueError, match="Empty dataset"):
            anomaly_detector._preprocess_data(df)

    def test_preprocess_data_invalid_input(self, anomaly_detector):
        """Test data preprocessing with invalid input."""
        with pytest.raises(ValueError, match="Input must be a pandas DataFrame"):
            anomaly_detector._preprocess_data("invalid_input")

    @patch('ml_models.anomaly_detector.IsolationForest')
    def test_train_success(self, mock_isolation_forest, anomaly_detector, sample_data):
        """Test successful model training."""
        mock_model = Mock()
        mock_isolation_forest.return_value = mock_model
        
        df = pd.DataFrame(sample_data, columns=['value'])
        
        result = anomaly_detector.train(df)
        
        assert result is True
        assert anomaly_detector.is_trained is True
        assert anomaly_detector.model is mock_model
        assert anomaly_detector.training_data is not None
        assert anomaly_detector.feature_names == ['value']
        
        # Verify model was trained
        mock_model.fit.assert_called_once()

    def test_train_without_model_creation(self, anomaly_detector, sample_data):
        """Test training when model creation fails."""
        df = pd.DataFrame(sample_data, columns=['value'])
        
        with patch.object(anomaly_detector, '_create_model', side_effect=Exception("Model creation failed")):
            with pytest.raises(Exception, match="Model creation failed"):
                anomaly_detector.train(df)

    def test_train_with_preprocessing_error(self, anomaly_detector):
        """Test training when preprocessing fails."""
        df = pd.DataFrame()  # Empty DataFrame will cause preprocessing error
        
        result = anomaly_detector.train(df)
        
        assert result is False
        assert anomaly_detector.is_trained is False

    @patch('ml_models.anomaly_detector.IsolationForest')
    def test_train_with_training_error(self, mock_isolation_forest, anomaly_detector, sample_data):
        """Test training when model training fails."""
        mock_model = Mock()
        mock_model.fit.side_effect = Exception("Training failed")
        mock_isolation_forest.return_value = mock_model
        
        df = pd.DataFrame(sample_data, columns=['value'])
        
        result = anomaly_detector.train(df)
        
        assert result is False
        assert anomaly_detector.is_trained is False

    def test_predict_not_trained(self, anomaly_detector, sample_data):
        """Test prediction when model is not trained."""
        df = pd.DataFrame(sample_data, columns=['value'])
        
        with pytest.raises(ValueError, match="Model must be trained"):
            anomaly_detector.predict(df)

    @patch('ml_models.anomaly_detector.IsolationForest')
    def test_predict_success(self, mock_isolation_forest, anomaly_detector, sample_data):
        """Test successful prediction."""
        # Train the model first
        mock_model = Mock()
        mock_model.predict.return_value = np.array([1, -1, 1, -1, 1])
        mock_isolation_forest.return_value = mock_model
        
        df_train = pd.DataFrame(sample_data[:100], columns=['value'])
        anomaly_detector.train(df_train)
        
        # Test prediction
        df_test = pd.DataFrame(sample_data[100:105], columns=['value'])
        predictions = anomaly_detector.predict(df_test)
        
        assert isinstance(predictions, np.ndarray)
        assert len(predictions) == len(df_test)
        assert all(pred in [-1, 1] for pred in predictions)

    @patch('ml_models.anomaly_detector.IsolationForest')
    def test_predict_with_scores(self, mock_isolation_forest, anomaly_detector, sample_data):
        """Test prediction with anomaly scores."""
        # Train the model first
        mock_model = Mock()
        mock_model.predict.return_value = np.array([1, -1, 1])
        mock_model.score_samples.return_value = np.array([-0.5, -2.0, -0.3])
        mock_isolation_forest.return_value = mock_model
        
        df_train = pd.DataFrame(sample_data[:100], columns=['value'])
        anomaly_detector.train(df_train)
        
        # Test prediction with scores
        df_test = pd.DataFrame(sample_data[100:103], columns=['value'])
        predictions, scores = anomaly_detector.predict_with_scores(df_test)
        
        assert isinstance(predictions, np.ndarray)
        assert isinstance(scores, np.ndarray)
        assert len(predictions) == len(df_test)
        assert len(scores) == len(df_test)

    def test_predict_with_preprocessing_error(self, anomaly_detector, sample_data):
        """Test prediction when preprocessing fails."""
        # Train the model first
        with patch('ml_models.anomaly_detector.IsolationForest') as mock_isolation_forest:
            mock_model = Mock()
            mock_isolation_forest.return_value = mock_model
            
            df_train = pd.DataFrame(sample_data[:100], columns=['value'])
            anomaly_detector.train(df_train)
        
        # Test prediction with invalid data
        with pytest.raises(ValueError, match="Input must be a pandas DataFrame"):
            anomaly_detector.predict("invalid_input")

    @patch('ml_models.anomaly_detector.IsolationForest')
    def test_predict_with_model_error(self, mock_isolation_forest, anomaly_detector, sample_data):
        """Test prediction when model prediction fails."""
        # Train the model first
        mock_model = Mock()
        mock_model.predict.side_effect = Exception("Prediction failed")
        mock_isolation_forest.return_value = mock_model
        
        df_train = pd.DataFrame(sample_data[:100], columns=['value'])
        anomaly_detector.train(df_train)
        
        # Test prediction
        df_test = pd.DataFrame(sample_data[100:105], columns=['value'])
        
        with pytest.raises(Exception, match="Prediction failed"):
            anomaly_detector.predict(df_test)

    def test_get_model_info_not_trained(self, anomaly_detector):
        """Test getting model info when not trained."""
        info = anomaly_detector.get_model_info()
        
        assert info['is_trained'] is False
        assert info['model_type'] == 'isolation_forest'
        assert info['training_data_size'] is None

    @patch('ml_models.anomaly_detector.IsolationForest')
    def test_get_model_info_trained(self, mock_isolation_forest, anomaly_detector, sample_data):
        """Test getting model info when trained."""
        # Train the model first
        mock_model = Mock()
        mock_isolation_forest.return_value = mock_model
        
        df_train = pd.DataFrame(sample_data[:100], columns=['value'])
        anomaly_detector.train(df_train)
        
        info = anomaly_detector.get_model_info()
        
        assert info['is_trained'] is True
        assert info['model_type'] == 'isolation_forest'
        assert info['training_data_size'] == 100
        assert info['feature_names'] == ['value']

    def test_save_model_not_trained(self, anomaly_detector):
        """Test saving model when not trained."""
        with pytest.raises(ValueError, match="Model must be trained"):
            anomaly_detector.save_model('test_model.pkl')

    @patch('ml_models.anomaly_detector.IsolationForest')
    @patch('ml_models.anomaly_detector.joblib.dump')
    def test_save_model_success(self, mock_dump, mock_isolation_forest, anomaly_detector, sample_data):
        """Test successful model saving."""
        # Train the model first
        mock_model = Mock()
        mock_isolation_forest.return_value = mock_model
        
        df_train = pd.DataFrame(sample_data[:100], columns=['value'])
        anomaly_detector.train(df_train)
        
        result = anomaly_detector.save_model('test_model.pkl')
        
        assert result is True
        mock_dump.assert_called_once()

    def test_load_model_success(self, anomaly_detector):
        """Test successful model loading."""
        mock_model = Mock()
        mock_data = {
            'model': mock_model,
            'feature_names': ['value'],
            'training_data_size': 100
        }
        
        with patch('ml_models.anomaly_detector.joblib.load', return_value=mock_data):
            result = anomaly_detector.load_model('test_model.pkl')
            
            assert result is True
            assert anomaly_detector.model is mock_model
            assert anomaly_detector.is_trained is True
            assert anomaly_detector.feature_names == ['value']

    def test_load_model_file_not_found(self, anomaly_detector):
        """Test loading model when file doesn't exist."""
        with patch('ml_models.anomaly_detector.joblib.load', side_effect=FileNotFoundError):
            result = anomaly_detector.load_model('nonexistent_model.pkl')
            
            assert result is False

    def test_load_model_invalid_format(self, anomaly_detector):
        """Test loading model with invalid format."""
        with patch('ml_models.anomaly_detector.joblib.load', return_value={'invalid': 'data'}):
            result = anomaly_detector.load_model('invalid_model.pkl')
            
            assert result is False

    @patch('ml_models.anomaly_detector.IsolationForest')
    def test_evaluate_model(self, mock_isolation_forest, anomaly_detector, sample_data):
        """Test model evaluation."""
        # Train the model first
        mock_model = Mock()
        mock_model.predict.return_value = np.array([1, -1, 1, -1, 1])
        mock_isolation_forest.return_value = mock_model
        
        df_train = pd.DataFrame(sample_data[:100], columns=['value'])
        anomaly_detector.train(df_train)
        
        # Test evaluation
        df_test = pd.DataFrame(sample_data[100:150], columns=['value'])
        metrics = anomaly_detector.evaluate_model(df_test)
        
        assert isinstance(metrics, dict)
        assert 'predictions' in metrics
        assert 'scores' in metrics
        assert 'anomaly_count' in metrics
        assert 'anomaly_percentage' in metrics

    def test_evaluate_model_not_trained(self, anomaly_detector, sample_data):
        """Test model evaluation when not trained."""
        df_test = pd.DataFrame(sample_data[100:150], columns=['value'])
        
        with pytest.raises(ValueError, match="Model must be trained"):
            anomaly_detector.evaluate_model(df_test)

    @patch('ml_models.anomaly_detector.IsolationForest')
    def test_update_model(self, mock_isolation_forest, anomaly_detector, sample_data):
        """Test model updating with new data."""
        # Train the model first
        mock_model = Mock()
        mock_isolation_forest.return_value = mock_model
        
        df_train = pd.DataFrame(sample_data[:100], columns=['value'])
        anomaly_detector.train(df_train)
        
        # Update with new data
        df_new = pd.DataFrame(sample_data[200:250], columns=['value'])
        result = anomaly_detector.update_model(df_new)
        
        assert result is True
        # Verify model was retrained
        assert mock_model.fit.call_count == 2


class TestModelVersioning:
    """Test suite for ModelVersioning class."""

    @pytest.fixture
    def model_versioning(self):
        """Create ModelVersioning instance for testing."""
        return ModelVersioning()

    @pytest.fixture
    def mock_model(self):
        """Mock model for testing."""
        return Mock()

    def test_init_default_values(self, model_versioning):
        """Test ModelVersioning initialization with default values."""
        assert model_versioning.version_format == 'v{major}.{minor}.{patch}'
        assert model_versioning.models == {}
        assert model_versioning.current_version is None

    def test_create_version_string(self, model_versioning):
        """Test version string creation."""
        version = model_versioning._create_version_string(1, 2, 3)
        assert version == 'v1.2.3'

    def test_parse_version_string(self, model_versioning):
        """Test version string parsing."""
        major, minor, patch = model_versioning._parse_version_string('v1.2.3')
        assert major == 1
        assert minor == 2
        assert patch == 3

    def test_parse_version_string_invalid(self, model_versioning):
        """Test parsing invalid version string."""
        with pytest.raises(ValueError, match="Invalid version format"):
            model_versioning._parse_version_string('invalid_version')

    def test_get_next_version_no_versions(self, model_versioning):
        """Test getting next version when no versions exist."""
        next_version = model_versioning._get_next_version()
        assert next_version == 'v1.0.0'

    def test_get_next_version_with_existing(self, model_versioning):
        """Test getting next version with existing versions."""
        model_versioning.models = {
            'v1.0.0': Mock(),
            'v1.0.1': Mock(),
            'v1.1.0': Mock()
        }
        
        next_version = model_versioning._get_next_version()
        assert next_version == 'v1.1.1'

    def test_save_model_success(self, model_versioning, mock_model):
        """Test successful model saving."""
        result = model_versioning.save_model(mock_model, 'test_model')
        
        assert result is True
        assert len(model_versioning.models) == 1
        assert 'v1.0.0' in model_versioning.models
        assert model_versioning.current_version == 'v1.0.0'

    def test_save_model_with_version(self, model_versioning, mock_model):
        """Test saving model with specific version."""
        result = model_versioning.save_model(mock_model, 'test_model', version='v2.0.0')
        
        assert result is True
        assert 'v2.0.0' in model_versioning.models
        assert model_versioning.current_version == 'v2.0.0'

    def test_load_model_success(self, model_versioning, mock_model):
        """Test successful model loading."""
        # Save a model first
        model_versioning.save_model(mock_model, 'test_model')
        
        loaded_model = model_versioning.load_model('v1.0.0')
        
        assert loaded_model is mock_model

    def test_load_model_not_found(self, model_versioning):
        """Test loading non-existent model."""
        with pytest.raises(ValueError, match="Model version not found"):
            model_versioning.load_model('v1.0.0')

    def test_load_current_model(self, model_versioning, mock_model):
        """Test loading current model."""
        # Save a model first
        model_versioning.save_model(mock_model, 'test_model')
        
        loaded_model = model_versioning.load_current_model()
        
        assert loaded_model is mock_model

    def test_load_current_model_none(self, model_versioning):
        """Test loading current model when none exists."""
        with pytest.raises(ValueError, match="No current model"):
            model_versioning.load_current_model()

    def test_list_versions(self, model_versioning, mock_model):
        """Test listing model versions."""
        # Save multiple models
        model_versioning.save_model(mock_model, 'test_model')
        model_versioning.save_model(mock_model, 'test_model')
        
        versions = model_versioning.list_versions()
        
        assert len(versions) == 2
        assert 'v1.0.0' in versions
        assert 'v1.0.1' in versions

    def test_delete_model_success(self, model_versioning, mock_model):
        """Test successful model deletion."""
        # Save a model first
        model_versioning.save_model(mock_model, 'test_model')
        
        result = model_versioning.delete_model('v1.0.0')
        
        assert result is True
        assert 'v1.0.0' not in model_versioning.models

    def test_delete_model_not_found(self, model_versioning):
        """Test deleting non-existent model."""
        result = model_versioning.delete_model('v1.0.0')
        
        assert result is False

    def test_delete_current_model(self, model_versioning, mock_model):
        """Test deleting current model."""
        # Save a model first
        model_versioning.save_model(mock_model, 'test_model')
        
        result = model_versioning.delete_current_model()
        
        assert result is True
        assert model_versioning.current_version is None

    def test_get_model_info(self, model_versioning, mock_model):
        """Test getting model information."""
        # Save a model first
        model_versioning.save_model(mock_model, 'test_model')
        
        info = model_versioning.get_model_info('v1.0.0')
        
        assert info['version'] == 'v1.0.0'
        assert info['created_at'] is not None
        assert info['model'] is mock_model

    def test_get_model_info_not_found(self, model_versioning):
        """Test getting info for non-existent model."""
        with pytest.raises(ValueError, match="Model version not found"):
            model_versioning.get_model_info('v1.0.0')

    def test_set_current_version(self, model_versioning, mock_model):
        """Test setting current version."""
        # Save a model first
        model_versioning.save_model(mock_model, 'test_model')
        
        result = model_versioning.set_current_version('v1.0.0')
        
        assert result is True
        assert model_versioning.current_version == 'v1.0.0'

    def test_set_current_version_not_found(self, model_versioning):
        """Test setting current version for non-existent model."""
        result = model_versioning.set_current_version('v1.0.0')
        
        assert result is False

    def test_get_version_history(self, model_versioning, mock_model):
        """Test getting version history."""
        # Save multiple models
        model_versioning.save_model(mock_model, 'test_model')
        model_versioning.save_model(mock_model, 'test_model')
        
        history = model_versioning.get_version_history()
        
        assert len(history) == 2
        assert all('version' in entry for entry in history)
        assert all('created_at' in entry for entry in history)
