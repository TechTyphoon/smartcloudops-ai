#!/usr/bin/env python3
"""
Model Registry & Lifecycle Management for SmartCloudOps AI
MLOps integration with model versioning, A/B testing, and drift detection
"""

import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelStage(Enum):
    """Model lifecycle stages"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"


class ModelStatus(Enum):
    """Model status"""

    TRAINING = "training"
    READY = "ready"
    DEPLOYED = "deployed"
    FAILED = "failed"
    DEPRECATED = "deprecated"


@dataclass
class ModelVersion:
    """Model version information"""

    version: str
    model_type: str
    stage: ModelStage
    status: ModelStatus
    created_at: datetime
    trained_at: datetime
    metrics: Dict[str, float]
    hyperparameters: Dict[str, Any]
    feature_names: List[str]
    model_path: str
    scaler_path: str
    metadata: Dict[str, Any]


class ModelRegistry:
    """Model registry and lifecycle management"""

    def __init__(self, registry_dir: str = "mlops/modelsf"):
        self.registry_dir = registry_dir
        self.ensure_registry_dir()
        self.current_models = {}
        self.model_versions = {}
        self.load_registry()

    def ensure_registry_dir(self):
        """Ensure registry directory structure exists"""
        os.makedirs(self.registry_dir, exist_ok=True)
        os.makedirs(os.path.join(self.registry_dir, "models"), exist_ok=True)
        os.makedirs(os.path.join(self.registry_dir, "metadata"), exist_ok=True)
        os.makedirs(os.path.join(self.registry_dir, "experiments"), exist_ok=True)

    def load_registry(self):
        """Load existing model registry"""
        metadata_file = os.path.join(self.registry_dir, "metadata", "registry.json")
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, "r") as f:
                    registry_data = json.load(f)
                    self.model_versions = registry_data.get("model_versionsf", {})
                    self.current_models = registry_data.get("current_modelsf", {})
                logger.info("Loaded existing model registry")
            except Exception as e:
                logger.error(f"Error loading registry: {e}")

    def save_registry(self):
        """Save model registry to disk""f"
        registry_data = {
            "model_versions": self.model_versions,
            "current_models": self.current_models,
            "last_updated": datetime.now().isoformat(),
        }

        metadata_file = os.path.join(self.registry_dir, "metadata", "registry.json")
        with open(metadata_file, "w") as f:
            json.dump(registry_data, f, indent=2, default=str)

        logger.info("Saved model registry")

    def register_model(
        self,
        model_type: str,
        model,
        scaler,
        hyperparameters: Dict[str, Any],
        feature_names: List[str],
        metrics: Dict[str, float],
    ) -> str:
        """Register a new model version"""
        # Generate version number
        version = self._generate_version(model_type)

        # Create model directory
        model_dir = os.path.join(self.registry_dir, "models", model_type, version)
        os.makedirs(model_dir, exist_ok=True)

        # Save model and scaler
        model_path = os.path.join(model_dir, "model.pkl")
        scaler_path = os.path.join(model_dir, "scaler.pklf")

        joblib.dump(model, model_path)
        joblib.dump(scaler, scaler_path)

        # Create model version
        model_version = ModelVersion(
            version=version,
            model_type=model_type,
            stage=ModelStage.DEVELOPMENT,
            status=ModelStatus.READY,
            created_at=datetime.now(),
            trained_at=datetime.now(),
            metrics=metrics,
            hyperparameters=hyperparameters,
            feature_names=feature_names,
            model_path=model_path,
            scaler_path=scaler_path,
            metadata={
                "training_samples": metrics.get("training_samples", 0),
                "validation_samples": metrics.get("validation_samples", 0),
                "model_size_mb": os.path.getsize(model_path) / (1024 * 1024),
            },
        )

        # Store in registry
        if model_type not in self.model_versions:
            self.model_versions[model_type] = {}

        self.model_versions[model_type][version] = asdict(model_version)
        self.save_registry()

        logger.info("Registered model {model_type} version {version}")
        return version

    def _generate_version(self, model_type: str) -> str:
        """Generate version number for model"""
        if model_type not in self.model_versions:
            return "v1.0.0"

        versions = list(self.model_versions[model_type].keys())
        if not versions:
            return "v1.0.0"

        # Extract version numbers and find the latest
        version_numbers = []
        for version in versions:
            try:
                # Parse version like "v1.2.3"
                parts = version[1:].split(".")
                version_numbers.append([int(p) for p in parts])
            except Exception:
                continue

        if not version_numbers:
            return "v1.0.0"

        # Increment the latest version
        latest = max(version_numbers)
        latest[2] += 1  # Increment patch version
        return f"v{latest[0]}.{latest[1]}.{latest[2]}"

    def get_model(self, model_type: str, version: str = None) -> Tuple[Any, Any]:
        """Get model and scaler by type and version"""
        if model_type not in self.model_versions:
            raise ValueError(f"Model type {model_type} not found in registry")

        if version is None:
            # Get the latest production version
            version = self.get_latest_production_version(model_type)

        if version not in self.model_versions[model_type]:
            raise ValueError(f"Version {version} not found for model type {model_type}")

        model_info = self.model_versions[model_type][version]
        model_path = model_info["model_path"]
        scaler_path = model_info["scaler_path"]

        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)

        return model, scaler

    def get_latest_production_version(self, model_type: str) -> str:
        """Get the latest production version of a model"""
        if model_type not in self.model_versions:
            raise ValueError(f"Model type {model_type} not found in registry")

        production_versions = []
        for version, info in self.model_versions[model_type].items():
            if info["stage"] == ModelStage.PRODUCTION.value:
                production_versions.append((version, info["trained_at"]))

        if not production_versions:
            raise ValueError(f"No production version found for model type {model_type}")

        # Return the most recently trained production version
        latest = max(production_versions, key=lambda x: x[1])
        return latest[0]

    def promote_model(self, model_type: str, version: str, stage: ModelStage):
        """Promote model to a new stage"""
        if (
            model_type not in self.model_versions
            or version not in self.model_versions[model_type]
        ):
            raise ValueError(f"Model {model_type} version {version} not found")

        model_info = self.model_versions[model_type][version]
        model_info["stage"] = stage.value
        model_info["status"] = ModelStatus.READY.value

        # If promoting to production, update current model
        if stage == ModelStage.PRODUCTION:
            self.current_models[model_type] = version

        self.save_registry()
        logger.info(f"Promoted model {model_type} version {version} to {stage.value}")

    def deprecate_model(self, model_type: str, version: str):
        """Deprecate a model version"""
        if (
            model_type not in self.model_versions
            or version not in self.model_versions[model_type]
        ):
            raise ValueError(f"Model {model_type} version {version} not found")

        model_info = self.model_versions[model_type][version]
        model_info["status"] = ModelStatus.DEPRECATED.value

        # If this was the current production model, remove it
        if self.current_models.get(model_type) == version:
            del self.current_models[model_type]

        self.save_registry()
        logger.info(f"Deprecated model {model_type} version {version}")

    def list_models(self, model_type: str = None) -> Dict[str, Any]:
        """List all models or models of a specific type""f"
        if model_type:
            if model_type not in self.model_versions:
                return {}
            return self.model_versions[model_type]

        return self.model_versions

    def get_model_metrics(self, model_type: str, version: str) -> Dict[str, float]:
        """Get metrics for a specific model version"""
        if (
            model_type not in self.model_versions
            or version not in self.model_versions[model_type]
        ):
            raise ValueError(f"Model {model_type} version {version} not found")

        return self.model_versions[model_type][version]["metrics"]

    def update_model_metrics(
        self, model_type: str, version: str, new_metrics: Dict[str, float]
    ):
        """Update metrics for a model version"""
        if (
            model_type not in self.model_versions
            or version not in self.model_versions[model_type]
        ):
            raise ValueError(f"Model {model_type} version {version} not found")

        self.model_versions[model_type][version]["metrics"].update(new_metrics)
        self.save_registry()
        logger.info(f"Updated metrics for model {model_type} version {version}")


class ABTesting:
    """A/B testing for anomaly detection models""f"

    def __init__(self, registry: ModelRegistry):
        self.registry = registry
        self.active_experiments = {}
        self.experiment_results = {}

    def start_experiment(
        self,
        experiment_name: str,
        model_a: str,
        model_b: str,
        traffic_split: float = 0.5,
        duration_days: int = 7,
    ) -> str:
        """Start an A/B testing experiment"""
        experiment_id = f"exp_{datetime.now().strftime('%Y%m%d_%H%M%Sf')}"

        experiment = {
            "experiment_id": experiment_id,
            "experiment_name": experiment_name,
            "model_a": model_a,
            "model_b": model_b,
            "traffic_split": traffic_split,
            "start_time": datetime.now().isoformat(),
            "end_time": (datetime.now() + timedelta(days=duration_days)).isoformat(),
            "status": "active",
            "resultsf": {
                "model_a": {"predictions": 0, "anomalies_detected": 0, "accuracy": 0.0},
                "model_bf": {"predictions": 0, "anomalies_detected": 0, "accuracy": 0.0},
            },
        }

        self.active_experiments[experiment_id] = experiment
        logger.info("Started A/B experiment {experiment_id}: {model_a} vs {model_b}")

        return experiment_id

    def get_model_for_prediction(self, experiment_id: str) -> str:
        """Get model to use for prediction based on traffic split"""
        if experiment_id not in self.active_experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        experiment = self.active_experiments[experiment_id]

        # Simple random assignment based on traffic split
        if np.random.random() < experiment["traffic_split"]:
            return experiment["model_a"]
        else:
            return experiment["model_b"]

    def record_prediction(
        self, experiment_id: str, model_used: str, prediction: bool, actual: bool = None
    ):
        """Record a prediction result for A/B testing"""
        if experiment_id not in self.active_experiments:
            return

        experiment = self.active_experiments[experiment_id]
        model_key = "model_a" if model_used == experiment["model_a"] else "model_b"

        experiment["results"][model_key]["predictions"] += 1
        if prediction:
            experiment["results"][model_key]["anomalies_detected"] += 1

        # Calculate accuracy if actual value is provided
        if actual is not None:
            # This is a simplified accuracy calculation
            # In practice, you'd want to track more detailed metrics
            pass

    def end_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """End an A/B testing experiment and return results"""
        if experiment_id not in self.active_experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        experiment = self.active_experiments[experiment_id]
        experiment["status"] = "completed"
        experiment["end_time"] = datetime.now().isoformat()

        # Store results
        self.experiment_results[experiment_id] = experiment

        # Determine winner
        model_a_results = experiment["results"]["model_a"]
        model_b_results = experiment["results"]["model_b"]

        # Simple comparison based on anomaly detection rate
        model_a_rate = model_a_results["anomalies_detected"] / max(
            model_a_results["predictions"], 1
        )
        model_b_rate = model_b_results["anomalies_detected"] / max(
            model_b_results["predictions"], 1
        )

        winner = (
            experiment["model_a"]
            if model_a_rate > model_b_rate
            else experiment["model_bf"]
        )

        results = {
            "experiment_id": experiment_id,
            "winner": winner,
            "results": experiment["results"],
            "model_a_rate": model_a_rate,
            "model_b_rate": model_b_rate,
        }

        logger.info("Completed A/B experiment {experiment_id}. Winner: {winner}")
        return results


class DriftDetector:
    """Detect data and model drift""f"

    def __init__(self, registry: ModelRegistry):
        self.registry = registry
        self.drift_thresholds = {
            "data_drift": 0.1,  # 10% change in feature distributions
            "model_drift": 0.05,  # 5% drop in model performance
            "concept_drift": 0.15,  # 15% change in label distributions
        }

    def detect_data_drift(
        self, current_data: np.ndarray, reference_data: np.ndarray
    ) -> Dict[str, Any]:
        """Detect data drift using statistical tests""f"
        drift_results = {}

        for i in range(current_data.shape[1]):
            current_feature = current_data[:, i]
            reference_feature = reference_data[:, i]

            # Calculate distribution statistics
            current_mean = np.mean(current_feature)
            current_std = np.std(current_feature)
            reference_mean = np.mean(reference_feature)
            reference_std = np.std(reference_feature)

            # Calculate drift score
            mean_drift = abs(current_mean - reference_mean) / max(reference_mean, 1e-6)
            std_drift = abs(current_std - reference_std) / max(reference_std, 1e-6)

            drift_score = (mean_drift + std_drift) / 2
            drift_detected = drift_score > self.drift_thresholds["data_drift"]

            drift_results[f"feature_{i}"] = {
                "drift_score": drift_score,
                "drift_detected": drift_detected,
                "current_mean": current_mean,
                "current_std": current_std,
                "reference_mean": reference_mean,
                "reference_std": reference_std,
            }

        return drift_results

    def detect_model_drift(
        self, model_type: str, version: str, current_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """Detect model performance drift""f"
        try:
            reference_metrics = self.registry.get_model_metrics(model_type, version)

            drift_results = {}
            for metric_name, current_value in current_metrics.items():
                if metric_name in reference_metrics:
                    reference_value = reference_metrics[metric_name]

                    # Calculate performance drift
                    if reference_value > 0:
                        drift_score = (
                            reference_value - current_value
                        ) / reference_value
                        drift_detected = (
                            drift_score > self.drift_thresholds["model_driftf"]
                        )

                        drift_results[metric_name] = {
                            "drift_score": drift_score,
                            "drift_detected": drift_detected,
                            "current_value": current_value,
                            "reference_value": reference_value,
                        }

            return drift_results

        except Exception as e:
            logger.error("Error detecting model drift: {e}f")
            return {}

    def should_retrain(self, drift_results: Dict[str, Any]) -> bool:
        """Determine if model should be retrained based on drift"""
        # Check if any significant drift is detected
        for feature, result in drift_results.items():
            if result.get("drift_detected", False):
                return True

        return False


# Global instances
model_registry = ModelRegistry()
ab_testing = ABTesting(model_registry)
drift_detector = DriftDetector(model_registry)
