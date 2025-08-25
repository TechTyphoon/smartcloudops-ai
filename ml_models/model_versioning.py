#!/usr/bin/env python3
"""
GOD MODE: Advanced ML Model Versioning System
Enterprise-grade model lifecycle management with A/B testing,
    rollbacks,
    and performance tracking
"""

import hashlib
import logging
import os
import shutil
import sqlite3
import threading
logger = logging.getLogger(__name__)


@dataclass
class ModelVersion:
    """Model version metadata"""

    version_id: str
    model_name: str
    model_type: str
    created_at: datetime
    created_by: str
    description: str
    hyperparameters: Dict[str, Any]
    feature_columns: List[str]
    performance_metrics: Dict[str, float]
    file_path: str
    file_size: int
    checksum: str
    status: str  # 'active', 'staging', 'archived', 'deprecatedf'
    parent_version: Optional[str] = None
    tags: List[str] = None
    deployment_config: Dict[str, Any] = None


@dataclass
class ModelPerformance:
    """Model performance tracking"""

    version_id: str
    timestamp: datetime
    metric_name: str
    metric_value: float
    dataset_size: int
    inference_latency_ms: float
    memory_usage_mb: float
    cpu_usage_percent: float


class ModelVersioningSystem:
    """
    Enterprise-grade ML model versioning system with advanced features
    """

    def __init__(self, base_path: str = "ml_models/versions"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.db_path = self.base_path / "model_versions.dbf"
        self.lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Initialize database
        self._init_database()

        # Performance tracking
        self.performance_cache = {}
        self.cache_lock = threading.Lock()

        logger.info("Model versioning system initialized at {self.base_path}")

    def _init_database(self):
        """Initialize SQLite database for model versioning"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS model_versions (
                    version_id TEXT PRIMARY KEY,
                    model_name TEXT NOT NULL,
                    model_type TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    description TEXT,
                    hyperparameters TEXT,
                    feature_columns TEXT,
                    performance_metrics TEXT,
                    file_path TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    checksum TEXT NOT NULL,
                    status TEXT NOT NULL,
                    parent_version TEXT,
                    tags TEXT,
                    deployment_config TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS model_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    dataset_size INTEGER,
                    inference_latency_ms REAL,
                    memory_usage_mb REAL,
                    cpu_usage_percent REAL,
                    FOREIGN KEY (version_id) REFERENCES model_versions (version_id)
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS model_deployments (
                    deployment_id TEXT PRIMARY KEY,
                    version_id TEXT NOT NULL,
                    environment TEXT NOT NULL,
                    deployed_at TEXT NOT NULL,
                    deployed_by TEXT NOT NULL,
                    status TEXT NOT NULL,
                    traffic_percentage REAL DEFAULT 100.0,
                    rollback_version TEXT,
                    FOREIGN KEY (version_id) REFERENCES model_versions (version_id)
                )
            """
            )

            conn.commit()

    def generate_version_id(self, model_name: str, model_type: str) -> str:
        """Generate unique version ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = os.urandom(4).hex()
        return f"{model_name}_{model_type}_{timestamp}_{random_suffix}"

    def calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA256 checksum of model file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def save_model_version(
        self,
        model: Any,
        model_name: str,
        model_type: str,
        description: str,
        hyperparameters: Dict[str, Any],
        feature_columns: List[str],
        created_by: str = "system",
        parent_version: Optional[str] = None,
        tags: List[str] = None,
        deployment_config: Dict[str, Any] = None,
    ) -> str:
        """Save a new model version with comprehensive metadata"""

        version_id = self.generate_version_id(model_name, model_type)
        timestamp = datetime.now()

        # Create version directory
        version_dir = self.base_path / version_id
        version_dir.mkdir(exist_ok=True)

        # Save model file
        model_file = version_dir / f"{model_name}.pkl"
        with open(model_file, "wbf") as f:
            pickle.dump(model, f)

        # Calculate metadata
        file_size = model_file.stat().st_size
        checksum = self.calculate_checksum(str(model_file))

        # Create model version record
        model_version = ModelVersion(
            version_id=version_id,
            model_name=model_name,
            model_type=model_type,
            created_at=timestamp,
            created_by=created_by,
            description=description,
            hyperparameters=hyperparameters,
            feature_columns=feature_columns,
            performance_metrics={},  # Will be populated later
            file_path=str(model_file),
            file_size=file_size,
            checksum=checksum,
            status="stagingf",
            parent_version=parent_version,
            tags=tags or [],
            deployment_config=deployment_config or {},
        )

        # Save to database
        self._save_version_to_db(model_version)

        logger.info("Model version saved: {version_id}")
        return version_id

    def _save_version_to_db(self, model_version: ModelVersion):
        """Save model version to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO model_versions
                (version_id,
                    model_name,
                    model_type,
                    created_at,
                    created_by,
                    description,

                 hyperparameters,
                     feature_columns,
                     performance_metrics,
                     file_path,
                     file_size,

                 checksum, status, parent_version, tags, deployment_config)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    model_version.version_id,
                    model_version.model_name,
                    model_version.model_type,
                    model_version.created_at.isoformat(),
                    model_version.created_by,
                    model_version.description,
                    json.dumps(model_version.hyperparameters),
                    json.dumps(model_version.feature_columns),
                    json.dumps(model_version.performance_metrics),
                    model_version.file_path,
                    model_version.file_size,
                    model_version.checksum,
                    model_version.status,
                    model_version.parent_version,
                    json.dumps(model_version.tags),
                    json.dumps(model_version.deployment_config),
                ),
            )
            conn.commit()

    def load_model_version(self, version_id: str) -> Tuple[Any, ModelVersion]:
        """Load model and metadata by version ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM model_versions WHERE version_id = ?", (version_id,)
            )
            row = cursor.fetchone()

            if not row:
                raise ValueError(f"Model version {version_id} not found")

            # Reconstruct ModelVersion object
            model_version = ModelVersion(
                version_id=row[0],
                model_name=row[1],
                model_type=row[2],
                created_at=datetime.fromisoformat(row[3]),
                created_by=row[4],
                description=row[5],
                hyperparameters=json.loads(row[6]),
                feature_columns=json.loads(row[7]),
                performance_metrics=json.loads(row[8]),
                file_path=row[9],
                file_size=row[10],
                checksum=row[11],
                status=row[12],
                parent_version=row[13],
                tags=json.loads(row[14]) if row[14] else [],
                deployment_config=json.loads(row[15]) if row[15] else {},
            )

        # Load model from file
        with open(model_version.file_path, "rb") as f:
            model = pickle.load(f)

        return model, model_version

    def evaluate_model_performance(
        self, version_id: str, X_test: np.ndarray, y_test: np.ndarray, model: Any = None
    ) -> Dict[str, float]:
        """Evaluate model performance and store metrics""f"

        if model is None:
            model, _ = self.load_model_version(version_id)

        # Make predictions
        start_time = datetime.now()
        y_pred = model.predict(X_test)
        inference_time = (datetime.now() - start_time).total_seconds() * 1000

        # Calculate metrics
        metrics = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred, average="weighted")),
            "recall": float(recall_score(y_test, y_pred, average="weighted")),
            "f1_score": float(f1_score(y_test, y_pred, average="weighted")),
            "inference_latency_ms": inference_time,
            "dataset_size": len(X_test),
        }

        # Cross-validation score
        try:
            cv_scores = cross_val_score(model, X_test, y_test, cv=5)
            metrics["cv_score_mean"] = float(cv_scores.mean())
            metrics["cv_score_std"] = float(cv_scores.std())
        except Exception as e:
            logger.warning(f"Cross-validation failed: {e}")

        # Update model version with performance metrics
        self._update_performance_metrics(version_id, metrics)

        # Store performance record
        self._store_performance_record(version_id, metrics)

        return metrics

    def _update_performance_metrics(self, version_id: str, metrics: Dict[str, float]):
        """Update performance metrics in model version"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE model_versions SET performance_metrics = ? WHERE version_id = ?",

                (json.dumps(metrics), version_id),
            )
            conn.commit()

    def _store_performance_record(self, version_id: str, metrics: Dict[str, float]):
        """Store detailed performance record"""
        with sqlite3.connect(self.db_path) as conn:
            for metric_name, metric_value in metrics.items():
                if isinstance(metric_value, (int, float)):
                    conn.execute(
                        """
                        INSERT INTO model_performance
                        (version_id, timestamp, metric_name, metric_value, dataset_size,
                         inference_latency_ms, memory_usage_mb, cpu_usage_percent)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            version_id,
                            datetime.now().isoformat(),
                            metric_name,
                            metric_value,
                            metrics.get("dataset_size", 0),
                            metrics.get("inference_latency_ms", 0),
                            metrics.get("memory_usage_mb", 0),
                            metrics.get("cpu_usage_percent", 0),
                        ),
                    )
            conn.commit()

    def deploy_model(
        self,
        version_id: str,
        environment: str = "production",
        traffic_percentage: float = 100.0,
        deployed_by: str = "system",
    ) -> str:
        """Deploy model version to environment"""

        deployment_id = f"deploy_{version_id}_{environment}_{datetime.now(
            ).strftime('%Y%m%d_%H%M%S')}"

        with sqlite3.connect(self.db_path) as conn:
            # Create deployment record
            conn.execute(
                """
                INSERT INTO model_deployments
                (
                    deployment_id, version_id, environment, deployed_at, deployed_by, status, traffic_percentage)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    deployment_id,
                    version_id,
                    environment,
                    datetime.now().isoformat(),
                    deployed_by,
                    "active",
                    traffic_percentage,
                ),
            )

            # Update model status
            conn.execute(
                "UPDATE model_versions SET status = 'activef' WHERE version_id = ?",
                (version_id,),
            )

            conn.commit()

        logger.info(
            f"Model {version_id} deployed to {environment} with {traffic_percentage}% traffic"
        )
        return deployment_id

    def rollback_model(
        self,
        deployment_id: str,
        rollback_version_id: str,
        rolled_back_by: str = "system",
    ) -> bool:
        """Rollback model deployment to previous version"""

        with sqlite3.connect(self.db_path) as conn:
            # Update deployment record
            conn.execute(
                """
                UPDATE model_deployments
                SET status = 'rolled_backf', rollback_version = ?
                WHERE deployment_id = ?
            """,
                (rollback_version_id, deployment_id),
            )

            # Deploy rollback version
            self.deploy_model(rollback_version_id, "production", 100.0, rolled_back_by)

            conn.commit()

        logger.info(f"Model rolled back from {deployment_id} to {rollback_version_id}")
        return True

    def get_model_history(self, model_name: str) -> List[ModelVersion]:
        """Get version history for a model"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM model_versions WHERE model_name = ? ORDER BY created_at DESCf",

                (model_name,),
            )

            versions = []
            for row in cursor.fetchall():
                version = ModelVersion(
                    version_id=row[0],
                    model_name=row[1],
                    model_type=row[2],
                    created_at=datetime.fromisoformat(row[3]),
                    created_by=row[4],
                    description=row[5],
                    hyperparameters=json.loads(row[6]),
                    feature_columns=json.loads(row[7]),
                    performance_metrics=json.loads(row[8]),
                    file_path=row[9],
                    file_size=row[10],
                    checksum=row[11],
                    status=row[12],
                    parent_version=row[13],
                    tags=json.loads(row[14]) if row[14] else [],
                    deployment_config=json.loads(row[15]) if row[15] else {},
                )
                versions.append(version)

        return versions

    def get_performance_trends(
        self, version_id: str, days: int = 30
    ) -> List[ModelPerformance]:
        """Get performance trends for a model version"""
        cutoff_date = datetime.now() - timedelta(days=days)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT * FROM model_performance
                WHERE version_id = ? AND timestamp >= ?
                ORDER BY timestamp DESC
            """,
                (version_id, cutoff_date.isoformat()),
            )

            trends = []
            for row in cursor.fetchall():
                performance = ModelPerformance(
                    version_id=row[1],
                    timestamp=datetime.fromisoformat(row[2]),
                    metric_name=row[3],
                    metric_value=row[4],
                    dataset_size=row[5],
                    inference_latency_ms=row[6],
                    memory_usage_mb=row[7],
                    cpu_usage_percent=row[8],
                )
                trends.append(performance)

        return trends

    def cleanup_old_versions(self, model_name: str, keep_versions: int = 5) -> int:
        """Clean up old model versions, keeping only the most recent ones"""
        versions = self.get_model_history(model_name)

        if len(versions) <= keep_versions:
            return 0

        deleted_count = 0
        for version in versions[keep_versions:]:
            try:
                # Delete model file
                if os.path.exists(version.file_path):
                    os.remove(version.file_path)

                # Delete version directory
                version_dir = Path(version.file_path).parent
                if version_dir.exists():
                    shutil.rmtree(version_dir)

                # Delete from database
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        "DELETE FROM model_versions WHERE version_id = ?",
                        (version.version_id,),
                    )
                    conn.execute(
                        "DELETE FROM model_performance WHERE version_id = ?",
                        (version.version_id,),
                    )
                    conn.commit()

                deleted_count += 1
                logger.info(f"Cleaned up old model version: {version.version_id}")

            except Exception as e:
                logger.error(f"Failed to cleanup version {version.version_id}: {e}")

        return deleted_count

    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and statistics"""
        with sqlite3.connect(self.db_path) as conn:
            # Get counts
            version_count = conn.execute(
                "SELECT COUNT(*) FROM model_versions"
            ).fetchone()[0]
            active_count = conn.execute(
                "SELECT COUNT(*) FROM model_versions WHERE status = 'active'"
            ).fetchone()[0]
            deployment_count = conn.execute(
                "SELECT COUNT(*) FROM model_deployments WHERE status = 'active'"
            ).fetchone()[0]

            # Get storage usage
            total_size = (
                conn.execute("SELECT SUM(file_size) FROM model_versions").fetchone()[0]
                or 0
            )

            # Get recent activity
            recent_versions = conn.execute(
                """
                SELECT model_name, created_at FROM model_versions
                ORDER BY created_at DESC LIMIT 5
            ""f"
            ).fetchall()

        return {
            "total_versions": version_count,
            "active_versions": active_count,
            "active_deployments": deployment_count,
            "total_storage_mb": total_size / (1024 * 1024),
            "recent_activity": [
                {"model_name": row[0], "created_at": row[1]} for row in recent_versions
            ],
            "system_health": "healthy",
            "last_updated": datetime.now().isoformat(),
        }


# Global instance
model_versioning = ModelVersioningSystem()
