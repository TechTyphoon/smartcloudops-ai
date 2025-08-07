#!/usr/bin/env python3
"""
Generate Massive Real Metrics Data for ML Training
Extended version to generate thousands of real data points
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

def generate_massive_traffic(duration_hours=6):
    """Generate massive traffic to Flask app for thousands of real data points."""
    print(f"🚀 Generating massive traffic for {duration_hours} hours...")
    print(f"🎯 Target: {duration_hours * 60 * 60 * 10} data points")
    
    # Start Flask app
    flask_process = subprocess.Popen([
        "python", "-c", 
        "from app.main import create_app; app = create_app(); app.run(host='0.0.0.0', port=3005, debug=False)"
    ])
    
    try:
        # Wait for app to start
        time.sleep(5)
        
        # Generate massive traffic
        endpoints = ['/health', '/metrics', '/status', '/', '/logs']
        start_time = time.time()
        request_count = 0
        
        while time.time() - start_time < duration_hours * 3600:
            for endpoint in endpoints:
                try:
                    response = requests.get(f"http://localhost:3005{endpoint}", timeout=1)
                    request_count += 1
                    if request_count % 1000 == 0:
                        elapsed_hours = (time.time() - start_time) / 3600
                        print(f"✅ Generated {request_count} requests ({elapsed_hours:.1f}h elapsed)")
                except:
                    pass
            
            # Vary the timing to create realistic patterns
            time.sleep(0.05 + (time.time() % 3) * 0.02)
            
        print(f"✅ Generated {request_count} requests over {duration_hours} hours")
        
    finally:
        # Clean up
        flask_process.terminate()
        flask_process.wait()

def extract_massive_real_data():
    """Extract massive real metrics data from Prometheus."""
    print("📊 Extracting massive real metrics data...")
    
    processor = DataProcessor()
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=24)  # Get 24 hours of data
    
    # Extract metrics
    data = processor.extract_metrics(start_time, end_time)
    
    print(f"📈 Extracted data shape: {data.shape}")
    print(f"📈 Data source: {'REAL PROMETHEUS' if processor.prom else 'SYNTHETIC'}")
    
    if data.shape[0] > 500:  # We want at least 500 data points
        print("✅ Massive real metrics data extracted successfully!")
        return data
    else:
        print("❌ Insufficient real data extracted")
        return None

def retrain_model_with_massive_data():
    """Retrain the ML model with massive real data."""
    print("🤖 Retraining ML model with massive real data...")
    
    detector = AnomalyDetector()
    
    # Train model
    result = detector.train_model(force_retrain=True)
    
    print(f"✅ Model training result: {result['status']}")
    if result['status'] == 'success':
        print(f"✅ F1 Score: {result.get('f1_score', 'N/A')}")
        print(f"✅ Data points used: {result.get('total_samples', 'N/A')}")
        print(f"✅ Model saved: {result.get('model_path', 'N/A')}")
    
    return result

def analyze_data_quality(data):
    """Analyze the quality of the extracted data."""
    if data is None:
        return
    
    print("\n📊 Data Quality Analysis:")
    print(f"   📈 Total data points: {len(data)}")
    print(f"   📈 Time range: {data.index.min()} to {data.index.max()}")
    print(f"   📈 Time span: {(data.index.max() - data.index.min()).total_seconds() / 3600:.1f} hours")
    print(f"   📈 Average interval: {(data.index.max() - data.index.min()).total_seconds() / len(data) / 60:.1f} minutes")
    
    # Check for anomalies in the data
    print(f"\n🔍 Data Statistics:")
    for col in data.columns:
        if data[col].dtype in ['float64', 'int64']:
            print(f"   {col}: mean={data[col].mean():.2f}, std={data[col].std():.2f}, min={data[col].min():.2f}, max={data[col].max():.2f}")

def main():
    """Main function to generate massive real data and retrain model."""
    print("🎯 Smart CloudOps AI - Massive Real Data Generation")
    print("=" * 70)
    
    # Step 1: Generate massive traffic (6 hours)
    generate_massive_traffic(duration_hours=6)
    
    # Step 2: Extract massive real data
    data = extract_massive_real_data()
    
    # Step 3: Analyze data quality
    analyze_data_quality(data)
    
    # Step 4: Retrain model if we have sufficient real data
    if data is not None and data.shape[0] > 500:
        retrain_model_with_massive_data()
        print("🎉 SUCCESS: Model retrained with MASSIVE REAL data!")
        print(f"📊 Total real data points: {data.shape[0]}")
        print(f"🎯 Model quality: {'EXCELLENT' if data.shape[0] > 1000 else 'GOOD' if data.shape[0] > 500 else 'ACCEPTABLE'}")
    else:
        print("⚠️  WARNING: Insufficient real data extracted")
        print("💡 Try running for longer duration or check Prometheus connectivity")
    
    print("=" * 70)
    print("✅ Massive real data generation complete!")

if __name__ == "__main__":
    main() 