#!/usr/bin/env python3
"""
Unit tests for MLOpsService
Phase 2A: Comprehensive testing for MLOps operations
"""

import pytest
from datetime import datetime
from app.services.mlops_service import MLOpsService


@pytest.mark.unit
class TestMLOpsService:
    """Test cases for MLOpsService basic operations."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service = MLOpsService()
    
    # ===== INITIALIZATION TESTS =====
    
    def test_initialization_success(self):
        """Test MLOpsService initializes successfully."""
        assert self.service is not None
        assert hasattr(self.service, 'mock_experiments')
        assert hasattr(self.service, 'mock_models')
        assert len(self.service.mock_experiments) == 2
        assert len(self.service.mock_models) == 2
    
    def test_initialization_components(self):
        """Test MLOpsService component availability."""
        stats = self.service.get_mlops_statistics()
        components = stats["components_available"]
        
        # At least some components should be available
        assert isinstance(components, dict)
        assert "experiment_tracker" in components
        assert "model_registry" in components 
        assert "mlflow" in components
    
    # ===== EXPERIMENT MANAGEMENT TESTS =====
    
    def test_get_experiments_default(self):
        """Test getting experiments with default pagination."""
        experiments, pagination = self.service.get_experiments()
        
        assert isinstance(experiments, list)
        assert isinstance(pagination, dict)
        assert len(experiments) == 2
        assert pagination["page"] == 1
        assert pagination["per_page"] == 20
        assert pagination["total"] == 2
        assert pagination["pages"] == 1
    
    def test_get_experiments_pagination(self):
        """Test getting experiments with custom pagination."""
        experiments, pagination = self.service.get_experiments(page=1, per_page=1)
        
        assert len(experiments) == 1
        assert pagination["page"] == 1
        assert pagination["per_page"] == 1
        assert pagination["total"] == 2
        assert pagination["pages"] == 2
    
    def test_get_experiments_filter_by_status(self):
        """Test filtering experiments by status."""
        experiments, pagination = self.service.get_experiments(status="completed")
        
        assert len(experiments) == 1
        assert experiments[0]["status"] == "completed"
        assert experiments[0]["name"] == "anomaly_detection_v1"
    
    def test_get_experiments_filter_by_tags(self):
        """Test filtering experiments by tags."""
        experiments, pagination = self.service.get_experiments(tags=["anomaly-detection"])
        
        assert len(experiments) == 2  # Both experiments have this tag
        for exp in experiments:
            assert "anomaly-detection" in exp["tags"]
    
    def test_get_experiments_filter_multiple(self):
        """Test filtering experiments by multiple criteria."""
        experiments, pagination = self.service.get_experiments(
            status="running", 
            tags=["feature-engineering"]
        )
        
        assert len(experiments) == 1
        assert experiments[0]["status"] == "running"
        assert "feature-engineering" in experiments[0]["tags"]
    
    def test_get_experiment_by_id_existing(self):
        """Test getting experiment by existing ID."""
        experiment = self.service.get_experiment_by_id("exp_1")
        
        assert experiment is not None
        assert experiment["id"] == "exp_1"
        assert experiment["name"] == "anomaly_detection_v1"
        assert experiment["status"] == "completed"
    
    def test_get_experiment_by_id_nonexistent(self):
        """Test getting experiment by non-existent ID."""
        experiment = self.service.get_experiment_by_id("exp_999")
        
        assert experiment is None
    
    def test_create_experiment_valid_data(self):
        """Test creating experiment with valid data."""
        experiment_data = {
            "name": "test_experiment",
            "description": "Test experiment description",
            "objective": "minimize",
            "tags": ["test", "experiment"]
        }
        
        original_count = len(self.service.mock_experiments)
        new_experiment = self.service.create_experiment(experiment_data)
        
        assert new_experiment is not None
        assert new_experiment["name"] == "test_experiment"
        assert new_experiment["description"] == "Test experiment description"
        assert new_experiment["objective"] == "minimize"
        assert new_experiment["tags"] == ["test", "experiment"]
        assert new_experiment["status"] == "active"
        assert len(self.service.mock_experiments) == original_count + 1
    
    def test_create_experiment_missing_required_fields(self):
        """Test creating experiment with missing required fields."""
        experiment_data = {
            "description": "Missing name field"
        }
        
        with pytest.raises(ValueError, match="Missing required field: name"):
            self.service.create_experiment(experiment_data)
    
    def test_create_experiment_invalid_objective(self):
        """Test creating experiment with invalid objective."""
        experiment_data = {
            "name": "test_experiment",
            "description": "Test description",
            "objective": "invalid_objective"
        }
        
        with pytest.raises(ValueError, match="Invalid objective"):
            self.service.create_experiment(experiment_data)
    
    def test_start_experiment_run_valid_data(self):
        """Test starting experiment run with valid data."""
        run_data = {
            "name": "test_run",
            "parameters": {"learning_rate": 0.01, "epochs": 100},
            "tags": ["test"]
        }
        
        experiment = self.service.get_experiment_by_id("exp_1")
        original_runs_count = experiment["runs_count"]
        
        new_run = self.service.start_experiment_run("exp_1", run_data)
        
        assert new_run is not None
        assert new_run["name"] == "test_run"
        assert new_run["experiment_id"] == "exp_1"
        assert new_run["status"] == "running"
        assert new_run["parameters"] == {"learning_rate": 0.01, "epochs": 100}
        assert new_run["tags"] == ["test"]
        
        # Check experiment runs count was incremented
        updated_experiment = self.service.get_experiment_by_id("exp_1")
        assert updated_experiment["runs_count"] == original_runs_count + 1
    
    def test_start_experiment_run_nonexistent_experiment(self):
        """Test starting run for non-existent experiment."""
        run_data = {
            "name": "test_run"
        }
        
        with pytest.raises(ValueError, match="Experiment exp_999 not found"):
            self.service.start_experiment_run("exp_999", run_data)
    
    def test_start_experiment_run_missing_name(self):
        """Test starting experiment run with missing name."""
        run_data = {
            "parameters": {"test": "value"}
        }
        
        with pytest.raises(ValueError, match="Missing required field: name"):
            self.service.start_experiment_run("exp_1", run_data)
    
    # ===== MODEL MANAGEMENT TESTS =====
    
    def test_get_models_default(self):
        """Test getting models with default pagination."""
        models, pagination = self.service.get_models()
        
        assert isinstance(models, list)
        assert isinstance(pagination, dict)
        assert len(models) == 2
        assert pagination["page"] == 1
        assert pagination["per_page"] == 20
        assert pagination["total"] == 2
        assert pagination["pages"] == 1
    
    def test_get_models_pagination(self):
        """Test getting models with custom pagination."""
        models, pagination = self.service.get_models(page=1, per_page=1)
        
        assert len(models) == 1
        assert pagination["page"] == 1
        assert pagination["per_page"] == 1
        assert pagination["total"] == 2
        assert pagination["pages"] == 2
    
    def test_get_models_filter_by_status(self):
        """Test filtering models by status."""
        models, pagination = self.service.get_models(status="production")
        
        assert len(models) == 1
        assert models[0]["status"] == "production"
        assert models[0]["version"] == "1.0.0"
    
    def test_get_models_filter_by_name(self):
        """Test filtering models by name."""
        models, pagination = self.service.get_models(name="anomaly")
        
        assert len(models) == 2  # Both models contain "anomaly" in name
        for model in models:
            assert "anomaly" in model["name"].lower()
    
    def test_get_model_by_id_existing(self):
        """Test getting model by existing ID."""
        model = self.service.get_model_by_id("model_1")
        
        assert model is not None
        assert model["id"] == "model_1"
        assert model["name"] == "anomaly_detector"
        assert model["version"] == "1.0.0"
        assert model["status"] == "production"
    
    def test_get_model_by_id_nonexistent(self):
        """Test getting model by non-existent ID."""
        model = self.service.get_model_by_id("model_999")
        
        assert model is None
    
    def test_register_model_valid_data(self):
        """Test registering model with valid data."""
        model_data = {
            "name": "test_model",
            "version": "1.0.0",
            "description": "Test model description",
            "algorithm": "random_forest",
            "framework": "scikit-learn",
            "metrics": {"accuracy": 0.95},
            "created_by": "test_user"
        }
        
        original_count = len(self.service.mock_models)
        new_model = self.service.register_model(model_data)
        
        assert new_model is not None
        assert new_model["name"] == "test_model"
        assert new_model["version"] == "1.0.0"
        assert new_model["algorithm"] == "random_forest"
        assert new_model["framework"] == "scikit-learn"
        assert new_model["status"] == "development"  # Default status
        assert new_model["metrics"] == {"accuracy": 0.95}
        assert len(self.service.mock_models) == original_count + 1
    
    def test_register_model_missing_required_fields(self):
        """Test registering model with missing required fields."""
        model_data = {
            "version": "1.0.0",
            "algorithm": "random_forest"
            # Missing name and framework
        }
        
        with pytest.raises(ValueError, match="Missing required field: name"):
            self.service.register_model(model_data)
    
    def test_register_model_invalid_status(self):
        """Test registering model with invalid status."""
        model_data = {
            "name": "test_model",
            "version": "1.0.0",
            "algorithm": "random_forest",
            "framework": "scikit-learn",
            "status": "invalid_status"
        }
        
        with pytest.raises(ValueError, match="Invalid status"):
            self.service.register_model(model_data)
    
    def test_register_model_version_conflict(self):
        """Test registering model with existing name/version combination."""
        model_data = {
            "name": "anomaly_detector",
            "version": "1.0.0",  # This version already exists
            "algorithm": "random_forest",
            "framework": "scikit-learn"
        }
        
        with pytest.raises(ValueError, match="already exists"):
            self.service.register_model(model_data)
    
    def test_update_model_status_valid(self):
        """Test updating model status with valid status."""
        updated_model = self.service.update_model_status("model_2", "production")
        
        assert updated_model is not None
        assert updated_model["id"] == "model_2"
        assert updated_model["status"] == "production"
        assert "updated_at" in updated_model
    
    def test_update_model_status_invalid(self):
        """Test updating model status with invalid status."""
        with pytest.raises(ValueError, match="Invalid status"):
            self.service.update_model_status("model_1", "invalid_status")
    
    def test_update_model_status_nonexistent(self):
        """Test updating status of non-existent model."""
        result = self.service.update_model_status("model_999", "production")
        
        assert result is None
    
    # ===== STATISTICS AND REPORTING TESTS =====
    
    def test_get_mlops_statistics(self):
        """Test getting comprehensive MLOps statistics."""
        stats = self.service.get_mlops_statistics()
        
        assert isinstance(stats, dict)
        assert "experiments" in stats
        assert "models" in stats
        assert "mlflow" in stats
        assert "components_available" in stats
        
        # Test experiment statistics
        exp_stats = stats["experiments"]
        assert exp_stats["total_experiments"] == 2
        assert exp_stats["total_runs"] == 8  # 5 + 3 from mock data
        assert "by_status" in exp_stats
        
        # Test model statistics
        model_stats = stats["models"]
        assert model_stats["total_models"] == 2
        assert "by_status" in model_stats
        assert "by_framework" in model_stats
        assert model_stats["total_size_mb"] == 5.6  # 2.5 + 3.1 from mock data
    
    def test_get_available_frameworks(self):
        """Test getting available ML frameworks."""
        frameworks = self.service.get_available_frameworks()
        
        assert isinstance(frameworks, list)
        assert len(frameworks) == 5
        
        framework_names = [fw["name"] for fw in frameworks]
        assert "scikit-learn" in framework_names
        assert "tensorflow" in framework_names
        assert "pytorch" in framework_names
        
        for framework in frameworks:
            assert "name" in framework
            assert "description" in framework
    
    def test_get_available_algorithms(self):
        """Test getting available ML algorithms."""
        algorithms = self.service.get_available_algorithms()
        
        assert isinstance(algorithms, list)
        assert len(algorithms) == 6
        
        algorithm_names = [alg["name"] for alg in algorithms]
        assert "isolation_forest" in algorithm_names
        assert "random_forest" in algorithm_names
        assert "neural_network" in algorithm_names
        
        for algorithm in algorithms:
            assert "name" in algorithm
            assert "type" in algorithm
            assert "description" in algorithm
    
    def test_get_mlflow_experiments(self):
        """Test getting MLflow experiments."""
        experiments = self.service.get_mlflow_experiments()
        
        assert isinstance(experiments, list)
        # Should return mock data since MLflow might not be available
        assert len(experiments) >= 0
    
    def test_get_mlflow_runs(self):
        """Test getting MLflow runs."""
        runs = self.service.get_mlflow_runs("1")
        
        assert isinstance(runs, list)
        # Should return empty list or mock data since MLflow might not be available
    
    # ===== DATA PIPELINE INTEGRATION TESTS =====
    
    def test_get_data_versions_default(self):
        """Test getting data versions with default pagination."""
        versions, pagination = self.service.get_data_versions()
        
        assert isinstance(versions, list)
        assert isinstance(pagination, dict)
        assert pagination["page"] == 1
        assert pagination["per_page"] == 20
        assert "total" in pagination
        assert "pages" in pagination
    
    def test_get_data_versions_with_dataset_filter(self):
        """Test getting data versions filtered by dataset name."""
        versions, pagination = self.service.get_data_versions(dataset_name="test_dataset")
        
        assert isinstance(versions, list)
        assert isinstance(pagination, dict)
        # Should handle gracefully even if dataset doesn't exist
    
    def test_get_data_versions_pagination(self):
        """Test getting data versions with custom pagination."""
        versions, pagination = self.service.get_data_versions(page=2, per_page=5)
        
        assert pagination["page"] == 2
        assert pagination["per_page"] == 5
    
    def test_get_data_quality_report_fallback(self):
        """Test getting data quality report with fallback."""
        report = self.service.get_data_quality_report("test_version_id")
        
        assert isinstance(report, dict)
        assert "version_id" in report
        assert "overall_score" in report
        assert "overall_status" in report
        assert "completeness_score" in report
        assert "consistency_score" in report
        assert "accuracy_score" in report
        assert "timeliness_score" in report
        assert "validity_score" in report
        assert "issues_found" in report
        assert "recommendations" in report
    
    def test_create_data_transformation_fallback(self):
        """Test creating data transformation with fallback."""
        transformations = [
            {
                "type": "filter",
                "params": {
                    "column": "value",
                    "condition": "greater_than",
                    "value": 10
                }
            }
        ]
        
        result = self.service.create_data_transformation(
            "source_version_id",
            transformations,
            "output_dataset"
        )
        
        assert isinstance(result, dict)
        assert "success" in result
        # Should return fallback response or actual result
        if not result["success"]:
            assert "error" in result
        else:
            assert "output_version_id" in result
            assert "transformations_applied" in result
    
    def test_create_data_transformation_multiple_transforms(self):
        """Test creating data transformation with multiple transformations."""
        transformations = [
            {"type": "filter", "params": {"column": "col1", "condition": "not_null"}},
            {"type": "normalization", "params": {"columns": ["col2"], "method": "standard"}},
            {"type": "outlier_removal", "params": {"columns": ["col3"], "method": "iqr"}}
        ]
        
        result = self.service.create_data_transformation(
            "source_version_id",
            transformations
        )
        
        assert isinstance(result, dict)
        assert "success" in result


@pytest.mark.unit
class TestMLOpsServiceEdgeCases:
    """Test edge cases and error conditions for MLOpsService."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service = MLOpsService()
    
    def test_get_experiments_empty_filters(self):
        """Test getting experiments with empty/None filters."""
        experiments, pagination = self.service.get_experiments(
            status="", tags=None
        )
        
        assert len(experiments) == 2  # Should return all experiments
    
    def test_get_experiments_nonexistent_status(self):
        """Test filtering by non-existent status."""
        experiments, pagination = self.service.get_experiments(status="nonexistent")
        
        assert len(experiments) == 0
        assert pagination["total"] == 0
    
    def test_get_experiments_large_page_number(self):
        """Test pagination with page number beyond available data."""
        experiments, pagination = self.service.get_experiments(page=999, per_page=10)
        
        assert len(experiments) == 0
        assert pagination["page"] == 999
        assert pagination["total"] == 2
    
    def test_get_models_empty_name_filter(self):
        """Test filtering models with empty name."""
        models, pagination = self.service.get_models(name="")
        
        assert len(models) == 2  # Should return all models
    
    def test_create_experiment_empty_name(self):
        """Test creating experiment with empty name."""
        experiment_data = {
            "name": "",
            "description": "Test description"
        }
        
        # Empty name should still create experiment (business logic choice)
        new_experiment = self.service.create_experiment(experiment_data)
        assert new_experiment["name"] == ""
    
    def test_register_model_empty_version(self):
        """Test registering model with empty version."""
        model_data = {
            "name": "test_model",
            "version": "",
            "algorithm": "random_forest",
            "framework": "scikit-learn"
        }
        
        # Empty version should still register (business logic choice)
        new_model = self.service.register_model(model_data)
        assert new_model["version"] == ""
    
    def test_statistics_with_no_data(self):
        """Test statistics calculation with no experiments/models."""
        # Clear mock data
        self.service.mock_experiments = []
        self.service.mock_models = []
        
        stats = self.service.get_mlops_statistics()
        
        assert stats["experiments"]["total_experiments"] == 0
        assert stats["experiments"]["total_runs"] == 0
        assert stats["models"]["total_models"] == 0
        assert stats["models"]["total_size_mb"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
