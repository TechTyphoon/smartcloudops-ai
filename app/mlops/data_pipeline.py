#!/usr/bin/env python3
"""
Enhanced Data Pipeline - Production-ready data processing and versioning
Phase 2A Week 3: Data Pipeline Automation with quality monitoring and versioning
"""

import hashlib
import json
import logging
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

# cross_val_score may be imported from sklearn.model_selection in some
# environments; import defensively to avoid collection-time ImportError.
try:
    pass

    SKLEARN_CV_AVAILABLE = True
except Exception:
    try:
        # older code paths sometimes import from sklearn.metrics
        pass

        SKLEARN_CV_AVAILABLE = True
    except Exception:
        SKLEARN_CV_AVAILABLE = False

# Try to import pandas and numpy with fallback
try:
    import numpy as np
    import pandas as pd

    PANDAS_AVAILABLE = True
    logger.info("Pandas and NumPy imported successfully")
except ImportError as e:
    PANDAS_AVAILABLE = False
    logger.warning(f"Pandas/NumPy not available: {e}")

    # Create mock classes for fallback
    class MockDataFrame:
        def __init__(self, data=None):
            self.data = data or {}
            self.columns = list(self.data.keys() if isinstance(data, dict) else [])
            self.size = 0

        def isnull(self):
            return MockDataFrame()

        def sum(self):
            return {}

        def to_parquet(self, path):
            pass

        def __len__(self):
            return self.size

        def copy(self):
            return MockDataFrame(self.data)

    pd = type(
        "MockPandas",
        (),
        {
            "DataFrame": MockDataFrame,
            "read_csv": lambda x: MockDataFrame(),
            "read_parquet": lambda x: MockDataFrame(),
            "read_excel": lambda x: MockDataFrame(),
            "read_json": lambda x: MockDataFrame(),
            "util": type(
                "util",
                (),
                {"hash_pandas_object": lambda x: type("hash", (), {"values": b"mock"})},
            )(),
        },
    )()

    np = type(
        "MockNumPy",
        (),
        {
            "random": type(
                "random",
                (),
                {"randn": lambda x: [0] * x, "choice": lambda a, x: ["A"] * x},
            )(),
            "number": object,
            "inf": float("inf"),
            "nan": float("nan"),
            "mean": lambda x: 0,
            "issubdtype": lambda a, b: False,
        },
    )()


class DataQualityStatus(Enum):
    """Data quality assessment status"""

    EXCELLENT = "excellent"
    GOOD = "good"
    WARNING = "warning"
    POOR = "poor"
    FAILED = "failed"


class PipelineStage(Enum):
    """Data pipeline processing stages"""

    INGESTION = "ingestion"
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    QUALITY_CHECK = "quality_check"
    STORAGE = "storage"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class DataQualityMetrics:
    """Data quality metrics for monitoring"""

    completeness: float = 0.0
    accuracy: float = 0.0
    consistency: float = 0.0
    timeliness: float = 0.0
    validity: float = 0.0
    uniqueness: float = 0.0
    integrity: float = 0.0

    def calculate_overall_score(self) -> float:
        """Calculate overall data quality score."""
        metrics = [
            self.completeness,
            self.accuracy,
            self.consistency,
            self.timeliness,
            self.validity,
            self.uniqueness,
            self.integrity,
        ]
        return sum(metrics) / len(metrics)

    def get_quality_status(self) -> DataQualityStatus:
        """Get quality status based on overall score."""
        score = self.calculate_overall_score()
        if score >= 0.9:
            return DataQualityStatus.EXCELLENT
        elif score >= 0.8:
            return DataQualityStatus.GOOD
        elif score >= 0.7:
            return DataQualityStatus.WARNING
        elif score >= 0.6:
            return DataQualityStatus.POOR
        else:
            return DataQualityStatus.FAILED


@dataclass
class DataVersion:
    version_id: str
    dataset_name: str
    row_count: int
    column_count: int
    tags: List[str]
    quality_score: float
    quality_status: DataQualityStatus
    metadata: Dict[str, Any]


@dataclass
class QualityReport:
    version_id: str
    dataset_name: str
    overall_score: float
    overall_status: DataQualityStatus
    missing_values: Dict[str, int]
    duplicate_rows: int
    issues_found: List[str]
    recommendations: List[str]
    created_at: str


@dataclass
class PipelineMetadata:
    """Metadata for data pipeline runs"""

    pipeline_id: str
    version: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: PipelineStage = PipelineStage.INGESTION
    records_processed: int = 0
    records_failed: int = 0
    quality_metrics: Optional[DataQualityMetrics] = None
    error_message: Optional[str] = None
    config_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "pipeline_id": self.pipeline_id,
            "version": self.version,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status.value,
            "records_processed": self.records_processed,
            "records_failed": self.records_failed,
            "quality_metrics": (
                asdict(self.quality_metrics) if self.quality_metrics else None
            ),
            "error_message": self.error_message,
            "config_hash": self.config_hash,
        }


class DataPipeline:
    """Enhanced data pipeline with quality monitoring and versioning"""

    def __init__(self, pipeline_name: str, config: Dict[str, Any]):
        """Initialize data pipeline."""
        self.pipeline_name = pipeline_name
        self.config = config
        self.metadata = PipelineMetadata(
            pipeline_id=f"{pipeline_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            version=config.get("version", "1.0.0"),
            start_time=datetime.now(timezone.utc),
        )
        self.data = None
        self.quality_metrics = DataQualityMetrics()

    def run(self) -> Dict[str, Any]:
        """Run the complete data pipeline."""
        try:
            logger.info(f"Starting pipeline: {self.pipeline_name}")

            # Stage 1: Data Ingestion
            self._ingest_data()
            self.metadata.status = PipelineStage.INGESTION

            # Stage 2: Data Validation
            self._validate_data()
            self.metadata.status = PipelineStage.VALIDATION

            # Stage 3: Data Transformation
            self._transform_data()
            self.metadata.status = PipelineStage.TRANSFORMATION

            # Stage 4: Quality Check
            self._check_quality()
            self.metadata.status = PipelineStage.QUALITY_CHECK

            # Stage 5: Data Storage
            self._store_data()
            self.metadata.status = PipelineStage.STORAGE

            # Complete pipeline
            self.metadata.status = PipelineStage.COMPLETED
            self.metadata.end_time = datetime.now(timezone.utc)
            self.metadata.quality_metrics = self.quality_metrics

            logger.info(f"Pipeline completed successfully: {self.pipeline_name}")
            return self._get_pipeline_result()

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            self.metadata.status = PipelineStage.FAILED
            self.metadata.end_time = datetime.now(timezone.utc)
            self.metadata.error_message = str(e)
            raise

    def _ingest_data(self):
        """Ingest data from source."""
        logger.info("Ingesting data...")

        # Simulate data ingestion
        source_path = self.config.get("source_path", "data/input.csv")

        if PANDAS_AVAILABLE:
            try:
                self.data = pd.read_csv(source_path)
                self.metadata.records_processed = len(self.data)
                logger.info(f"Ingested {len(self.data)} records")
            except Exception as e:
                logger.error(f"Data ingestion failed: {e}")
                raise
        else:
            # Mock data for testing
            self.data = pd.DataFrame(
                {
                    "id": range(100),
                    "value": [i * 2 for i in range(100)],
                    "category": ["A", "B", "C"] * 33 + ["A"],
                }
            )
            self.metadata.records_processed = len(self.data)
            logger.info(f"Ingested {len(self.data)} mock records")

    def _validate_data(self):
        """Validate data quality and structure."""
        logger.info("Validating data...")

        if self.data is None or len(self.data) == 0:
            raise ValueError("No data to validate")

        # Check for null values
        null_counts = self.data.isnull().sum()
        total_cells = self.data.size
        null_cells = null_counts.sum()

        self.quality_metrics.completeness = 1.0 - (null_cells / total_cells)

        # Check data types
        expected_types = self.config.get("expected_types", {})
        type_accuracy = 0.0
        if expected_types:
            correct_types = 0
            total_columns = len(expected_types)
            for column, expected_type in expected_types.items():
                if column in self.data.columns:
                    if str(self.data[column].dtype) == expected_type:
                        correct_types += 1
            type_accuracy = correct_types / total_columns
        else:
            type_accuracy = 1.0

        self.quality_metrics.accuracy = type_accuracy
        logger.info(
            f"Data validation completed. Completeness: "
            f"{self.quality_metrics.completeness:.2f}"
        )

    def _transform_data(self):
        """Transform data according to configuration."""
        logger.info("Transforming data...")

        transformations = self.config.get("transformations", [])

        for transform in transformations:
            transform_type = transform.get("type")
            column = transform.get("column")

            if transform_type == "fill_null" and column in self.data.columns:
                fill_value = transform.get("value", 0)
                self.data[column] = self.data[column].fillna(fill_value)
            elif transform_type == "rename" and column in self.data.columns:
                new_name = transform.get("new_name")
                self.data = self.data.rename(columns={column: new_name})
            elif transform_type == "drop_column" and column in self.data.columns:
                self.data = self.data.drop(columns=[column])

        logger.info("Data transformation completed")

    def _check_quality(self):
        """Perform comprehensive quality checks."""
        logger.info("Checking data quality...")

        # Calculate additional quality metrics
        if len(self.data) > 0:
            # Consistency check (example: check for duplicate IDs)
            if "id" in self.data.columns:
                duplicates = self.data["id"].duplicated().sum()
                self.quality_metrics.consistency = 1.0 - (duplicates / len(self.data))

            # Validity check (example: check for negative values in positive fields)
            if "value" in self.data.columns:
                invalid_values = (self.data["value"] < 0).sum()
                self.quality_metrics.validity = 1.0 - (invalid_values / len(self.data))

            # Uniqueness check
            total_rows = len(self.data)
            unique_rows = len(self.data.drop_duplicates())
            self.quality_metrics.uniqueness = unique_rows / total_rows

            # Integrity check (example: check referential integrity)
            self.quality_metrics.integrity = 1.0  # Simplified for demo

        # Timeliness (simplified - would check data freshness in real scenario)
        self.quality_metrics.timeliness = 1.0

        quality_status = self.quality_metrics.get_quality_status()
        logger.info(f"Quality check completed. Status: {quality_status.value}")

    def _store_data(self):
        """Store processed data."""
        logger.info("Storing data...")

        output_path = self.config.get("output_path", "data/output.parquet")

        if PANDAS_AVAILABLE:
            try:
                self.data.to_parquet(output_path, index=False)
                logger.info(f"Data stored to {output_path}")
            except Exception as e:
                logger.error(f"Data storage failed: {e}")
                raise
        else:
            logger.info("Mock data storage completed")

    def _get_pipeline_result(self) -> Dict[str, Any]:
        """Get pipeline execution results."""
        return {
            "pipeline_name": self.pipeline_name,
            "status": "completed",
            "metadata": self.metadata.to_dict(),
            "quality_score": self.quality_metrics.calculate_overall_score(),
            "quality_status": self.quality_metrics.get_quality_status().value,
        }

    def get_quality_report(self) -> Dict[str, Any]:
        """Get detailed quality report."""
        return {
            "pipeline_id": self.metadata.pipeline_id,
            "quality_metrics": asdict(self.quality_metrics),
            "overall_score": self.quality_metrics.calculate_overall_score(),
            "status": self.quality_metrics.get_quality_status().value,
            "recommendations": self._get_quality_recommendations(),
        }

    def _get_quality_recommendations(self) -> List[str]:
        """Get quality improvement recommendations."""
        recommendations = []

        if self.quality_metrics.completeness < 0.9:
            recommendations.append(
                "Improve data completeness by addressing null values"
            )

        if self.quality_metrics.accuracy < 0.9:
            recommendations.append("Improve data accuracy by validating data types")

        if self.quality_metrics.consistency < 0.9:
            recommendations.append("Improve data consistency by removing duplicates")

        if self.quality_metrics.validity < 0.9:
            recommendations.append("Improve data validity by checking value ranges")

        return recommendations


# For backward compatibility with tests that import DataPipelineManager,
# provide a simple alias that instantiates DataPipeline with a standard
# configuration object.
class DataPipelineManager:
    def __init__(self, storage_path: Union[str, Path] = "./data_pipeline_storage"):
        """Manage dataset versions, storage and quality reports for pipelines.

        This manager is a lightweight implementation used by unit tests and
        provides basic ingestion, versioning and querying capabilities.
        """
        self.storage_path = Path(storage_path)
        self.data_path = self.storage_path / "data"
        self.versions_path = self.storage_path / "versions"
        self.quality_path = self.storage_path / "quality"
        self.logs_path = self.storage_path / "logs"
        self.db_path = self.storage_path / "data_pipeline.db"

        # Ensure directories exist
        for p in [
            self.data_path,
            self.versions_path,
            self.quality_path,
            self.logs_path,
        ]:
            p.mkdir(parents=True, exist_ok=True)

        # Initialize DB
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS data_versions (
                    version_id TEXT PRIMARY KEY,
                    dataset_name TEXT NOT NULL,
                    row_count INTEGER,
                    column_count INTEGER,
                    tags TEXT,
                    metadata TEXT,
                    quality_score REAL,
                    quality_status TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS quality_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version_id TEXT NOT NULL,
                    report_json TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS pipeline_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pipeline_name TEXT,
                    result_json TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def _generate_version_id(self, dataset_name: str) -> str:
        """Generate a unique version ID."""
        import uuid

        return (
            f"{dataset_name}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}_"
            f"{uuid.uuid4().hex[:8]}"
        )

    def _compute_basic_stats(self, df) -> tuple:
        """Compute basic statistics from dataframe."""
        try:
            row_count = int(len(df))
            column_count = int(len(df.columns)) if hasattr(df, "columns") else 0
        except Exception:
            row_count = 0
            column_count = 0
        return row_count, column_count

    def _compute_quality_metrics(self, df, row_count: int, column_count: int) -> tuple:
        """Compute quality metrics from dataframe."""
        missing_cells = 0
        infinite_count = 0
        duplicate_rows = 0

        if PANDAS_AVAILABLE:
            try:
                null_counts = df.isnull().sum().sum()
                missing_cells = int(null_counts)
                duplicate_rows = int(df.duplicated().sum())

                numeric = (
                    df.select_dtypes(include=["number"])
                    if hasattr(df, "select_dtypes")
                    else df
                )

                try:
                    infinite_count = int(
                        (numeric == float("inf")).sum().sum()
                        + (numeric == -float("inf")).sum().sum()
                    )
                except Exception:
                    infinite_count = 0
            except Exception:
                missing_cells = 0
                duplicate_rows = 0
                infinite_count = 0

        return missing_cells, infinite_count, duplicate_rows

    def _calculate_quality_score(
        self,
        row_count: int,
        column_count: int,
        missing_cells: int,
        duplicate_rows: int,
        infinite_count: int,
    ) -> float:
        """Calculate quality score based on metrics."""
        if row_count == 0 or column_count == 0:
            return 0.0

        total_cells = max(1, row_count * column_count)
        missing_ratio = missing_cells / total_cells
        duplicate_ratio = (duplicate_rows / row_count) if row_count > 0 else 0
        infinite_ratio = infinite_count / total_cells

        return max(
            0.0,
            1.0
            - (missing_ratio * 0.7)
            - (duplicate_ratio * 0.2)
            - (infinite_ratio * 0.1),
        )

    def _determine_quality_status(self, quality_score: float) -> DataQualityStatus:
        """Determine quality status based on score."""
        if quality_score >= 0.9:
            return DataQualityStatus.EXCELLENT
        elif quality_score >= 0.8:
            return DataQualityStatus.GOOD
        elif quality_score >= 0.7:
            return DataQualityStatus.WARNING
        elif quality_score >= 0.6:
            return DataQualityStatus.POOR
        else:
            return DataQualityStatus.FAILED

    def _persist_version_record(
        self,
        version_id: str,
        dataset_name: str,
        row_count: int,
        column_count: int,
        tags: list,
        metadata: dict,
        quality_score: float,
        quality_status: DataQualityStatus,
        created_at: str,
    ):
        """Persist version record to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO data_versions (version_id, dataset_name, row_count, "
                "column_count, tags, metadata, quality_score, quality_status, "
                "created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    version_id,
                    dataset_name,
                    row_count,
                    column_count,
                    json.dumps(tags),
                    json.dumps(metadata),
                    float(quality_score),
                    quality_status.value,
                    created_at,
                ),
            )
            conn.commit()

    def _persist_dataframe(
        self, df, version_id: str, row_count: int, column_count: int
    ):
        """Persist dataframe to disk."""
        version_file = self.versions_path / f"{version_id}.parquet"
        try:
            if PANDAS_AVAILABLE:
                try:
                    df.to_parquet(version_file, index=False)
                except Exception:
                    version_file = self.versions_path / f"{version_id}.json"
                    df.to_json(version_file, orient="records")
            else:
                version_file.write_text(
                    json.dumps({"rows": row_count, "cols": column_count})
                )
        except Exception:
            pass

    def _create_quality_report(
        self,
        df,
        version_id: str,
        dataset_name: str,
        quality_score: float,
        quality_status: DataQualityStatus,
        created_at: str,
    ) -> QualityReport:
        """Create quality report."""
        missing_values = {}
        duplicate_rows = 0
        issues = []

        if PANDAS_AVAILABLE:
            try:
                null_counts = df.isnull().sum().to_dict()
                missing_values = {k: int(v) for k, v in null_counts.items()}
                duplicate_rows = int(df.duplicated().sum())

                if duplicate_rows > 0:
                    issues.append("duplicates_found")
                if any(
                    v == float("inf") or v == -float("inf")
                    for row in df.itertuples(index=False)
                    for v in row
                    if isinstance(v, (int, float))
                ):
                    issues.append("infinite_values")
            except Exception:
                missing_values = {}
                duplicate_rows = 0

        return QualityReport(
            version_id=version_id,
            dataset_name=dataset_name,
            overall_score=float(quality_score),
            overall_status=quality_status,
            missing_values=missing_values,
            duplicate_rows=duplicate_rows,
            issues_found=issues,
            recommendations=self._get_quality_recommendations_internal(quality_score),
            created_at=created_at,
        )

    def _persist_quality_report(
        self, report: QualityReport, version_id: str, dataset_name: str, created_at: str
    ):
        """Persist quality report to database."""
        report_dict = {
            "version_id": report.version_id,
            "dataset_name": report.dataset_name,
            "overall_score": report.overall_score,
            "overall_status": (
                report.overall_status.value
                if isinstance(report.overall_status, DataQualityStatus)
                else str(report.overall_status)
            ),
            "missing_values": report.missing_values,
            "duplicate_rows": report.duplicate_rows,
            "issues_found": report.issues_found,
            "recommendations": report.recommendations,
            "created_at": report.created_at,
        }

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO quality_reports (version_id, report_json, "
                "created_at) VALUES (?, ?, ?)",
                (version_id, json.dumps(report_dict), created_at),
            )
            conn.execute(
                "INSERT INTO pipeline_runs (pipeline_name, result_json, "
                "created_at) VALUES (?, ?, ?)",
                (dataset_name, json.dumps({"version_id": version_id}), created_at),
            )
            conn.commit()

    def ingest_data(
        self,
        df,
        dataset_name: str,
        source_metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ):
        """Ingest a pandas DataFrame (or compatible mock) and produce a
        version record."""
        version_id = self._generate_version_id(dataset_name)
        row_count, column_count = self._compute_basic_stats(df)

        tags = tags or []
        metadata = source_metadata or {}

        missing_cells, infinite_count, duplicate_rows = self._compute_quality_metrics(
            df, row_count, column_count
        )

        quality_score = self._calculate_quality_score(
            row_count, column_count, missing_cells, duplicate_rows, infinite_count
        )

        quality_status = self._determine_quality_status(quality_score)
        created_at = datetime.now().isoformat()

        self._persist_version_record(
            version_id,
            dataset_name,
            row_count,
            column_count,
            tags,
            metadata,
            quality_score,
            quality_status,
            created_at,
        )

        self._persist_dataframe(df, version_id, row_count, column_count)

        report = self._create_quality_report(
            df, version_id, dataset_name, quality_score, quality_status, created_at
        )

        self._persist_quality_report(report, version_id, dataset_name, created_at)

        return DataVersion(
            version_id=version_id,
            dataset_name=dataset_name,
            row_count=row_count,
            column_count=column_count,
            tags=tags,
            quality_score=float(quality_score),
            quality_status=quality_status,
            metadata=metadata,
        )

    def get_data_version(self, version_id: str):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "SELECT version_id, dataset_name, row_count, column_count, tags, "
                "metadata, quality_score, quality_status FROM data_versions "
                "WHERE version_id = ?",
                (version_id,),
            )
            row = cur.fetchone()
            if not row:
                raise ValueError("Data version not found")
            return DataVersion(
                version_id=row[0],
                dataset_name=row[1],
                row_count=row[2],
                column_count=row[3],
                tags=json.loads(row[4]) if row[4] else [],
                quality_score=float(row[6]) if row[6] is not None else 0.0,
                quality_status=(
                    DataQualityStatus(row[7]) if row[7] else DataQualityStatus.FAILED
                ),
                metadata=json.loads(row[5]) if row[5] else {},
            )

    def get_latest_version(self, dataset_name: str):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "SELECT version_id FROM data_versions WHERE dataset_name = ? "
                "ORDER BY created_at DESC LIMIT 1",
                (dataset_name,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return self.get_data_version(row[0])

    def list_versions(self, dataset_name: Optional[str] = None):
        with sqlite3.connect(self.db_path) as conn:
            if dataset_name:
                cur = conn.execute(
                    "SELECT version_id FROM data_versions WHERE dataset_name = ? "
                    "ORDER BY created_at ASC",
                    (dataset_name,),
                )
            else:
                cur = conn.execute(
                    "SELECT version_id FROM data_versions ORDER BY created_at ASC"
                )
            rows = cur.fetchall()
            return [self.get_data_version(r[0]) for r in rows]

    def get_quality_report(self, version_id: str) -> QualityReport:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "SELECT report_json FROM quality_reports WHERE version_id = ?",
                (version_id,),
            )
            row = cur.fetchone()
            if not row:
                raise ValueError("Quality report not found")
            data = json.loads(row[0])
            # map back to QualityReport
            return QualityReport(
                version_id=data.get("version_id"),
                dataset_name=data.get("dataset_name"),
                overall_score=float(data.get("overall_score", 0.0)),
                overall_status=(
                    DataQualityStatus(data.get("overall_status"))
                    if data.get("overall_status")
                    else DataQualityStatus.FAILED
                ),
                missing_values=data.get("missing_values", {}),
                duplicate_rows=int(data.get("duplicate_rows", 0)),
                issues_found=data.get("issues_found", []),
                recommendations=data.get("recommendations", []),
                created_at=data.get("created_at"),
            )

    def _get_quality_recommendations_internal(self, quality_score: float) -> List[str]:
        recs = []
        if quality_score < 0.9:
            recs.append("Improve data completeness by addressing " "null values")
        if quality_score < 0.8:
            recs.append("Improve data accuracy by validating " "data types")
        return recs

    def _find_source_file(self, source_version_id: str):
        """Find the source data file."""
        src = self.versions_path / f"{source_version_id}.parquet"
        if not src.exists():
            src = self.versions_path / f"{source_version_id}.json"
        if not src.exists():
            raise ValueError("Data version not found")
        return src

    def _load_dataframe(self, src):
        """Load dataframe from file."""
        if not PANDAS_AVAILABLE:
            raise ValueError("Pandas not available for transformations")

        try:
            if str(src).endswith(".parquet"):
                return pd.read_parquet(src)
            else:
                return pd.read_json(src, orient="records")
        except Exception:
            raise

    def _apply_filter_transformation(self, df, params):
        """Apply filter transformation to dataframe."""
        col = params.get("column")
        cond = params.get("condition")
        val = params.get("value")

        if cond == "greater_than":
            return df[df[col] > val]
        elif cond == "less_than":
            return df[df[col] < val]
        elif cond == "equals":
            return df[df[col] == val]
        else:
            raise ValueError("Unknown transformation condition")

    def _apply_transformations(self, df, transformations):
        """Apply all transformations to dataframe."""
        for t in transformations:
            ttype = t.get("type")
            params = t.get("params", {})

            if ttype == "filter":
                df = self._apply_filter_transformation(df, params)
            else:
                raise ValueError("Unknown transformation type")

        return df

    def transform_data(
        self,
        source_version_id: str,
        transformations: List[Dict[str, Any]],
        target_dataset_name: Optional[str] = None,
    ):
        """Transform data by applying specified transformations."""
        src = self._find_source_file(source_version_id)
        df = self._load_dataframe(src)
        df = self._apply_transformations(df, transformations)

        return self.ingest_data(
            df,
            target_dataset_name or f"transformed_{source_version_id}",
            tags=["transformed"],
        )

    def _calculate_dataframe_hash(self, df) -> str:
        try:
            if PANDAS_AVAILABLE:
                h = pd.util.hash_pandas_object(df, index=True).values.tobytes()
                return hashlib.sha256(h).hexdigest()
        except Exception:
            pass
        return ""

    def _calculate_file_hash(self, path: Path) -> str:
        try:
            if not path.exists():
                return ""
            sha256_hash = hashlib.sha256()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception:
            return ""


# Singleton manager used in tests
_GLOBAL_DATA_PIPELINE_MANAGER = None


def get_data_pipeline_manager(
    storage_path: Union[str, Path] = None,
) -> "DataPipelineManager":
    global _GLOBAL_DATA_PIPELINE_MANAGER
    if _GLOBAL_DATA_PIPELINE_MANAGER is None:
        _GLOBAL_DATA_PIPELINE_MANAGER = DataPipelineManager(
            storage_path or "./data_pipeline_storage"
        )
    return _GLOBAL_DATA_PIPELINE_MANAGER


# Global pipeline manager
class PipelineManager:
    """Manages multiple data pipelines"""

    def __init__(self):
        self.pipelines = {}
        self.history = []

    def create_pipeline(self, name: str, config: Dict[str, Any]) -> DataPipeline:
        """Create a new data pipeline."""
        pipeline = DataPipeline(name, config)
        self.pipelines[name] = pipeline
        return pipeline

    def run_pipeline(self, name: str) -> Dict[str, Any]:
        """Run a specific pipeline."""
        if name not in self.pipelines:
            raise ValueError(f"Pipeline '{name}' not found")

        pipeline = self.pipelines[name]
        result = pipeline.run()
        self.history.append(result)
        return result

    def get_pipeline_status(self, name: str) -> Dict[str, Any]:
        """Get status of a specific pipeline."""
        if name not in self.pipelines:
            return {"error": f"Pipeline '{name}' not found"}

        pipeline = self.pipelines[name]
        return {
            "name": name,
            "status": pipeline.metadata.status.value,
            "records_processed": pipeline.metadata.records_processed,
            "start_time": pipeline.metadata.start_time.isoformat(),
            "end_time": (
                pipeline.metadata.end_time.isoformat()
                if pipeline.metadata.end_time
                else None
            ),
        }

    def get_quality_report(self, name: str) -> Dict[str, Any]:
        """Get quality report for a specific pipeline."""
        if name not in self.pipelines:
            return {"error": f"Pipeline '{name}' not found"}

        return self.pipelines[name].get_quality_report()


# Global instance
pipeline_manager = PipelineManager()
