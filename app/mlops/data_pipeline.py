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

logger = logging.getLogger(__name__)

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
            f"Data validation completed. Completeness: {self.quality_metrics.completeness:.2f}"
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
