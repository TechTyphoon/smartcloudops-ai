#!/usr/bin/env python3
"""
Data Processor for ML Anomaly Detection
Handles Prometheus data extraction, preprocessing, and feature engineering
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import requests
import yaml
from prometheus_api_client import PrometheusConnect

logger = logging.getLogger(__name__)


class DataProcessor:
    """Handles data extraction and preprocessing for anomaly detection."""

    def __init__(self, config_path: str = "ml_models/config.yaml"):
        """Initialize data processor with configuration."""
        self.config = self._load_config(config_path)
        # Allow environment override for Prometheus URL (e.g., compose, AWS)
        self.prometheus_url = os.getenv(
            "PROMETHEUS_URL", self.config["data"]["prometheus_url"]
        )
        self.features = self.config["features"]
        # Configure HTTP timeout for Prometheus requests (seconds)
        self.timeout = int(self.config.get("data", {}).get("timeout", 30))

        try:
            self.prom = PrometheusConnect(url=self.prometheus_url, disable_ssl=True)
            logger.info(f"Connected to Prometheus at {self.prometheus_url}")
        except Exception as e:
            logger.warning(f"Could not connect to Prometheus: {e}")
            self.prom = None

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, "r") as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """Return default configuration if config file is missing."""
        return {
            "data": {
                "prometheus_url": "http://localhost:9090",
                "lookback_hours": 168,
                "feature_window": 60,
                "timeout": 30,
            },
            "features": [
                "cpu_usage_avg",
                "cpu_usage_max",
                "memory_usage_pct",
                "disk_usage_pct",
                "network_bytes_total",
                "request_rate",
            ],
        }

    def extract_metrics(self, start_time, end_time):
        """Extract metrics from Prometheus."""
        try:
            if not self.prom:
                raise RuntimeError(
                    "Prometheus not available - real metrics data required"
                )

            # Query Prometheus for metrics
            query = f"""
            rate(node_cpu_seconds_total{{mode!="idle"}}[5m]) * 100
            """

            response = requests.get(
                f"{self.prometheus_url}/api/v1/query_range",
                params={
                    "query": query,
                    "start": start_time.timestamp(),
                    "end": end_time.timestamp(),
                    "step": "60s",
                },
                timeout=self.timeout,
            )

            if response.status_code != 200:
                raise RuntimeError(f"Prometheus query failed: {response.status_code}")

            data = response.json()
            if data["status"] != "success":
                raise RuntimeError(
                    f"Prometheus query error: {data.get('error', 'Unknown error')}"
                )

            # Process the data
            result_data = data["data"]["result"]
            if not result_data:
                raise RuntimeError("No metrics data available from Prometheus")

            # Convert to DataFrame
            df = self._process_prometheus_data(result_data, start_time, end_time)

            if df.empty:
                raise RuntimeError("No valid metrics data extracted from Prometheus")

            logger.info(f"Extracted {len(df)} data points from Prometheus")
            return df

        except Exception as e:
            logger.error(f"Failed to extract metrics from Prometheus: {e}")
            raise RuntimeError(f"Real metrics data extraction failed: {e}")

    def _generate_synthetic_data(
        self, start_time: datetime, end_time: datetime
    ) -> pd.DataFrame:
        """Generate synthetic data for development/testing when Prometheus is not available."""
        logger.info("Generating synthetic metrics data for development")

        # Generate time series
        time_range = pd.date_range(start=start_time, end=end_time, freq="1min")

        # Generate realistic synthetic data
        np.random.seed(42)
        data = {
            "timestamp": time_range,
            "cpu_usage_avg": np.random.normal(30, 10, len(time_range)).clip(0, 100),
            "cpu_usage_max": np.random.normal(50, 15, len(time_range)).clip(0, 100),
            "memory_usage_pct": np.random.normal(60, 15, len(time_range)).clip(0, 100),
            "disk_usage_pct": np.random.normal(45, 10, len(time_range)).clip(0, 100),
            "network_bytes_total": np.random.exponential(1000, len(time_range)),
            "request_rate": np.random.poisson(10, len(time_range)),
            "response_time_p95": np.random.exponential(0.1, len(time_range)),
        }

        # Add some anomalies
        anomaly_indices = np.random.choice(
            len(time_range), size=len(time_range) // 20, replace=False
        )
        for idx in anomaly_indices:
            data["cpu_usage_avg"][idx] *= 2.5
            data["memory_usage_pct"][idx] *= 1.8
            data["response_time_p95"][idx] *= 3.0

        df = pd.DataFrame(data)
        df.set_index("timestamp", inplace=True)
        logger.info(f"Generated synthetic data shape: {df.shape}")
        return df

    def _process_prometheus_data(self, result_data, start_time, end_time):
        """Process Prometheus query results into a DataFrame."""
        try:
            # Extract data from Prometheus response
            df_data = {}
            timestamps = set()

            for series in result_data:
                metric_name = series["metric"].get("__name__", "unknown_metric")
                for timestamp, value in series["values"]:
                    timestamps.add(timestamp)
                    if timestamp not in df_data:
                        df_data[timestamp] = {}
                    df_data[timestamp][metric_name] = float(value)

            if not df_data:
                return pd.DataFrame()

            # Create DataFrame
            df = pd.DataFrame.from_dict(df_data, orient="index")
            df.index = pd.to_datetime(df.index, unit="s")
            df = df.sort_index()

            # Fill missing values
            df = df.ffill().fillna(0)

            # Ensure we have the required columns for ML
            required_columns = ["cpu_usage_avg", "memory_usage_pct", "disk_usage_pct"]
            for col in required_columns:
                if col not in df.columns:
                    # Use available metrics or reasonable defaults
                    if "node_cpu_seconds_total" in df.columns:
                        df[col] = df["node_cpu_seconds_total"]
                    else:
                        df[col] = 50.0  # Default value

            return df

        except Exception as e:
            logger.error(f"Error processing Prometheus data: {e}")
            return pd.DataFrame()

    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess and engineer features from raw metrics data."""
        try:
            # Create a copy to avoid modifying original data
            processed_df = df.copy()

            # Handle missing values
            processed_df = processed_df.ffill().bfill()

            # Add time-based features only if index is datetime
            if isinstance(processed_df.index, pd.DatetimeIndex):
                processed_df["hour"] = processed_df.index.hour
                processed_df["day_of_week"] = processed_df.index.dayofweek
                processed_df["is_weekend"] = (
                    processed_df["day_of_week"].isin([5, 6]).astype(int)
                )

            # Add rolling statistics (only if we have enough data)
            window_size = (
                min(10, len(processed_df) // 2) if len(processed_df) > 1 else 1
            )
            for col in ["cpu_usage_avg", "memory_usage_pct", "disk_usage_pct"]:
                if col in processed_df.columns and len(processed_df) > window_size:
                    processed_df[f"{col}_rolling_mean"] = (
                        processed_df[col]
                        .rolling(window=window_size, min_periods=1)
                        .mean()
                    )
                    processed_df[f"{col}_rolling_std"] = (
                        processed_df[col]
                        .rolling(window=window_size, min_periods=1)
                        .std()
                    )
                    processed_df[f"{col}_rolling_max"] = (
                        processed_df[col]
                        .rolling(window=window_size, min_periods=1)
                        .max()
                    )

            # Add rate of change features
            for col in ["cpu_usage_avg", "memory_usage_pct"]:
                if col in processed_df.columns:
                    processed_df[f"{col}_rate"] = processed_df[col].diff().fillna(0)

            # Remove rows with NaN values after feature engineering
            processed_df = processed_df.dropna()

            logger.info(f"Preprocessed data shape: {processed_df.shape}")
            return processed_df

        except Exception as e:
            logger.error(f"Error in preprocess_data: {e}")
            return df

    def validate_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate data quality and return issues."""
        issues = []

        # Check for minimum data points (reduced for real data scenarios)
        min_points = self.config.get("training", {}).get("min_data_points", 10)
        if len(df) < min_points:
            issues.append(f"Insufficient data points: {len(df)} < {min_points}")

        # Check for missing values
        missing_cols = df.columns[df.isnull().any()].tolist()
        if len(missing_cols) > 0:
            issues.append(f"Missing values in columns: {missing_cols}")

        # Check for infinite values
        numeric_df = df.select_dtypes(include=[np.number])
        if not numeric_df.empty:
            inf_cols = numeric_df.columns[np.isinf(numeric_df).any()].tolist()
            if len(inf_cols) > 0:
                issues.append(f"Infinite values in columns: {inf_cols}")

        # Check data types
        non_numeric_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
        if non_numeric_cols:
            issues.append(f"Non-numeric columns found: {non_numeric_cols}")

        is_valid = len(issues) == 0
        return is_valid, issues

    def save_data(self, df: pd.DataFrame, filename: str) -> bool:
        """Save processed data to CSV file."""
        try:
            filepath = os.path.join("ml_models", "data", filename)
            df.to_csv(filepath)
            logger.info(f"Data saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            return False

    def load_data(self, filename: str) -> Optional[pd.DataFrame]:
        """Load data from CSV file."""
        try:
            filepath = os.path.join("ml_models", "data", filename)
            df = pd.read_csv(filepath, index_col=0, parse_dates=True)
            logger.info(f"Data loaded from {filepath}")
            return df
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return None
