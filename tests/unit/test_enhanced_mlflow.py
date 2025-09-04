#!/usr/bin/env python3
"""
Unit tests for Enhanced MLflow Configuration
Phase 2A: Comprehensive testing for MLflow integration with fallback
"""

import json
import os
import shutil
import tempfile
from unittest.mock import patch

import pytest

from ml_models.mlflow_config import MLflowManager, get_mlflow_manager


@pytest.mark.unit
class TestMLflowManagerEnhanced:
    """Test cases for enhanced MLflow manager."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create temporary directory for fallback storage
        self.temp_dir = tempfile.mkdtemp()
        self.mlflow_manager = MLflowManager(
            tracking_uri="http://test:5000",
            experiment_name="test_experiment",
            enable_fallback_logging=True,
        )
        # Override fallback storage path for testing
        self.mlflow_manager.fallback_storage_path = os.path.join(
            self.temp_dir, "fallback_logs"
        )
        os.makedirs(self.mlflow_manager.fallback_storage_path, exist_ok=True)

    def teardown_method(self):
        """Clean up test fixtures after each test method."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    # ===== INITIALIZATION TESTS =====

    def test_initialization_without_mlflow(self):
        """Test MLflow manager initializes correctly without MLflow package."""
        assert self.mlflow_manager is not None
        assert self.mlflow_manager.tracking_uri == "http://test:5000"
        assert self.mlflow_manager.experiment_name == "test_experiment"
        assert self.mlflow_manager.enable_fallback_logging is True
        # MLflow package not available in test environment
        assert self.mlflow_manager.available is False

    def test_initialization_with_environment_variables(self):
        """Test initialization with environment variables."""
        with patch.dict(
            os.environ,
            {
                "MLFLOW_TRACKING_URI": "http://env:6000",
                "MLFLOW_REGISTRY_URI": "sqlite:///env_test.db",
                "ENVIRONMENT": "test",
                "APP_VERSION": "2.0.0",
            },
        ):
            manager = MLflowManager()
            assert manager.tracking_uri == "http://env:6000"
            assert manager.registry_uri == "sqlite:///env_test.db"

    def test_get_experiment_info(self):
        """Test getting experiment information."""
        info = self.mlflow_manager.get_experiment_info()

        assert isinstance(info, dict)
        assert info["name"] == "test_experiment"
        assert info["tracking_uri"] == "http://test:5000"
        assert info["mlflow_available"] is False
        assert info["fallback_enabled"] is True

    # ===== RUN MANAGEMENT TESTS =====

    def test_start_run_fallback(self):
        """Test starting a run with fallback logging."""
        run = self.mlflow_manager.start_run(
            "test_run", tags={"custom_tag": "test_value"}
        )

        assert isinstance(run, dict)
        assert run["run_name"] == "test_run"
        assert run["status"] == "RUNNING"
        assert "run_id" in run
        assert "start_time" in run
        assert run["tags"]["custom_tag"] == "test_value"
        assert run["tags"]["project"] == "smartcloudops-ai"

        # Check fallback file was created
        run_files = os.listdir(self.mlflow_manager.fallback_storage_path)
        assert len(run_files) > 0
        assert any(f.endswith(".json") for f in run_files)

    def test_start_nested_run(self):
        """Test starting nested runs."""
        parent_run = self.mlflow_manager.start_run("parent_run")
        nested_run = self.mlflow_manager.start_run("nested_run", nested=True)

        assert parent_run["run_name"] == "parent_run"
        assert nested_run["run_name"] == "nested_run"

    def test_end_run(self):
        """Test ending a run."""
        # Should not raise an exception
        self.mlflow_manager.end_run("FINISHED")
        self.mlflow_manager.end_run("FAILED")

    # ===== PARAMETER LOGGING TESTS =====

    def test_log_model_params_fallback(self):
        """Test logging parameters with fallback."""
        params = {
            "learning_rate": 0.01,
            "epochs": 100,
            "batch_size": 32,
            "optimizer": "adam",
        }

        self.mlflow_manager.log_model_params(params)

        # Check fallback file was created
        params_file = os.path.join(
            self.mlflow_manager.fallback_storage_path, "latest_params.json"
        )
        assert os.path.exists(params_file)

        with open(params_file, "r") as f:
            saved_params = json.load(f)

        assert saved_params == params

    def test_log_model_params_complex_types(self):
        """Test logging parameters with complex types."""
        params = {
            "string_param": "test_value",
            "int_param": 42,
            "float_param": 3.14159,
            "bool_param": True,
            "list_param": [1, 2, 3],
            "dict_param": {"nested": "value"},
        }

        self.mlflow_manager.log_model_params(params)

        params_file = os.path.join(
            self.mlflow_manager.fallback_storage_path, "latest_params.json"
        )
        with open(params_file, "r") as f:
            saved_params = json.load(f)

        assert saved_params == params

    # ===== METRICS LOGGING TESTS =====

    def test_log_model_metrics_fallback(self):
        """Test logging metrics with fallback."""
        metrics = {
            "accuracy": 0.95,
            "precision": 0.92,
            "recall": 0.88,
            "f1_score": 0.90,
        }

        self.mlflow_manager.log_model_metrics(metrics, step=1)

        # Check fallback file was created
        metrics_file = os.path.join(
            self.mlflow_manager.fallback_storage_path, "latest_metrics.json"
        )
        assert os.path.exists(metrics_file)

        with open(metrics_file, "r") as f:
            saved_metrics = json.load(f)

        assert saved_metrics["metrics"] == metrics
        assert saved_metrics["step"] == 1
        assert "timestamp" in saved_metrics

    def test_log_model_metrics_without_step(self):
        """Test logging metrics without step parameter."""
        metrics = {"loss": 0.05}

        self.mlflow_manager.log_model_metrics(metrics)

        metrics_file = os.path.join(
            self.mlflow_manager.fallback_storage_path, "latest_metrics.json"
        )
        with open(metrics_file, "r") as f:
            saved_metrics = json.load(f)

        assert saved_metrics["metrics"] == metrics
        assert saved_metrics["step"] is None

    # ===== ARTIFACT LOGGING TESTS =====

    def test_log_model_artifact_fallback(self):
        """Test logging artifacts with fallback."""
        # Create a temporary test file
        test_file = os.path.join(self.temp_dir, "test_artifact.txt")
        with open(test_file, "w") as f:
            f.write("test artifact content")

        self.mlflow_manager.log_model_artifact(test_file, "artifacts/test.txt")

        # Check fallback file was created
        artifacts_file = os.path.join(
            self.mlflow_manager.fallback_storage_path, "artifacts.json"
        )
        assert os.path.exists(artifacts_file)

        with open(artifacts_file, "r") as f:
            artifacts = json.load(f)

        assert len(artifacts) == 1
        assert artifacts[0]["local_path"] == test_file
        assert artifacts[0]["artifact_path"] == "artifacts/test.txt"
        assert "timestamp" in artifacts[0]

    def test_log_multiple_artifacts(self):
        """Test logging multiple artifacts."""
        # Create multiple test files
        for i in range(3):
            test_file = os.path.join(self.temp_dir, f"test_artifact_{i}.txt")
            with open(test_file, "w") as f:
                f.write(f"test artifact content {i}")

            self.mlflow_manager.log_model_artifact(test_file, f"artifacts/test_{i}.txt")

        artifacts_file = os.path.join(
            self.mlflow_manager.fallback_storage_path, "artifacts.json"
        )
        with open(artifacts_file, "r") as f:
            artifacts = json.load(f)

        assert len(artifacts) == 3
        for i, artifact in enumerate(artifacts):
            assert f"test_artifact_{i}.txt" in artifact["local_path"]
            assert artifact["artifact_path"] == f"artifacts/test_{i}.txt"

    # ===== MODEL MANAGEMENT TESTS =====

    def test_save_model_fallback(self):
        """Test saving model with fallback."""
        # Create a mock model
        mock_model = {"type": "test_model", "parameters": {"test": "value"}}

        model_uri = self.mlflow_manager.save_model(
            mock_model, "test_model", flavor="sklearn"
        )

        assert model_uri.startswith(self.mlflow_manager.fallback_storage_path)
        assert "test_model" in model_uri

        # Check model file was created
        models_dir = os.path.join(self.mlflow_manager.fallback_storage_path, "models")
        assert os.path.exists(models_dir)

        model_files = os.listdir(models_dir)
        assert len(model_files) == 1
        assert model_files[0].startswith("test_model")
        assert model_files[0].endswith(".pkl")

    def test_save_model_different_flavors(self):
        """Test saving models with different flavors."""
        mock_model = {"test": "model"}

        sklearn_uri = self.mlflow_manager.save_model(
            mock_model, "sklearn_model", "sklearn"
        )
        pytorch_uri = self.mlflow_manager.save_model(
            mock_model, "pytorch_model", "pytorch"
        )

        assert "sklearn_model" in sklearn_uri
        assert "pytorch_model" in pytorch_uri

        models_dir = os.path.join(self.mlflow_manager.fallback_storage_path, "models")
        model_files = os.listdir(models_dir)
        assert len(model_files) == 2

    def test_register_model_fallback(self):
        """Test registering model with fallback."""
        model_uri = "file:///test/model/path"

        result = self.mlflow_manager.register_model(
            model_uri,
            "test_model",
            description="Test model description",
            tags={"version": "1.0", "type": "test"},
        )

        assert result["name"] == "test_model"
        assert result["version"] == 1
        assert result["model_uri"] == model_uri
        assert result["status"] == "registered"

        # Check registry file was created
        registry_file = os.path.join(
            self.mlflow_manager.fallback_storage_path, "model_registry.json"
        )
        assert os.path.exists(registry_file)

        with open(registry_file, "r") as f:
            registry = json.load(f)

        assert len(registry) == 1
        assert registry[0]["name"] == "test_model"
        assert registry[0]["description"] == "Test model description"
        assert registry[0]["tags"]["version"] == "1.0"

    def test_register_multiple_model_versions(self):
        """Test registering multiple versions of the same model."""
        model_name = "multi_version_model"

        # Register version 1
        result1 = self.mlflow_manager.register_model("uri_v1", model_name)
        assert result1["version"] == 1

        # Register version 2
        result2 = self.mlflow_manager.register_model("uri_v2", model_name)
        assert result2["version"] == 2

        # Check registry
        registry_file = os.path.join(
            self.mlflow_manager.fallback_storage_path, "model_registry.json"
        )
        with open(registry_file, "r") as f:
            registry = json.load(f)

        assert len(registry) == 2
        versions = [
            entry["version"] for entry in registry if entry["name"] == model_name
        ]
        assert sorted(versions) == [1, 2]

    def test_list_registered_models_fallback(self):
        """Test listing registered models with fallback."""
        # Register some models
        self.mlflow_manager.register_model("uri1", "model1")
        self.mlflow_manager.register_model("uri2", "model2")

        models = self.mlflow_manager.list_registered_models()

        assert len(models) == 2
        model_names = [model["name"] for model in models]
        assert "model1" in model_names
        assert "model2" in model_names

    def test_list_registered_models_empty(self):
        """Test listing registered models when registry is empty."""
        models = self.mlflow_manager.list_registered_models()
        assert models == []


@pytest.mark.unit
class TestMLflowManagerGlobalInstance:
    """Test global MLflow manager instance."""

    def test_get_mlflow_manager(self):
        """Test getting global MLflow manager instance."""
        manager1 = get_mlflow_manager()
        manager2 = get_mlflow_manager()

        # Should return the same instance
        assert manager1 is manager2
        assert isinstance(manager1, MLflowManager)

    def test_global_manager_configuration(self):
        """Test global manager has correct configuration."""
        manager = get_mlflow_manager()

        assert manager.experiment_name == "smartcloudops-ai"
        assert manager.enable_fallback_logging is True


@pytest.mark.unit
class TestMLflowManagerEdgeCases:
    """Test edge cases and error conditions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = MLflowManager(enable_fallback_logging=True)
        self.manager.fallback_storage_path = os.path.join(self.temp_dir, "fallback")
        os.makedirs(self.manager.fallback_storage_path, exist_ok=True)

    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_fallback_logging_disabled(self):
        """Test manager with fallback logging disabled."""
        # Create isolated temp directory for this test
        isolated_temp = tempfile.mkdtemp()

        try:
            manager = MLflowManager(enable_fallback_logging=False)
            # Override fallback path to isolated directory
            manager.fallback_storage_path = os.path.join(
                isolated_temp, "isolated_fallback"
            )

            # Operations should not raise exceptions
            manager.log_model_params({"test": "value"})
            manager.log_model_metrics({"metric": 0.5})
            manager.save_model({"test": "model"}, "test")

            # With fallback logging disabled, no directory should be created
            assert not os.path.exists(manager.fallback_storage_path)

        finally:
            # Clean up isolated temp directory
            if os.path.exists(isolated_temp):
                shutil.rmtree(isolated_temp)

    def test_empty_parameters_and_metrics(self):
        """Test logging empty parameters and metrics."""
        self.manager.log_model_params({})
        self.manager.log_model_metrics({})

        # Should not raise exceptions
        params_file = os.path.join(
            self.manager.fallback_storage_path, "latest_params.json"
        )
        metrics_file = os.path.join(
            self.manager.fallback_storage_path, "latest_metrics.json"
        )

        assert os.path.exists(params_file)
        assert os.path.exists(metrics_file)

    def test_large_parameter_values(self):
        """Test logging large parameter values."""
        large_params = {
            "large_string": "x" * 10000,
            "large_list": list(range(1000)),
            "large_dict": {f"key_{i}": f"value_{i}" for i in range(100)},
        }

        # Should not raise exceptions
        self.manager.log_model_params(large_params)

        params_file = os.path.join(
            self.manager.fallback_storage_path, "latest_params.json"
        )
        assert os.path.exists(params_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
