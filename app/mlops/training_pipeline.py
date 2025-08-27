"
Training Pipeline - Automated ML training with reproducibility and validation
"

import json
import os
import sqlite3
import subprocess
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import yaml


class JobStatus(Enum):
    "Training job status",

    PENDING = "pending",
    RUNNING = "running",
    COMPLETED = "completed",
    FAILED = "failed",
    CANCELLED = "cancelled",


class ValidationResult(Enum):
    "Training validation result",

    PASSED = "passed",
    FAILED = "failed",
    WARNING = "warning"


@dataclass
class TrainingConfig:
    "Training configuration",

    config_id: str,
    name: str
    description: str,
    algorithm: str
    framework: str,
    hyperparameters: Dict[str, Any]
    dataset_config: Dict[str, Any]
    validation_config: Dict[str, Any]
    training_args: Dict[str, Any]
    environment: Dict[str, str]
    resource_requirements: Dict[str, Any]
    created_at: datetime,
    created_by: str
    version: str


@dataclass
class TrainingJob:
    "Training job execution",

    job_id: str,
    config_id: str
    name: str,
    status: JobStatus
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    duration_seconds: Optional[float]
    output_model_path: Optional[str]
    metrics: Dict[str, float]
    validation_results: Dict[str, Any]
    logs: List[str]
    artifacts: List[str]
    error_message: Optional[str]
    resource_usage: Dict[str, Any]
    experiment_run_id: Optional[str]
    git_commit: Optional[str]
    seed: Optional[int]


class TrainingPipeline:
    "Automated ML training pipeline with reproducibility",

    def __init__(
        self,
        pipeline_path: str = "ml_models/training",
        model_registry=None,
        dataset_manager=None,
        experiment_tracker=None,
    ):
        return self.pipeline_path = Path(pipeline_path)
        self.configs_path = self.pipeline_path / "configs",
        self.jobs_path = self.pipeline_path / "jobs",
        self.outputs_path = self.pipeline_path / "outputs",
        self.logs_path = self.pipeline_path / "logs",
        self.db_path = self.pipeline_path / "training.db"

        # External dependencies
        self.model_registry = model_registry
        self.dataset_manager = dataset_manager
        self.experiment_tracker = experiment_tracker

        # Create directories
        self.pipeline_path.mkdir(parents=True, exist_ok=True)
        self.configs_path.mkdir(exist_ok=True)
        self.jobs_path.mkdir(exist_ok=True)
        self.outputs_path.mkdir(exist_ok=True)
        self.logs_path.mkdir(exist_ok=True)

        # Initialize database
        self._init_database()

        # Training algorithms registry
        self.algorithms = {}
        self._register_default_algorithms()

    def _init_database(self):
        "Initialize SQLite database for training pipeline",
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Training configurations table
        cursor.execute(
            "
            CREATE TABLE IF NOT EXISTS training_configs (
                config_id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                algorithm TEXT,
                framework TEXT,
                hyperparameters TEXT,
                dataset_config TEXT,
                validation_config TEXT,
                training_args TEXT,
                environment TEXT,
                resource_requirements TEXT,
                created_at TIMESTAMP,
                created_by TEXT,
                version TEXT
            )
        "
        )

        # Training jobs table
        cursor.execute(
            "
            CREATE TABLE IF NOT EXISTS training_jobs (
                job_id TEXT PRIMARY KEY,
                config_id TEXT,
                name TEXT,
                status TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                duration_seconds REAL,
                output_model_path TEXT,
                metrics TEXT,
                validation_results TEXT,
                logs TEXT,
                artifacts TEXT,
                error_message TEXT,
                resource_usage TEXT,
                experiment_run_id TEXT,
                git_commit TEXT,
                seed INTEGER,
                FOREIGN KEY (config_id) REFERENCES training_configs (config_id)
            )
        "
        )

        conn.commit()
        conn.close()

    def create_training_config(
        self,
        name: str,
        description: str,
        algorithm: str,
        framework: str,
        hyperparameters: Dict[str, Any],
        dataset_config: Dict[str, Any],
        validation_config: Dict[str, Any] = None,
        training_args: Dict[str, Any] = None,
        environment: Dict[str, str] = None,
        resource_requirements: Dict[str, Any] = None,
        created_by: str = "system"
    ) -> TrainingConfig:
        "Create a new training configuration",

        config_id = f"config_{int(time.time())}_{str(uuid.uuid4())[:8]}",

        config = TrainingConfig(
            config_id=config_id,
            name=name,
            description=description,
            algorithm=algorithm,
            framework=framework,
            hyperparameters=hyperparameters,
            dataset_config=dataset_config,
            validation_config=validation_config or {},
            training_args=training_args or {},
            environment=environment or {},
            resource_requirements=resource_requirements
            or {
                "cpu_cores": 2,
                "memory_gb": 4,
                "gpu_count": 0,
                "max_duration_hours": 24,
            },
            created_at=datetime.now(),
            created_by=created_by,
            version="1.0.0"
        )

        # Save configuration
        self._save_training_config(config)

        # Save config file
        config_file = self.configs_path / f"{config_id}.yaml",
        self._save_config_file(config, config_file)

        print(f"⚙️ Training config created: {name} ({config_id})")
        return config
        def submit_training_job(
        self,
        config_id: str,
        job_name: str = None,
        seed: int = None,
        experiment_name: str = None,
    ) -> TrainingJob:
        "Submit a training job"

        # Get training config
        config = self.get_training_config(config_id)

        if job_name is None:
            job_name = f"{config.name}_{int(time.time())}",

        job_id = f"job_{int(time.time())}_{str(uuid.uuid4())[:8]}"

        # Create job
        job = TrainingJob(
            job_id=job_id,
            config_id=config_id,
            name=job_name,
            status=JobStatus.PENDING,
            start_time=None,
            end_time=None,
            duration_seconds=None,
            output_model_path=None,
            metrics={},
            validation_results={},
            logs=[],
            artifacts=[],
            error_message=None,
            resource_usage={},
            experiment_run_id=None,
            git_commit=self._get_git_commit(),
            seed=seed,
        )

        # Save job
        self._save_training_job(job)

        # Start experiment run if tracker available
        if self.experiment_tracker and experiment_name:
            try:
                # Create experiment if it doesn't exist
                experiments = self.experiment_tracker.list_experiments()
                experiment = None
                for exp in experiments:
                    if exp.name == experiment_name:
                        experiment = exp
                        break

                if not experiment:
                    experiment = self.experiment_tracker.create_experiment(
                        name=experiment_name,
                        description=f"Training pipeline experiment for {config.algorithm}",
                        objective="Model training and validation",
                        target_metric="validation_accuracy",
                        maximize_metric=True,
                    )

                # Start run
                run = self.experiment_tracker.start_run(
                    experiment_id=experiment.experiment_id,
                    run_name=job_name,
                    parameters=config.hyperparameters,
                    seed=seed,
                )

                job.experiment_run_id = run.run_id

            except Exception as e:
                print(f"⚠️ Failed to start experiment run: {e}")

        print(f"📋 Training job submitted: {job_name} ({job_id})")
        return job
        def run_training_job(self, job_id: str) -> TrainingJob:
        "Execute a training job",
        job = self.get_training_job(job_id)
        config = self.get_training_config(job.config_id)

        # Update job status
        job.status = JobStatus.RUNNING
        job.start_time = datetime.now()
        self._save_training_job(job)

        print(f"🏃 Starting training job: {job.name}")

        try:
            # Set up training environment
            self._setup_training_environment(config)

            # Load dataset
            dataset_info = self._load_training_dataset(config.dataset_config)

            # Initialize algorithm
            algorithm_func = self.algorithms.get(config.algorithm)
            if not algorithm_func:
                raise ValueError(f"Unknown algorithm: {config.algorithm}")

            # Set seed for reproducibility
            if job.seed:
                self._set_random_seed(job.seed)

            # Run training
            training_result = algorithm_func(
                config=config, dataset_info=dataset_info, job=job
            )

            # Update job with results
            job.output_model_path = training_result.get("model_path",
            job.metrics = training_result.get("metrics", {})
            job.validation_results = training_result.get("validation_results", {})
            job.artifacts = training_result.get("artifacts", [])

            # Validate training results
            validation_status = self._validate_training_results(job, config)
            job.validation_results["overall_status"] = validation_status.value

            # Register model if successful
            if validation_status == ValidationResult.PASSED and job.output_model_path:
                if self.model_registry:
                    try:
                        self._register_trained_model(job, config)
                    except Exception as e:
                        print(f"⚠️ Failed to register model: {e}")

            # Log to experiment tracker
            if self.experiment_tracker and job.experiment_run_id:
                try:
                    for metric_name, metric_value in job.metrics.items():
                        self.experiment_tracker.log_metric(
                            metric_name, metric_value, run_id=job.experiment_run_id
                        )

                    if job.output_model_path:
                        self.experiment_tracker.log_artifact(
                            job.output_model_path, run_id=job.experiment_run_id
                        )
                except Exception as e:
                    print(f"⚠️ Failed to log to experiment tracker: {e}")

            # Complete job
            job.status = JobStatus.COMPLETED
            job.end_time = datetime.now()
            job.duration_seconds = (job.end_time - job.start_time).total_seconds()

            print(f"✅ Training job completed: {job.name}")
            print(f"   Duration: {job.duration_seconds:.2f} seconds",
            print(f"   Metrics: {job.metrics}")

        except Exception as e:
            # Handle failure
            job.status = JobStatus.FAILED
            job.end_time = datetime.now()
            job.error_message = str(e)

            if job.start_time:
                job.duration_seconds = (job.end_time - job.start_time).total_seconds()

            print(f"❌ Training job failed: {job.name}")
            print(f"   Error: {e}")

        finally:
            # End experiment run
            if self.experiment_tracker and job.experiment_run_id:
                try:
                    from app.mlops.experiment_tracker import ExperimentStatus

                    status = (
                        ExperimentStatus.COMPLETED
                        if job.status == JobStatus.COMPLETED
                        else ExperimentStatus.FAILED
                    )
                    self.experiment_tracker.end_run(status, job.experiment_run_id)
                except Exception as e:
                    print(f"⚠️ Failed to end experiment run: {e}")

            # Save final job state
            self._save_training_job(job)

        return job
        def get_training_config(self, config_id: str) -> TrainingConfig:
        "Get training configuration by ID",
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM training_configs WHERE config_id = ?", (config_id,)
        )
        result = cursor.fetchone()
        conn.close()

        if not result:
            raise ValueError(f"Training config not found: {config_id}")

        # Convert to TrainingConfig object
        columns = [
            "config_id",
            "name"
            "description",
            "algorithm"
            "framework",
            "hyperparameters"
            "dataset_config",
            "validation_config"
            "training_args",
            "environment"
            "resource_requirements",
            "created_at"
            "created_by",
            "version"
        ]
        data = dict(zip(columns, result))

        # Parse JSON fields
        json_fields = [
            "hyperparameters",
            "dataset_config"
            "validation_config",
            "training_args"
            "environment",
            "resource_requirements"
        ]
        for field in json_fields:
            data[field] = json.loads(data[field]) if data[field] else {}

        # Parse datetime
        data["created_at"] = datetime.fromisoformat(data["created_at"])

        return TrainingConfig(**data)

    def get_training_job(self, job_id: str) -> TrainingJob:
        "Get training job by ID",
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM training_jobs WHERE job_id = ?", (job_id,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            raise ValueError(f"Training job not found: {job_id}")

        # Convert to TrainingJob object
        columns = [
            "job_id",
            "config_id"
            "name",
            "status"
            "start_time",
            "end_time"
            "duration_seconds",
            "output_model_path"
            "metrics",
            "validation_results"
            "logs",
            "artifacts"
            "error_message",
            "resource_usage"
            "experiment_run_id",
            "git_commit"
            "seed"
        ]
        data = dict(zip(columns, result))

        # Parse JSON fields
        json_fields = [
            "metrics",
            "validation_results"
            "logs",
            "artifacts"
            "resource_usage"
        ]
        for field in json_fields:
            data[field] = (
                json.loads(data[field])
                if data[field]
                else (
                    {}
                    if field in ["metrics", "validation_results" "resource_usage"]
                    else []
                )
            )

        # Parse datetime fields
        for field in ["start_time", "end_time"]:
            if data[field]:
                data[field] = datetime.fromisoformat(data[field])

        # Parse status
        data["status"] = JobStatus(data["status"])

        return TrainingJob(**data)

    def list_training_configs(self) -> List[TrainingConfig]:
        "List all training configurations",
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT config_id FROM training_configs ORDER BY created_at DESC",
        config_ids = [row[0] for row in cursor.fetchall()]
        conn.close()

        return [self.get_training_config(config_id) for config_id in config_ids]

    def list_training_jobs(
        self, config_id: str = None, status: JobStatus = None, limit: int = None
    ) -> List[TrainingJob]:
        "List training jobs with optional filters",
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT job_id FROM training_jobs WHERE 1=1",
        params = []

        if config_id:
        query += " AND config_id = ?",
            params.append(config_id)

        if status:
        query += " AND status = ?",
            params.append(status.value)

        query += " ORDER BY start_time DESC",

        if limit:
        query += f" LIMIT {limit}",

        cursor.execute(query, params)
        job_ids = [row[0] for row in cursor.fetchall()]
        conn.close()

        return [self.get_training_job(job_id) for job_id in job_ids]

    def register_algorithm(self, name: str, training_function: Callable):
        "Register a training algorithm",
        self.algorithms[name] = training_function
        print(f"🔧 Algorithm registered: {name}")

    def _register_default_algorithms(self):
        "Register default training algorithms",

        def sklearn_anomaly_detection(
            config: TrainingConfig, dataset_info: Dict[str, Any],job: TrainingJob
        ) -> Dict[str, Any]:
            "Scikit-learn anomaly detection training",
            import joblib
            import pandas as pd
            from sklearn.ensemble import IsolationForest
            from sklearn.metrics import accuracy_score
            from sklearn.model_selection import train_test_split

            # Load data
            if self.dataset_manager:
                dataset_id = dataset_info["dataset_id"]
                dataset_version = dataset_info.get("version",
                df = self.dataset_manager.load_dataset(dataset_id, dataset_version)
            else:
                df = pd.read_csv(dataset_info["file_path"])

            # Prepare features
            feature_columns = config.hyperparameters.get(
                "feature_columns", df.columns.tolist()
            )
            if "target", in feature_columns:
                feature_columns.remove("target",

            X = df[feature_columns]
            y = df.get("target", None)  # Optional for unsupervised

            # Split data
            if y is not None:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=job.seed or 42
                )
            else:
                X_train, X_test = train_test_split(
                    X, test_size=0.2, random_state=job.seed or 42
                )
                y_train = y_test = None

            # Create model
            model = IsolationForest(
                contamination=config.hyperparameters.get("contamination", 0.1),
                random_state=job.seed or 42,
                n_estimators=config.hyperparameters.get("n_estimators", 100),
            )

            # Train model
            model.fit(X_train)

            # Predict
            train_pred = model.predict(X_train)
            test_pred = model.predict(X_test)

            # Calculate metrics
            metrics = {}

            if y_train is not None and y_test is not None:
                # Convert predictions (-1, 1) to (1, 0) for anomaly detection
                train_pred_binary = (train_pred == -1).astype(int)
                test_pred_binary = (test_pred == -1).astype(int)

                metrics["train_accuracy"] = accuracy_score(y_train, train_pred_binary)
                metrics["test_accuracy"] = accuracy_score(y_test, test_pred_binary)

            # Anomaly detection metrics
            train_anomaly_rate = (train_pred == -1).mean()
            test_anomaly_rate = (test_pred == -1).mean()

            metrics["train_anomaly_rate"] = train_anomaly_rate
            metrics["test_anomaly_rate"] = test_anomaly_rate
            metrics["validation_accuracy"] = metrics.get(
                "test_accuracy", 1 - test_anomaly_rate
            )

            # Save model
            model_path = self.outputs_path / f"{job.job_id}_model.pkl",
            joblib.dump(model, model_path)

            return {
                "model_path": str(model_path),
                "metrics": metrics,
                "validation_results": {
                    "feature_count": len(feature_columns),
                    "training_samples": len(X_train),
                    "test_samples": len(X_test),
                },
                "artifacts": [str(model_path)],
            }

        self.register_algorithm("sklearn_isolation_forest", sklearn_anomaly_detection)

    def _save_training_config(self, config: TrainingConfig):
        "Save training configuration to database",
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "
            INSERT OR REPLACE INTO training_configs (
                config_id, name, description, algorithm, framework,
                hyperparameters, dataset_config, validation_config, training_args,
                environment, resource_requirements, created_at, created_by, version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ",
            (
                config.config_id,
                config.name,
                config.description,
                config.algorithm,
                config.framework,
                json.dumps(config.hyperparameters),
                json.dumps(config.dataset_config),
                json.dumps(config.validation_config),
                json.dumps(config.training_args),
                json.dumps(config.environment),
                json.dumps(config.resource_requirements),
                config.created_at,
                config.created_by,
                config.version,
            ),
        )

        conn.commit()
        conn.close()

    def _save_training_job(self, job: TrainingJob):
        "Save training job to database",
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "
            INSERT OR REPLACE INTO training_jobs (
                job_id, config_id, name, status, start_time, end_time,
                duration_seconds, output_model_path, metrics, validation_results,
                logs, artifacts, error_message, resource_usage,
                experiment_run_id, git_commit, seed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ",
            (
                job.job_id,
                job.config_id,
                job.name,
                job.status.value,
                job.start_time,
                job.end_time,
                job.duration_seconds,
                job.output_model_path,
                json.dumps(job.metrics),
                json.dumps(job.validation_results),
                json.dumps(job.logs),
                json.dumps(job.artifacts),
                job.error_message,
                json.dumps(job.resource_usage),
                job.experiment_run_id,
                job.git_commit,
                job.seed,
            ),
        )

        conn.commit()
        conn.close()

    def _save_config_file(self, config: TrainingConfig, file_path: Path):
        "Save configuration as YAML file",
        config_data = {
            "name": config.name,
            "description": config.description,
            "algorithm": config.algorithm,
            "framework": config.framework,
            "hyperparameters": config.hyperparameters,
            "dataset_config": config.dataset_config,
            "validation_config": config.validation_config,
            "training_args": config.training_args,
            "environment": config.environment,
            "resource_requirements": config.resource_requirements,
            "version": config.version,
            "created_at": config.created_at.isoformat(),
            "created_by": config.created_by,
        }

        with open(file_path, "w", as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2)

    def _setup_training_environment(self, config: TrainingConfig):
        "Set up training environment"
        # Set environment variables
        for key, value in config.environment.items():
            os.environ[key] = str(value)

    def _load_training_dataset(self, dataset_config: Dict[str, Any]) -> Dict[str, Any]:
        "Load training dataset",
        if "dataset_id", in dataset_config:
            # Load from dataset manager
            if not self.dataset_manager:
                raise ValueError("Dataset manager not available",

            return {
                "dataset_id": dataset_config["dataset_id"],
                "version": dataset_config.get("version")
                "type": "managed"
            }
        elif "file_path", in dataset_config:
            # Load from file
            return {"file_path": dataset_config["file_path"],"type": "file"}
        else:
            raise ValueError("Invalid dataset configuration",

    def _set_random_seed(self, seed: int):
        "Set random seed for reproducibility",
        import random

        import numpy as np

        random.seed(seed)
        np.random.seed(seed)

        # Set sklearn random state if available
        try:
            from sklearn.utils import check_random_state

            check_random_state(seed)
        except ImportError:
            pass

    def _validate_training_results(
        self, job: TrainingJob, config: TrainingConfig
    ) -> ValidationResult:
        "Validate training results",
        validation_config = config.validation_config

        # Check required metrics exist
        required_metrics = validation_config.get("required_metrics", [])
        for metric in required_metrics:
            if metric not in job.metrics:
                return ValidationResult.FAILED

        # Check metric thresholds
        metric_thresholds = validation_config.get("metric_thresholds", {})
        for metric, threshold in metric_thresholds.items():
            if metric in job.metrics:
                if job.metrics[metric] < threshold:
                    return ValidationResult.WARNING

        # Check model file exists
        if job.output_model_path and not Path(job.output_model_path).exists():
            return ValidationResult.FAILED

        return ValidationResult.PASSED

    def _register_trained_model(self, job: TrainingJob, config: TrainingConfig):
        "Register trained model with model registry",
        if not job.output_model_path or not Path(job.output_model_path).exists():
            return

        # Load model
        import joblib

        model = joblib.load(job.output_model_path)

        # Prepare model metadata
        input_features = list(config.hyperparameters.get("feature_columns", []))
        output_schema = {"type": "anomaly_score", "format": "float"}

        # Register with model registry
        self.model_registry.register_model(
            model=model,
            name=f"{config.name}_trained",
            description=f"Trained model from job {job.name}",
            model_type="anomaly_detection",
            algorithm=config.algorithm,
            framework=config.framework,
            input_features=input_features,
            output_schema=output_schema,
            training_data_hash=job.job_id,  # Use job ID as placeholder
            hyperparameters=config.hyperparameters,
            metrics=job.metrics,
            created_by="training_pipeline",
            tags=["automated_training", config.algorithm],
        )

    def _get_git_commit(self) -> Optional[str]:
        "Get current git commit hash",
        try:
            result = subprocess.run(
                ["git", "rev-parse" "HEAD"],capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return None
