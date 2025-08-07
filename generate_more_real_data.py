#!/usr/bin/env python3
"""
Generate More Real Metrics Data for ML Training
Extended version to generate larger amounts of real data
"""

import time
import requests
import json
import subprocess
import signal
import os
from datetime import datetime, timedelta
from ml_models.data_processor import DataProcessor
from ml_models.anomaly_detector import AnomalyDetector

def generate_extended_traffic(duration_minutes=60):
    """Generate extended traffic to Flask app for more real data."""
    print(f"🚀 Generating extended traffic for {duration_minutes} minutes...")
    
    # Start Flask app
    flask_process = subprocess.Popen([
        "python", "-c", 
        "from app.main import create_app; app = create_app(); app.run(host='0.0.0.0', port=3004, debug=False)"
    ])
    
    try:
        # Wait for app to start
        time.sleep(5)
        
        # Generate extended traffic
        endpoints = ['/health', '/metrics', '/status', '/', '/query', '/logs']
        start_time = time.time()
        request_count = 0
        
        while time.time() - start_time < duration_minutes * 60:
            for endpoint in endpoints:
                try:
                    response = requests.get(f"http://localhost:3004{endpoint}", timeout=1)
                    request_count += 1
                    if request_count % 100 == 0:
                        print(f"✅ Generated {request_count} requests...")
                except:
                    pass
            
            # Vary the timing to create realistic patterns
            time.sleep(0.1 + (time.time() % 2) * 0.1)
            
        print(f"✅ Generated {request_count} requests over {duration_minutes} minutes")
        
    finally:
        # Clean up
        flask_process.terminate()
        flask_process.wait()

def extract_extended_real_data():
    """Extract extended real metrics data from Prometheus."""
    print("📊 Extracting extended real metrics data...")
    
    processor = DataProcessor()
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=24)  # Get 24 hours of data
    
    # Extract metrics
    data = processor.extract_metrics(start_time, end_time)
    
    print(f"📈 Extracted data shape: {data.shape}")
    print(f"📈 Data source: {'REAL PROMETHEUS' if processor.prom else 'SYNTHETIC'}")
    
    if data.shape[0] > 100:  # We want at least 100 data points
        print("✅ Extended real metrics data extracted successfully!")
        return data
    else:
        print("❌ Insufficient real data extracted")
        return None

def retrain_model_with_extended_data():
    """Retrain the ML model with extended real data."""
    print("🤖 Retraining ML model with extended real data...")
    
    detector = AnomalyDetector()
    
    # Train model
    result = detector.train_model(force_retrain=True)
    
    print(f"✅ Model training result: {result['status']}")
    if result['status'] == 'success':
        print(f"✅ F1 Score: {result.get('f1_score', 'N/A')}")
        print(f"✅ Data points used: {result.get('total_samples', 'N/A')}")
        print(f"✅ Model saved: {result.get('model_path', 'N/A')}")
    
    return result

def main():
    """Main function to generate extended real data and retrain model."""
    print("🎯 Smart CloudOps AI - Extended Real Data Generation")
    print("=" * 60)
    
    # Step 1: Generate extended traffic (60 minutes)
    generate_extended_traffic(duration_minutes=60)
    
    # Step 2: Extract extended real data
    data = extract_extended_real_data()
    
    # Step 3: Retrain model if we have sufficient real data
    if data is not None and data.shape[0] > 100:
        retrain_model_with_extended_data()
        print("🎉 SUCCESS: Model retrained with EXTENDED REAL data!")
        print(f"📊 Total real data points: {data.shape[0]}")
    else:
        print("⚠️  WARNING: Insufficient real data extracted")
    
    print("=" * 60)
    print("✅ Extended real data generation complete!")

if __name__ == "__main__":
    main() 