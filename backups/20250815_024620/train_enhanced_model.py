#!/usr/bin/env python3
"""
Enhanced ML Model Training Script
Train the anomaly detection model with real AWS data and enhanced parameters
"""

import sys
import os
import logging
from datetime import datetime, timedelta
import pandas as pd

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ml_models.anomaly_detector import AnomalyDetector
from ml_models.data_processor import DataProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/enhanced_training.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


def main():
    """Main function to train the enhanced ML model."""
    print("🚀 Smart CloudOps AI - Enhanced ML Model Training")
    print("=" * 60)
    print("🎯 Training with real AWS data and enhanced parameters")
    print("📊 Multiple iterations for optimal performance")
    print("🔍 Stricter quality thresholds for production readiness")
    print()

    try:
        # Initialize components
        logger.info("Initializing enhanced anomaly detection system...")
        detector = AnomalyDetector("ml_models/config.yaml")
        processor = DataProcessor("ml_models/config.yaml")

        # Extract real data from AWS Prometheus
        logger.info("Extracting real metrics data from AWS Prometheus...")
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)  # Get 24 hours of data

        data = processor.extract_metrics(start_time, end_time)

        if data is None or len(data) == 0:
            logger.error("No data extracted from Prometheus")
            return False

        logger.info(f"Extracted {len(data)} data points from AWS infrastructure")
        logger.info(f"Data columns: {list(data.columns)}")
        logger.info(f"Data shape: {data.shape}")

        # Check data quality
        min_data_points = 100
        if len(data) < min_data_points:
            logger.warning(
                f"Limited data points ({len(data)}), but proceeding with training"
            )

        # Train the enhanced model
        logger.info("Starting enhanced model training...")
        training_result = detector.train_model(data)

        if training_result["status"] == "success":
            print("\n✅ Enhanced Model Training Completed Successfully!")
            print("=" * 50)
            print(f"📊 F1 Score: {training_result['f1_score']:.3f}")
            print(f"🎯 Precision: {training_result['precision']:.3f}")
            print(f"🔄 Recall: {training_result['recall']:.3f}")
            print(f"📈 Total Samples: {training_result['total_samples']}")
            print(f"🚨 Anomaly Samples: {training_result['anomaly_samples']}")
            print(
                f"🔄 Iterations Trained: {training_result.get('iterations_trained', 1)}"
            )
            print(
                f"🏆 Model Quality: {training_result.get('model_quality', 'standard')}"
            )

            # Save the enhanced model
            logger.info("Saving enhanced model...")
            if detector.save_model():
                print("💾 Enhanced model saved successfully!")

                # Get model info
                model_info = detector.get_model_info()
                print(f"\n📋 Model Information:")
                print(f"   Type: {model_info['model_type']}")
                print(f"   Features: {model_info['feature_count']}")
                print(f"   Feature Columns: {model_info['feature_columns']}")

                # Test inference
                logger.info("Testing model inference...")
                test_result = detector.detect_anomalies(data.head(10))
                print(f"\n🧪 Inference Test:")
                print(f"   Test samples: {len(test_result)}")
                print(
                    f"   Anomalies detected: {sum(1 for r in test_result if r['is_anomaly'])}"
                )

                print("\n🎉 Enhanced ML Model is ready for production!")
                print("🔗 Ready for Phase 4: Auto-Remediation Logic")

                return True
            else:
                logger.error("Failed to save enhanced model")
                return False
        else:
            logger.error(
                f"Enhanced model training failed: {training_result.get('reason', 'Unknown error')}"
            )
            return False

    except Exception as e:
        logger.error(f"Error in enhanced model training: {e}")
        print(f"\n❌ Enhanced model training failed: {e}")
        return False


if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    success = main()
    if success:
        print("\n🚀 Ready to proceed to Phase 4!")
    else:
        print("\n❌ Enhanced training failed. Please check logs and try again.")
        sys.exit(1)
