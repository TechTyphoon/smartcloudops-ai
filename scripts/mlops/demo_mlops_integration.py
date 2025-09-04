#!/usr/bin/env python3
"""
MLOps Integration Demo - Complete end-to-end ML lifecycle demonstration
"""

import os
import sys

import numpy as np
import pandas as pd

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "app"))


def main():
    """Demonstrate complete MLOps workflow"""

    print("🤖 SmartCloudOps AI - MLOps Integration Demo")
    print("=" * 50)

    # Initialize MLOps components
    print("\n1. 🔧 Initializing MLOps Framework...")

    from app.mlops.dataset_manager import DatasetManager, DatasetType
    from app.mlops.experiment_tracker import ExperimentTracker
    from app.mlops.model_monitor import ModelMonitor
    from app.mlops.model_registry import ModelRegistry
    from app.mlops.reproducibility import ReproducibilityManager
    from app.mlops.training_pipeline import TrainingPipeline

    # Initialize components
    model_registry = ModelRegistry()
    dataset_manager = DatasetManager()
    experiment_tracker = ExperimentTracker()
    training_pipeline = TrainingPipeline(
        model_registry=model_registry,
        dataset_manager=dataset_manager,
        experiment_tracker=experiment_tracker,
    )
    model_monitor = ModelMonitor(model_registry=model_registry)
    reproducibility_manager = ReproducibilityManager()

    print("✅ MLOps framework initialized")

    # Step 2: Create environment snapshot
    print("\n2. 📸 Creating Environment Snapshot...")

    snapshot = reproducibility_manager.create_snapshot(
        name="mlops_demo_environment",
        description="Environment snapshot for MLOps demo",
        created_by="demo_script",
    )

    print(f"✅ Environment snapshot created: {snapshot.snapshot_id}")

    # Step 3: Create and register sample dataset
    print("\n3. 📊 Creating Sample Dataset...")

    # Create synthetic anomaly detection dataset
    np.random.seed(42)
    n_samples = 1000
    n_features = 5

    # Normal data
    normal_data = np.random.normal(0, 1, (n_samples * 9 // 10, n_features))

    # Anomalous data
    anomalous_data = np.random.normal(3, 1, (n_samples // 10, n_features))

    # Combine data
    X = np.vstack([normal_data, anomalous_data])
    y = np.hstack([np.zeros(len(normal_data)), np.ones(len(anomalous_data))])

    # Create DataFrame
    feature_names = [f"feature_{i}" for i in range(n_features)]
    df = pd.DataFrame(X, columns=feature_names)
    df["target"] = y

    # Register dataset
    dataset_version = dataset_manager.register_dataset(
        data=df,
        name="anomaly_detection_demo",
        description="Synthetic dataset for anomaly detection demo",
        dataset_type=DatasetType.TRAINING,
        source="synthetic_generation",
        created_by="demo_script",
        tags=["synthetic", "anomaly_detection", "demo"],
    )

    print(f"✅ Dataset registered: {dataset_version.dataset_id}")
    print(
        f"   Rows: {dataset_version.row_count}, Columns: {dataset_version.column_count}"
    )
    print(f"   Validation Status: {dataset_version.validation_status.value}")

    # Step 4: Create experiment and run training
    print("\n4. 🧪 Running ML Experiment...")

    # Create experiment
    experiment = experiment_tracker.create_experiment(
        name="anomaly_detection_demo",
        description="Demo experiment for anomaly detection",
        objective="Train and validate anomaly detection model",
        target_metric="validation_accuracy",
        maximize_metric=True,
        created_by="demo_script",
    )

    print(f"✅ Experiment created: {experiment.experiment_id}")

    # Create training configuration
    training_config = training_pipeline.create_training_config(
        name="isolation_forest_demo",
        description="Isolation Forest for anomaly detection demo",
        algorithm="sklearn_isolation_forest",
        framework="scikit-learn",
        hyperparameters={
            "contamination": 0.1,
            "n_estimators": 100,
            "feature_columns": feature_names,
        },
        dataset_config={
            "dataset_id": dataset_version.dataset_id,
            "version": dataset_version.version,
        },
        validation_config={
            "required_metrics": ["validation_accuracy"],
            "metric_thresholds": {"validation_accuracy": 0.8},
        },
        created_by="demo_script",
    )

    print(f"✅ Training config created: {training_config.config_id}")

    # Submit and run training job
    training_job = training_pipeline.submit_training_job(
        config_id=training_config.config_id,
        job_name="demo_training_run",
        seed=42,
        experiment_name=experiment.name,
    )

    print(f"✅ Training job submitted: {training_job.job_id}")

    # Execute training
    print("   🏃 Running training...")
    completed_job = training_pipeline.run_training_job(training_job.job_id)

    if completed_job.status.value == "completed":
        print(f"✅ Training completed successfully!")
        print(f"   Metrics: {completed_job.metrics}")
        print(f"   Model: {completed_job.output_model_path}")
    else:
        print(f"❌ Training failed: {completed_job.error_message}")
        return

    # Step 5: Get registered model
    print("\n5. 📦 Retrieving Registered Model...")

    models = model_registry.list_models()
    if models:
        latest_model = models[0]  # Get the latest model
        print(f"✅ Found registered model: {latest_model['name']}")

        # Load model metadata
        model_metadata = model_registry.get_model_metadata(latest_model["model_id"])
        print(f"   Version: {model_metadata.version}")
        print(f"   Algorithm: {model_metadata.algorithm}")
        print(f"   Status: {model_metadata.status.value}")
        print(f"   Metrics: {model_metadata.metrics}")

        # Start monitoring the model
        print("\n6. 📊 Starting Model Monitoring...")

        model_monitor.start_monitoring(
            model_id=latest_model["model_id"],
            model_version=model_metadata.version,
            monitoring_interval=60,  # 1 minute for demo
        )

        # Simulate some predictions for monitoring
        print("   🔮 Simulating predictions...")

        for i in range(10):
            # Create sample input
            input_features = {
                f"feature_{j}": float(np.random.normal(0, 1)) for j in range(n_features)
            }

            # Simulate prediction (normally would use actual model)
            prediction = {
                "anomaly_score": float(np.random.random()),
                "is_anomaly": bool(np.random.random() > 0.9),
            }
            confidence = float(np.random.uniform(0.7, 0.99))
            prediction_time = float(np.random.uniform(10, 100))  # ms

            # Log prediction
            model_monitor.log_prediction(
                model_id=latest_model["model_id"],
                model_version=model_metadata.version,
                input_features=input_features,
                prediction=prediction,
                confidence=confidence,
                prediction_time_ms=prediction_time,
            )

        print("✅ Predictions logged for monitoring")

        # Compute metrics
        metrics = model_monitor.compute_metrics(
            latest_model["model_id"], model_metadata.version, time_window_hours=1
        )

        print(f"   Metrics computed:")
        print(f"   - Predictions: {metrics.prediction_count}")
        print(f"   - Avg Response Time: {metrics.avg_prediction_time_ms:.1f}ms")
        print(f"   - Error Rate: {metrics.error_rate:.1%}")
        print(f"   - Data Quality: {metrics.data_quality_score:.2f}")

        # Check for alerts
        alerts = model_monitor.check_alerts(metrics)
        if alerts:
            print(f"   ⚠️ {len(alerts)} alerts generated")
            for alert in alerts:
                print(f"     - {alert.severity.value}: {alert.message}")
        else:
            print("   ✅ No alerts - model performing well")

        # Get model health
        health = model_monitor.get_model_health(
            latest_model["model_id"], model_metadata.version
        )
        print(f"   Health Status: {health.value}")

        # Stop monitoring
        model_monitor.stop_monitoring(latest_model["model_id"], model_metadata.version)

    # Step 7: Reproducibility check
    print("\n7. 🔄 Testing Reproducibility...")

    # Create current environment snapshot
    current_snapshot = reproducibility_manager.create_snapshot(
        name="current_environment_check",
        description="Current environment for reproducibility check",
    )

    # Compare environments
    report = reproducibility_manager.compare_environments(
        target_snapshot_id=snapshot.snapshot_id,
        current_snapshot_id=current_snapshot.snapshot_id,
    )

    print(f"✅ Reproducibility report generated:")
    print(f"   Reproducible: {'✅ Yes' if report.is_reproducible else '❌ No'}")
    print(f"   Compatibility Score: {report.compatibility_score:.1%}")
    print(f"   Risk Level: {report.risk_level}")

    if report.recommendations:
        print("   Recommendations:")
        for rec in report.recommendations[:3]:  # Show first 3
            print(f"     - {rec}")

    # Step 8: Export reproducibility artifacts
    print("\n8. 📤 Exporting Reproducibility Artifacts...")

    # Export requirements
    requirements_file = reproducibility_manager.export_requirements(
        snapshot.snapshot_id, format="pip"
    )
    print(f"✅ Requirements exported: {requirements_file}")

    # Step 9: Summary
    print("\n9. 📋 MLOps Demo Summary")
    print("=" * 30)

    # List all components
    print("✅ Components Demonstrated:")
    print("   - Model Registry: Model versioning and lifecycle")
    print("   - Dataset Manager: Data versioning and validation")
    print("   - Experiment Tracker: Experiment management")
    print("   - Training Pipeline: Automated training")
    print("   - Model Monitor: Performance monitoring")
    print("   - Reproducibility Manager: Environment tracking")

    print("\n✅ Demo Data Created:")
    datasets = dataset_manager.list_datasets()
    print(f"   - Datasets: {len(datasets)}")

    models = model_registry.list_models()
    print(f"   - Models: {len(models)}")

    experiments = experiment_tracker.list_experiments()
    print(f"   - Experiments: {len(experiments)}")

    snapshots = reproducibility_manager.list_snapshots()
    print(f"   - Environment Snapshots: {len(snapshots)}")

    configs = training_pipeline.list_training_configs()
    print(f"   - Training Configs: {len(configs)}")

    jobs = training_pipeline.list_training_jobs()
    print(f"   - Training Jobs: {len(jobs)}")

    print("\n🎉 MLOps Integration Demo Complete!")
    print("    All components working together successfully!")

    return {
        "dataset_id": dataset_version.dataset_id,
        "model_id": latest_model["model_id"] if "latest_model" in locals() else None,
        "experiment_id": experiment.experiment_id,
        "snapshot_id": snapshot.snapshot_id,
        "training_job_id": completed_job.job_id,
        "reproducibility_report_id": report.report_id,
    }


if __name__ == "__main__":
    try:
        result = main()
        print(f"\n📊 Demo Results: {result}")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
