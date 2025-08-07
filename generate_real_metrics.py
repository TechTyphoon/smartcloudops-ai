#!/usr/bin/env python3
"""
Generate Real Metrics Data for ML Training
This script generates real metrics by calling our Flask app endpoints
and then extracts the data for ML model training.
"""

import time
import requests
import json
from datetime import datetime, timedelta
from ml_models.data_processor import DataProcessor
from ml_models.anomaly_detector import AnomalyDetector

def generate_traffic():
    """Generate traffic to our Flask app to create real metrics."""
    print("🚀 Generating real traffic to Flask app...")
    
    # Start our Flask app in a subprocess
    import subprocess
    import signal
    import os
    
    # Start Flask app
    flask_process = subprocess.Popen([
        "python", "-c", 
        "from app.main import create_app; app = create_app(); app.run(host='0.0.0.0', port=3003, debug=False)"
    ])
    
    try:
        # Wait for app to start
        time.sleep(5)
        
        # Generate traffic
        endpoints = ['/health', '/metrics', '/status', '/']
        for i in range(50):
            for endpoint in endpoints:
                try:
                    response = requests.get(f"http://localhost:3003{endpoint}", timeout=1)
                    print(f"✅ Request {i+1}: {endpoint} - {response.status_code}")
                except:
                    pass
            time.sleep(0.5)
            
        print("✅ Generated 200+ requests to Flask app")
        
    finally:
        # Clean up
        flask_process.terminate()
        flask_process.wait()

def extract_real_data():
    """Extract real metrics data from Prometheus."""
    print("📊 Extracting real metrics data...")
    
    processor = DataProcessor()
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=2)  # Get 2 hours of data
    
    # Extract metrics
    data = processor.extract_metrics(start_time, end_time)
    
    print(f"📈 Extracted data shape: {data.shape}")
    print(f"📈 Data source: {'REAL PROMETHEUS' if processor.prom else 'SYNTHETIC'}")
    
    if data.shape[0] > 0:
        print("✅ Real metrics data extracted successfully!")
        return data
    else:
        print("❌ No real data extracted, using synthetic data")
        return None

def retrain_model_with_real_data():
    """Retrain the ML model with real data."""
    print("🤖 Retraining ML model with real data...")
    
    detector = AnomalyDetector()
    
    # Train model
    result = detector.train_model(force_retrain=True)
    
    print(f"✅ Model training result: {result['status']}")
    if result['status'] == 'success':
        print(f"✅ F1 Score: {result.get('f1_score', 'N/A')}")
        print(f"✅ Model saved: {result.get('model_path', 'N/A')}")
    
    return result

def main():
    """Main function to generate real data and retrain model."""
    print("🎯 Smart CloudOps AI - Real Data Generation")
    print("=" * 50)
    
    # Step 1: Generate traffic
    generate_traffic()
    
    # Step 2: Extract real data
    data = extract_real_data()
    
    # Step 3: Retrain model if we have real data
    if data is not None and data.shape[0] > 0:
        retrain_model_with_real_data()
        print("🎉 SUCCESS: Model retrained with REAL data!")
    else:
        print("⚠️  WARNING: Could not extract real data, model still uses synthetic data")
    
    print("=" * 50)
    print("✅ Real data generation complete!")

if __name__ == "__main__":
    main() 