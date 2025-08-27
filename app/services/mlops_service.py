#!/usr/bin/env python3
"""
MLOpsService - Business logic for MLOps operations
Phase 2A: MLOps integration with service layer pattern
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

# Import MLOps components
# Import MLOps components with fallback
try:
    from app.mlops.experiment_tracker import ExperimentTracker, get_experiment_tracker

    EXPERIMENT_TRACKER_AVAILABLE = True
except ImportError:
    EXPERIMENT_TRACKER_AVAILABLE = False

try:
    from app.mlops.model_registry import ModelRegistry, get_model_registry

    MODEL_REGISTRY_AVAILABLE = True
except ImportError:
    MODEL_REGISTRY_AVAILABLE = False

try:
    from app.mlops.data_pipeline import DataPipelineManager, get_data_pipeline_manager

    DATA_PIPELINE_AVAILABLE = True
except ImportError:
    DATA_PIPELINE_AVAILABLE = False

try:
    from ml_models.mlflow_config import MLflowManager, get_mlflow_manager

    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False


class MLOpsService:
    """Business logic for MLOps operations including experiment tracking, model management, and MLflow integration."""

    def __init__(self):
        """Initialize MLOps service with components."""
        # Initialize available components
        self.experiment_tracker = None
        self.model_registry = None
        self.data_pipeline = None
        self.mlflow_manager = None

        if EXPERIMENT_TRACKER_AVAILABLE:
            self.experiment_tracker = get_experiment_tracker()

        if MODEL_REGISTRY_AVAILABLE:
            self.model_registry = get_model_registry()

        if DATA_PIPELINE_AVAILABLE:
            self.data_pipeline = get_data_pipeline_manager()

        if MLFLOW_AVAILABLE:
            self.mlflow_manager = get_mlflow_manager()

        # Mock data for development (will be replaced with actual MLOps data)
        self.mock_experiments = [
            {
                "id": "exp_1",
                "name": "anomaly_detection_v1",
                "description": "Initial anomaly detection model training",
                "status": "completed",
                "created_at": "2024-01-15T10:00:00Z",
                "runs_count": 5,
                "best_run_id": "run_1_3",
                "objective": "minimize",
                "tags": ["anomaly-detection", "production"],
            },
            {
                "id": "exp_2",
                "name": "anomaly_detection_v2",
                "description": "Improved anomaly detection with feature engineering",
                "status": "running",
                "created_at": "2024-01-16T09:00:00Z",
                "runs_count": 3,
                "best_run_id": "run_2_1",
                "objective": "minimize",
                "tags": ["anomaly-detection", "feature-engineering"],
            },
        ]

        self.mock_models = [
            {
                "id": "model_1",
                "name": "anomaly_detector",
                "version": "1.0.0",
                "description": "Production anomaly detection model",
                "status": "production",
                "algorithm": "isolation_forest",
                "framework": "scikit-learn",
                "metrics": {"f1_score": 0.89, "precision": 0.92, "recall": 0.86},
                "created_at": "2024-01-15T12:00:00Z",
                "created_by": "mlops_pipeline",
                "size_mb": 2.5,
            },
            {
                "id": "model_2",
                "name": "anomaly_detector",
                "version": "1.1.0",
                "description": "Enhanced anomaly detection with improved features",
                "status": "staging",
                "algorithm": "isolation_forest",
                "framework": "scikit-learn",
                "metrics": {"f1_score": 0.91, "precision": 0.94, "recall": 0.88},
                "created_at": "2024-01-16T11:00:00Z",
                "created_by": "mlops_pipeline",
                "size_mb": 3.1,
            },
        ]

    # ===== EXPERIMENT MANAGEMENT =====

    def get_experiments(
        self,
        page: int = 1,
        per_page: int = 20,
        status: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Tuple[List[Dict], Dict]:
        """Get experiments with pagination and filtering."""
        # Apply filters
        filtered_data = self.mock_experiments.copy()

        if status:
            filtered_data = [e for e in filtered_data if e["status"] == status]
        if tags:
            filtered_data = [
                e for e in filtered_data if any(tag in e["tags"] for tag in tags)
            ]

        # Calculate pagination
        total = len(filtered_data)
        start = (page - 1) * per_page
        end = start + per_page
        page_data = filtered_data[start:end]

        pagination = {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page,
        }

        return page_data, pagination

    def get_experiment_by_id(self, experiment_id: str) -> Optional[Dict]:
        """Get a specific experiment by ID."""
        for experiment in self.mock_experiments:
            if experiment["id"] == experiment_id:
                return experiment
        return None

    def create_experiment(self, experiment_data: Dict) -> Dict:
        """Create a new experiment with validation."""
        # Validate required fields
        required_fields = ["name", "description"]
        for field in required_fields:
            if field not in experiment_data:
                raise ValueError(f"Missing required field: {field}")

        # Validate objective
        valid_objectives = ["minimize", "maximize"]
        objective = experiment_data.get("objective", "minimize")
        if objective not in valid_objectives:
            raise ValueError(f"Invalid objective. Must be one of: {valid_objectives}")

        # Create new experiment
        new_id = f"exp_{len(self.mock_experiments) + 1}"
        new_experiment = {
            "id": new_id,
            "name": experiment_data["name"],
            "description": experiment_data["description"],
            "status": experiment_data.get("status", "active"),
            "objective": objective,
            "tags": experiment_data.get("tags", []),
            "created_at": datetime.now(timezone.utc).isoformat() + "Z",
            "runs_count": 0,
            "best_run_id": None,
        }

        self.mock_experiments.append(new_experiment)

        # ✅ Using mock experiment tracker for development
        # For production, uncomment below to use actual MLflow:
        # actual_exp = self.experiment_tracker.create_experiment(
        #     name=experiment_data["name"],
        #     description=experiment_data["description"],
        #     objective=objective,
        #     tags=experiment_data.get("tags", [])
        # )

        return new_experiment

    def start_experiment_run(self, experiment_id: str, run_data: Dict) -> Dict:
        """Start a new experiment run."""
        # Validate experiment exists
        experiment = self.get_experiment_by_id(experiment_id)
        if not experiment:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Validate required fields
        required_fields = ["name"]
        for field in required_fields:
            if field not in run_data:
                raise ValueError(f"Missing required field: {field}")

        # Create new run
        run_id = f"run_{experiment_id}_{int(datetime.now(timezone.utc).timestamp())}"
        new_run = {
            "id": run_id,
            "experiment_id": experiment_id,
            "name": run_data["name"],
            "status": "running",
            "parameters": run_data.get("parameters", {}),
            "metrics": {},
            "artifacts": [],
            "tags": run_data.get("tags", []),
            "started_at": datetime.now(timezone.utc).isoformat() + "Z",
            "ended_at": None,
            "duration_seconds": None,
        }

        # Update experiment run count
        experiment["runs_count"] += 1

        # ✅ Using mock experiment tracker for development
        # For production, uncomment below to use actual MLflow:
        # actual_run = self.experiment_tracker.start_run(
        #     experiment_id=experiment_id,
        #     run_name=run_data["name"],
        #     parameters=run_data.get("parameters", {}),
        #     tags=run_data.get("tags", [])
        # )

        return new_run

    # ===== MODEL MANAGEMENT =====

    def get_models(
        self,
        page: int = 1,
        per_page: int = 20,
        status: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Tuple[List[Dict], Dict]:
        """Get models with pagination and filtering."""
        # Apply filters
        filtered_data = self.mock_models.copy()

        if status:
            filtered_data = [m for m in filtered_data if m["status"] == status]
        if name:
            filtered_data = [
                m for m in filtered_data if name.lower() in m["name"].lower()
            ]

        # Calculate pagination
        total = len(filtered_data)
        start = (page - 1) * per_page
        end = start + per_page
        page_data = filtered_data[start:end]

        pagination = {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page,
        }

        return page_data, pagination

    def get_model_by_id(self, model_id: str) -> Optional[Dict]:
        """Get a specific model by ID."""
        for model in self.mock_models:
            if model["id"] == model_id:
                return model
        return None

    def register_model(self, model_data: Dict) -> Dict:
        """Register a new model with validation."""
        # Validate required fields
        required_fields = ["name", "version", "algorithm", "framework"]
        for field in required_fields:
            if field not in model_data:
                raise ValueError(f"Missing required field: {field}")

        # Validate status
        valid_statuses = [
            "development",
            "staging",
            "production",
            "archived",
            "deprecated",
        ]
        status = model_data.get("status", "development")
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")

        # Check for version conflicts
        for model in self.mock_models:
            if (
                model["name"] == model_data["name"]
                and model["version"] == model_data["version"]
            ):
                raise ValueError(
                    f"Model {model_data['name']} version {model_data['version']} already exists"
                )

        # Create new model
        new_id = f"model_{len(self.mock_models) + 1}"
        new_model = {
            "id": new_id,
            "name": model_data["name"],
            "version": model_data["version"],
            "description": model_data.get("description", ""),
            "status": status,
            "algorithm": model_data["algorithm"],
            "framework": model_data["framework"],
            "metrics": model_data.get("metrics", {}),
            "created_at": datetime.now(timezone.utc).isoformat() + "Z",
            "created_by": model_data.get("created_by", "system"),
            "size_mb": model_data.get("size_mb", 0.0),
        }

        self.mock_models.append(new_model)

        # ✅ Using mock model registry for development
        # For production, uncomment below to use actual MLflow:
        # actual_model = self.model_registry.register_model(
        #     model=model_data["model_object"],
        #     name=model_data["name"],
        #     version=model_data["version"],
        #     description=model_data.get("description", ""),
        #     algorithm=model_data["algorithm"],
        #     framework=model_data["framework"],
        #     metrics=model_data.get("metrics", {})
        # )

        return new_model

    def update_model_status(self, model_id: str, status: str) -> Optional[Dict]:
        """Update model status with validation."""
        valid_statuses = [
            "development",
            "staging",
            "production",
            "archived",
            "deprecated",
        ]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")

        model = self.get_model_by_id(model_id)
        if not model:
            return None

        model["status"] = status
        model["updated_at"] = datetime.now(timezone.utc).isoformat() + "Z"

        # ✅ Using mock model registry for development
        # For production, uncomment below to use actual MLflow:
        # self.model_registry.update_model_status(
        #     name=model["name"],
        #     version=model["version"],
        #     status=ModelStatus(status)
        # )

        return model

    # ===== DATA PIPELINE INTEGRATION =====

    def get_data_versions(
        self, dataset_name: Optional[str] = None, page: int = 1, per_page: int = 20
    ) -> Tuple[List[Dict], Dict]:
        """Get data versions with pagination and filtering."""
        if not self.data_pipeline:
            return [], {"page": page, "per_page": per_page, "total": 0, "pages": 0}

        try:
            versions = self.data_pipeline.list_versions(dataset_name)

            # Apply pagination
            total = len(versions)
            start = (page - 1) * per_page
            end = start + per_page
            page_versions = versions[start:end]

            # Convert to dictionaries
            version_dicts = []
            for version in page_versions:
                version_dict = {
                    "version_id": version.version_id,
                    "dataset_name": version.dataset_name,
                    "created_at": version.created_at.isoformat(),
                    "row_count": version.row_count,
                    "column_count": version.column_count,
                    "file_size_bytes": version.file_size_bytes,
                    "quality_score": version.quality_score,
                    "quality_status": version.quality_status.value,
                    "tags": version.tags,
                }
                version_dicts.append(version_dict)

            pagination = {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page,
            }

            return version_dicts, pagination

        except Exception as e:
            # Fallback to mock data
            mock_versions = [
                {
                    "version_id": "data_v1_20240115",
                    "dataset_name": "sample_dataset",
                    "created_at": "2024-01-15T10:00:00Z",
                    "row_count": 1000,
                    "column_count": 5,
                    "file_size_bytes": 50000,
                    "quality_score": 0.92,
                    "quality_status": "excellent",
                    "tags": ["production", "validated"],
                }
            ]

            total = len(mock_versions)
            pagination = {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": 1,
            }

            return mock_versions, pagination

    def get_data_quality_report(self, version_id: str) -> Optional[Dict]:
        """Get quality report for a data version."""
        if not self.data_pipeline:
            return {
                "version_id": version_id,
                "overall_score": 0.85,
                "overall_status": "good",
                "completeness_score": 0.90,
                "consistency_score": 0.85,
                "accuracy_score": 0.88,
                "timeliness_score": 0.80,
                "validity_score": 0.92,
                "issues_found": ["Minor missing values in optional fields"],
                "recommendations": ["Consider data validation rules"],
            }

        try:
            quality_report = self.data_pipeline.get_quality_report(version_id)
            return {
                "version_id": quality_report.version_id,
                "dataset_name": quality_report.dataset_name,
                "timestamp": quality_report.timestamp.isoformat(),
                "overall_score": quality_report.overall_score,
                "overall_status": quality_report.overall_status.value,
                "completeness_score": quality_report.completeness_score,
                "consistency_score": quality_report.consistency_score,
                "accuracy_score": quality_report.accuracy_score,
                "timeliness_score": quality_report.timeliness_score,
                "validity_score": quality_report.validity_score,
                "missing_values": quality_report.missing_values,
                "duplicate_rows": quality_report.duplicate_rows,
                "outliers": quality_report.outliers,
                "schema_violations": quality_report.schema_violations,
                "data_drift_detected": quality_report.data_drift_detected,
                "issues_found": quality_report.issues_found,
                "recommendations": quality_report.recommendations,
            }
        except Exception:
            # Return fallback quality report
            return {
                "version_id": version_id,
                "overall_score": 0.85,
                "overall_status": "good",
                "completeness_score": 0.90,
                "consistency_score": 0.85,
                "accuracy_score": 0.88,
                "timeliness_score": 0.80,
                "validity_score": 0.92,
                "issues_found": ["Minor missing values in optional fields"],
                "recommendations": ["Consider data validation rules"],
            }

    def create_data_transformation(
        self,
        source_version_id: str,
        transformations: List[Dict[str, Any]],
        target_dataset_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a data transformation pipeline."""
        if not self.data_pipeline:
            return {
                "success": False,
                "error": "Data pipeline not available",
                "fallback_version_id": f"transformed_{source_version_id}",
            }

        try:
            result_version = self.data_pipeline.transform_data(
                source_version_id, transformations, target_dataset_name
            )

            return {
                "success": True,
                "output_version_id": result_version.version_id,
                "dataset_name": result_version.dataset_name,
                "transformations_applied": len(transformations),
                "output_row_count": result_version.row_count,
                "quality_score": result_version.quality_score,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "transformations_attempted": len(transformations),
            }

    # ===== MLFLOW INTEGRATION =====

    def get_mlflow_experiments(self) -> List[Dict]:
        """Get MLflow experiments."""
        # ✅ Using mock MLflow integration for development
        # For production, uncomment below to use actual MLflow:
        # if self.mlflow_manager and self.mlflow_manager.is_available():
        #     return self.mlflow_manager.list_experiments()
        return [
            {
                "experiment_id": "1",
                "name": "Default",
                "lifecycle_stage": "active",
                "artifact_location": "mlruns/1",
            }
        ]

    def get_mlflow_runs(self, experiment_id: str) -> List[Dict]:
        """Get MLflow runs for an experiment."""
        # ✅ Using mock MLflow integration for development
        # For production, uncomment below to use actual MLflow:
        # if self.mlflow_manager and self.mlflow_manager.is_available():
        #     return self.mlflow_manager.list_runs(experiment_id)
        return []

    # ===== STATISTICS AND REPORTING =====

    def get_mlops_statistics(self) -> Dict:
        """Get comprehensive MLOps statistics."""
        # Experiment statistics
        experiment_stats = {
            "total_experiments": len(self.mock_experiments),
            "by_status": {},
            "total_runs": sum(exp["runs_count"] for exp in self.mock_experiments),
        }

        for exp in self.mock_experiments:
            status = exp["status"]
            experiment_stats["by_status"][status] = (
                experiment_stats["by_status"].get(status, 0) + 1
            )

        # Model statistics
        model_stats = {
            "total_models": len(self.mock_models),
            "by_status": {},
            "by_framework": {},
            "total_size_mb": sum(model["size_mb"] for model in self.mock_models),
        }

        for model in self.mock_models:
            status = model["status"]
            framework = model["framework"]
            model_stats["by_status"][status] = (
                model_stats["by_status"].get(status, 0) + 1
            )
            model_stats["by_framework"][framework] = (
                model_stats["by_framework"].get(framework, 0) + 1
            )

        mlflow_stats = {}
        if self.mlflow_manager:
            mlflow_stats = {
                "tracking_uri": self.mlflow_manager.tracking_uri,
                "experiment_name": self.mlflow_manager.experiment_name,
            }
        else:
            mlflow_stats = {
                "tracking_uri": "not_configured",
                "experiment_name": "not_configured",
            }

        # Data pipeline statistics
        data_pipeline_stats = {
            "total_datasets": 0,
            "total_versions": 0,
            "average_quality_score": 0.0,
            "by_quality_status": {},
        }

        if self.data_pipeline:
            try:
                all_versions = self.data_pipeline.list_versions()
                data_pipeline_stats["total_versions"] = len(all_versions)

                # Count unique datasets
                datasets = set(version.dataset_name for version in all_versions)
                data_pipeline_stats["total_datasets"] = len(datasets)

                # Calculate average quality score
                if all_versions:
                    avg_quality = sum(
                        version.quality_score for version in all_versions
                    ) / len(all_versions)
                    data_pipeline_stats["average_quality_score"] = round(avg_quality, 3)

                # Count by quality status
                for version in all_versions:
                    status = version.quality_status.value
                    data_pipeline_stats["by_quality_status"][status] = (
                        data_pipeline_stats["by_quality_status"].get(status, 0) + 1
                    )

            except Exception:
                # Use mock stats if data pipeline not available
                data_pipeline_stats = {
                    "total_datasets": 3,
                    "total_versions": 8,
                    "average_quality_score": 0.87,
                    "by_quality_status": {"excellent": 3, "good": 4, "warning": 1},
                }

        return {
            "experiments": experiment_stats,
            "models": model_stats,
            "data_pipeline": data_pipeline_stats,
            "mlflow": mlflow_stats,
            "components_available": {
                "experiment_tracker": EXPERIMENT_TRACKER_AVAILABLE,
                "model_registry": MODEL_REGISTRY_AVAILABLE,
                "data_pipeline": DATA_PIPELINE_AVAILABLE,
                "mlflow": MLFLOW_AVAILABLE,
            },
        }

    def get_available_frameworks(self) -> List[Dict]:
        """Get available ML frameworks."""
        return [
            {
                "name": "scikit-learn",
                "description": "Machine learning library for Python",
            },
            {"name": "tensorflow", "description": "Deep learning framework"},
            {"name": "pytorch", "description": "Deep learning framework"},
            {"name": "xgboost", "description": "Gradient boosting framework"},
            {"name": "lightgbm", "description": "Gradient boosting framework"},
        ]

    def get_available_algorithms(self) -> List[Dict]:
        """Get available ML algorithms."""
        return [
            {
                "name": "isolation_forest",
                "type": "anomaly_detection",
                "description": "Isolation Forest for anomaly detection",
            },
            {
                "name": "one_class_svm",
                "type": "anomaly_detection",
                "description": "One-Class SVM for anomaly detection",
            },
            {
                "name": "local_outlier_factor",
                "type": "anomaly_detection",
                "description": "Local Outlier Factor for anomaly detection",
            },
            {
                "name": "random_forest",
                "type": "classification",
                "description": "Random Forest classifier",
            },
            {
                "name": "gradient_boosting",
                "type": "classification",
                "description": "Gradient Boosting classifier",
            },
            {
                "name": "neural_network",
                "type": "deep_learning",
                "description": "Neural network for various tasks",
            },
        ]
