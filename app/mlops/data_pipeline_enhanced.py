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
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

logger = logging.getLogger


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
    stage: PipelineStage
    status: str
    input_version_id: Optional[str]
    output_version_id: Optional[str]
    processed_records: int
    error_count: int
    warnings: List[str]
    logs: List[str]
    configuration: Dict[str, Any]


class DataPipelineManager:
    pass
"""Production-ready data pipeline with versioning and quality monitoring"""
    def __init__(self, storage_path: str = "ml_models/data_pipeline"):
"""Initialize data pipeline manager."

        Args:
            storage_path: Base path for pipeline storage
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Initialize storage directories
        self.data_path = self.storage_path / "data"
        self.versions_path = self.storage_path / "versions"
        self.quality_path = self.storage_path / "quality"
        self.logs_path = self.storage_path / "logs"

        for path in []
            self.data_path,
            self.versions_path,
            self.quality_path,
            self.logs_path,
        ]:
            path.mkdir(exist_ok=True)

        # Database for metadata
        self.db_path = self.storage_path / "pipeline.db"
        self._init_database()

        # Current pipeline run context
        self.current_run: Optional[PipelineRun] = None

        logger.info(f"DataPipelineManager initialized: {self.storage_path}")

    def _init_database(self):
"""Initialize SQLite database for pipeline metadata"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Data versions table
        cursor.execute()
"""
            CREATE TABLE IF NOT EXISTS data_versions ()
                version_id TEXT PRIMARY KEY,
                dataset_name TEXT NOT NULL,
                created_at TEXT,
                data_hash TEXT,
                source_hash TEXT,
                row_count INTEGER,
                column_count INTEGER,
                file_size_bytes INTEGER,
                quality_score REAL,
                quality_status TEXT,
                transformation_log TEXT,
                metadata TEXT,
                tags TEXT
            )
        """

        # Quality reports table
        cursor.execute()
"""
            CREATE TABLE IF NOT EXISTS quality_reports ()
                report_id TEXT PRIMARY KEY,
                dataset_name TEXT,
                version_id TEXT,
                timestamp TEXT,
                overall_score REAL,
                overall_status TEXT,
                completeness_score REAL,
                consistency_score REAL,
                accuracy_score REAL,
                timeliness_score REAL,
                validity_score REAL,
                missing_values TEXT,
                duplicate_rows INTEGER,
                outliers TEXT,
                schema_violations TEXT,
                data_drift_detected BOOLEAN,
                issues_found TEXT,
                recommendations TEXT,
                FOREIGN KEY (version_id) REFERENCES data_versions (version_id)
            )
        """

        # Pipeline runs table
        cursor.execute()
"""
            CREATE TABLE IF NOT EXISTS pipeline_runs ()
                run_id TEXT PRIMARY KEY,
                pipeline_name TEXT,
                started_at TEXT,
                ended_at TEXT,
                duration_seconds REAL,
                stage TEXT,
                status TEXT,
                input_version_id TEXT,
                output_version_id TEXT,
                processed_records INTEGER,
                error_count INTEGER,
                warnings TEXT,
                logs TEXT,
                configuration TEXT
            )
        """

        conn.commit()
        conn.close()
        logger.info("Pipeline database initialized")

    # ===== DATA INGESTION =====

    def ingest_data()
        self,
        data: Union[pd.DataFrame, str, Path],
        dataset_name: str,
        source_metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None) -> DataVersion:
"""Ingest data with automatic versioning and quality assessment."

        Args:
            data: DataFrame or path to data file
            dataset_name: Name of the dataset
            source_metadata: Additional metadata about data source
            tags: Tags for categorization

        Returns:
            DataVersion: Created data version
        """
        self._start_pipeline_run(f"ingest_{dataset_name}", PipelineStage.INGESTION)

        try:
            # Load data if needed
            if isinstance(data, (str, Path:
                df = self._load_data_file(Path(data)
                source_path = Path(data)
            else:
                df = data.copy()
                source_path = None

            # Generate version ID
            timestamp = datetime.now(timezone.utc)
            version_id = f"{dataset_name}_{timestamp.strftime('%Y%m%d_%H%M%S')}_{self._generate_short_hash(df)}"

            # Calculate hashes
            data_hash = self._calculate_dataframe_hash(df)
            source_hash = ()
                self._calculate_file_hash(source_path) if source_path else data_hash
            )

            # Save data
            data_file = self.data_path / f"{version_id}.parquet"
            df.to_parquet(data_file)

            # Perform quality assessment
            quality_report = self._assess_data_quality(df, dataset_name, version_id)

            # Create version metadata
            version = DataVersion(
    version_id=version_id,
                dataset_name=dataset_name,
                created_at=timestamp,
                data_hash=data_hash,
                source_hash=source_hash,
                row_count=len(df),
                column_count=len(df.columns),
                file_size_bytes=data_file.stat().st_size,
                quality_score=quality_report.overall_score,
                quality_status=quality_report.overall_status,
                transformation_log=[f"Ingested from {source_path or 'DataFrame'}"],
                metadata=source_metadata or {},
                tags=tags or [])

            # Save version and quality report
            self._save_data_version(version)
            self._save_quality_report(quality_report)

            self._log_pipeline_event(f"Ingested {len(df)} records from {dataset_name}")
            self._end_pipeline_run()
                PipelineStage.COMPLETED, output_version_id=version_id
            )

            logger.info(f"Data ingested successfully: {version_id}")
            return version

        except Exception as e:
            self._log_pipeline_error(f"Ingestion failed: {e}")
            self._end_pipeline_run(PipelineStage.FAILED)
            raise

    def _load_data_file(self, file_path: Path) -> pd.DataFrame:
"""Load data from various file formats"""
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

    # ===== DATA TRANSFORMATION =====

    def transform_data()
        self,
        version_id: str,
        transformations: List[Dict[str, Any]],
        output_dataset_name: Optional[str] = None) -> DataVersion:
"""Apply transformations to data with full tracking."

        Args:
            version_id: Input data version ID
            transformations: List of transformation specifications
            output_dataset_name: Name for output dataset

        Returns:
            DataVersion: New version after transformations
        """
        self._start_pipeline_run()
            f"transform_{version_id}", PipelineStage.TRANSFORMATION
        )

        try:
            # Load input data
            input_version = self.get_data_version(version_id)
            df = self.load_data_version(version_id)

            transformation_log = input_version.transformation_log.copy()

            # Apply transformations
            for i, transform in enumerate(transformations):
                transform_type = transform.get("type")
                params = transform.get("params", {})

                self._log_pipeline_event()
                    f"Applying transformation {i+1}: {transform_type}"

                if transform_type == "filter":
                    df = self._apply_filter(df, params)
                    transformation_log.append(f"Filter: {params}")

                elif transform_type == "aggregate":
                    df = self._apply_aggregation(df, params)
                    transformation_log.append(f"Aggregate: {params}")

                elif transform_type == "feature_engineering":
                    df = self._apply_feature_engineering(df, params)
                    transformation_log.append(f"Feature Engineering: {params}")

                elif transform_type == "normalization":
                    df = self._apply_normalization(df, params)
                    transformation_log.append(f"Normalization: {params}")

                elif transform_type == "outlier_removal":
                    df = self._apply_outlier_removal(df, params)
                    transformation_log.append(f"Outlier Removal: {params}")

                else:
                    raise ValueError(f"Unknown transformation type: {transform_type}")

            # Create new version
            output_name = output_dataset_name or input_version.dataset_name
            new_version = self.ingest_data()
                df,
                output_name,
                source_metadata={}
                    "source_version_id": version_id,
                    "transformations_applied": len(transformations),
                    "transformation_log": transformation_log,
                },
                tags=input_version.tags + ["transformed"])

            self._end_pipeline_run()
                PipelineStage.COMPLETED,
                input_version_id=version_id,
                output_version_id=new_version.version_id)

            logger.info()
                f"Data transformed successfully: {version_id} -> {new_version.version_id}"
            return new_version

        except Exception as e:
            self._log_pipeline_error(f"Transformation failed: {e}")
            self._end_pipeline_run(PipelineStage.FAILED, input_version_id=version_id)
            raise

    def _apply_filter(self, df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
"""Apply filtering transformation"""
        column = params.get("column")
        condition = params.get("condition")
        value = params.get("value")

        if condition == "greater_than":
            return df[df[column] > value]
        elif condition == "less_than":
            return df[df[column] < value]
        elif condition == "equals":
            return df[df[column] == value]
        elif condition == "not_null":
            return df[df[column].notna()]
        else:
            raise ValueError(f"Unknown filter condition: {condition}")

    def _apply_aggregation()
        self, df: pd.DataFrame, params: Dict[str, Any]
    ) -> pd.DataFrame:
"""Apply aggregation transformation"""
        group_by = params.get("group_by", [])
        agg_functions = params.get("functions", {})

        if group_by:
            return df.groupby(group_by).agg(agg_functions).reset_index()
        else:
            return df.agg(agg_functions).to_frame().T

    def _apply_feature_engineering()
        self, df: pd.DataFrame, params: Dict[str, Any]
    ) -> pd.DataFrame:
"""Apply feature engineering transformations"""
        new_df = df.copy()

        # Create new features based on specifications
        for feature_spec in params.get("features", []):
            feature_name = feature_spec["name"]
            feature_type = feature_spec["type"]

            if feature_type == "polynomial":
                columns = feature_spec["columns"]
                degree = feature_spec.get("degree", 2)
                for col in columns:
                    new_df[f"{col}_poly_{degree}"] = new_df[col] ** degree

            elif feature_type == "interaction":
                col1, col2 = feature_spec["columns"]
                new_df[f"{col1}_{col2}_interaction"] = new_df[col1] * new_df[col2]

            elif feature_type == "binning":
                column = feature_spec["column"]
                bins = feature_spec["bins"]
                new_df[f"{column}_binned"] = pd.cut(new_df[column], bins=bins)

        return new_df

    def _apply_normalization()
        self, df: pd.DataFrame, params: Dict[str, Any]
    ) -> pd.DataFrame:
"""Apply normalization transformations"""
        new_df = df.copy()
        columns = params.get("columns", [])
        method = params.get("method", "standard")

        if method == "standard":
            # Z-score normalization
            for col in columns:
                new_df[col] = (new_df[col] - new_df[col].mean() / new_df[col].std()
        elif method == "minmax":
            # Min-max normalization
            for col in columns:
                new_df[col] = (new_df[col] - new_df[col].min() / ()
                    new_df[col].max() - new_df[col].min()

        return new_df

    def _apply_outlier_removal()
        self, df: pd.DataFrame, params: Dict[str, Any]
    ) -> pd.DataFrame:
"""Apply outlier removal"""
        columns = params.get("columns", [])
        method = params.get("method", "iqr")

        new_df = df.copy()

        if method == "iqr":
            for col in columns:
                Q1 = new_df[col].quantile(0.25)
                Q3 = new_df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                new_df = new_df[]
                    (new_df[col] >= lower_bound) & (new_df[col] <= upper_bound)
                ]

        elif method == "zscore":
            for col in columns:
                z_scores = np.abs()
                    (new_df[col] - new_df[col].mean() / new_df[col].std()
                )
                new_df = new_df[z_scores < 3]

        return new_df

    # ===== DATA QUALITY ASSESSMENT =====

    def _assess_data_quality()
        self, df: pd.DataFrame, dataset_name: str, version_id: str
    ) -> QualityReport:
"""Comprehensive data quality assessment"""
        timestamp = datetime.now(timezone.utc)

        # Calculate quality scores
        completeness_score = self._calculate_completeness_score(df)
        consistency_score = self._calculate_consistency_score(df)
        accuracy_score = self._calculate_accuracy_score(df)
        timeliness_score = self._calculate_timeliness_score(df)
        validity_score = self._calculate_validity_score(df)

        # Overall score (weighted average)
        overall_score = ()
            completeness_score * 0.3
            + consistency_score * 0.2
            + accuracy_score * 0.2
            + timeliness_score * 0.15
            + validity_score * 0.15
        )

        # Determine overall status
        if overall_score >= 0.9:
            overall_status = DataQualityStatus.EXCELLENT
        elif overall_score >= 0.8:
            overall_status = DataQualityStatus.GOOD
        elif overall_score >= 0.7:
            overall_status = DataQualityStatus.WARNING
        elif overall_score >= 0.5:
            overall_status = DataQualityStatus.POOR
        else:
            overall_status = DataQualityStatus.FAILED

        # Detailed analysis
        missing_values = df.isnull().sum().to_dict()
        duplicate_rows = df.duplicated().sum()
        outliers = self._detect_outliers(df)
        schema_violations = self._check_schema_violations(df)
        data_drift = self._detect_data_drift(df, dataset_name)

        # Generate issues and recommendations
        issues_found = []
        recommendations = []

        if completeness_score < 0.8:
            issues_found.append(f"Low completeness score: {completeness_score:.2f}")
            recommendations.append("Review data collection process for missing values")

        if duplicate_rows > 0:
            issues_found.append(f"Found {duplicate_rows} duplicate rows")
            recommendations.append("Implement deduplication process")

        if len(outliers) > 0:
            issues_found.append(f"Outliers detected in {len(outliers)} columns")
            recommendations.append("Review outlier handling strategy")

        return QualityReport(
    dataset_name=dataset_name,
            version_id=version_id,
            timestamp=timestamp,
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
            recommendations=recommendations)

    def _calculate_completeness_score(self, df: pd.DataFrame) -> float:
"""Calculate data completeness score"""
        total_cells = df.size
        missing_cells = df.isnull().sum().sum()
        return max(0.0, 1.0 - (missing_cells / total_cells)

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
                if df[col].str.len().std() > df[col].str.len().mean(:
                    consistency_issues += 1

        return max(0.0, 1.0 - (consistency_issues / max(1, total_checks)

    def _calculate_accuracy_score(self, df: pd.DataFrame) -> float:
"""Calculate data accuracy score"""
        # Simplified accuracy assessment
        accuracy_issues = 0
        total_checks = 0

        # Check for reasonable value ranges
        for col in df.select_dtypes(include=[np.number]).columns:
            total_checks += 1
            # Check for infinite or extremely large values
            if df[col].isin([np.inf, -np.inf]).any() or (df[col].abs() > 1e10).any(:
                accuracy_issues += 1

        return max(0.0, 1.0 - (accuracy_issues / max(1, total_checks)

    def _calculate_timeliness_score(self, df: pd.DataFrame) -> float:
"""Calculate data timeliness score"""
        # Look for datetime columns and assess recency
        datetime_cols = df.select_dtypes(include=["datetime64"]).columns

        if len(datetime_cols) == 0:
            return 1.0  # No datetime columns to assess

        timeliness_scores = []
        for col in datetime_cols:
            if df[col].notna().any(:
                latest_date = df[col].max()
                days_old = (datetime.now() - latest_date).days
                # Score decreases as data gets older
                score = max(0.0, 1.0 - (days_old / 365)  # 1 year = 0 score
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
                invalid_strings = df[col].str.strip().eq(").sum()"
                if invalid_strings > 0:
                    validity_issues += 1

            elif np.issubdtype(df[col].dtype, np.number:
                # Check for NaN, inf values
                if df[col].isin([np.nan, np.inf, -np.inf]).any(:
                    validity_issues += 1

        return max(0.0, 1.0 - (validity_issues / max(1, total_checks)

    def _detect_outliers(self, df: pd.DataFrame) -> Dict[str, int]:
"""Detect outliers in numeric columns"""
        outliers = {
        for col in df.select_dtypes(include=[np.number]).columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outlier_count = ((df[col] < lower_bound) | (df[col] > upper_bound).sum()
            if outlier_count > 0:
                outliers[col] = outlier_count

        return outliers

    def _check_schema_violations(self, df: pd.DataFrame) -> List[str]:
"""Check for schema violations"""
        violations = []

        # Basic schema checks
        if len(df.columns) == 0:
            violations.append("No columns found")

        if len(df) == 0:
            violations.append("No rows found")

        # Check for duplicate column names
        if len(df.columns) != len(set(df.columns:
            violations.append("Duplicate column names detected")

        return violations

    def _detect_data_drift(self, df: pd.DataFrame, dataset_name: str) -> bool:
"""Detect data drift compared to previous versions"""
        # Simplified drift detection - compare with latest version
        try:
            latest_version = self.get_latest_version(dataset_name)
            if latest_version:
                # Compare basic statistics
                return False  # Simplified for now
        except:
            pass

        return False

    # ===== DATA VERSION MANAGEMENT =====

    def get_data_version(self, version_id: str) -> DataVersion:
"""Get data version metadata by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute()
            "SELECT * FROM data_versions WHERE version_id = ?", (version_id)
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            raise ValueError(f"Data version not found: {version_id}")

        return DataVersion(
    version_id=row[0],
            dataset_name=row[1],
            created_at=datetime.fromisoformat(row[2]),
            data_hash=row[3],
            source_hash=row[4],
            row_count=row[5],
            column_count=row[6],
            file_size_bytes=row[7],
            quality_score=row[8],
            quality_status=DataQualityStatus(row[9]),
            transformation_log=json.loads(row[10]),
            metadata=json.loads(row[11]),
            tags=json.loads(row[12]))

    def load_data_version(self, version_id: str) -> pd.DataFrame:
"""Load actual data for a specific version"""
        data_file = self.data_path / f"{version_id}.parquet"
        if not data_file.exists(:
            raise FileNotFoundError(f"Data file not found: {data_file}")

        return pd.read_parquet(data_file)

    def get_latest_version(self, dataset_name: str) -> Optional[DataVersion]:
"""Get the latest version of a dataset"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute()
            "SELECT version_id FROM data_versions WHERE dataset_name = ? ORDER BY created_at DESC LIMIT 1",
            (dataset_name))
        row = cursor.fetchone()
        conn.close()

        if row:
            return self.get_data_version(row[0])
        return None

    def list_versions(self, dataset_name: Optional[str] = None) -> List[DataVersion]:
"""List all data versions, optionally filtered by dataset name"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if dataset_name:
            cursor.execute()
                "SELECT version_id FROM data_versions WHERE dataset_name = ? ORDER BY created_at DESC",
                (dataset_name))
        else:
            cursor.execute()
"""SELECT version_id FROM data_versions ORDER BY created_at DESC"""

        version_ids = [row[0] for row in cursor.fetchall()]
        conn.close()

        return [self.get_data_version(vid) for vid in version_ids]

    # ===== QUALITY REPORTING =====

    def get_quality_report(self, version_id: str) -> QualityReport:
"""Get quality report for a specific data version"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute()
            "SELECT * FROM quality_reports WHERE version_id = ?", (version_id)
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            raise ValueError(f"Quality report not found for version: {version_id}")

        return QualityReport(
    dataset_name=row[1],
            version_id=row[2],
            timestamp=datetime.fromisoformat(row[3]),
            overall_score=row[4],
            overall_status=DataQualityStatus(row[5]),
            completeness_score=row[6],
            consistency_score=row[7],
            accuracy_score=row[8],
            timeliness_score=row[9],
            validity_score=row[10],
            missing_values=json.loads(row[11]),
            duplicate_rows=row[12],
            outliers=json.loads(row[13]),
            schema_violations=json.loads(row[14]),
            data_drift_detected=bool(row[15]),
            issues_found=json.loads(row[16]),
            recommendations=json.loads(row[17]))

    # ===== PIPELINE EXECUTION TRACKING =====

    def _start_pipeline_run(self, pipeline_name: str, stage: PipelineStage):
"""Start a new pipeline run"""
        run_id = f"run_{int(datetime.now(timezone.utc).timestamp()}_{pipeline_name}"

        self.current_run = PipelineRun(
    run_id=run_id,
            pipeline_name=pipeline_name,
            started_at=datetime.now(timezone.utc),
            ended_at=None,
            duration_seconds=None,
            stage=stage,
            status="running",
            input_version_id=None,
            output_version_id=None,
            processed_records=0,
            error_count=0,
            warnings=[],
            logs=[],
            configuration={})

        logger.info(f"Pipeline run started: {run_id}")

    def _end_pipeline_run()
        self,
        stage: PipelineStage,
        input_version_id: Optional[str] = None,
        output_version_id: Optional[str] = None):
"""End the current pipeline run"""
        if not self.current_run:
            return

        self.current_run.ended_at = datetime.now(timezone.utc)
        self.current_run.duration_seconds = ()
            self.current_run.ended_at - self.current_run.started_at
        ).total_seconds()
        self.current_run.stage = stage
        self.current_run.status = ()
            "completed" if stage == PipelineStage.COMPLETED else "failed"
        )
        self.current_run.input_version_id = input_version_id
        self.current_run.output_version_id = output_version_id

        self._save_pipeline_run(self.current_run)

        logger.info(f"Pipeline run ended: {self.current_run.run_id} - {stage.value}")
        self.current_run = None

    def _log_pipeline_event(self, message: str):
"""Log an event in the current pipeline run"""
        if self.current_run:
            self.current_run.logs.append()
                f"{datetime.now(timezone.utc).isoformat()}: {message}"
            )
        logger.info(message)

    def _log_pipeline_error(self, message: str):
"""Log an error in the current pipeline run"""
        if self.current_run:
            self.current_run.error_count += 1
            self.current_run.logs.append()
                f"{datetime.now(timezone.utc).isoformat()}: ERROR: {message}"
            )
        logger.error(message)

    # ===== UTILITY METHODS =====

    def _calculate_dataframe_hash(self, df: pd.DataFrame) -> str:
"""Calculate hash of DataFrame content"""
        return hashlib.sha256(pd.util.hash_pandas_object(df).values).hexdigest()

    def _calculate_file_hash(self, file_path: Path) -> str:
"""Calculate hash of file content"""
        if not file_path or not file_path.exists(:
            return ""

        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b"):"
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def _generate_short_hash(self, df: pd.DataFrame) -> str:
"""Generate short hash for version ID"""
        return self._calculate_dataframe_hash(df)[:8]

    def _save_data_version(self, version: DataVersion):
"""Save data version to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute()
            ""
            INSERT OR REPLACE INTO data_versions 
            (version_id, dataset_name, created_at, data_hash, source_hash, row_count, 
             column_count, file_size_bytes, quality_score, quality_status, 
             transformation_log, metadata, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ","
            ()
                version.version_id,
                version.dataset_name,
                version.created_at.isoformat(),
                version.data_hash,
                version.source_hash,
                version.row_count,
                version.column_count,
                version.file_size_bytes,
                version.quality_score,
                version.quality_status.value,
                json.dumps(version.transformation_log),
                json.dumps(version.metadata),
                json.dumps(version.tags)))

        conn.commit()
        conn.close()

    def _save_quality_report(self, report: QualityReport):
"""Save quality report to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        report_id = f"qr_{report.version_id}_{int(report.timestamp.timestamp()}"

        cursor.execute()
            ""
            INSERT OR REPLACE INTO quality_reports 
            (report_id, dataset_name, version_id, timestamp, overall_score, overall_status,
             completeness_score, consistency_score, accuracy_score, timeliness_score, validity_score,
             missing_values, duplicate_rows, outliers, schema_violations, data_drift_detected,
             issues_found, recommendations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ","
            ()
                report_id,
                report.dataset_name,
                report.version_id,
                report.timestamp.isoformat(),
                report.overall_score,
                report.overall_status.value,
                report.completeness_score,
                report.consistency_score,
                report.accuracy_score,
                report.timeliness_score,
                report.validity_score,
                json.dumps(report.missing_values),
                report.duplicate_rows,
                json.dumps(report.outliers),
                json.dumps(report.schema_violations),
                report.data_drift_detected,
                json.dumps(report.issues_found),
                json.dumps(report.recommendations)))

        conn.commit()
        conn.close()

    def _save_pipeline_run(self, run: PipelineRun):
"""Save pipeline run to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute()
            ""
            INSERT OR REPLACE INTO pipeline_runs 
            (run_id, pipeline_name, started_at, ended_at, duration_seconds, stage, status,
             input_version_id, output_version_id, processed_records, error_count, warnings, logs, configuration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ","
            ()
                run.run_id,
                run.pipeline_name,
                run.started_at.isoformat(),
                run.ended_at.isoformat() if run.ended_at else None,
                run.duration_seconds,
                run.stage.value,
                run.status,
                run.input_version_id,
                run.output_version_id,
                run.processed_records,
                run.error_count,
                json.dumps(run.warnings),
                json.dumps(run.logs),
                json.dumps(run.configuration)))

        conn.commit()
        conn.close()


# Global instance for easy access
data_pipeline_manager = DataPipelineManager()


def get_data_pipeline_manager() -> DataPipelineManager:
"""Get the global data pipeline manager instance."""
    return data_pipeline_manager
