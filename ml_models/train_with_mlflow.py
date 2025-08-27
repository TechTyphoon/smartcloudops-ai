"""
ML Training Pipeline with MLflow Integration
Automated model training, evaluation, and deployment
"""

import os
import sys
import logging
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_models.mlflow_config import get_mlflow_manager
from ml_models.anomaly_detector import AnomalyDetector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MLTrainingPipeline:
    """ML training pipeline with MLflow integration."""""

    def __init__(self, experiment_name: str = "anomaly-detection"):
        """Initialize training pipeline.

        Args:
            experiment_name: Name of the MLflow experiment
        """
        self.mlflow_manager = get_mlflow_manager()
        self.experiment_name = experiment_name
        self.model_name = "anomaly-detector"

        # Training parameters
        self.default_params = {
            "contamination": 0.05,
            "n_estimators": 100,
            "max_samples": "auto",
            "random_state": 42,
        }

    def prepare_data(self, data_path: str) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data.

        Args:
            data_path: Path to training data

        Returns:
            Tuple of (X_train, X_test)
        """
        logger.info(f"Loading data from {data_path}")

        # Load data (example with synthetic data)
        # In production, this would load from your data source
        np.random.seed(42)
        n_samples = 10000

        # Generate normal data
        normal_data = np.random.normal(0, 1, (n_samples, 10))

        # Generate some anomalies
        n_anomalies = int(n_samples * 0.05)
        anomaly_data = np.random.normal(5, 2, (n_anomalies, 10))

        # Combine data
        X = np.vstack([normal_data, anomaly_data])

        # Split data
        X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)

        logger.info(
            f"Data prepared: {X_train.shape[0]} training samples, {X_test.shape[0]} test samples"
        )
        return X_train, X_test

    def train_model(
        self, X_train: np.ndarray, params: Optional[Dict[str, Any]] = None
    ) -> IsolationForest:
        """Train the anomaly detection model.

        Args:
            X_train: Training data
            params: Model parameters

        Returns:
            Trained model
        """
        if params is None:
            params = self.default_params

        logger.info(f"Training model with parameters: {params}")

        # Scale the data
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)

        # Train model
        model = IsolationForest(**params)
        model.fit(X_train_scaled)

        # Save scaler
        scaler_path = "models/scaler.pkl"
        os.makedirs("models", exist_ok=True)
        joblib.dump(scaler, scaler_path)

        logger.info("Model training completed")
        return model, scaler

    def evaluate_model(
        self, model: IsolationForest, X_test: np.ndarray, scaler: StandardScaler
    ) -> Dict[str, float]:
        """Evaluate the trained model.

        Args:
            model: Trained model
            X_test: Test data
            scaler: Fitted scaler

        Returns:
            Dictionary of evaluation metrics
        """
        logger.info("Evaluating model")

        # Scale test data
        X_test_scaled = scaler.transform(X_test)

        # Make predictions
        predictions = model.predict(X_test_scaled)
        scores = model.score_samples(X_test_scaled)

        # Calculate metrics
        # For anomaly detection, we use the score distribution
        metrics = {
            "mean_score": float(np.mean(scores)),
            "std_score": float(np.std(scores)),
            "min_score": float(np.min(scores)),
            "max_score": float(np.max(scores)),
            "anomaly_ratio": float(np.sum(predictions == -1) / len(predictions)),
            "model_contamination": model.contamination,
        }

        logger.info(f"Model evaluation completed: {metrics}")
        return metrics

    def run_training_pipeline(
        self, data_path: str, params: Optional[Dict[str, Any]] = None
    ) -> str:
        """Run the complete training pipeline.

        Args:
            data_path: Path to training data
            params: Model parameters

        Returns:
            Model URI
        """
        logger.info("Starting ML training pipeline")

        # Start MLflow run
        run_name = f"anomaly-detection-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        with self.mlflow_manager.start_run(run_name=run_name) as run:
            logger.info(f"MLflow run started: {run.info.run_id}")

            # Log parameters
            if params is None:
                params = self.default_params
            self.mlflow_manager.log_model_params(params)

            # Prepare data
            X_train, X_test = self.prepare_data(data_path)

            # Log data info
            self.mlflow_manager.log_model_params(
                {
                    "n_training_samples": X_train.shape[0],
                    "n_test_samples": X_test.shape[0],
                    "n_features": X_train.shape[1],
                }
            )

            # Train model
            model, scaler = self.train_model(X_train, params)

            # Evaluate model
            metrics = self.evaluate_model(model, X_test, scaler)
            self.mlflow_manager.log_model_metrics(metrics)

            # Save model artifacts
            model_path = "models/anomaly_detector.pkl"
            os.makedirs("models", exist_ok=True)
            joblib.dump(model, model_path)

            # Log model artifacts
            self.mlflow_manager.log_model_artifact(model_path, "model")
            self.mlflow_manager.log_model_artifact("models/scaler.pkl", "scaler")

            # Save model to MLflow
            model_uri = self.mlflow_manager.save_model(
                model, self.model_name, "sklearn"
            )

            # Register model
            registered_uri = self.mlflow_manager.register_model(
                model_uri, self.model_name
            )

            logger.info(f"Training pipeline completed. Model URI: {registered_uri}")
            return registered_uri

    def deploy_model(
        self, model_name: str, version: str, stage: str = "Staging"
    ) -> None:
        """Deploy model to specified stage.

        Args:
            model_name: Name of the model
            version: Model version
            stage: Target stage
        """
        logger.info(f"Deploying model {model_name} v{version} to {stage}")

        # Transition model to target stage
        self.mlflow_manager.transition_model_stage(model_name, version, stage)

        # Export model for deployment
        export_path = f"models/{model_name}-{version}"
        self.mlflow_manager.export_model(model_name, version, export_path)

        logger.info(f"Model deployed to {stage} and exported to {export_path}")

    def compare_and_promote(
        self, model_name: str, new_version: str, baseline_version: str = "latest"
    ) -> bool:
        """Compare new model with baseline and promote if better.

        Args:
            model_name: Name of the model
            new_version: New model version
            baseline_version: Baseline version to compare against

        Returns:
            True if model should be promoted, False otherwise
        """
        logger.info(
            f"Comparing model {model_name} v{new_version} with v{baseline_version}"
        )

        # Compare models
        comparison = self.mlflow_manager.compare_models(
            model_name, new_version, baseline_version
        )

        # Simple promotion logic (can be enhanced)
        new_score = comparison["version1"]["metrics"].get("mean_score", 0)
        baseline_score = comparison["version2"]["metrics"].get("mean_score", 0)

        # Promote if new model has better score (higher mean_score for anomaly detection)
        should_promote = new_score > baseline_score

        if should_promote:
            logger.info(
                f"Model {new_version} performs better. Promoting to Production."
            )
            self.mlflow_manager.transition_model_stage(
                model_name, new_version, "Production"
            )
        else:
            logger.info(
                f"Model {new_version} does not perform better. Keeping in Staging."
            )

        return should_promote

    def cleanup_old_models(self, model_name: str, keep_versions: int = 5) -> None:
        """Clean up old model versions.

        Args:
            model_name: Name of the model
            keep_versions: Number of versions to keep
        """
        logger.info(f"Cleaning up old versions of {model_name}")

        # Get all versions
        versions = self.mlflow_manager.get_model_versions(model_name)

        # Sort by creation time
        versions.sort(key=lambda x: x.creation_timestamp, reverse=True)

        # Delete old versions
        for version in versions[keep_versions:]:
            if version.current_stage != "Production":  # Don't delete production models
                logger.info(f"Deleting old version {version.version}")
                self.mlflow_manager.delete_model_version(
                    model_name, str(version.version)
                )


def main():
    """Main training pipeline execution."""""
    # Initialize pipeline
    pipeline = MLTrainingPipeline()

    # Run training
    data_path = "data/training_data.csv"  # Update with your data path
    model_uri = pipeline.run_training_pipeline(data_path)

    # Deploy to staging
    pipeline.deploy_model("anomaly-detector", "latest", "Staging")

    # Compare and promote if better
    pipeline.compare_and_promote("anomaly-detector", "latest")

    # Cleanup old models
    pipeline.cleanup_old_models("anomaly-detector")


if __name__ == "__main__":
    main()
