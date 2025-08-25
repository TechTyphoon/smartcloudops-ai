"""
Model Registry - Centralized ML model versioning and lifecycle management
"""

import os
import json
import time
import hashlib
import pickle
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import sqlite3
from enum import Enum

class ModelStatus(Enum):
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

@dataclass 
class ModelVersion:
    """Model version information"""
    model_id: str
    version: str
    major: int
    minor: int
    patch: int
    is_latest: bool
    parent_version: Optional[str]
    changelog: str

class ModelRegistry:
    """Centralized model registry for ML lifecycle management"""
    
    def __init__(self, registry_path: str = "ml_models/registry"):
        self.registry_path = Path(registry_path)
        self.models_path = self.registry_path / "models"
        self.metadata_path = self.registry_path / "metadata"
        self.db_path = self.registry_path / "registry.db"
        
        # Create directories
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.models_path.mkdir(exist_ok=True)
        self.metadata_path.mkdir(exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for model registry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Models table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS models (
                model_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                current_version TEXT,
                description TEXT,
                model_type TEXT,
                algorithm TEXT,
                framework TEXT,
                created_at TIMESTAMP,
                created_by TEXT,
                status TEXT,
                tags TEXT,
                UNIQUE(name)
            )
        ''')
        
        # Model versions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_versions (
                model_id TEXT,
                version TEXT,
                major INTEGER,
                minor INTEGER,
                patch INTEGER,
                is_latest BOOLEAN,
                parent_version TEXT,
                changelog TEXT,
                input_features TEXT,
                output_schema TEXT,
                training_data_hash TEXT,
                hyperparameters TEXT,
                metrics TEXT,
                size_bytes INTEGER,
                checksum TEXT,
                created_at TIMESTAMP,
                status TEXT,
                PRIMARY KEY (model_id, version),
                FOREIGN KEY (model_id) REFERENCES models (model_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_model(self, 
                      model: Any,
                      name: str,
                      description: str,
                      model_type: str,
                      algorithm: str,
                      framework: str,
                      input_features: List[str],
                      output_schema: Dict[str, Any],
                      training_data_hash: str,
                      hyperparameters: Dict[str, Any],
                      metrics: Dict[str, float],
                      created_by: str,
                      tags: List[str] = None,
                      version: str = None) -> ModelMetadata:
        """Register a new model or new version of existing model"""
        
        # Generate model ID
        model_id = self._generate_model_id(name)
        
        # Determine version
        if version is None:
            version = self._get_next_version(model_id)
        
        # Serialize and save model
        model_file_path = self.models_path / f"{model_id}_v{version}.pkl"
        with open(model_file_path, 'wb') as f:
            pickle.dump(model, f)
        
        # Calculate model checksum and size
        checksum = self._calculate_checksum(model_file_path)
        size_bytes = model_file_path.stat().st_size
        
        # Create metadata
        metadata = ModelMetadata(
            model_id=model_id,
            name=name,
            version=version,
            description=description,
            model_type=model_type,
            algorithm=algorithm,
            framework=framework,
            input_features=input_features,
            output_schema=output_schema,
            training_data_hash=training_data_hash,
            hyperparameters=hyperparameters,
            metrics=metrics,
            created_at=datetime.now(),
            created_by=created_by,
            status=ModelStatus.DEVELOPMENT,
            tags=tags or [],
            size_bytes=size_bytes,
            checksum=checksum
        )
        
        # Save metadata
        self._save_metadata(metadata)
        
        # Update database
        self._update_database(metadata)
        
        print(f"✅ Model registered: {name} v{version} ({model_id})")
        return metadata
    
    def load_model(self, model_id: str, version: str = None) -> Any:
        """Load a model from the registry"""
        if version is None:
            version = self.get_latest_version(model_id)
        
        model_file_path = self.models_path / f"{model_id}_v{version}.pkl"
        
        if not model_file_path.exists():
            raise FileNotFoundError(f"Model not found: {model_id} v{version}")
        
        with open(model_file_path, 'rb') as f:
            model = pickle.load(f)
        
        print(f"📦 Loaded model: {model_id} v{version}")
        return model
    
    def get_latest_version(self, model_id: str) -> str:
        """Get the latest version of a model"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT version FROM model_versions 
            WHERE model_id = ?
            ORDER BY major DESC, minor DESC, patch DESC
            LIMIT 1
        ''', (model_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0]
        else:
            return "1.0.0"
    
    def _generate_model_id(self, name: str) -> str:
        """Generate a unique model ID"""
        # Check if model already exists
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT model_id FROM models WHERE name = ?', (name,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0]
        
        # Generate new ID
        timestamp = str(int(time.time()))
        name_hash = hashlib.md5(name.encode()).hexdigest()[:8]
        return f"model_{name_hash}_{timestamp}"
    
    def _get_next_version(self, model_id: str) -> str:
        """Get the next version number for a model"""
        latest = self.get_latest_version(model_id)
        
        if latest == "1.0.0" and not self._model_exists(model_id):
            return "1.0.0"
        
        # Parse version
        major, minor, patch = map(int, latest.split('.'))
        
        # Increment patch version by default
        patch += 1
        
        return f"{major}.{minor}.{patch}"
    
    def _model_exists(self, model_id: str) -> bool:
        """Check if model exists in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM models WHERE model_id = ?', (model_id,))
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def _save_metadata(self, metadata: ModelMetadata):
        """Save model metadata to JSON file"""
        metadata_file = self.metadata_path / f"{metadata.model_id}_v{metadata.version}.json"
        
        # Convert to dict for JSON serialization
        data = asdict(metadata)
        data['created_at'] = metadata.created_at.isoformat()
        data['status'] = metadata.status.value
        
        with open(metadata_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _update_database(self, metadata: ModelMetadata):
        """Update SQLite database with model information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Parse version
        major, minor, patch = map(int, metadata.version.split('.'))
        
        # Insert or update model
        cursor.execute('''
            INSERT OR REPLACE INTO models (
                model_id, name, current_version, description, model_type,
                algorithm, framework, created_at, created_by, status, tags
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metadata.model_id, metadata.name, metadata.version, metadata.description,
            metadata.model_type, metadata.algorithm, metadata.framework,
            metadata.created_at, metadata.created_by, metadata.status.value,
            json.dumps(metadata.tags)
        ))
        
        # Insert model version
        cursor.execute('''
            INSERT OR REPLACE INTO model_versions (
                model_id, version, major, minor, patch, is_latest, parent_version,
                changelog, input_features, output_schema, training_data_hash,
                hyperparameters, metrics, size_bytes, checksum, created_at, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metadata.model_id, metadata.version, major, minor, patch, True, None,
            "", json.dumps(metadata.input_features), json.dumps(metadata.output_schema),
            metadata.training_data_hash, json.dumps(metadata.hyperparameters),
            json.dumps(metadata.metrics), metadata.size_bytes, metadata.checksum,
            metadata.created_at, metadata.status.value
        ))
        
        conn.commit()
        conn.close()