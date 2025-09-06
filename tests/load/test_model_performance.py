"""
Load testing for ML model performance
"""

import requests
import time
import statistics
import json
from typing import List, Dict, Any


def test_model_performance(base_url: str = "http://localhost:5000", num_requests: int = 100):
    """Test ML model performance under load."""
    
    print(f"🚀 Starting ML model performance test with {num_requests} requests...")
    
    response_times = []
    errors = []
    
    # Test data
    test_data = {
        "metric_name": "cpu_usage",
        "value": 85.5,
        "threshold": 80.0,
        "severity": "high",
        "source": "load_test"
    }
    
    for i in range(num_requests):
        try:
            start_time = time.time()
            
            # Test anomaly detection endpoint
            response = requests.post(
                f"{base_url}/api/anomalies/",
                json=test_data,
                timeout=10
            )
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            if response.status_code == 200:
                response_times.append(response_time)
            else:
                errors.append(f"HTTP {response.status_code}")
                
        except Exception as e:
            errors.append(str(e))
        
        # Progress indicator
        if (i + 1) % 10 == 0:
            print(f"Completed {i + 1}/{num_requests} requests...")
    
    # Calculate statistics
    if response_times:
        avg_time = statistics.mean(response_times)
        median_time = statistics.median(response_times)
        p95_time = sorted(response_times)[int(len(response_times) * 0.95)]
        p99_time = sorted(response_times)[int(len(response_times) * 0.99)]
        
        print(f"\n📊 Performance Results:")
        print(f"  Average Response Time: {avg_time:.2f}ms")
        print(f"  Median Response Time: {median_time:.2f}ms")
        print(f"  95th Percentile: {p95_time:.2f}ms")
        print(f"  99th Percentile: {p99_time:.2f}ms")
        print(f"  Total Requests: {len(response_times)}")
        print(f"  Errors: {len(errors)}")
        
        # Performance thresholds
        if avg_time < 500:
            print("✅ Performance: EXCELLENT")
        elif avg_time < 1000:
            print("✅ Performance: GOOD")
        elif avg_time < 2000:
            print("⚠️ Performance: ACCEPTABLE")
        else:
            print("❌ Performance: POOR")
            
        return {
            "avg_response_time": avg_time,
            "median_response_time": median_time,
            "p95_response_time": p95_time,
            "p99_response_time": p99_time,
            "total_requests": len(response_times),
            "errors": len(errors),
            "success_rate": len(response_times) / num_requests * 100
        }
    else:
        print("❌ No successful requests completed")
        return None


if __name__ == "__main__":
    test_model_performance()
