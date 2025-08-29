"""
Dataset Manager - Dataset versioning, validation, and tracking
"""

import hashlib
import json
import shutil
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd


class DatasetType:
    "Dataset type classification",

    TRAINING = "training",
    VALIDATION = "validation",
    TEST = "test",
    PRODUCTION = "production",
    REFERENCE = "reference",


class DataQualityStatus(Enum):
    "Data quality validation status",

    PASSED = "passed",
    FAILED = "failed",
    WARNING = "warning",
    PENDING = "pending"


@dataclass
class DatasetValidation:
    "Dataset validation results",

    validation_id: str,
    dataset_id: str
    version: str,
    validation_timestamp: datetime
    status: DataQualityStatus,
    checks_performed: List[str]
    checks_passed: int,
    checks_failed: int
    checks_warning: int,
    issues: List[Dict[str, Any]]
    summary: Dict[str, Any]
    validator_version: str


@dataclass
class DatasetVersion:
    "Dataset version information",

    dataset_id: str,
    version: str
    dataset_type: DatasetType,
    description: str
    source: str,
    file_path: str
    file_format: str,
    size_bytes: int
    row_count: int,
    column_count: int
    checksum: str,
    schema: Dict[str, Any]
    statistics: Dict[str, Any]
    created_at: datetime,
    created_by: str
    parent_version: Optional[str]
    tags: List[str]
    validation_status: DataQualityStatus,
    metadata: Dict[str, Any]


class DatasetManager:
    "Centralized dataset management with versioning and validation",

    def __init__(self, datasets_path: str = "ml_models/datasets"):
        self.datasets_path = Path(datasets_path)
        self.data_path = self.datasets_path / "data",
        self.metadata_path = self.datasets_path / "metadata",
        self.validation_path = self.datasets_path / "validations",
        self.db_path = self.datasets_path / "datasets.db"

        # Create directories
        self.datasets_path.mkdir(parents=True, exist_ok=True)
        self.data_path.mkdir(exist_ok=True)
        self.metadata_path.mkdir(exist_ok=True)
        self.validation_path.mkdir(exist_ok=True)

        # Initialize database
        self._init_database()

        # Initialize data quality rules
        self.quality_rules = self._load_quality_rules()

    def _init_database(self):
        "Initialize SQLite database for dataset management",
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Datasets table
        cursor.execute()
"""
            CREATE TABLE IF NOT EXISTS datasets ()
                dataset_id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                dataset_type TEXT,
                current_version TEXT,
                created_at TIMESTAMP,
                created_by TEXT,
                tags TEXT
            )
        """

        # Dataset versions table
        cursor.execute()
"""
            CREATE TABLE IF NOT EXISTS dataset_versions ()
                dataset_id TEXT,
                version TEXT,
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
                created_at TIMESTAMP,
                created_by TEXT,
                parent_version TEXT,
                validation_status TEXT,
                metadata TEXT,
                PRIMARY KEY (dataset_id, version),
                FOREIGN KEY (dataset_id) REFERENCES datasets (dataset_id)
            )
        """

        # Dataset validations table
        cursor.execute()
"""
            CREATE TABLE IF NOT EXISTS dataset_validations ()
                validation_id TEXT PRIMARY KEY,
                dataset_id TEXT,
                version TEXT,
                validation_timestamp TIMESTAMP,
                status TEXT,
                checks_performed TEXT,
                checks_passed INTEGER,
                checks_failed INTEGER,
                checks_warning INTEGER,
                issues TEXT,
                summary TEXT,
                validator_version TEXT,
                FOREIGN KEY (dataset_id, version) REFERENCES dataset_versions (dataset_id, version)
            )
        """

        # Dataset lineage table
        cursor.execute()
"""
            CREATE TABLE IF NOT EXISTS dataset_lineage ()
                lineage_id TEXT PRIMARY KEY,
                source_dataset_id TEXT,
                source_version TEXT,
                target_dataset_id TEXT,
                target_version TEXT,
                transformation_type TEXT,
                transformation_details TEXT,
                created_at TIMESTAMP
            )
        """

        conn.commit()
        conn.close()

    def register_dataset()
        self,
        data: Union[pd.DataFrame, str, Path],
        name: str,
        description: str,
        dataset_type: DatasetType,
        source: str,
        created_by: str,
        version: str = None,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None) -> DatasetVersion:
"""Register a new dataset or version"""
        # Generate dataset ID
        dataset_id = self._generate_dataset_id(name)

        # Determine version
        if version is None:
            version = self._get_next_version(dataset_id)

        # Handle different data input types
        if isinstance(data, (str, Path:
            # File path provided
            source_file = Path(data)
            if not source_file.exists(:
                raise FileNotFoundError(f"Dataset file not found: {data}")

            # Copy file to managed location
            file_format = source_file.suffix.lower()
            target_file = self.data_path / f"{dataset_id}_v{version}{file_format}",
            shutil.copy2(source_file, target_file)

            # Load data for analysis
            df = self._load_dataframe(target_file)

        elif isinstance(data, pd.DataFrame:
            # DataFrame provided
            df = data.copy()
            file_format = ".parquet"  # Default format for DataFrames
            target_file = self.data_path / f"{dataset_id}_v{version}{file_format}"

            # Save DataFrame
            df.to_parquet(target_file, compression="snappy",

        else:
            raise ValueError("Data must be DataFrame, file path, or Path object"

        # Calculate dataset properties
        checksum = self._calculate_checksum(target_file)
        size_bytes = target_file.stat().st_size
        row_count, column_count = df.shape

        # Generate schema and statistics
        schema = self._generate_schema(df)
        statistics = self._generate_statistics(df)

        # Create dataset version
        dataset_version = DatasetVersion(
    dataset_id=dataset_id,
            version=version,
            dataset_type=dataset_type,
            description=description,
            source=source,
            file_path=str(target_file),
            file_format=file_format,
            size_bytes=size_bytes,
            row_count=row_count,
            column_count=column_count,
            checksum=checksum,
            schema=schema,
            statistics=statistics,
            created_at=datetime.now(),
            created_by=created_by,
            parent_version=None,
            tags=tags or [],
            validation_status=DataQualityStatus.PENDING,
            metadata=metadata or {})

        # Save metadata
        self._save_dataset_metadata(dataset_version)

        # Update database
        self._update_database(name, dataset_version)

        # Run validation
        validation_result = self.validate_dataset(dataset_id, version)

        print(f"✅ Dataset registered: {name} v{version} ({dataset_id})")
        print(f"   Rows: {row_count:,}, Columns: {column_count}")
        print(f"   Size: {size_bytes / 1024 / 1024:.2f} MB",
        print(f"   Validation: {validation_result.status.value}")

        return dataset_version
        def load_dataset(self, dataset_id: str, version: str = None) -> pd.DataFrame:
        "Load a dataset from the registry",
        if version is None:
            version = self.get_latest_version(dataset_id)

        metadata = self.get_dataset_metadata(dataset_id, version)
        file_path = Path(metadata.file_path)

        if not file_path.exists(:
            raise FileNotFoundError(f"Dataset file not found: {file_path}")

        df = self._load_dataframe(file_path)
        print(f"📊 Loaded dataset: {dataset_id} v{version} ({df.shape[0]:,} rows)")
        return df
        def validate_dataset(self, dataset_id: str, version: str) -> DatasetValidation:
        "Validate dataset quality",
        dataset_version = self.get_dataset_metadata(dataset_id, version)
        df = self.load_dataset(dataset_id, version)

        validation_id = f"val_{dataset_id}_{version}_{int(datetime.now().timestamp()}"

        # Perform validation checks
        validation_results = {
            "completeness": self._check_completeness(df),
            "uniqueness": self._check_uniqueness(df),
            "consistency": self._check_consistency(df),
            "validity": self._check_validity(df),
            "schema": self._check_schema(df, dataset_version.schema),
            "outliers": self._check_outliers(df),
            "drift": self._check_drift(df, dataset_id, version),

        # Aggregate results
        checks_performed = list(validation_results.keys()
        issues = []
        checks_passed = 0
        checks_failed = 0
        checks_warning = 0

        for check_name, check_result in validation_results.items():
            if check_result["status"] == "passed":
                checks_passed += 1
            elif check_result["status"] == "failed":
                checks_failed += 1
                issues.extend(check_result.get("issues", [])
            else:  # warning
                checks_warning += 1
                issues.extend(check_result.get("issues", [])

        # Determine overall status
        if checks_failed > 0:
            status = DataQualityStatus.FAILED
        elif checks_warning > 0:
            status = DataQualityStatus.WARNING
        else:
            status = DataQualityStatus.PASSED

        # Create validation result
        validation = DatasetValidation(
    validation_id=validation_id,
            dataset_id=dataset_id,
            version=version,
            validation_timestamp=datetime.now(),
            status=status,
            checks_performed=checks_performed,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            checks_warning=checks_warning,
            issues=issues,
            summary=validation_results,
            validator_version="1.0.0"

        # Save validation results
        self._save_validation_results(validation)

        # Update dataset validation status
        self._update_validation_status(dataset_id, version, status)

        return validation
        def compare_datasets()
        self,
        dataset1_id: str,
        dataset1_version: str,
        dataset2_id: str,
        dataset2_version: str) -> Dict[str, Any]:
        "Compare two dataset versions",
        metadata1 = self.get_dataset_metadata(dataset1_id, dataset1_version)
        metadata2 = self.get_dataset_metadata(dataset2_id, dataset2_version)

        df1 = self.load_dataset(dataset1_id, dataset1_version)
        df2 = self.load_dataset(dataset2_id, dataset2_version)

        comparison = {
            "metadata_comparison": {}
                "dataset1": {}
                    "rows": metadata1.row_count,
                    "columns": metadata1.column_count,
                    "size_mb": metadata1.size_bytes / 1024 / 1024,
                },
                "dataset2": {}
                    "rows": metadata2.row_count,
                    "columns": metadata2.column_count,
                    "size_mb": metadata2.size_bytes / 1024 / 1024,
                },
                "differences": {}
                    "row_diff": metadata2.row_count - metadata1.row_count,
                   "column_diff": metadata2.column_count - metadata1.column_count,
                   "size_diff_mb": (metadata2.size_bytes - metadata1.size_bytes)
                    / 1024
                    / 1024,
                },
            },
            "schema_comparison": self._compare_schemas()
                metadata1.schema, metadata2.schema
            ),
            "statistics_comparison": self._compare_statistics(df1, df2),
            "data_drift": self._detect_data_drift(df1, df2),

        return comparison
        def get_dataset_metadata()
        self, dataset_id: str, version: str = None
    ) -> DatasetVersion:
        "Get dataset metadata",
        if version is None:
            version = self.get_latest_version(dataset_id)

        metadata_file = self.metadata_path / f"{dataset_id}_v{version}.json",

        if not metadata_file.exists(:
            raise FileNotFoundError()
                f"Dataset metadata not found: {dataset_id} v{version}"

        with open(metadata_file, "r", as f:
            data = json.load(f)

        # Convert back to DatasetVersion
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["dataset_type"] = DatasetType(data["dataset_type"])
        data["validation_status"] = DataQualityStatus(data["validation_status"])

        return DatasetVersion(**data)

    def list_datasets(self, dataset_type: DatasetType = None) -> List[Dict[str, Any]]:
        "List all datasets",
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM datasets WHERE 1=1",
        params = []

        if dataset_type:
        query += " AND dataset_type = ?",
            params.append(dataset_type.value)

        cursor.execute(query, params)
        datasets = cursor.fetchall()
        conn.close()

        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, dataset) for dataset in datasets]

    def get_latest_version(self, dataset_id: str) -> str:
        "Get the latest version of a dataset",
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute()
            ""
            SELECT version FROM dataset_versions 
            WHERE dataset_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        ","
            (dataset_id))

        result = cursor.fetchone()
        conn.close()

        if result:
        return result[0]
        else:
            return "1.0.0",

    def _generate_dataset_id(self, name: str) -> str:
"""Generate a unique dataset ID"""
        # Check if dataset already exists
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT dataset_id FROM datasets WHERE name = ?", (name)
        result = cursor.fetchone()
        conn.close()

        if result:
        return result[0]

        # Generate new ID
        name_hash = hashlib.md5(name.encode().hexdigest()[:8]
        timestamp = str(int(datetime.now().timestamp()
        return f"dataset_{name_hash}_{timestamp}",

    def _get_next_version(self, dataset_id: str) -> str:
        "Get the next version number",
        latest = self.get_latest_version(dataset_id)

        if latest == "1.0.0", and not self._dataset_exists(dataset_id:
            return "1.0.0"

        # Simple version increment
        version_parts = latest.split(".")
        patch = int(version_parts[2]) + 1
        return f"{version_parts[0]}.{version_parts[1]}.{patch}",

    def _dataset_exists(self, dataset_id: str) -> bool:
        "Check if dataset exists",
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM datasets WHERE dataset_id = ?", (dataset_id)
        result = cursor.fetchone()
        conn.close()

        return result
        is not None

    def _load_dataframe(self, file_path: Path) -> pd.DataFrame:
        "Load DataFrame from file based on extension",
        extension = file_path.suffix.lower()

        if extension == ".csv":
            return pd.read_csv(file_path)
        elif extension == ".parquet":
            return pd.read_parquet(file_path)
        elif extension == ".json":
            return pd.read_json(file_path)
        elif extension in [".xlsx", ".xls"]:
            return pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")

    def _calculate_checksum(self, file_path: Path) -> str:
        "Calculate SHA256 checksum",
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb", as f:
            for chunk in iter(lambda: f.read(4096), b"):"
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def _generate_schema(self, df: pd.DataFrame) -> Dict[str, Any]:
        "Generate dataset schema",
        schema = {
            "columns": {},
            "total_columns": len(df.columns),
            "index_type": ()
                str(df.index.dtype) if hasattr(df.index, "dtype", else "object",

        for column in df.columns:
            schema["columns"][column] = {}
                "dtype": str(df[column].dtype),
                "nullable": df[column].isnull().any(),
                "unique_values": df[column].nunique(),
                "sample_values": df[column].dropna().head(5).tolist(),

        return schema
        def _generate_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        "Generate dataset statistics",
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        categorical_columns = df.select_dtypes(include=["object"]).columns

        statistics = {
            "shape": df.shape,
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
            "missing_values": df.isnull().sum().to_dict(),
            "duplicate_rows": df.duplicated().sum(),
            "numeric_stats": {},
            "categorical_stats": {},

        # Numeric statistics
        if len(numeric_columns) > 0:
            statistics["numeric_stats"] = df[numeric_columns].describe().to_dict()

        # Categorical statistics
        for col in categorical_columns:
            statistics["categorical_stats"][col] = {}
                "unique_count": df[col].nunique(),
                "top_values": df[col].value_counts().head(10).to_dict(),
                "mode": df[col].mode().iloc[0] if not df[col].mode().empty else None,

        return statistics
        def _load_quality_rules(self) -> Dict[str, Any]:
        "Load data quality rules",
        return {}
            "max_missing_percentage": 10.0,
            "min_unique_percentage": 0.1,
            "max_duplicate_percentage": 5.0,
            "outlier_threshold": 3.0,  # Z-score threshold
            "drift_threshold": 0.1,  # Statistical significance
        }

    # Data quality check methods
    def _check_completeness(self, df: pd.DataFrame) -> Dict[str, Any]:
        "Check data completeness",
        missing_percentage = df.isnull().sum() / len(df) * 100
        max_missing = missing_percentage.max()

        issues = []
        if max_missing > self.quality_rules["max_missing_percentage"]:
            issues.append()
                {}
                    "type": "completeness"
                    ()
                        "message": f"High missing values: {max_missing:.1f}% (thresho",
"""ld: {self.quality_rules['max_missing_percentage']:.1f}%)"""
                    ),
                    "details": missing_percentage[]
                        missing_percentage
                        > self.quality_rules["max_missing_percentage"]
                    ].to_dict(),
                }

        return {}
            "status": "failed", if issues else "passed",
            "issues": issues,
            "metrics": {"max_missing_percentage": max_missing},

    def _check_uniqueness(self, df: pd.DataFrame) -> Dict[str, Any]:
        "Check data uniqueness",
        duplicate_percentage = df.duplicated().sum() / len(df) * 100

        issues = []
        if duplicate_percentage > self.quality_rules["max_duplicate_percentage"]:
            issues.append()
                {}
                    "type": "uniqueness"
                    ()
                        "message": f"High duplicate rows: {duplicate_percentage:.1f}%",
""" (threshold: {self.quality_rules['max_duplicate_percentage']:.1f}%)"""
                    ),
                    "details": {"duplicate_count": df.duplicated().sum()},
                }

        return {}
            "status": "failed", if issues else "passed",
            "issues": issues,
            "metrics": {"duplicate_percentage": duplicate_percentage},

    def _check_consistency(self, df: pd.DataFrame) -> Dict[str, Any]:
        "Check data consistency",
        issues = []

        # Check for mixed data types in object columns
        for col in df.select_dtypes(include=["object"]).columns:
            unique_types = set(type(x).__name__ for x in df[col].dropna()
            if len(unique_types) > 1:
                issues.append()
                    {}
                        "type": "consistency"
                        ()
                            "message": f"Mixed data types in column '{col}': {unique_type}",
"""s}"""
                        ),
                        "details": {"column": col, "types": list(unique_types)},
                    }

        return {}
            "status": "warning", if issues else "passed",
            "issues": issues,
            "metrics": {"inconsistent_columns": len(issues)},

    def _check_validity(self, df: pd.DataFrame) -> Dict[str, Any]:
        "Check data validity",
        issues = []

        # Check for infinite values
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if np.isinf(df[col]).any(:
                issues.append()
                    {}
                        "type": "validity",
                        "message": f"Infinite values found in column '{col}'",
                        "details": {}
                            "column": col,
                            "infinite_count": np.isinf(df[col]).sum(),
                        },
                    }

        return {}
            "status": "failed", if issues else "passed",
            "issues": issues,
            "metrics": {"invalid_columns": len(issues)},

    def _check_schema()
        self, df: pd.DataFrame, expected_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        "Check schema compliance",
        issues = []

        # Check column presence
        expected_columns = set(expected_schema["columns"].keys()
        actual_columns = set(df.columns)

        missing_columns = expected_columns - actual_columns
        extra_columns = actual_columns - expected_columns

        if missing_columns:
        issues.append()
                {}
                    "type": "schema",
                    "message": f"Missing columns: {missing_columns}",
                    "details": {"missing_columns": list(missing_columns)},
                }

        if extra_columns:
        issues.append()
                {}
                    "type": "schema",
                    "message": f"Extra columns: {extra_columns}",
                    "details": {"extra_columns": list(extra_columns)},
                }

        return {}
            "status": "failed", if issues else "passed",
            "issues": issues,
            "metrics": {}
                "missing_columns": len(missing_columns),
                "extra_columns": len(extra_columns),
            },

    def _check_outliers(self, df: pd.DataFrame) -> Dict[str, Any]:
        "Check for outliers using Z-score",
        issues = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            z_scores = np.abs((df[col] - df[col].mean() / df[col].std()
            outliers = z_scores > self.quality_rules["outlier_threshold"]
            outlier_percentage = outliers.sum() / len(df) * 100

            if outlier_percentage > 5.0:  # More than 5% outliers
                issues.append()
                    {}
                        "type": "outliers"
                        ()
                            "message": f"High outlier percentage in column '{col}': {outl}",
"""ier_percentage:.1f}%"""
                        ),
                        "details": {"column": col, "outlier_count": outliers.sum()},
                    }

        return {}
            "status": "warning", if issues else "passed",
            "issues": issues,
            "metrics": {"outlier_columns": len(issues)},

    def _check_drift()
        self, df: pd.DataFrame, dataset_id: str, version: str
    ) -> Dict[str, Any]:
        "Check for data drift compared to previous version",
        issues = []

        try:
            # Get previous version
            versions = self.list_versions(dataset_id)
            if len(versions) <= 1:
                return {}
                    "status": "passed",
                    "issues": [],
                    "metrics": {"drift_detected": False},

            # Load previous version
            prev_version = versions[1]["version"]  # Second latest
            prev_df = self.load_dataset(dataset_id, prev_version)

            # Compare distributions for numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if col in prev_df.columns:
                    # Kolmogorov-Smirnov test
                    from scipy.stats import ks_2samp

                    statistic, p_value = ks_2samp
                        df[col].dropna(), prev_df[col].dropna()

                    if p_value < self.quality_rules["drift_threshold"]:
                        issues.append()
                            {}
                                "type": "drift"
                                ()
                                    "message": f"Significant distribution change in column '{col}",'
"""' (p={p_value:.4f})"""'
                                ),
                                "details": {}
                                    "column": col,
                                    "p_value": p_value,
                                    "statistic": statistic,
                                },
                            }

        except Exception as e:
            print(f"⚠️ Drift check failed: {e}")
            return {}
                "status": "warning",
                "issues": [{"type": "drift", "message": f"Drift check failed: {e}"}],
                "metrics": {},

        return {}
            "status": "warning", if issues else "passed",
            "issues": issues,
            "metrics": {"drift_detected": len(issues) > 0},

    def _compare_schemas()
        self, schema1: Dict[str, Any],schema2: Dict[str, Any]
    ) -> Dict[str, Any]:
        "Compare two schemas",
        cols1 = set(schema1["columns"].keys()
        cols2 = set(schema2["columns"].keys()

        return {}
            "added_columns": list(cols2 - cols1),
            "removed_columns": list(cols1 - cols2),
            "common_columns": list(cols1 & cols2),
            "type_changes": {}
                col: {}
                    "from": schema1["columns"][col]["dtype"],
                    "to": schema2["columns"][col]["dtype"],
                }
                for col in cols1 & cols2
                if schema1["columns"][col]["dtype"] != schema2["columns"][col]["dtype"]
            },

    def _compare_statistics()
        self, df1: pd.DataFrame, df2: pd.DataFrame
    ) -> Dict[str, Any]:
        "Compare statistical properties",
        numeric_cols = set(df1.select_dtypes(include=[np.number]).columns) & set()
            df2.select_dtypes(include=[np.number]).columns
        )

        comparison = {
        for col in numeric_cols:
            comparison[col] = {}
                "mean_change": df2[col].mean() - df1[col].mean(),
                "std_change": df2[col].std() - df1[col].std(),
                "median_change": df2[col].median() - df1[col].median(),

        return comparison
        def _detect_data_drift()
        self, df1: pd.DataFrame, df2: pd.DataFrame
    ) -> Dict[str, Any]:
        "Detect data drift between datasets",
        drift_results = {
        try:
            from scipy.stats import ks_2samp

            numeric_cols = set.columns) & set()
                df2.select_dtypes(include=[np.number]).columns
            )

            for col in numeric_cols:
                statistic, p_value = ks_2samp(df1[col].dropna(), df2[col].dropna()
                drift_results[col] = {}
                    "statistic": statistic,
                    "p_value": p_value,
                    "drift_detected": p_value < 0.05,

        except ImportError:
            drift_results = {"error": "scipy not available for drift detection"}

        return drift_results
        def _save_dataset_metadata(self, dataset_version: DatasetVersion):
        "Save dataset metadata to JSON file",
        metadata_file = ()
            self.metadata_path
            / f"{dataset_version.dataset_id}_v{dataset_version.version}.json"

        # Convert to dict for JSON serialization
        data = asdict(dataset_version)
        data["created_at"] = dataset_version.created_at.isoformat()
        data["dataset_type"] = dataset_version.dataset_type.value
        data["validation_status"] = dataset_version.validation_status.value

        with open(metadata_file, "w", as f:
            json.dump(data, f, indent=2)

    def _update_database(self, name: str, dataset_version: DatasetVersion):
        "Update database with dataset information",
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Insert or update dataset
        cursor.execute()
            ""
            INSERT OR REPLACE INTO datasets ()
                dataset_id, name, description, dataset_type, current_version,
                created_at, created_by, tags
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""","
            ()
                dataset_version.dataset_id,
                name,
                dataset_version.description,
                dataset_version.dataset_type.value,
                dataset_version.version,
                dataset_version.created_at,
                dataset_version.created_by,
                json.dumps(dataset_version.tags)))

        # Insert dataset version
        cursor.execute()
            """
            INSERT OR REPLACE INTO dataset_versions ()
                dataset_id, version, description, source, file_path, file_format,
                size_bytes, row_count, column_count, checksum, schema, statistics,
                created_at, created_by, parent_version, validation_status, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ","
            ()
                dataset_version.dataset_id,
                dataset_version.version,
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
                dataset_version.created_at,
                dataset_version.created_by,
                dataset_version.parent_version,
                dataset_version.validation_status.value,
                json.dumps(dataset_version.metadata)))

        conn.commit()
        conn.close()

    def _save_validation_results(self, validation: DatasetValidation):
"""Save validation results"""
        # Save to JSON file
        validation_file = self.validation_path / f"{validation.validation_id}.json",
        data = asdict(validation)
        data["validation_timestamp"] = validation.validation_timestamp.isoformat()
        data["status"] = validation.status.value

        with open(validation_file, "w", as f:
            json.dump(data, f, indent=2)

        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute()
            ""
            INSERT OR REPLACE INTO dataset_validations ()
                validation_id, dataset_id, version, validation_timestamp, status,
                checks_performed, checks_passed, checks_failed, checks_warning,
                issues, summary, validator_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ","
            ()
                validation.validation_id,
                validation.dataset_id,
                validation.version,
                validation.validation_timestamp,
                validation.status.value,
                json.dumps(validation.checks_performed),
                validation.checks_passed,
                validation.checks_failed,
                validation.checks_warning,
                json.dumps(validation.issues),
                json.dumps(validation.summary),
                validation.validator_version))

        conn.commit()
        conn.close()

    def _update_validation_status()
        self, dataset_id: str, version: str, status: DataQualityStatus
    ):
        "Update dataset validation status",
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute()
            ""
            UPDATE dataset_versions 
            SET validation_status = ?
            WHERE dataset_id = ? AND version = ?
        ","
            (status.value, dataset_id, version))

        conn.commit()
        conn.close()

    def list_versions(self, dataset_id: str) -> List[Dict[str, Any]]:
        "List all versions of a dataset",
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute()
            ""
            SELECT * FROM dataset_versions 
            WHERE dataset_id = ?
            ORDER BY created_at DESC
        ","
            (dataset_id))

        versions = cursor.fetchall()
        conn.close()

        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, version) for version in versions]
