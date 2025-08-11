# ML Models Package for Smart CloudOps AI

A production-ready machine learning package for anomaly detection in cloud operations.

## 🚀 Quick Start

```python
from ml_models import create_anomaly_detector

# Create detector
detector = create_anomaly_detector()

# Train model (if needed)
results = detector.train_model()

# Detect anomalies
metrics = {
    'cpu_usage_avg': 85.0,
    'memory_usage_pct': 75.0,
    'disk_usage_pct': 60.0
}
result = detector.detect_anomaly(metrics)
print(f"Anomaly detected: {result['is_anomaly']}")
```

## 📦 Package Contents

### Core Classes

- **`AnomalyDetector`**: Main anomaly detection orchestrator
- **`DataProcessor`**: Data preprocessing and validation
- **`AnomalyModelTrainer`**: Model training and validation
- **`AnomalyInferenceEngine`**: Real-time inference engine
- **`ProductionAnomalyDetector`**: Production-ready ensemble detector

### Utility Functions

- **`create_anomaly_detector()`**: Create configured detector instance
- **`create_production_detector()`**: Create production-ready detector
- **`get_package_info()`**: Get comprehensive package information
- **`validate_package_health()`**: Check package health and readiness
- **`get_usage_statistics()`**: Get usage statistics and file information
- **`get_quick_start_example()`**: Get quick start code example

## 🔧 Installation & Setup

1. **Activate virtual environment**:
   ```bash
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**:
   ```python
   from ml_models import get_package_info
   print(get_package_info())
   ```

## 📊 Usage Examples

### Basic Anomaly Detection

```python
from ml_models import create_anomaly_detector

detector = create_anomaly_detector()

# Check system status
status = detector.get_system_status()
print(f"Model loaded: {status['model_exists']}")

# Train model if needed
if not status['model_exists']:
    results = detector.train_model()
    print(f"Training completed: {results['status']}")

# Detect anomalies
metrics = {
    'cpu_usage_avg': 85.0,
    'memory_usage_pct': 75.0,
    'disk_usage_pct': 60.0,
    'network_bytes_total': 1000.0,
    'request_rate': 15.0,
    'response_time_p95': 0.3
}

result = detector.detect_anomaly(metrics)
print(f"Anomaly: {result['is_anomaly']}")
print(f"Confidence: {result['confidence']}")
```

### Production Ensemble Detection

```python
from ml_models import create_production_detector

detector = create_production_detector()

# Train ensemble models
training_data = pd.DataFrame(...)  # Your training data
results = detector.train_ensemble(training_data)

# Detect anomalies with ensemble
metrics = {...}  # Your metrics
result = detector.detect_anomalies_production(metrics)
print(f"Ensemble result: {result}")
```

### Package Health Monitoring

```python
from ml_models import validate_package_health, get_usage_statistics

# Check package health
health = validate_package_health()
if health['healthy']:
    print("✅ Package is healthy")
else:
    print("❌ Package has issues:")
    for error in health['errors']:
        print(f"  - {error}")

# Get usage statistics
stats = get_usage_statistics()
print(f"Available models: {stats['available_models']}")
print(f"Config files: {stats['config_files']}")
```

## 🏗️ Architecture

The package follows a modular architecture:

```
ml_models/
├── __init__.py              # Package initialization and utilities
├── anomaly_detector.py      # Main orchestrator
├── data_processor.py        # Data preprocessing
├── model_trainer.py         # Model training
├── inference_engine.py      # Real-time inference
├── production_enhancements.py # Production ensemble methods
├── config.yaml              # Configuration
├── models/                  # Trained models
├── data/                    # Training data
└── tests/                   # Unit tests
```

## ⚙️ Configuration

The package uses `config.yaml` for configuration:

```yaml
data:
  lookback_hours: 168  # 1 week
  feature_window: 60

training:
  min_f1_score: 0.85
  validation_split: 0.2

inference:
  cache_size: 1000
  confidence_threshold: 0.7
```

## 🧪 Testing

Run the example script to test all functionality:

```bash
python ml_models/example_usage.py
```

## 📈 Performance

- **Training**: Supports incremental training and model updates
- **Inference**: Real-time anomaly detection with caching
- **Scalability**: Handles batch processing for multiple metrics
- **Accuracy**: F1-score threshold of 0.85 for production use

## 🔒 Security

- Input validation and sanitization
- Secure model loading and caching
- Error handling without information leakage
- Configurable access controls

## 🚨 Troubleshooting

### Common Issues

1. **Module not found**: Ensure virtual environment is activated
2. **Model not loaded**: Train the model first using `detector.train_model()`
3. **Scaler not fitted**: Production detector needs training data first

### Health Checks

Use the built-in health validation:

```python
from ml_models import validate_package_health
health = validate_package_health()
print(health)
```

## 📚 API Reference

For detailed API documentation, see the individual module files:

- `anomaly_detector.py` - Main detector class
- `data_processor.py` - Data processing utilities
- `model_trainer.py` - Training functionality
- `inference_engine.py` - Inference engine
- `production_enhancements.py` - Production methods

## 🤝 Contributing

1. Follow the existing code style
2. Add tests for new functionality
3. Update documentation
4. Ensure all health checks pass

## 📄 License

Part of the Smart CloudOps AI project. See main project LICENSE file.

---

**Version**: 1.0.0  
**Author**: Smart CloudOps AI Team  
**Status**: Production Ready ✅ 