# Phase 3: Anomaly Detection (ML Layer)

**Status**: ⏳ Pending (Requires Phase 2 completion)  
**Prerequisites**: Phase 2 Flask App completed  
**Estimated Duration**: 3-4 hours  

## 📋 Overview

Phase 3 implements machine learning-based anomaly detection using Prometheus metrics data. This phase creates an intelligent system that can identify unusual patterns in system behavior and integrate with the ChatOps interface.

## 🎯 Objectives

### Phase 3.1: Data Preparation
- [ ] Extract Prometheus metrics to CSV format
- [ ] Process node_exporter logs and metrics
- [ ] Create data preprocessing pipeline
- [ ] Implement data validation and cleaning

### Phase 3.2: Model Training
- [ ] Implement Isolation Forest algorithm
- [ ] Alternative: Prophet time series analysis
- [ ] Model validation with F1-score ≥ 0.85
- [ ] Save trained model to ml_models/anomaly_model.pkl

### Phase 3.3: Inference Pipeline
- [ ] Real-time anomaly detection system
- [ ] Live metrics processing
- [ ] Anomaly severity scoring
- [ ] Integration with monitoring stack

## 📁 Files to be Created

```
📂 ml_models/
├── 📄 anomaly_detector.py          # Main anomaly detection class
├── 📄 data_processor.py            # Data preprocessing and validation
├── 📄 model_trainer.py             # Model training pipeline
├── 📄 inference_engine.py          # Real-time inference
├── 📄 requirements.txt             # ML-specific dependencies
├── 📄 config.yaml                  # Model configuration
├── 📂 models/
│   ├── 📄 anomaly_model.pkl        # Trained model artifact
│   └── 📄 scaler.pkl               # Data scaler
├── 📂 data/
│   ├── 📄 training_data.csv        # Historical metrics
│   └── 📄 validation_data.csv      # Validation dataset
└── 📂 tests/
    ├── 📄 test_anomaly_detector.py
    ├── 📄 test_data_processor.py
    └── 📄 test_inference.py
```

## 🔧 Dependencies

### 📦 ML Dependencies
```python
# Core ML Libraries
scikit-learn==1.3.2
pandas==2.1.3
numpy==1.24.3
scipy==1.11.4

# Time Series Analysis
prophet==1.1.4

# Data Processing
joblib==1.3.2
matplotlib==3.7.2
seaborn==0.12.2

# Prometheus Integration
prometheus-api-client==0.5.3
```

### 📊 Data Sources
- **Prometheus Metrics**: Via API queries
- **Node Exporter Data**: System metrics
- **Application Metrics**: Flask app performance data
- **Historical Data**: Past 30 days for training

## 🏗️ Implementation Plan

### Phase 3.1: Data Preparation

#### Prometheus Data Extraction
```python
# ml_models/data_processor.py structure
import pandas as pd
from prometheus_api_client import PrometheusConnect

class DataProcessor:
    def __init__(self, prometheus_url: str):
        self.prom = PrometheusConnect(url=prometheus_url)
    
    def extract_metrics(self, start_time, end_time):
        # Extract key metrics for anomaly detection
        metrics = [
            'node_cpu_seconds_total',
            'node_memory_MemAvailable_bytes',
            'node_filesystem_avail_bytes',
            'node_network_receive_bytes_total'
        ]
        return self.fetch_and_process(metrics, start_time, end_time)
```

#### Feature Engineering
- **CPU Usage**: Average, max, variance over time windows
- **Memory Usage**: Available memory percentage, trends
- **Disk Usage**: Filesystem utilization patterns
- **Network**: Traffic volume and packet rates
- **Time Features**: Hour of day, day of week seasonality

### Phase 3.2: Model Training

#### Isolation Forest Implementation
```python
# ml_models/model_trainer.py structure
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

class AnomalyModelTrainer:
    def __init__(self):
        self.model = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
    
    def train(self, data: pd.DataFrame):
        # Feature scaling and model training
        pass
    
    def validate(self, test_data: pd.DataFrame):
        # Model validation with F1-score calculation
        pass
```

#### Model Selection Criteria
- **Primary**: Isolation Forest for unsupervised anomaly detection
- **Alternative**: Prophet for time series anomalies
- **Validation**: F1-score ≥ 0.85 on validation set
- **Performance**: Inference time < 100ms per prediction

### Phase 3.3: Inference Pipeline

#### Real-time Anomaly Detection
```python
# ml_models/inference_engine.py structure
import joblib
from typing import Dict, List, Tuple

class AnomalyInferenceEngine:
    def __init__(self, model_path: str):
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(model_path.replace('model', 'scaler'))
    
    def detect_anomalies(self, live_metrics: Dict) -> Tuple[bool, float]:
        # Real-time anomaly detection
        # Returns: (is_anomaly, severity_score)
        pass
    
    def explain_anomaly(self, metrics: Dict) -> str:
        # Generate human-readable explanation
        pass
```

#### Integration Points
- **Flask App**: /anomaly endpoint for real-time detection
- **Prometheus**: Alert rule integration
- **ChatOps**: Anomaly explanations and recommendations

## 📊 Model Configuration

### Training Parameters
```yaml
# ml_models/config.yaml
model:
  type: "isolation_forest"
  contamination: 0.1
  n_estimators: 100
  random_state: 42

data:
  lookback_hours: 168  # 7 days
  feature_window: 60   # 1 hour aggregation
  update_frequency: 3600  # 1 hour

thresholds:
  anomaly_score: -0.5
  severity_levels:
    low: [-0.5, -0.3]
    medium: [-0.3, -0.1]
    high: [-0.1, 1.0]

features:
  - cpu_usage_avg
  - cpu_usage_max
  - memory_usage_pct
  - disk_usage_pct
  - network_bytes_total
  - request_rate
  - response_time_p95
```

## 🔍 Anomaly Detection Logic

### Detection Criteria
1. **Statistical Outliers**: Beyond 3 standard deviations
2. **Behavioral Changes**: Significant pattern shifts
3. **Threshold Violations**: Critical metric breaches
4. **Seasonal Anomalies**: Unusual patterns for time of day/week

### Severity Scoring
- **Low (0.0-0.3)**: Minor deviation, monitoring only
- **Medium (0.4-0.7)**: Notable anomaly, investigation recommended
- **High (0.8-1.0)**: Critical anomaly, immediate action required

### Anomaly Types
- **Resource Anomalies**: CPU, memory, disk spikes
- **Performance Anomalies**: Response time degradation
- **Traffic Anomalies**: Unusual request patterns
- **System Anomalies**: Service failures or errors

## 🧪 Testing Strategy

### Model Testing
```python
# ml_models/tests/test_anomaly_detector.py
def test_model_accuracy():
    # Test F1-score ≥ 0.85
    pass

def test_inference_speed():
    # Test inference time < 100ms
    pass

def test_anomaly_explanation():
    # Test human-readable explanations
    pass
```

### Integration Testing
- **Data Pipeline**: Prometheus to model data flow
- **Real-time Detection**: Live metrics processing
- **Flask Integration**: API endpoint functionality

### Performance Testing
- **Scalability**: Handle high-frequency metrics
- **Memory Usage**: Efficient data processing
- **Response Time**: Fast anomaly detection

## 📈 Monitoring and Evaluation

### Model Performance Metrics
- **Precision**: True anomalies / Total detected anomalies
- **Recall**: Detected anomalies / Total actual anomalies
- **F1-Score**: Harmonic mean of precision and recall
- **False Positive Rate**: Incorrect anomaly detections

### Operational Metrics
- **Detection Latency**: Time from metric to detection
- **Model Drift**: Performance degradation over time
- **Resource Usage**: CPU/memory consumption
- **Alert Fatigue**: Balance sensitivity vs. noise

## 🔄 Model Lifecycle

### Training Schedule
- **Initial Training**: Historical 30-day data
- **Retraining**: Weekly with new data
- **Validation**: Continuous performance monitoring
- **Model Updates**: When F1-score drops below 0.8

### Data Management
- **Data Retention**: 90 days of training data
- **Feature Store**: Preprocessed feature cache
- **Model Versioning**: Git-based model tracking
- **Rollback**: Previous model restoration capability

## 📋 Prerequisites

### Phase 2 Completion Required ✅
- Flask application operational
- Prometheus metrics collection
- Basic monitoring infrastructure

### Data Requirements
- **Historical Data**: 30+ days of metrics
- **Labeled Anomalies**: Optional but recommended
- **Clean Data**: Validated and preprocessed

### Infrastructure Requirements
- **Compute**: Additional CPU for model training
- **Storage**: Model artifacts and training data
- **Memory**: Data processing and model inference

## 🚀 Integration Points

### Flask App Integration
```python
# In app/main.py
@app.route('/anomaly', methods=['POST'])
def detect_anomaly():
    # Real-time anomaly detection endpoint
    pass

@app.route('/anomaly/explain/<anomaly_id>')
def explain_anomaly(anomaly_id):
    # Anomaly explanation endpoint
    pass
```

### ChatOps Integration
- **Query**: "Are there any current anomalies?"
- **Response**: Anomaly summary with explanations
- **Recommendations**: Suggested actions for detected anomalies

### Monitoring Integration
- **Prometheus Alerts**: ML-detected anomaly alerts
- **Grafana Dashboards**: Anomaly detection visualizations
- **Notification**: Integration with alerting systems

---

**Dependencies**: Phase 2 completion, historical metrics data  
**Estimated Timeline**: 3-4 hours for complete implementation  
**Next Phase**: [Phase 4: Auto-Remediation Logic](phase-4-auto-remediation.md)