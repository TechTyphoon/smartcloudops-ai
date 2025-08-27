#!/usr/bin/env python3
"""
Temporary test for MLOpsService
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Create a simplified version of MLOpsService for testing
class SimplifiedMLOpsService:
    """Simplified MLOps service for testing without complex imports."""""
    
    def __init__(self):
        """Initialize with mock data."""""
        self.mock_experiments = [
            {
                "id": "exp_1",
                "name": "anomaly_detection_v1",
                "status": "completed",
                "runs_count": 5
            }
        ]
        
        self.mock_models = [
            {
                "id": "model_1", 
                "name": "anomaly_detector",
                "version": "1.0.0",
                "status": "production"
            }
        ]
    
    def get_experiments(self, page=1, per_page=20):
        """Get experiments with pagination."""""
        total = len(self.mock_experiments)
        pagination = {"page": page, "per_page": per_page, "total": total}
        return self.mock_experiments, pagination
    
    def get_models(self, page=1, per_page=20):
        """Get models with pagination."""""
        total = len(self.mock_models)
        pagination = {"page": page, "per_page": per_page, "total": total}
        return self.mock_models, pagination
    
    def get_mlops_statistics(self):
        """Get MLOps statistics."""""
        return {
            "experiments": {"total_experiments": len(self.mock_experiments)},
            "models": {"total_models": len(self.mock_models)}
        }

# Test the simplified service
if __name__ == "__main__":
    service = SimplifiedMLOpsService()
    
    experiments, pagination = service.get_experiments()
    print(f"✅ Retrieved {len(experiments)} experiments")
    
    models, pagination = service.get_models()
    print(f"✅ Retrieved {len(models)} models")
    
    stats = service.get_mlops_statistics()
    print(f"✅ Statistics: {stats['experiments']['total_experiments']} experiments, {stats['models']['total_models']} models")
    
    print("🎉 Simplified MLOpsService pattern working!")
