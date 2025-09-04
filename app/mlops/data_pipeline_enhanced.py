#!/usr/bin/env python3
"""
Enhanced Data Pipeline - Production-ready data processing and versioning
Phase 2A Week 3: Data Pipeline Automation with quality monitoring and versioning
"""

import hashlib
import json
import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


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
class DataVersion:
    """Data version metadata for tracking and reproducibility"""

    version_id: str
    dataset_name: str
    created_at: datetime
    data_hash: str
    source_hash: str
    row_count: int
    column_count: int
    file_size_bytes: int
    quality_score: float
    quality_status: DataQualityStatus
    transformation_log: List[str]
    metadata: Dict[str, Any]
    tags: List[str]


@dataclass
class QualityReport:
    """Comprehensive data quality assessment report"""

    dataset_name: str
    version_id: str
    timestamp: datetime
    overall_score: float
    overall_status: DataQualityStatus

    # Quality metrics
    completeness_score: float
    consistency_score: float
    accuracy_score: float
    timeliness_score: float
    validity_score: float

    # Detailed findings
    missing_values: Dict[str, int]
    duplicate_rows: int
    outliers: Dict[str, int]
    schema_violations: List[str]
    data_drift_detected: bool

    # Recommendations
    issues_found: List[str]
    recommendations: List[str]


@dataclass
class PipelineRun:
    """Individual pipeline execution tracking"""

    run_id: str
    pipeline_name: str
    started_at: datetime
    ended_at: Optional[datetime]
    duration_seconds: Optional[float]
    status: PipelineStage
    input_data_path: str
    output_data_path: Optional[str]
    quality_report_path: Optional[str]
    error_message: Optional[str]
    metadata: Dict[str, Any]


class EnhancedDataPipeline:
    """
    Enhanced data pipeline with comprehensive quality monitoring,
    versioning, and automated processing capabilities.
    """

    def __init__(self, pipeline_name: str, base_path: str = "./data_pipeline"):
        """
        Initialize the enhanced data pipeline.

        Args:
            pipeline_name: Name of the pipeline
            base_path: Base directory for pipeline artifacts
        """
        self.pipeline_name = pipeline_name
        self.base_path = Path(base_path)
        self.data_path = self.base_path / "data"
        self.logs_path = self.base_path / "logs"
        self.reports_path = self.base_path / "reports"
        self.models_path = self.base_path / "models"

        # Create necessary directories
        for path in [
            self.data_path,
            self.logs_path,
            self.reports_path,
            self.models_path,
        ]:
            path.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self.db_path = self.base_path / "pipeline.db"
        self._init_database()

        logger.info(f"Enhanced data pipeline '{pipeline_name}' initialized")

    def _init_database(self):
        """Initialize SQLite database for pipeline tracking"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create data versions table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS data_versions (
                    version_id TEXT PRIMARY KEY,
                    dataset_name TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    data_hash TEXT NOT NULL,
                    source_hash TEXT NOT NULL,
                    row_count INTEGER NOT NULL,
                    column_count INTEGER NOT NULL,
                    file_size_bytes INTEGER NOT NULL,
                    quality_score REAL NOT NULL,
                    quality_status TEXT NOT NULL,
                    transformation_log TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    tags TEXT NOT NULL
                )
            """
            )

            # Create quality reports table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS quality_reports (
                    report_id TEXT PRIMARY KEY,
                    dataset_name TEXT NOT NULL,
                    version_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    overall_score REAL NOT NULL,
                    overall_status TEXT NOT NULL,
                    completeness_score REAL NOT NULL,
                    consistency_score REAL NOT NULL,
                    accuracy_score REAL NOT NULL,
                    timeliness_score REAL NOT NULL,
                    validity_score REAL NOT NULL,
                    missing_values TEXT NOT NULL,
                    duplicate_rows INTEGER NOT NULL,
                    outliers TEXT NOT NULL,
                    schema_violations TEXT NOT NULL,
                    data_drift_detected BOOLEAN NOT NULL,
                    issues_found TEXT NOT NULL,
                    recommendations TEXT NOT NULL,
                    FOREIGN KEY (version_id) REFERENCES data_versions (version_id)
                )
            """
            )

            # Create pipeline runs table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS pipeline_runs (
                    run_id TEXT PRIMARY KEY,
                    pipeline_name TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    duration_seconds REAL,
                    status TEXT NOT NULL,
                    input_data_path TEXT NOT NULL,
                    output_data_path TEXT,
                    quality_report_path TEXT,
                    error_message TEXT,
                    metadata TEXT NOT NULL
                )
            """
            )

            conn.commit()

    def ingest_data(
        self, data_source: Union[str, pd.DataFrame], dataset_name: str
    ) -> str:
        """
        Ingest data from various sources with quality checks.

        Args:
            data_source: Path to data file or DataFrame
            dataset_name: Name for the dataset

        Returns:
            Version ID of the ingested data
        """
        logger.info(f"Ingesting data for dataset: {dataset_name}")

        # Load data
        if isinstance(data_source, str):
            data_path = Path(data_source)
            if data_path.suffix == ".csv":
                df = pd.read_csv(data_path)
            elif data_path.suffix == ".parquet":
                df = pd.read_parquet(data_path)
            elif data_path.suffix == ".json":
                df = pd.read_json(data_path)
            else:
                raise ValueError(f"Unsupported file format: {data_path.suffix}")
        else:
            df = data_source.copy()

        # Generate version ID
        version_id = self._generate_version_id(dataset_name, df)

        # Calculate data hash
        data_hash = self._calculate_data_hash(df)

        # Calculate source hash
        source_hash = (
            self._calculate_source_hash(data_source)
            if isinstance(data_source, str)
            else "dataframe"
        )

        # Create data version
        data_version = DataVersion(
            version_id=version_id,
            dataset_name=dataset_name,
            created_at=datetime.now(timezone.utc),
            data_hash=data_hash,
            source_hash=source_hash,
            row_count=len(df),
            column_count=len(df.columns),
            file_size_bytes=len(df.to_csv(index=False).encode()),
            quality_score=0.0,  # Will be calculated later
            quality_status=DataQualityStatus.WARNING,
            transformation_log=["Data ingested"],
            metadata={
                "source": (
                    str(data_source) if isinstance(data_source, str) else "dataframe"
                )
            },
            tags=["ingested"],
        )

        # Save data version to database
        self._save_data_version(data_version)

        # Save data file
        output_path = self.data_path / f"{version_id}.parquet"
        df.to_parquet(output_path, index=False)

        logger.info(f"Data ingested successfully. Version ID: {version_id}")
        return version_id

    def transform_data(
        self, version_id: str, transformations: List[Dict[str, Any]]
    ) -> str:
        """
        Apply transformations to the data.

        Args:
            version_id: Version ID of the input data
            transformations: List of transformation operations

        Returns:
            Version ID of the transformed data
        """
        logger.info(f"Applying transformations to version: {version_id}")

        # Load input data
        input_data = self._load_data_version(version_id)
        if not input_data:
            raise ValueError(f"Data version not found: {version_id}")

        # Load the actual data
        data_path = self.data_path / f"{version_id}.parquet"
        df = pd.read_parquet(data_path)

        # Apply transformations
        transformation_log = []
        for i, transform in enumerate(transformations):
            transform_type = transform.get("type")
            transform_params = transform.get("params", {})

            try:
                if transform_type == "filter":
                    df = self._apply_filter(df, transform_params)
                elif transform_type == "aggregate":
                    df = self._apply_aggregation(df, transform_params)
                elif transform_type == "normalize":
                    df = self._apply_normalization(df, transform_params)
                elif transform_type == "outlier_removal":
                    df = self._apply_outlier_removal(df, transform_params)
                else:
                    logger.warning(f"Unknown transformation type: {transform_type}")
                    continue

                transformation_log.append(f"Applied {transform_type} transformation")
                logger.info(
                    f"Applied transformation {i+1}/{len(transformations)}: {transform_type}"
                )

            except Exception as e:
                error_msg = f"Failed to apply transformation {transform_type}: {str(e)}"
                transformation_log.append(error_msg)
                logger.error(error_msg)
                raise

        # Generate new version ID
        new_version_id = self._generate_version_id(input_data.dataset_name, df)

        # Calculate new data hash
        data_hash = self._calculate_data_hash(df)

        # Create new data version
        new_data_version = DataVersion(
            version_id=new_version_id,
            dataset_name=input_data.dataset_name,
            created_at=datetime.now(timezone.utc),
            data_hash=data_hash,
            source_hash=input_data.data_hash,  # Previous version as source
            row_count=len(df),
            column_count=len(df.columns),
            file_size_bytes=len(df.to_csv(index=False).encode()),
            quality_score=0.0,  # Will be calculated later
            quality_status=DataQualityStatus.WARNING,
            transformation_log=input_data.transformation_log + transformation_log,
            metadata={**input_data.metadata, "parent_version": version_id},
            tags=input_data.tags + ["transformed"],
        )

        # Save new data version
        self._save_data_version(new_data_version)

        # Save transformed data
        output_path = self.data_path / f"{new_version_id}.parquet"
        df.to_parquet(output_path, index=False)

        logger.info(f"Data transformation completed. New version ID: {new_version_id}")
        return new_version_id

    def assess_data_quality(self, version_id: str) -> QualityReport:
        """
        Perform comprehensive data quality assessment.

        Args:
            version_id: Version ID of the data to assess

        Returns:
            Quality report with detailed assessment
        """
        logger.info(f"Assessing data quality for version: {version_id}")

        # Load data
        data_path = self.data_path / f"{version_id}.parquet"
        df = pd.read_parquet(data_path)

        # Calculate quality scores
        completeness_score = self._calculate_completeness_score(df)
        consistency_score = self._calculate_consistency_score(df)
        accuracy_score = self._calculate_accuracy_score(df)
        timeliness_score = self._calculate_timeliness_score(df)
        validity_score = self._calculate_validity_score(df)

        # Calculate overall score
        overall_score = np.mean(
            [
                completeness_score,
                consistency_score,
                accuracy_score,
                timeliness_score,
                validity_score,
            ]
        )

        # Determine overall status
        if overall_score >= 0.9:
            overall_status = DataQualityStatus.EXCELLENT
        elif overall_score >= 0.8:
            overall_status = DataQualityStatus.GOOD
        elif overall_score >= 0.7:
            overall_status = DataQualityStatus.WARNING
        elif overall_score >= 0.6:
            overall_status = DataQualityStatus.POOR
        else:
            overall_status = DataQualityStatus.FAILED

        # Detect issues
        missing_values = {k: int(v) for k, v in df.isnull().sum().to_dict().items()}
        duplicate_rows = int(df.duplicated().sum())
        outliers = self._detect_outliers(df)
        schema_violations = self._check_schema_violations(df)
        data_drift = self._detect_data_drift(df, version_id)

        # Generate recommendations
        issues_found, recommendations = self._generate_quality_recommendations(
            df, missing_values, duplicate_rows, outliers, schema_violations, data_drift
        )

        # Create quality report
        quality_report = QualityReport(
            dataset_name=df.columns[0] if len(df.columns) > 0 else "unknown",
            version_id=version_id,
            timestamp=datetime.now(timezone.utc),
            overall_score=overall_score,
            overall_status=overall_status,
            completeness_score=completeness_score,
            consistency_score=consistency_score,
            accuracy_score=accuracy_score,
            timeliness_score=timeliness_score,
            validity_score=validity_score,
            missing_values=missing_values,
            duplicate_rows=duplicate_rows,
            outliers=outliers,
            schema_violations=schema_violations,
            data_drift_detected=data_drift,
            issues_found=issues_found,
            recommendations=recommendations,
        )

        # Save quality report
        self._save_quality_report(quality_report)

        # Update data version with quality score
        self._update_data_version_quality(version_id, overall_score, overall_status)

        logger.info(f"Quality assessment completed. Overall score: {overall_score:.3f}")
        return quality_report

    def _calculate_completeness_score(self, df: pd.DataFrame) -> float:
        """Calculate data completeness score"""
        total_cells = df.size
        missing_cells = df.isnull().sum().sum()
        return max(0.0, 1.0 - (missing_cells / total_cells))

    def _calculate_consistency_score(self, df: pd.DataFrame) -> float:
        """Calculate data consistency score"""
        # Simplified consistency check - can be enhanced
        consistency_issues = 0
        total_checks = 0

        # Check for consistent data types in each column
        for col in df.columns:
            if df[col].dtype == "object":
                # Check string consistency (basic patterns)
                total_checks += 1
                if df[col].str.len().std() > df[col].str.len().mean():
                    consistency_issues += 1

        return max(0.0, 1.0 - (consistency_issues / max(1, total_checks)))

    def _calculate_accuracy_score(self, df: pd.DataFrame) -> float:
        """Calculate data accuracy score"""
        # Simplified accuracy assessment
        accuracy_issues = 0
        total_checks = 0

        # Check for reasonable value ranges
        for col in df.select_dtypes(include=[np.number]).columns:
            total_checks += 1
            # Check for infinite or extremely large values
            if df[col].isin([np.inf, -np.inf]).any() or (df[col].abs() > 1e10).any():
                accuracy_issues += 1

        return max(0.0, 1.0 - (accuracy_issues / max(1, total_checks)))

    def _calculate_timeliness_score(self, df: pd.DataFrame) -> float:
        """Calculate data timeliness score"""
        # Look for datetime columns and assess recency
        datetime_cols = df.select_dtypes(include=["datetime64"]).columns

        if len(datetime_cols) == 0:
            return 1.0  # No datetime columns to assess

        timeliness_scores = []
        for col in datetime_cols:
            if df[col].notna().any():
                latest_date = df[col].max()
                days_old = (datetime.now() - latest_date).days
                # Score decreases as data gets older
                score = max(0.0, 1.0 - (days_old / 365))  # 1 year = 0 score
                timeliness_scores.append(score)

        return np.mean(timeliness_scores) if timeliness_scores else 1.0

    def _calculate_validity_score(self, df: pd.DataFrame) -> float:
        """Calculate data validity score"""
        validity_issues = 0
        total_checks = 0

        # Check for valid data patterns
        for col in df.columns:
            total_checks += 1

            # Check for obviously invalid values
            if df[col].dtype == "object":
                # Check for empty strings, whitespace-only strings
                invalid_strings = df[col].str.strip().eq("").sum()
                if invalid_strings > 0:
                    validity_issues += 1

            elif np.issubdtype(df[col].dtype, np.number):
                # Check for NaN, inf values
                if df[col].isin([np.nan, np.inf, -np.inf]).any():
                    validity_issues += 1

        return max(0.0, 1.0 - (validity_issues / max(1, total_checks)))

    def _detect_outliers(self, df: pd.DataFrame) -> Dict[str, int]:
        """Detect outliers in numeric columns"""
        outliers = {}

        for col in df.select_dtypes(include=[np.number]).columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outlier_count = int(
                ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
            )
            if outlier_count > 0:
                outliers[col] = outlier_count

        return outliers

    def _check_schema_violations(self, df: pd.DataFrame) -> List[str]:
        """Check for schema violations"""
        violations = []

        # Check for unexpected data types
        for col in df.columns:
            if df[col].dtype == "object":
                # Check if object column should be numeric
                try:
                    pd.to_numeric(df[col], errors="raise")
                    violations.append(
                        f"Column '{col}' contains numeric data but is object type"
                    )
                except (ValueError, TypeError):
                    pass

        return violations

    def _detect_data_drift(self, df: pd.DataFrame, version_id: str) -> bool:
        """Detect data drift by comparing with previous versions"""
        # Simplified drift detection - can be enhanced with statistical tests
        try:
            # Get previous version
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT data_hash FROM data_versions WHERE dataset_name = ? ORDER BY created_at DESC LIMIT 1 OFFSET 1",
                    (df.columns[0] if len(df.columns) > 0 else "unknown",),
                )
                result = cursor.fetchone()

                if result:
                    previous_hash = result[0]
                    current_hash = self._calculate_data_hash(df)
                    return previous_hash != current_hash
        except Exception as e:
            logger.warning(f"Error detecting data drift: {e}")

        return False

    def _generate_quality_recommendations(
        self,
        df: pd.DataFrame,
        missing_values: Dict[str, int],
        duplicate_rows: int,
        outliers: Dict[str, int],
        schema_violations: List[str],
        data_drift: bool,
    ) -> Tuple[List[str], List[str]]:
        """Generate quality recommendations based on findings"""
        issues_found = []
        recommendations = []

        # Check missing values
        high_missing_cols = [
            col for col, count in missing_values.items() if count > len(df) * 0.1
        ]
        if high_missing_cols:
            issues_found.append(f"High missing values in columns: {high_missing_cols}")
            recommendations.append(
                "Consider imputation or removal of columns with >10% missing values"
            )

        # Check duplicates
        if duplicate_rows > 0:
            issues_found.append(f"Found {duplicate_rows} duplicate rows")
            recommendations.append("Remove duplicate rows to improve data quality")

        # Check outliers
        if outliers:
            issues_found.append(
                f"Outliers detected in columns: {list(outliers.keys())}"
            )
            recommendations.append("Investigate and handle outliers appropriately")

        # Check schema violations
        if schema_violations:
            issues_found.extend(schema_violations)
            recommendations.append("Fix data type inconsistencies")

        # Check data drift
        if data_drift:
            issues_found.append("Data drift detected")
            recommendations.append("Investigate changes in data distribution")

        return issues_found, recommendations

    def _apply_filter(self, df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Apply filtering transformation"""
        column = params.get("column")
        condition = params.get("condition")
        value = params.get("value")

        if column and condition and value is not None:
            if condition == "equals":
                return df[df[column] == value]
            elif condition == "greater_than":
                return df[df[column] > value]
            elif condition == "less_than":
                return df[df[column] < value]
            elif condition == "contains":
                return df[df[column].str.contains(str(value), na=False)]

        return df

    def _apply_aggregation(
        self, df: pd.DataFrame, params: Dict[str, Any]
    ) -> pd.DataFrame:
        """Apply aggregation transformation"""
        group_by = params.get("group_by", [])
        aggregations = params.get("aggregations", {})

        if group_by and aggregations:
            return df.groupby(group_by).agg(aggregations).reset_index()

        return df

    def _apply_normalization(
        self, df: pd.DataFrame, params: Dict[str, Any]
    ) -> pd.DataFrame:
        """Apply normalization transformation"""
        columns = params.get("columns", [])
        method = params.get("method", "zscore")

        if not columns:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()

        df_normalized = df.copy()
        for col in columns:
            if col in df.columns and df[col].dtype in [np.number]:
                if method == "zscore":
                    mean_val = df[col].mean()
                    std_val = df[col].std()
                    if std_val > 0:
                        df_normalized[col] = (df[col] - mean_val) / std_val
                elif method == "minmax":
                    min_val = df[col].min()
                    max_val = df[col].max()
                    if max_val > min_val:
                        df_normalized[col] = (df[col] - min_val) / (max_val - min_val)

        return df_normalized

    def _apply_outlier_removal(
        self, df: pd.DataFrame, params: Dict[str, Any]
    ) -> pd.DataFrame:
        """Apply outlier removal transformation"""
        columns = params.get("columns", [])
        method = params.get("method", "iqr")
        threshold = params.get("threshold", 1.5)

        if not columns:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()

        df_clean = df.copy()
        for col in columns:
            if col in df.columns and df[col].dtype in [np.number]:
                if method == "iqr":
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - threshold * IQR
                    upper_bound = Q3 + threshold * IQR

                    # Remove outliers
                    mask = (df_clean[col] >= lower_bound) & (
                        df_clean[col] <= upper_bound
                    )
                    df_clean = df_clean[mask]

        return df_clean

    def _generate_version_id(self, dataset_name: str, df: pd.DataFrame) -> str:
        """Generate unique version ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        data_hash = self._calculate_data_hash(df)[:8]
        return f"{dataset_name}_{timestamp}_{data_hash}"

    def _calculate_data_hash(self, df: pd.DataFrame) -> str:
        """Calculate hash of data content"""
        data_str = df.to_csv(index=False)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def _calculate_source_hash(self, source_path: str) -> str:
        """Calculate hash of source file"""
        try:
            with open(source_path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return "unknown"

    def _save_data_version(self, data_version: DataVersion):
        """Save data version to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO data_versions
                (version_id, dataset_name, created_at, data_hash, source_hash,
                 row_count, column_count, file_size_bytes, quality_score,
                 quality_status, transformation_log, metadata, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    data_version.version_id,
                    data_version.dataset_name,
                    data_version.created_at.isoformat(),
                    data_version.data_hash,
                    data_version.source_hash,
                    data_version.row_count,
                    data_version.column_count,
                    data_version.file_size_bytes,
                    data_version.quality_score,
                    data_version.quality_status.value,
                    json.dumps(data_version.transformation_log),
                    json.dumps(data_version.metadata),
                    json.dumps(data_version.tags),
                ),
            )
            conn.commit()

    def _load_data_version(self, version_id: str) -> Optional[DataVersion]:
        """Load data version from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM data_versions WHERE version_id = ?", (version_id,)
            )
            result = cursor.fetchone()

            if result:
                return DataVersion(
                    version_id=result[0],
                    dataset_name=result[1],
                    created_at=datetime.fromisoformat(result[2]),
                    data_hash=result[3],
                    source_hash=result[4],
                    row_count=result[5],
                    column_count=result[6],
                    file_size_bytes=result[7],
                    quality_score=result[8],
                    quality_status=DataQualityStatus(result[9]),
                    transformation_log=json.loads(result[10]),
                    metadata=json.loads(result[11]),
                    tags=json.loads(result[12]),
                )

        return None

    def _save_quality_report(self, quality_report: QualityReport):
        """Save quality report to database"""
        report_id = f"qr_{quality_report.version_id}_{int(quality_report.timestamp.timestamp())}"

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO quality_reports
                (report_id, dataset_name, version_id, timestamp, overall_score,
                 overall_status, completeness_score, consistency_score,
                 accuracy_score, timeliness_score, validity_score,
                 missing_values, duplicate_rows, outliers, schema_violations,
                 data_drift_detected, issues_found, recommendations)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    report_id,
                    quality_report.dataset_name,
                    quality_report.version_id,
                    quality_report.timestamp.isoformat(),
                    quality_report.overall_score,
                    quality_report.overall_status.value,
                    quality_report.completeness_score,
                    quality_report.consistency_score,
                    quality_report.accuracy_score,
                    quality_report.timeliness_score,
                    quality_report.validity_score,
                    json.dumps(quality_report.missing_values),
                    quality_report.duplicate_rows,
                    json.dumps(quality_report.outliers),
                    json.dumps(quality_report.schema_violations),
                    quality_report.data_drift_detected,
                    json.dumps(quality_report.issues_found),
                    json.dumps(quality_report.recommendations),
                ),
            )
            conn.commit()

    def _update_data_version_quality(
        self, version_id: str, quality_score: float, quality_status: DataQualityStatus
    ):
        """Update data version with quality information"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE data_versions
                SET quality_score = ?, quality_status = ?
                WHERE version_id = ?
            """,
                (quality_score, quality_status.value, version_id),
            )
            conn.commit()

    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get overall pipeline status and statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get basic statistics
            cursor.execute("SELECT COUNT(*) FROM data_versions")
            total_versions = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM quality_reports")
            total_reports = cursor.fetchone()[0]

            cursor.execute(
                "SELECT AVG(quality_score) FROM data_versions WHERE quality_score > 0"
            )
            avg_quality = cursor.fetchone()[0] or 0.0

            cursor.execute(
                "SELECT COUNT(*) FROM data_versions WHERE quality_status = 'excellent'"
            )
            excellent_count = cursor.fetchone()[0]

            return {
                "pipeline_name": self.pipeline_name,
                "total_versions": total_versions,
                "total_quality_reports": total_reports,
                "average_quality_score": round(avg_quality, 3),
                "excellent_quality_count": excellent_count,
                "database_path": str(self.db_path),
                "data_directory": str(self.data_path),
            }

    def list_versions(self, dataset_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all data versions with optional filtering"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            if dataset_name:
                cursor.execute(
                    """
                    SELECT version_id, dataset_name, created_at, quality_score, quality_status
                    FROM data_versions
                    WHERE dataset_name = ?
                    ORDER BY created_at DESC
                """,
                    (dataset_name,),
                )
            else:
                cursor.execute(
                    """
                    SELECT version_id, dataset_name, created_at, quality_score, quality_status
                    FROM data_versions
                    ORDER BY created_at DESC
                """
                )

            results = cursor.fetchall()
            return [
                {
                    "version_id": row[0],
                    "dataset_name": row[1],
                    "created_at": row[2],
                    "quality_score": row[3],
                    "quality_status": row[4],
                }
                for row in results
            ]

    def cleanup_old_versions(self, keep_count: int = 10) -> int:
        """Clean up old versions, keeping only the most recent ones"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get versions to delete
            cursor.execute(
                """
                SELECT version_id FROM data_versions
                ORDER BY created_at DESC
                LIMIT -1 OFFSET ?
            """,
                (keep_count,),
            )

            versions_to_delete = [row[0] for row in cursor.fetchall()]

            if not versions_to_delete:
                return 0

            # Delete from database
            placeholders = ",".join(["?" for _ in versions_to_delete])
            cursor.execute(
                f"DELETE FROM data_versions WHERE version_id IN ({placeholders})",
                versions_to_delete,
            )

            # Delete data files
            deleted_files = 0
            for version_id in versions_to_delete:
                data_file = self.data_path / f"{version_id}.parquet"
                if data_file.exists():
                    data_file.unlink()
                    deleted_files += 1

            conn.commit()
            logger.info(
                f"Cleaned up {len(versions_to_delete)} old versions and {deleted_files} files"
            )
            return len(versions_to_delete)


# Global instance for easy access
enhanced_pipeline = None


def get_enhanced_pipeline(pipeline_name: str = "default") -> EnhancedDataPipeline:
    """Get or create global enhanced data pipeline instance"""
    global enhanced_pipeline
    if enhanced_pipeline is None:
        enhanced_pipeline = EnhancedDataPipeline(pipeline_name)
    return enhanced_pipeline
