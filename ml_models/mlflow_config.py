"""
Enhanced MLflow Configuration for SmartCloudOps AI
Production-ready model versioning, tracking, and deployment with fallback support
Phase 2A: Enhanced MLflow integration with graceful degradation
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

# Try to import MLflow with fallback
try:
    import mlflow
    import mlflow.pytorch
    import mlflow.sklearn

    MLFLOW_AVAILABLE = True
    logger.info("MLflow successfully imported")
except ImportError as e:
    MLFLOW_AVAILABLE = False
    logger.warning(f"MLflow not available: {e}")

    # Create mock mlflow for fallback
    class MockMLflow:
        """Mock MLflow for fallback when package is not available."""

        class ActiveRun:
            def __init__(self, run_id="mock_run"):
                self.info = type("Info", (), {"run_id": run_id})()

        @staticmethod
        def set_tracking_uri(uri):
            pass

        @staticmethod
        def set_registry_uri(uri):
            pass

        @staticmethod
        def set_experiment(name):
            pass

        @staticmethod
        def start_run(run_name=None, tags=None):
            return MockMLflow.ActiveRun()

        @staticmethod
        def log_params(params):
            pass

        @staticmethod
        def log_metrics(metrics):
            pass

        @staticmethod
        def log_artifact(path, artifact_path=None):
            pass

        @staticmethod
        def end_run():
            pass

        @staticmethod
        def log_model(model, artifact_path, **kwargs):
            pass

        @staticmethod
        def register_model(model_uri, name):
            pass

    mlflow = MockMLflow()


class MLflowManager:
    """Production-ready MLflow manager with fallback support."""

    def __init__(
        self,
        tracking_uri: Optional[str] = None,
        experiment_name: str = "smartcloudops-ai",
        registry_uri: Optional[str] = None,
        enable_fallback_logging: bool = True,
    ):
        """Initialize MLflow manager with enhanced configuration.

        Args:
            tracking_uri: MLflow tracking server URI
            experiment_name: Name of the MLflow experiment
            registry_uri: MLflow model registry URI
            enable_fallback_logging: Enable local logging when MLflow unavailable
        """
        self.tracking_uri = tracking_uri or os.getenv(
            "MLFLOW_TRACKING_URI", "http://localhost:5000"
        )
        self.experiment_name = experiment_name
        self.registry_uri = registry_uri or os.getenv(
            "MLFLOW_REGISTRY_URI", "sqlite:///ml_models/mlruns.db"
        )
        self.enable_fallback_logging = enable_fallback_logging
        self.available = MLFLOW_AVAILABLE

        # Fallback storage for when MLflow is not available
        self.fallback_storage_path = os.path.join("ml_models", "fallback_logs")
        if self.enable_fallback_logging:
            os.makedirs(self.fallback_storage_path, exist_ok=True)

        if self.available:
            self._configure_mlflow()
        else:
            logger.warning("MLflow not available - using fallback logging")

        logger.info(f"MLflowManager initialized (available: {self.available})")
        logger.info(f"Tracking URI: {self.tracking_uri}")
        logger.info(f"Experiment: {self.experiment_name}")

    def _configure_mlflow(self):
        """Configure MLflow settings."""
        try:
            mlflow.set_tracking_uri(self.tracking_uri)
            mlflow.set_registry_uri(self.registry_uri)
            mlflow.set_experiment(self.experiment_name)
            logger.info("MLflow configuration successful")
        except Exception as e:
            logger.error(f"MLflow configuration failed: {e}")
            self.available = False

    def start_run(
        self, run_name: str, tags: Optional[Dict[str, str]] = None, nested: bool = False
    ) -> Union[Any, Dict]:
        """Start a new MLflow run with enhanced metadata.

        Args:
            run_name: Name of the run
            tags: Additional tags for the run
            nested: Whether this is a nested run

        Returns:
            Active MLflow run or fallback run dict
        """
        default_tags = {
            "project": "smartcloudops-ai",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "version": os.getenv("APP_VERSION", "1.0.0"),
            "framework": "Phase2A-Enhanced",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if tags:
            default_tags.update(tags)

        if self.available:
            try:
                return mlflow.start_run(
                    run_name=run_name, tags=default_tags, nested=nested
                )
            except Exception as e:
                logger.error(f"Failed to start MLflow run: {e}")
                return self._fallback_start_run(run_name, default_tags)
        else:
            return self._fallback_start_run(run_name, default_tags)

    def _fallback_start_run(self, run_name: str, tags: Dict[str, str]) -> Dict:
        """Fallback run creation when MLflow is not available."""
        run_id = f"fallback_{int(datetime.now(timezone.utc).timestamp())}_{run_name}"
        run_data = {
            "run_id": run_id,
            "run_name": run_name,
            "tags": tags,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "status": "RUNNING",
            "params": {},
            "metrics": {},
            "artifacts": [],
        }

        if self.enable_fallback_logging:
            run_file = os.path.join(self.fallback_storage_path, f"{run_id}.json")
            with open(run_file, "w") as f:
                json.dump(run_data, f, indent=2)

        logger.info(f"Started fallback run: {run_name}")
        return run_data

    def log_model_params(self, params: Dict[str, Any]) -> None:
        """Log model parameters with enhanced tracking."""
        if self.available:
            try:
                mlflow.log_params(params)
                logger.info(f"Logged parameters to MLflow: {list(params.keys())}")
            except Exception as e:
                logger.error(f"Failed to log params to MLflow: {e}")
                self._fallback_log_params(params)
        else:
            self._fallback_log_params(params)

    def _fallback_log_params(self, params: Dict[str, Any]) -> None:
        """Fallback parameter logging."""
        if self.enable_fallback_logging:
            params_file = os.path.join(self.fallback_storage_path, "latest_params.json")
            with open(params_file, "w") as f:
                json.dump(params, f, indent=2)
        logger.info(f"Logged parameters to fallback: {list(params.keys())}")

    def log_model_metrics(
        self, metrics: Dict[str, float], step: Optional[int] = None
    ) -> None:
        """Log model metrics with enhanced tracking."""
        if self.available:
            try:
                mlflow.log_metrics(metrics, step=step)
                logger.info(f"Logged metrics to MLflow: {list(metrics.keys())}")
            except Exception as e:
                logger.error(f"Failed to log metrics to MLflow: {e}")
                self._fallback_log_metrics(metrics, step)
        else:
            self._fallback_log_metrics(metrics, step)

    def _fallback_log_metrics(
        self, metrics: Dict[str, float], step: Optional[int] = None
    ) -> None:
        """Fallback metrics logging."""
        if self.enable_fallback_logging:
            metrics_data = {
                "metrics": metrics,
                "step": step,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            metrics_file = os.path.join(
                self.fallback_storage_path, "latest_metrics.json"
            )
            with open(metrics_file, "w") as f:
                json.dump(metrics_data, f, indent=2)
        logger.info(f"Logged metrics to fallback: {list(metrics.keys())}")

    def log_model_artifact(
        self, local_path: str, artifact_path: Optional[str] = None
    ) -> None:
        """Log model artifacts with enhanced tracking."""
        if self.available:
            try:
                mlflow.log_artifact(local_path, artifact_path)
                logger.info(f"Logged artifact to MLflow: {local_path}")
            except Exception as e:
                logger.error(f"Failed to log artifact to MLflow: {e}")
                self._fallback_log_artifact(local_path, artifact_path)
        else:
            self._fallback_log_artifact(local_path, artifact_path)

    def _fallback_log_artifact(
        self, local_path: str, artifact_path: Optional[str] = None
    ) -> None:
        """Fallback artifact logging."""
        if self.enable_fallback_logging:
            artifacts_file = os.path.join(self.fallback_storage_path, "artifacts.json")
            artifact_entry = {
                "local_path": local_path,
                "artifact_path": artifact_path,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            # Load existing artifacts
            artifacts = []
            if os.path.exists(artifacts_file):
                with open(artifacts_file, "r") as f:
                    artifacts = json.load(f)

            artifacts.append(artifact_entry)

            with open(artifacts_file, "w") as f:
                json.dump(artifacts, f, indent=2)

        logger.info(f"Logged artifact to fallback: {local_path}")

    def save_model(
        self,
        model: Any,
        artifact_path: str = "model",
        flavor: str = "sklearn",
        **kwargs,
    ) -> str:
        """Save model with enhanced tracking and fallback."""
        if self.available:
            try:
                if flavor == "sklearn" and hasattr(mlflow, "sklearn"):
                    mlflow.sklearn.log_model(model, artifact_path, **kwargs)
                elif flavor == "pytorch" and hasattr(mlflow, "pytorch"):
                    mlflow.pytorch.log_model(model, artifact_path, **kwargs)
                else:
                    mlflow.log_model(model, artifact_path, **kwargs)

                logger.info(f"Saved model to MLflow: {artifact_path}")
                return f"runs:/{mlflow.active_run().info.run_id}/{artifact_path}"
            except Exception as e:
                logger.error(f"Failed to save model to MLflow: {e}")
                return self._fallback_save_model(model, artifact_path, flavor)
        else:
            return self._fallback_save_model(model, artifact_path, flavor)

    def _fallback_save_model(self, model: Any, artifact_path: str, flavor: str) -> str:
        """Fallback model saving."""
        if self.enable_fallback_logging:
            import pickle

            model_dir = os.path.join(self.fallback_storage_path, "models")
            os.makedirs(model_dir, exist_ok=True)

            timestamp = int(datetime.now(timezone.utc).timestamp())
            model_file = os.path.join(model_dir, f"{artifact_path}_{timestamp}.pkl")

            with open(model_file, "wb") as f:
                pickle.dump(model, f)

            logger.info(f"Saved model to fallback: {model_file}")
            return model_file

        return f"fallback:/{artifact_path}"

    def register_model(
        self,
        model_uri: str,
        name: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Register model in registry with enhanced metadata."""
        if self.available:
            try:
                registered_model = mlflow.register_model(model_uri, name)
                logger.info(f"Registered model: {name}")
                return {
                    "name": name,
                    "version": getattr(registered_model, "version", 1),
                    "model_uri": model_uri,
                    "status": "registered",
                }
            except Exception as e:
                logger.error(f"Failed to register model: {e}")
                return self._fallback_register_model(model_uri, name, description, tags)
        else:
            return self._fallback_register_model(model_uri, name, description, tags)

    def _fallback_register_model(
        self,
        model_uri: str,
        name: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Fallback model registration."""
        if self.enable_fallback_logging:
            registry_file = os.path.join(
                self.fallback_storage_path, "model_registry.json"
            )

            # Load existing registry
            registry = []
            if os.path.exists(registry_file):
                with open(registry_file, "r") as f:
                    registry = json.load(f)

            # Calculate version
            version = len([m for m in registry if m["name"] == name]) + 1

            model_entry = {
                "name": name,
                "version": version,
                "model_uri": model_uri,
                "description": description,
                "tags": tags or {},
                "registered_at": datetime.now(timezone.utc).isoformat(),
                "status": "registered",
            }

            registry.append(model_entry)

            with open(registry_file, "w") as f:
                json.dump(registry, f, indent=2)

        logger.info(f"Registered model in fallback: {name}")
        return {
            "name": name,
            "version": version,
            "model_uri": model_uri,
            "status": "registered",
        }

    def end_run(self, status: str = "FINISHED") -> None:
        """End the current run with enhanced cleanup."""
        if self.available:
            try:
                mlflow.end_run(status=status)
                logger.info(f"Ended MLflow run with status: {status}")
            except Exception as e:
                logger.error(f"Failed to end MLflow run: {e}")
        else:
            logger.info(f"Ended fallback run with status: {status}")

    def get_experiment_info(self) -> Dict[str, Any]:
        """Get comprehensive experiment information."""
        info = {
            "name": self.experiment_name,
            "tracking_uri": self.tracking_uri,
            "registry_uri": self.registry_uri,
            "mlflow_available": self.available,
            "fallback_enabled": self.enable_fallback_logging,
        }

        if self.available:
            try:
                experiment = mlflow.get_experiment_by_name(self.experiment_name)
                if experiment:
                    info.update(
                        {
                            "experiment_id": experiment.experiment_id,
                            "lifecycle_stage": experiment.lifecycle_stage,
                            "artifact_location": experiment.artifact_location,
                        }
                    )
            except Exception as e:
                logger.error(f"Failed to get experiment info: {e}")

        return info

    def list_registered_models(self) -> List[Dict[str, Any]]:
        """List all registered models."""
        if self.available:
            try:
                from mlflow.tracking import MlflowClient

                client = MlflowClient()
                models = client.list_registered_models()
                return [
                    {
                        "name": model.name,
                        "description": getattr(model, "description", ""),
                        "creation_timestamp": getattr(
                            model, "creation_timestamp", None
                        ),
                        "last_updated_timestamp": getattr(
                            model, "last_updated_timestamp", None
                        ),
                    }
                    for model in models
                ]
            except Exception as e:
                logger.error(f"Failed to list registered models: {e}")

        # Fallback model listing
        if self.enable_fallback_logging:
            registry_file = os.path.join(
                self.fallback_storage_path, "model_registry.json"
            )
            if os.path.exists(registry_file):
                with open(registry_file, "r") as f:
                    return json.load(f)

        return []


# Global instance for easy access
_mlflow_manager = None


def get_mlflow_manager() -> MLflowManager:
    """Get the global MLflow manager instance."""
    global _mlflow_manager
    if _mlflow_manager is None:
        _mlflow_manager = MLflowManager()
    return _mlflow_manager


def initialize_mlflow_manager(
    tracking_uri: Optional[str] = None,
    experiment_name: str = "smartcloudops-ai",
    registry_uri: Optional[str] = None,
) -> MLflowManager:
    """Initialize MLflow manager with custom configuration."""
    global _mlflow_manager
    _mlflow_manager = MLflowManager(
        tracking_uri=tracking_uri,
        experiment_name=experiment_name,
        registry_uri=registry_uri,
    )
    return _mlflow_manager


# Convenience functions for direct usage
def start_run(run_name: str, tags: Optional[Dict[str, str]] = None):
    """Start an MLflow run using the global manager."""
    return get_mlflow_manager().start_run(run_name, tags)


def log_params(params: Dict[str, Any]) -> None:
    """Log parameters using the global manager."""
    get_mlflow_manager().log_model_params(params)


def log_metrics(metrics: Dict[str, float], step: Optional[int] = None) -> None:
    """Log metrics using the global manager."""
    get_mlflow_manager().log_model_metrics(metrics, step)


def end_run(status: str = "FINISHED") -> None:
    """End run using the global manager."""
    get_mlflow_manager().end_run(status)
