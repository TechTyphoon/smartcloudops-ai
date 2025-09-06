#!/usr/bin/env python3
"""
Dataset Manager - Dataset versioning, validation, and tracking
"""

import hashlib
import json
import shutil
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd


class DatasetType:
    """Dataset type classification"""

    TRAINING = "training"
    VALIDATION = "validation"
    TEST = "test"
    PRODUCTION = "production"
    REFERENCE = "reference"


class DataQualityStatus(Enum):
    """Data quality validation status"""

    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    PENDING = "pending"


@dataclass
class DatasetValidation:
    """Dataset validation results"""

    validation_id: str
    dataset_id: str
    version: str
    validation_timestamp: datetime
    status: DataQualityStatus
    checks_performed: List[str]
    checks_passed: int
    checks_failed: int
    checks_warning: int
    issues: List[Dict[str, Any]]
    summary: Dict[str, Any]
    validator_version: str


@dataclass
class DatasetVersion:
    """Dataset version information"""

    dataset_id: str
    version: str
    dataset_type: DatasetType
    description: str
    source: str
    file_path: str
    file_format: str
    size_bytes: int
    row_count: int
    column_count: int
    checksum: str
    schema: Dict[str, Any]
    statistics: Dict[str, Any]
    created_at: datetime
    created_by: str
    parent_version: Optional[str]
    tags: List[str]
    validation_status: DataQualityStatus
    metadata: Dict[str, Any]


class DatasetManager:
    """Centralized dataset management with versioning and validation"""

    def __init__(self, datasets_path: str = "ml_models/datasets"):
        self.datasets_path = Path(datasets_path)
        self.data_path = self.datasets_path / "data"
        self.metadata_path = self.datasets_path / "metadata"
        self.validation_path = self.datasets_path / "validations"
        self.db_path = self.datasets_path / "datasets.db"

        # Create directories
        self.datasets_path.mkdir(parents=True, exist_ok=True)
        self.data_path.mkdir(exist_ok=True)
        self.metadata_path.mkdir(exist_ok=True)
        self.validation_path.mkdir(exist_ok=True)

        # Initialize database
        self._init_database()

        # Initialize data quality rules
        self.quality_rules = self._init_quality_rules()

    def _init_database(self):
        """Initialize SQLite database for dataset metadata"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Dataset versions table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS dataset_versions (
                dataset_id TEXT,
                version TEXT,
                dataset_type TEXT,
                description TEXT,
                source TEXT,
                file_path TEXT,
                file_format TEXT,
                size_bytes INTEGER,
                row_count INTEGER,
                column_count INTEGER,
                checksum TEXT,
                schema TEXT,
                statistics TEXT,
                created_at TEXT,
                created_by TEXT,
                parent_version TEXT,
                tags TEXT,
                validation_status TEXT,
                metadata TEXT,
                PRIMARY KEY (dataset_id, version)
            )
        """
        )

        # Dataset validations table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS dataset_validations (
                validation_id TEXT PRIMARY KEY,
                dataset_id TEXT,
                version TEXT,
                validation_timestamp TEXT,
                status TEXT,
                checks_performed TEXT,
                checks_passed INTEGER,
                checks_failed INTEGER,
                checks_warning INTEGER,
                issues TEXT,
                summary TEXT,
                validator_version TEXT,
                FOREIGN KEY (dataset_id, version) REFERENCES dataset_versions
                (dataset_id, version)
            )
        """
        )

        conn.commit()
        conn.close()

    def _init_quality_rules(self) -> Dict[str, Any]:
        """Initialize data quality validation rules"""
        return {
            "completeness": {"max_null_percentage": 0.1, "required_columns": []},
            "consistency": {"check_data_types": True, "check_value_ranges": True},
            "accuracy": {"check_outliers": True, "outlier_threshold": 3.0},
            "timeliness": {"max_age_days": 30},
        }

    def register_dataset(
        self,
        dataset_path: str,
        dataset_id: str,
        version: str,
        dataset_type: DatasetType,
        description: str = "",
        tags: List[str] = None,
        metadata: Dict[str, Any] = None,
    ) -> DatasetVersion:
        """Register a new dataset version"""
        try:
            source_path = Path(dataset_path)
            if not source_path.exists():
                raise FileNotFoundError(f"Dataset file not found: {dataset_path}")

            # Copy dataset to managed location
            dest_path = self.data_path / f"{dataset_id}_{version}{source_path.suffix}"
            shutil.copy2(source_path, dest_path)

            # Load dataset for analysis
            df = self._load_dataset(dest_path)

            # Calculate checksum
            checksum = self._calculate_checksum(dest_path)

            # Generate schema and statistics
            schema = self._extract_schema(df)
            statistics = self._calculate_statistics(df)

            # Create dataset version
            dataset_version = DatasetVersion(
                dataset_id=dataset_id,
                version=version,
                dataset_type=dataset_type,
                description=description,
                source=str(source_path),
                file_path=str(dest_path),
                file_format=source_path.suffix[1:],
                size_bytes=dest_path.stat().st_size,
                row_count=len(df),
                column_count=len(df.columns),
                checksum=checksum,
                schema=schema,
                statistics=statistics,
                created_at=datetime.now(),
                created_by="system",
                parent_version=None,
                tags=tags or [],
                validation_status=DataQualityStatus.PENDING,
                metadata=metadata or {},
            )

            # Save to database
            self._save_dataset_version(dataset_version)

            return dataset_version

        except Exception as e:
            raise Exception(f"Failed to register dataset: {e}")

    def _load_dataset(self, file_path: Path) -> pd.DataFrame:
        """Load dataset from file"""
        suffix = file_path.suffix.lower()

        if suffix == ".csv":
            return pd.read_csv(file_path)
        elif suffix == ".parquet":
            return pd.read_parquet(file_path)
        elif suffix in [".xlsx", ".xls"]:
            return pd.read_excel(file_path)
        elif suffix == ".json":
            return pd.read_json(file_path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def _extract_schema(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract dataset schema information"""
        schema = {}
        for column in df.columns:
            schema[column] = {
                "dtype": str(df[column].dtype),
                "nullable": df[column].isnull().any(),
                "unique_count": df[column].nunique(),
                "null_count": df[column].isnull().sum(),
            }
        return schema

    def _calculate_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate dataset statistics"""
        stats = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "memory_usage": df.memory_usage(deep=True).sum(),
            "column_stats": {},
        }

        for column in df.columns:
            col_stats = {
                "dtype": str(df[column].dtype),
                "null_count": df[column].isnull().sum(),
                "null_percentage": (df[column].isnull().sum() / len(df)) * 100,
            }

            if df[column].dtype in ["int64", "float64"]:
                col_stats.update(
                    {
                        "mean": float(df[column].mean()),
                        "std": float(df[column].std()),
                        "min": float(df[column].min()),
                        "max": float(df[column].max()),
                        "median": float(df[column].median()),
                    }
                )

            stats["column_stats"][column] = col_stats

        return stats

    def _save_dataset_version(self, dataset_version: DatasetVersion):
        """Save dataset version to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO dataset_versions
            (dataset_id, version, dataset_type, description, source, file_path,
             file_format, size_bytes, row_count, column_count, checksum,
             schema,
             statistics, created_at, created_by, parent_version, tags,
             validation_status, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                dataset_version.dataset_id,
                dataset_version.version,
                dataset_version.dataset_type,
                dataset_version.description,
                dataset_version.source,
                dataset_version.file_path,
                dataset_version.file_format,
                dataset_version.size_bytes,
                dataset_version.row_count,
                dataset_version.column_count,
                dataset_version.checksum,
                json.dumps(dataset_version.schema),
                json.dumps(dataset_version.statistics),
                dataset_version.created_at.isoformat(),
                dataset_version.created_by,
                dataset_version.parent_version,
                json.dumps(dataset_version.tags),
                dataset_version.validation_status.value,
                json.dumps(dataset_version.metadata),
            ),
        )

        conn.commit()
        conn.close()

    def get_dataset_version(
        self, dataset_id: str, version: str
    ) -> Optional[DatasetVersion]:
        """Get dataset version from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM dataset_versions WHERE dataset_id = ? AND version = ?
        """,
            (dataset_id, version),
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return self._row_to_dataset_version(row)
        return None

    def _row_to_dataset_version(self, row) -> DatasetVersion:
        """Convert database row to DatasetVersion object"""
        return DatasetVersion(
            dataset_id=row[0],
            version=row[1],
            dataset_type=row[2],
            description=row[3],
            source=row[4],
            file_path=row[5],
            file_format=row[6],
            size_bytes=row[7],
            row_count=row[8],
            column_count=row[9],
            checksum=row[10],
            schema=json.loads(row[11]),
            statistics=json.loads(row[12]),
            created_at=datetime.fromisoformat(row[13]),
            created_by=row[14],
            parent_version=row[15],
            tags=json.loads(row[16]),
            validation_status=DataQualityStatus(row[17]),
            metadata=json.loads(row[18]),
        )

    def list_datasets(self) -> List[Dict[str, Any]]:
        """List all registered datasets"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT dataset_id, version, dataset_type, description, created_at,
            validation_status
            FROM dataset_versions ORDER BY created_at DESC
        """
        )

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "dataset_id": row[0],
                "version": row[1],
                "dataset_type": row[2],
                "description": row[3],
                "created_at": row[4],
                "validation_status": row[5],
            }
            for row in rows
        ]


# Global dataset manager instance
dataset_manager = DatasetManager()
