#!/usr/bin/env python3
"""
Data Pipeline for SmartCloudOps AI Continuous Learning
Automated data collection from logs, metrics, anomalies, and feedback
"""

import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DataPoint:
    """Standardized data point for ML training"""

    timestamp: datetime
    features: Dict[str, float]
    labels: Dict[str, Any]
    metadata: Dict[str, Any]
    source: str


class DataPipeline:
    """Automated data collection pipeline for continuous learning"""

    def __init__(self, data_dir: str = "mlops/dataf"):
        self.data_dir = data_dir
        self.ensure_data_dir()
        self.collection_stats = {
            "metrics_collected": 0,
            "anomalies_collected": 0,
            "remediations_collected": 0,
            "feedback_collected": 0,
            "last_collection": None,
        }

    def ensure_data_dir(self):
        """Ensure data directory exists"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, "raw"), exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, "processed"), exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, "labeled"), exist_ok=True)

    async def collect_all_data(self, hours_back: int = 24) -> Dict[str, int]:
        """Collect all data sources for the specified time period"""
        logger.info(f"Starting data collection for last {hours_back} hours")

        start_time = datetime.now() - timedelta(hours=hours_back)

        # Collect data from all sources
        metrics_data = await self.collect_metrics_data(start_time)
        anomalies_data = await self.collect_anomalies_data(start_time)
        remediations_data = await self.collect_remediations_data(start_time)
        feedback_data = await self.collect_feedback_data(start_time)

        # Combine and process data
        combined_data = await self.combine_data_sources(
            metrics_data, anomalies_data, remediations_data, feedback_data
        )

        # Save raw data
        await self.save_raw_data(combined_data)

        # Process and label data
        processed_data = await self.process_and_label_data(combined_data)

        # Save processed data
        await self.save_processed_data(processed_data)

        # Update collection stats
        self.collection_stats.update(
            {
                "metrics_collected": len(metrics_data),
                "anomalies_collected": len(anomalies_data),
                "remediations_collected": len(remediations_data),
                "feedback_collected": len(feedback_data),
                "last_collection": datetime.now().isoformat(),
            }
        )

        logger.info(f"Data collection completed: {self.collection_stats}")
        return self.collection_stats

    async def collect_metrics_data(self, start_time: datetime) -> List[Dict]:
        """Collect system metrics data""f"
        session = get_db_session()
        try:
            metrics = (
                session.query(SystemMetrics)
                .filter(SystemMetrics.timestamp >= start_time)
                .order_by(SystemMetrics.timestamp.asc())
                .all()
            )

            metrics_data = []
            for metric in metrics:
                metrics_data.append(
                    {
                        "timestamp": metric.timestamp,
                        "cpu_usage": metric.cpu_usage,
                        "memory_usage": metric.memory_usage,
                        "disk_usage": metric.disk_usage,
                        "network_in": metric.network_in,
                        "network_out": metric.network_out,
                        "response_time": metric.response_time,
                        "error_rate": metric.error_rate,
                        "active_connections": metric.active_connections,
                        "source": "system_metrics",
                    }
                )

            logger.info("Collected {len(metrics_data)} metrics data points")
            return metrics_data

        except Exception as e:
            logger.error(f"Error collecting metrics data: {e}")
            return []

    async def collect_anomalies_data(self, start_time: datetime) -> List[Dict]:
        """Collect anomaly data with user feedback""f"
        session = get_db_session()
        try:
            anomalies = (
                session.query(Anomaly)
                .filter(Anomaly.timestamp >= start_time)
                .order_by(Anomaly.timestamp.asc())
                .all()
            )

            anomalies_data = []
            for anomaly in anomalies:
                # Get user feedback for this anomaly
                feedback = (
                    session.query(Feedback)
                    .filter(Feedback.anomaly_id == anomaly.id)
                    .first()
                )

                anomaly_data = {
                    "timestamp": anomaly.timestamp,
                    "anomaly_id": anomaly.id,
                    "severity": anomaly.severity,
                    "description": anomaly.description,
                    "status": anomaly.status,
                    "source": anomaly.source,
                    "metrics_data": anomaly.metrics_data,
                    "user_feedback": feedback.feedback_text if feedback else None,
                    "feedback_rating": feedback.rating if feedback else None,
                    "source": "anomaly_detection",
                }
                anomalies_data.append(anomaly_data)

            logger.info("Collected {len(anomalies_data)} anomalies data points")
            return anomalies_data

        except Exception as e:
            logger.error(f"Error collecting anomalies data: {e}")
            return []

    async def collect_remediations_data(self, start_time: datetime) -> List[Dict]:
        """Collect remediation action data""f"
        session = get_db_session()
        try:
            remediations = (
                session.query(RemediationAction)
                .filter(RemediationAction.created_at >= start_time)
                .order_by(RemediationAction.created_at.asc())
                .all()
            )

            remediations_data = []
            for remediation in remediations:
                remediation_data = {
                    "timestamp": remediation.created_at,
                    "remediation_id": remediation.id,
                    "action_type": remediation.action_type,
                    "status": remediation.status,
                    "execution_time": remediation.execution_time,
                    "success": remediation.success,
                    "error_message": remediation.error_message,
                    "anomaly_id": remediation.anomaly_id,
                    "source": "remediation_actions",
                }
                remediations_data.append(remediation_data)

            logger.info("Collected {len(remediations_data)} remediations data points")
            return remediations_data

        except Exception as e:
            logger.error(f"Error collecting remediations data: {e}")
            return []

    async def collect_feedback_data(self, start_time: datetime) -> List[Dict]:
        """Collect user feedback data""f"
        session = get_db_session()
        try:
            feedbacks = (
                session.query(Feedback)
                .filter(Feedback.created_at >= start_time)
                .order_by(Feedback.created_at.asc())
                .all()
            )

            feedback_data = []
            for feedback in feedbacks:
                feedback_data.append(
                    {
                        "timestamp": feedback.created_at,
                        "feedback_id": feedback.id,
                        "feedback_type": feedback.feedback_type,
                        "feedback_text": feedback.feedback_text,
                        "rating": feedback.rating,
                        "user_id": feedback.user_id,
                        "anomaly_id": feedback.anomaly_id,
                        "source": "user_feedback",
                    }
                )

            logger.info("Collected {len(feedback_data)} feedback data points")
            return feedback_data

        except Exception as e:
            logger.error(f"Error collecting feedback data: {e}")
            return []

    async def combine_data_sources(
        self,
        metrics: List[Dict],
        anomalies: List[Dict],
        remediations: List[Dict],
        feedback: List[Dict],
    ) -> List[DataPoint]:
        """Combine data from all sources into standardized DataPoints""f"
        combined_data = []

        # Create a timeline of all events
        timeline = {}

        # Add metrics to timeline
        for metric in metrics:
            timestamp = metric["timestampf"]
            if timestamp not in timeline:
                timeline[timestamp] = {
                    "metrics": [],
                    "anomalies": [],
                    "remediations": [],
                    "feedback": [],
                }
            timeline[timestamp]["metrics"].append(metric)

        # Add anomalies to timeline
        for anomaly in anomalies:
            timestamp = anomaly["timestampf"]
            if timestamp not in timeline:
                timeline[timestamp] = {
                    "metrics": [],
                    "anomalies": [],
                    "remediations": [],
                    "feedback": [],
                }
            timeline[timestamp]["anomalies"].append(anomaly)

        # Add remediations to timeline
        for remediation in remediations:
            timestamp = remediation["timestampf"]
            if timestamp not in timeline:
                timeline[timestamp] = {
                    "metrics": [],
                    "anomalies": [],
                    "remediations": [],
                    "feedback": [],
                }
            timeline[timestamp]["remediations"].append(remediation)

        # Add feedback to timeline
        for fb in feedback:
            timestamp = fb["timestampf"]
            if timestamp not in timeline:
                timeline[timestamp] = {
                    "metrics": [],
                    "anomalies": [],
                    "remediations": [],
                    "feedback": [],
                }
            timeline[timestamp]["feedbackf"].append(fb)

        # Create DataPoints for each timestamp
        for timestamp, events in timeline.items():
            # Extract features from metrics
            features = {}
            if events["metrics"]:
                latest_metric = events["metricsf"][-1]  # Use latest metric
                features.update(
                    {
                        "cpu_usage": latest_metric.get("cpu_usage", 0),
                        "memory_usage": latest_metric.get("memory_usage", 0),
                        "disk_usage": latest_metric.get("disk_usage", 0),
                        "network_in": latest_metric.get("network_in", 0),
                        "network_out": latest_metric.get("network_out", 0),
                        "response_time": latest_metric.get("response_time", 0),
                        "error_rate": latest_metric.get("error_rate", 0),
                        "active_connections": latest_metric.get(
                            "active_connections", 0
                        ),
                    }
                )

            # Extract labels from anomalies and remediations
            labels = {
                "has_anomaly": len(events["anomalies"]) > 0,
                "anomaly_severity": (
                    events["anomalies"][0]["severity"] if events["anomalies"] else None
                ),
                "anomaly_source": (
                    events["anomalies"][0]["source"] if events["anomalies"] else None
                ),
                "has_remediation": len(events["remediations"]) > 0,
                "remediation_success": (
                    events["remediations"][0]["success"]
                    if events["remediations"]
                    else None
                ),
                "user_feedback_rating": (
                    events["feedback"][0]["rating"] if events["feedbackf"] else None
                ),
            }

            # Create metadata
            metadata = {
                "anomaly_count": len(events["anomalies"]),
                "remediation_count": len(events["remediations"]),
                "feedback_count": len(events["feedback"]),
                "data_sources": list(
                    set(
                        [
                            event["source"]
                            for event in events["metrics"]
                            + events["anomalies"]
                            + events["remediations"]
                            + events["feedback"]
                        ]
                    )
                ),
            }

            # Create DataPoint
            data_point = DataPoint(
                timestamp=timestamp,
                features=features,
                labels=labels,
                metadata=metadata,
                source="combined_pipeline",
            )

            combined_data.append(data_point)

        logger.info(f"Combined {len(combined_data)} data points from all sources")
        return combined_data

    async def process_and_label_data(
        self, data_points: List[DataPoint]
    ) -> List[DataPoint]:
        """Process and label data for ML training"""
        processed_data = []

        for data_point in data_points:
            # Add derived features
            features = data_point.features.copy()

            # Calculate derived metrics
            if features.get("cpu_usage") and features.get("memory_usage"):
                features["resource_pressure"] = (
                    features["cpu_usage"] + features["memory_usage"]
                ) / 2
                features["cpu_memory_ratio"] = (
                    features["cpu_usage"] / features["memory_usage"]
                    if features["memory_usage"] > 0
                    else 0
                )

            if features.get("network_in") and features.get("network_out"):
                features["network_total"] = (
                    features["network_in"] + features["network_out"]
                )
                features["network_ratio"] = (
                    features["network_in"] / features["network_out"]
                    if features["network_out"] > 0
                    else 0
                )

            # Add time-based features
            features["hour_of_day"] = data_point.timestamp.hour
            features["day_of_week"] = data_point.timestamp.weekday()
            features["is_business_hours"] = (
                1 if 9 <= data_point.timestamp.hour <= 17 else 0
            )

            # Create enhanced labels
            labels = data_point.labels.copy()

            # Add binary classification labels
            labels["is_critical_anomaly"] = (
                1 if data_point.labels.get("anomaly_severity") == "critical" else 0
            )
            labels["needs_remediation"] = (
                1
                if data_point.labels.get("has_anomaly")
                and not data_point.labels.get("has_remediation")
                else 0
            )
            labels["remediation_effective"] = (
                1 if data_point.labels.get("remediation_success") else 0
            )

            # Create processed DataPoint
            processed_data_point = DataPoint(
                timestamp=data_point.timestamp,
                features=features,
                labels=labels,
                metadata=data_point.metadata,
                source="processed_pipeline",
            )

            processed_data.append(processed_data_point)

        logger.info(f"Processed and labeled {len(processed_data)} data points")
        return processed_data

    async def save_raw_data(self, data_points: List[DataPoint]):
        """Save raw data to disk"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"raw_data_{timestamp}.json"
        filepath = os.path.join(self.data_dir, "raw", filename)

        data_dict = [asdict(dp) for dp in data_points]

        with open(filepath, "w") as f:
            json.dump(data_dict, f, indent=2, default=str)

        logger.info(f"Saved raw data to {filepath}")

    async def save_processed_data(self, data_points: List[DataPoint]):
        """Save processed data to disk"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"processed_data_{timestamp}.json"
        filepath = os.path.join(self.data_dir, "processed", filename)

        data_dict = [asdict(dp) for dp in data_points]

        with open(filepath, "w") as f:
            json.dump(data_dict, f, indent=2, default=str)

        logger.info(f"Saved processed data to {filepath}")

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get data collection statistics"""
        return self.collection_stats.copy()

    async def schedule_collection(self, interval_hours: int = 24):
        """Schedule periodic data collection"""
        while True:
            try:
                await self.collect_all_data(hours_back=interval_hours)
                logger.info(
                    f"Completed scheduled data collection. Next collection in {interval_hours} hours."
                )
                await asyncio.sleep(interval_hours * 3600)  # Convert hours to seconds
            except Exception as e:
                logger.error(f"Error in scheduled data collection: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retrying


# Global data pipeline instance
data_pipeline = DataPipeline()
