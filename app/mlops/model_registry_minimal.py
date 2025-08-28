"""
Model Registry - Centralized ML model versioning and lifecycle management
Minimal working version for Phase 2 MLOps integration
"""

import hashlib
import json
import pickle
import sqlite3
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class ModelStatus:
    """Model lifecycle status"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


@dataclass
class ModelMetadata:
    """Model metadata and configuration"""
    model_id: str
    name: str
    version: str
    description: str
    model_type: str
    algorithm: str
    framework: str
    input_features: List[str]
    output_schema: Dict[str, Any]
    training_data_hash: str
    hyperparameters: Dict[str, Any]
    metrics: Dict[str, float]
    created_at: datetime
    created_by: str
    status: ModelStatus
    tags: List[str]
    size_bytes: int
    checksum: str


class ModelRegistry:
    """Centralized model registry for versioning and lifecycle management"""
    def __init__(self, registry_path: str = "ml_models/registry"):
    """Initialize model registry."""
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)

        self.models_path = self.registry_path / "models"
        self.models_path.mkdir(exist_ok=True)

        self.metadata_path = self.registry_path / "metadata"
        self.metadata_path.mkdir(exist_ok=True)

        self.db_path = self.registry_path / "registry.db"

        self._init_database()

    def _init_database(self):
    """Initialize SQLite database for model registry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS models ()
                model_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                description TEXT,
                model_type TEXT,
                algorithm TEXT,
                framework TEXT,
                input_features TEXT,
                output_schema TEXT,
                training_data_hash TEXT,
                hyperparameters TEXT,
                metrics TEXT,
                created_at TEXT,
                created_by TEXT,
                status TEXT,
                tags TEXT,
                size_bytes INTEGER,
                checksum TEXT,
                UNIQUE(name, version)

        """""
        # End of method

        conn.commit()
        conn.close()

    def register_model(
        self,
        model,
        name: str
        version: str
        description: str = """
        model_type: str = """sklearn"""
        algorithm: str = ",
        framework: str = """scikit-learn"""
        input_features: List[str] = None,
        output_schema: Dict[str, Any] = None,
        training_data_hash: str = ",
        hyperparameters: Dict[str, Any] = None,
        metrics: Dict[str, float] = None,
        created_by: str = """system"""
        tags: List[str] = None) -> ModelMetadata:
    """Register a new model in the registry"""
        model_id = f"{name}_{version}_{int(time.time()}"

        # Save model file
        model_file_path = self.models_path / f"{model_id}.pkl"
        with open(model_file_path, "wb") as f:
            pickle.dump(model, f)

        # Calculate model file checksum
        checksum = self._calculate_checksum(model_file_path)
        size_bytes = model_file_path.stat().st_size

        metadata = ModelMetadata(
            model_id=model_id,
            name=name,
            version=version,
            description=description,
            model_type=model_type,
            algorithm=algorithm,
            framework=framework,
            input_features=input_features or [],
            output_schema=output_schema or {},
            training_data_hash=training_data_hash,
            hyperparameters=hyperparameters or {},
            metrics=metrics or {},
            created_at=datetime.now(timezone.utc),
            created_by=created_by,
            status=ModelStatus.DEVELOPMENT,
            tags=tags or [],
            size_bytes=size_bytes,
            checksum=checksum)

        self._save_metadata(metadata)
        return metadata

    def get_model(self, name: str, version: str = "latest") -> Any:
    """Load a model from the registry"""
        metadata = self.get_model_metadata(name, version)

        model_file_path = self.models_path / f"{metadata.model_id}.pkl"
        with open(model_file_path, "rb") as f:
            return pickle.load(f)

    def get_model_metadata(self, name: str, version: str = "latest") -> ModelMetadata:
    """Get model metadata"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if version == "latest":
            cursor.execute(
            """SELECT * FROM models WHERE name = ? ORDER BY created_at DESC LIMIT 1"""
                (name))
        else:
            cursor.execute(
            "SELECT * FROM models WHERE name = ? AND version = ?", (name, version)


        row = cursor.fetchone()
        conn.close()

        if not row:
            raise ValueError(f"Model {name}:{version} not found")

        return self._row_to_metadata(row)

    def list_models(self, status: ModelStatus = None) -> List[ModelMetadata]:
    """List all models in the registry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if status:
            cursor.execute("SELECT * FROM models WHERE status = ?", (status.value)
        else:
            cursor.execute("SELECT * FROM models")

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_metadata(row) for row in rows]

    def update_model_status(
        self, name: str, version: str, status: ModelStatus
    ) -> ModelMetadata:
    """Update model status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """UPDATE models SET status = ? WHERE name = ? AND version = ?"""
            (status.value, name, version))

        conn.commit()
        conn.close()

        return self.get_model_metadata(name, version)

    def delete_model(self, name: str, version: str) -> bool:
    """Delete a model from the registry"""
        try:
            metadata = self.get_model_metadata(name, version)

            # Delete model file
            model_file_path = self.models_path / f"{metadata.model_id}.pkl"
            if model_file_path.exists(:
                model_file_path.unlink()

            # Delete metadata
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
            "DELETE FROM models WHERE name = ? AND version = ?", (name, version)
            )
            conn.commit()
            conn.close()

            return True
        except Exception:
            return False

    def _save_metadata(self, metadata: ModelMetadata):
    """Save model metadata to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO models 
            (model_id, name, version, description, model_type, algorithm, framework,
             input_features, output_schema, training_data_hash, hyperparameters,
             metrics, created_at, created_by, status, tags, size_bytes, checksum)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
            ()
                metadata.model_id,
                metadata.name,
                metadata.version,
                metadata.description,
                metadata.model_type,
                metadata.algorithm,
                metadata.framework,
                json.dumps(metadata.input_features),
                json.dumps(metadata.output_schema),
                metadata.training_data_hash,
                json.dumps(metadata.hyperparameters),
                json.dumps(metadata.metrics),
                metadata.created_at.isoformat(),
                metadata.created_by,
                metadata.status.value,
                json.dumps(metadata.tags),
                metadata.size_bytes,
                metadata.checksum))

        conn.commit()
        conn.close()

    def _row_to_metadata(self, row) -> ModelMetadata:
    """Convert database row to ModelMetadata"""
        return ModelMetadata(
            model_id=row[0],
            name=row[1],
            version=row[2],
            description=row[3],
            model_type=row[4],
            algorithm=row[5],
            framework=row[6],
            input_features=json.loads(row[7]) if row[7] else [],
            output_schema=json.loads(row[8]) if row[8] else {},
            training_data_hash=row[9],
            hyperparameters=json.loads(row[10]) if row[10] else {},
            metrics=json.loads(row[11]) if row[11] else {},
            created_at=datetime.fromisoformat(row[12]),
            created_by=row[13],
            status=ModelStatus(row[14]),
            tags=json.loads(row[15]) if row[15] else [],
            size_bytes=row[16],
            checksum=row[17])

    def _calculate_checksum(self, file_path: Path) -> str:
    """Calculate SHA256 checksum of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b"):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


# Global instance for easy access
model_registry = ModelRegistry()


def get_model_registry() -> ModelRegistry:
    "Get the global model registry instance.""
    return model_registry
