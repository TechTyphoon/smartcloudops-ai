"""
MLflow Configuration for SmartCloudOps AI
Model versioning, tracking, and deployment management
"""

import os
import mlflow
import mlflow.sklearn
import mlflow.pytorch
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MLflowManager:
    """MLflow manager for model versioning and tracking."""

    def __init__(self, tracking_uri: Optional[str] = None, experiment_name: str = "smartcloudops-ai"):
        """Initialize MLflow manager.
        
        Args:
            tracking_uri: MLflow tracking server URI
            experiment_name: Name of the MLflow experiment
        """
        self.tracking_uri = tracking_uri or os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
        self.experiment_name = experiment_name
        self.registry_uri = os.getenv("MLFLOW_REGISTRY_URI", "sqlite:///mlruns.db")
        
        # Configure MLflow
        mlflow.set_tracking_uri(self.tracking_uri)
        mlflow.set_registry_uri(self.registry_uri)
        
        # Set experiment
        mlflow.set_experiment(self.experiment_name)
        
        logger.info(f"MLflow initialized with tracking URI: {self.tracking_uri}")
        logger.info(f"Experiment: {self.experiment_name}")

    def start_run(self, run_name: str, tags: Optional[Dict[str, str]] = None) -> mlflow.ActiveRun:
        """Start a new MLflow run.
        
        Args:
            run_name: Name of the run
            tags: Additional tags for the run
            
        Returns:
            Active MLflow run
        """
        default_tags = {
            "project": "smartcloudops-ai",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "version": os.getenv("APP_VERSION", "1.0.0")
        }
        
        if tags:
            default_tags.update(tags)
            
        return mlflow.start_run(run_name=run_name, tags=default_tags)

    def log_model_params(self, params: Dict[str, Any]) -> None:
        """Log model parameters.
        
        Args:
            params: Model parameters to log
        """
        mlflow.log_params(params)
        logger.info(f"Logged parameters: {params}")

    def log_model_metrics(self, metrics: Dict[str, float]) -> None:
        """Log model metrics.
        
        Args:
            metrics: Model metrics to log
        """
        mlflow.log_metrics(metrics)
        logger.info(f"Logged metrics: {metrics}")

    def log_model_artifact(self, local_path: str, artifact_path: Optional[str] = None) -> None:
        """Log model artifacts.
        
        Args:
            local_path: Local path to the artifact
            artifact_path: Path within the run's artifact directory
        """
        mlflow.log_artifact(local_path, artifact_path)
        logger.info(f"Logged artifact: {local_path} -> {artifact_path}")

    def save_model(self, model, model_name: str, model_type: str = "sklearn") -> str:
        """Save model to MLflow registry.
        
        Args:
            model: The trained model
            model_name: Name of the model
            model_type: Type of model (sklearn, pytorch, etc.)
            
        Returns:
            Model URI
        """
        if model_type == "sklearn":
            mlflow.sklearn.log_model(model, model_name)
        elif model_type == "pytorch":
            mlflow.pytorch.log_model(model, model_name)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
            
        model_uri = f"runs:/{mlflow.active_run().info.run_id}/{model_name}"
        logger.info(f"Model saved with URI: {model_uri}")
        return model_uri

    def register_model(self, model_uri: str, model_name: str, version: str = "latest") -> str:
        """Register model in MLflow model registry.
        
        Args:
            model_uri: URI of the model to register
            model_name: Name for the registered model
            version: Model version
            
        Returns:
            Registered model URI
        """
        registered_model_uri = mlflow.register_model(model_uri, model_name)
        logger.info(f"Model registered: {registered_model_uri}")
        return registered_model_uri

    def load_model(self, model_name: str, version: str = "latest") -> Any:
        """Load model from MLflow registry.
        
        Args:
            model_name: Name of the model to load
            version: Model version to load
            
        Returns:
            Loaded model
        """
        model_uri = f"models:/{model_name}/{version}"
        model = mlflow.sklearn.load_model(model_uri)
        logger.info(f"Model loaded: {model_uri}")
        return model

    def transition_model_stage(self, model_name: str, version: str, stage: str) -> None:
        """Transition model to a new stage.
        
        Args:
            model_name: Name of the model
            version: Model version
            stage: Target stage (staging, production, archived)
        """
        client = mlflow.tracking.MlflowClient()
        client.transition_model_version_stage(model_name, version, stage)
        logger.info(f"Model {model_name} v{version} transitioned to {stage}")

    def get_model_versions(self, model_name: str) -> list:
        """Get all versions of a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            List of model versions
        """
        client = mlflow.tracking.MlflowClient()
        versions = client.search_model_versions(f"name='{model_name}'")
        return versions

    def get_latest_model(self, model_name: str, stage: str = "Production") -> Optional[str]:
        """Get the latest model URI for a given stage.
        
        Args:
            model_name: Name of the model
            stage: Model stage
            
        Returns:
            Model URI or None if not found
        """
        client = mlflow.tracking.MlflowClient()
        latest_versions = client.get_latest_versions(model_name, stages=[stage])
        
        if latest_versions:
            return latest_versions[0].source
        return None

    def compare_models(self, model_name: str, version1: str, version2: str) -> Dict[str, Any]:
        """Compare two model versions.
        
        Args:
            model_name: Name of the model
            version1: First version to compare
            version2: Second version to compare
            
        Returns:
            Comparison results
        """
        client = mlflow.tracking.MlflowClient()
        
        # Get model versions
        v1 = client.get_model_version(model_name, version1)
        v2 = client.get_model_version(model_name, version2)
        
        comparison = {
            "model_name": model_name,
            "version1": {
                "version": v1.version,
                "stage": v1.current_stage,
                "created_at": v1.creation_timestamp,
                "metrics": v1.run.data.metrics if v1.run else {}
            },
            "version2": {
                "version": v2.version,
                "stage": v2.current_stage,
                "created_at": v2.creation_timestamp,
                "metrics": v2.run.data.metrics if v2.run else {}
            }
        }
        
        return comparison

    def delete_model_version(self, model_name: str, version: str) -> None:
        """Delete a model version.
        
        Args:
            model_name: Name of the model
            version: Version to delete
        """
        client = mlflow.tracking.MlflowClient()
        client.delete_model_version(model_name, version)
        logger.info(f"Deleted model {model_name} v{version}")

    def export_model(self, model_name: str, version: str, export_path: str) -> None:
        """Export model to local filesystem.
        
        Args:
            model_name: Name of the model
            version: Model version
            export_path: Local path to export to
        """
        model_uri = f"models:/{model_name}/{version}"
        mlflow.sklearn.save_model(model_uri, export_path)
        logger.info(f"Model exported to: {export_path}")


# Global MLflow manager instance
mlflow_manager = MLflowManager()


def get_mlflow_manager() -> MLflowManager:
    """Get the global MLflow manager instance.
    
    Returns:
        MLflowManager instance
    """
    return mlflow_manager
