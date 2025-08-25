# 👨‍💻 SmartCloudOps AI - Developer Guide

**Complete developer onboarding and contribution guide**

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Code Architecture](#code-architecture)
- [Development Workflow](#development-workflow)
- [Testing Guidelines](#testing-guidelines)
- [API Development](#api-development)
- [Frontend Development](#frontend-development)
- [MLOps Development](#mlops-development)
- [Contributing Guidelines](#contributing-guidelines)

## 🚀 Getting Started

### Prerequisites

Before starting development, ensure you have:

- **Python 3.11+** with pip and virtualenv
- **Node.js 18+** with npm
- **Docker** and Docker Compose
- **Git** with proper SSH keys configured
- **PostgreSQL 13+** (optional, can use Docker)
- **Redis 6+** (optional, can use Docker)
- **Code Editor** (VS Code recommended with extensions)

### Quick Setup (5 minutes)

```bash
# 1. Clone the repository
git clone git@github.com:your-org/smartcloudops-ai.git
cd smartcloudops-ai

# 2. Run setup script
./scripts/dev-setup.sh

# 3. Start development environment
docker-compose -f docker-compose.dev.yml up -d

# 4. Install dependencies
pip install -r requirements-dev.txt
npm install

# 5. Initialize database
python scripts/init_db.py

# 6. Start development servers
# Terminal 1: Backend
python -m flask run --debug --host=0.0.0.0 --port=5000

# Terminal 2: Frontend
npm run dev
```

Your development environment should now be running at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Docs**: http://localhost:5000/docs

## 🏗️ Development Environment

### Recommended VS Code Extensions

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.flake8",
    "ms-python.mypy-type-checker",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next",
    "ms-kubernetes-tools.vscode-kubernetes-tools",
    "redhat.vscode-yaml",
    "ms-vscode.docker"
  ]
}
```

### Environment Configuration

Create a `.env` file from the template:

```bash
cp env.example .env
```

Essential environment variables for development:

```env
# Application
FLASK_APP=app/main.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key-change-in-production

# Database
DATABASE_URL=postgresql://dev:dev@localhost:5432/smartcloudops_dev
DATABASE_POOL_SIZE=5

# Redis
REDIS_URL=redis://localhost:6379/0

# AI/ML
OPENAI_API_KEY=your-openai-key-here
HUGGINGFACE_API_KEY=your-hf-key-here

# Monitoring (optional for dev)
PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus
LOG_LEVEL=DEBUG

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:5000
NEXT_PUBLIC_WS_URL=ws://localhost:5000
```

### Docker Development Setup

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: smartcloudops_dev
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  maildev:
    image: maildev/maildev
    ports:
      - "1080:1080"  # Web interface
      - "1025:1025"  # SMTP server

volumes:
  postgres_dev_data:
```

### Development Scripts

```bash
# Setup script (scripts/dev-setup.sh)
#!/bin/bash
echo "Setting up SmartCloudOps AI development environment..."

# Create Python virtual environment
python -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Install Node.js dependencies
npm install

# Setup database
python scripts/init_db.py

echo "Development environment setup complete!"
echo "Run 'docker-compose -f docker-compose.dev.yml up -d' to start services"
```

## 🏛️ Code Architecture

### Project Structure

```
smartcloudops-ai/
├── app/                          # Backend application
│   ├── __init__.py
│   ├── main.py                   # Flask application factory
│   ├── config.py                 # Configuration management
│   ├── database.py               # Database setup
│   ├── auth.py                   # Authentication logic
│   ├── api/                      # API blueprints
│   │   ├── __init__.py
│   │   ├── anomalies.py         # Anomaly detection endpoints
│   │   ├── remediation.py       # Remediation endpoints
│   │   ├── ml.py                # ML model endpoints
│   │   ├── ai.py                # AI/ChatOps endpoints
│   │   └── feedback.py          # Feedback endpoints
│   ├── models/                   # Database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── anomaly.py
│   │   └── remediation.py
│   ├── services/                 # Business logic services
│   │   ├── __init__.py
│   │   ├── anomaly_service.py
│   │   ├── ml_service.py
│   │   └── notification_service.py
│   ├── mlops/                    # MLOps framework
│   │   ├── __init__.py
│   │   ├── model_registry.py
│   │   ├── experiment_tracker.py
│   │   ├── training_pipeline.py
│   │   └── model_monitor.py
│   ├── remediation/              # Remediation engine
│   │   ├── __init__.py
│   │   ├── engine.py
│   │   ├── actions.py
│   │   └── safety.py
│   ├── observability/            # Observability stack
│   │   ├── __init__.py
│   │   ├── logging_config.py
│   │   ├── metrics.py
│   │   └── tracing.py
│   └── utils/                    # Utility functions
│       ├── __init__.py
│       ├── validators.py
│       └── helpers.py
├── frontend/                     # Next.js frontend
│   ├── components/              # React components
│   │   ├── ui/                  # UI components
│   │   ├── dashboard/           # Dashboard components
│   │   ├── anomalies/           # Anomaly components
│   │   └── common/              # Common components
│   ├── pages/                   # Next.js pages
│   │   ├── api/                 # API routes
│   │   ├── auth/                # Authentication pages
│   │   ├── dashboard/           # Dashboard pages
│   │   └── anomalies/           # Anomaly pages
│   ├── hooks/                   # Custom React hooks
│   ├── lib/                     # Utility libraries
│   ├── stores/                  # State management
│   └── styles/                  # CSS and styling
├── tests/                       # Test suites
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   ├── e2e/                     # End-to-end tests
│   └── fixtures/                # Test data
├── docs/                        # Documentation
├── deploy/                      # Deployment configurations
│   ├── helm/                    # Helm charts
│   ├── k8s/                     # Kubernetes manifests
│   └── docker/                  # Docker configurations
├── scripts/                     # Utility scripts
│   ├── performance/             # Performance testing
│   ├── mlops/                   # MLOps utilities
│   └── deployment/              # Deployment scripts
└── monitoring/                  # Monitoring configurations
    ├── prometheus/              # Prometheus configs
    ├── grafana/                 # Grafana dashboards
    └── alerting/                # Alert rules
```

### Backend Architecture Patterns

#### Flask Application Factory
```python
# app/main.py
from flask import Flask
from app.config import get_config
from app.database import init_db
from app.api import register_blueprints

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    register_blueprints(app)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
```

#### Service Layer Pattern
```python
# app/services/anomaly_service.py
from typing import List, Optional
from app.models.anomaly import Anomaly
from app.database import db

class AnomalyService:
    @staticmethod
    def create_anomaly(data: dict) -> Anomaly:
        anomaly = Anomaly(**data)
        db.session.add(anomaly)
        db.session.commit()
        return anomaly
    
    @staticmethod
    def get_anomalies(filters: dict) -> List[Anomaly]:
        query = Anomaly.query
        
        if filters.get('severity'):
            query = query.filter_by(severity=filters['severity'])
        
        if filters.get('start_date'):
            query = query.filter(Anomaly.timestamp >= filters['start_date'])
            
        return query.all()
```

#### API Blueprint Structure
```python
# app/api/anomalies.py
from flask import Blueprint, request, jsonify
from app.services.anomaly_service import AnomalyService
from app.utils.validators import validate_json

anomalies_bp = Blueprint('anomalies', __name__, url_prefix='/api/anomalies')

@anomalies_bp.route('/', methods=['GET'])
def get_anomalies():
    filters = {
        'severity': request.args.get('severity'),
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date')
    }
    
    anomalies = AnomalyService.get_anomalies(filters)
    
    return jsonify({
        'data': [anomaly.to_dict() for anomaly in anomalies],
        'count': len(anomalies)
    })

@anomalies_bp.route('/', methods=['POST'])
@validate_json(['metric_name', 'value', 'threshold'])
def create_anomaly():
    data = request.get_json()
    
    anomaly = AnomalyService.create_anomaly(data)
    
    return jsonify({
        'data': anomaly.to_dict(),
        'message': 'Anomaly created successfully'
    }), 201
```

### Frontend Architecture Patterns

#### Component Structure
```typescript
// components/anomalies/AnomalyCard.tsx
import React from 'react';
import { Anomaly } from '@/types/anomaly';
import { Badge } from '@/components/ui/Badge';
import { formatDateTime } from '@/lib/utils';

interface AnomalyCardProps {
  anomaly: Anomaly;
  onAcknowledge?: (id: string) => void;
  onRemediate?: (id: string) => void;
}

export const AnomalyCard: React.FC<AnomalyCardProps> = ({
  anomaly,
  onAcknowledge,
  onRemediate
}) => {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'red';
      case 'high': return 'orange';
      case 'medium': return 'yellow';
      default: return 'gray';
    }
  };

  return (
    <div className="border rounded-lg p-4 bg-white shadow-sm">
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-semibold">{anomaly.metric_name}</h3>
        <Badge color={getSeverityColor(anomaly.severity)}>
          {anomaly.severity}
        </Badge>
      </div>
      
      <div className="text-sm text-gray-600 mb-3">
        <p>Value: {anomaly.value} (Threshold: {anomaly.threshold})</p>
        <p>Detected: {formatDateTime(anomaly.timestamp)}</p>
      </div>
      
      <div className="flex gap-2">
        {onAcknowledge && (
          <button
            onClick={() => onAcknowledge(anomaly.id)}
            className="px-3 py-1 text-sm bg-blue-500 text-white rounded"
          >
            Acknowledge
          </button>
        )}
        {onRemediate && (
          <button
            onClick={() => onRemediate(anomaly.id)}
            className="px-3 py-1 text-sm bg-green-500 text-white rounded"
          >
            Remediate
          </button>
        )}
      </div>
    </div>
  );
};
```

#### Custom Hooks
```typescript
// hooks/useAnomalies.ts
import { useState, useEffect } from 'react';
import { Anomaly } from '@/types/anomaly';
import { anomalyApi } from '@/lib/api';

export const useAnomalies = (filters?: AnomalyFilters) => {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnomalies = async () => {
      try {
        setLoading(true);
        const data = await anomalyApi.getAnomalies(filters);
        setAnomalies(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchAnomalies();
  }, [filters]);

  const acknowledgeAnomaly = async (id: string) => {
    try {
      await anomalyApi.acknowledge(id);
      setAnomalies(prev => 
        prev.map(anomaly => 
          anomaly.id === id 
            ? { ...anomaly, status: 'acknowledged' }
            : anomaly
        )
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to acknowledge');
    }
  };

  return {
    anomalies,
    loading,
    error,
    acknowledgeAnomaly,
    refetch: () => fetchAnomalies()
  };
};
```

## 🔄 Development Workflow

### Git Workflow

#### Branch Naming Convention
- **Feature branches**: `feature/anomaly-detection-improvements`
- **Bug fixes**: `fix/dashboard-loading-issue`
- **Hotfixes**: `hotfix/security-vulnerability`
- **Documentation**: `docs/api-reference-update`
- **Refactoring**: `refactor/service-layer-cleanup`

#### Commit Message Format
```
type(scope): brief description

Longer description if needed, explaining what and why vs how.

Closes #123
```

**Types**: feat, fix, docs, style, refactor, test, chore

**Examples**:
```
feat(api): add anomaly severity filtering endpoint

Add support for filtering anomalies by severity level in the GET /api/anomalies endpoint.
Includes validation and tests.

Closes #45

fix(ui): resolve dashboard loading spinner issue

The loading spinner was not hiding after data loaded due to missing dependency in useEffect.

Closes #67
```

### Development Process

#### 1. Start New Feature
```bash
# Create feature branch
git checkout -b feature/new-awesome-feature

# Make changes
# ... code, test, commit ...

# Push branch
git push -u origin feature/new-awesome-feature

# Create pull request
gh pr create --title "Add awesome new feature" --body "Description of changes"
```

#### 2. Code Review Process
- All changes require code review
- At least one approval from a team member
- All tests must pass
- Code coverage must not decrease
- Documentation must be updated

#### 3. Merge Process
```bash
# After approval, merge with squash
git checkout main
git pull origin main
git merge --squash feature/new-awesome-feature
git commit -m "feat: add awesome new feature"
git push origin main

# Delete feature branch
git branch -d feature/new-awesome-feature
git push origin --delete feature/new-awesome-feature
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json

  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        additional_dependencies: [flake8-docstrings]

  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.0.0-alpha.4
    hooks:
      - id: prettier
        files: \.(js|ts|tsx|css|md|yaml|yml)$
```

## 🧪 Testing Guidelines

### Testing Strategy

#### Test Pyramid
1. **Unit Tests (70%)**: Individual functions and classes
2. **Integration Tests (20%)**: API endpoints and database interactions
3. **End-to-End Tests (10%)**: Complete user workflows

#### Backend Testing

```python
# tests/unit/test_anomaly_service.py
import pytest
from app.services.anomaly_service import AnomalyService
from app.models.anomaly import Anomaly

class TestAnomalyService:
    def test_create_anomaly_success(self, db_session):
        # Arrange
        data = {
            'metric_name': 'cpu_usage',
            'value': 95.5,
            'threshold': 80.0,
            'severity': 'high'
        }
        
        # Act
        anomaly = AnomalyService.create_anomaly(data)
        
        # Assert
        assert anomaly.metric_name == 'cpu_usage'
        assert anomaly.value == 95.5
        assert anomaly.severity == 'high'
        assert anomaly.id is not None

    def test_get_anomalies_with_filters(self, db_session, sample_anomalies):
        # Arrange
        filters = {'severity': 'high'}
        
        # Act
        anomalies = AnomalyService.get_anomalies(filters)
        
        # Assert
        assert len(anomalies) == 2
        assert all(a.severity == 'high' for a in anomalies)
```

#### Frontend Testing

```typescript
// components/__tests__/AnomalyCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { AnomalyCard } from '../AnomalyCard';
import { mockAnomaly } from '@/tests/fixtures';

describe('AnomalyCard', () => {
  it('renders anomaly information correctly', () => {
    render(<AnomalyCard anomaly={mockAnomaly} />);
    
    expect(screen.getByText('cpu_usage')).toBeInTheDocument();
    expect(screen.getByText('high')).toBeInTheDocument();
    expect(screen.getByText(/Value: 95.5/)).toBeInTheDocument();
  });

  it('calls onAcknowledge when acknowledge button is clicked', () => {
    const mockAcknowledge = jest.fn();
    
    render(
      <AnomalyCard 
        anomaly={mockAnomaly} 
        onAcknowledge={mockAcknowledge} 
      />
    );
    
    fireEvent.click(screen.getByText('Acknowledge'));
    
    expect(mockAcknowledge).toHaveBeenCalledWith(mockAnomaly.id);
  });
});
```

#### API Testing

```python
# tests/integration/test_anomaly_api.py
import pytest
from app.main import create_app

class TestAnomalyAPI:
    def test_get_anomalies_success(self, client, auth_headers):
        # Act
        response = client.get('/api/anomalies/', headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert isinstance(data['data'], list)

    def test_create_anomaly_success(self, client, auth_headers):
        # Arrange
        payload = {
            'metric_name': 'memory_usage',
            'value': 88.5,
            'threshold': 85.0,
            'severity': 'medium'
        }
        
        # Act
        response = client.post(
            '/api/anomalies/', 
            json=payload, 
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['metric_name'] == 'memory_usage'
```

### Running Tests

```bash
# Backend tests
pytest tests/ -v --cov=app --cov-report=html

# Frontend tests
npm test

# E2E tests
npm run test:e2e

# All tests
npm run test:all
```

## 📡 API Development

### API Design Principles

1. **RESTful Design**: Use HTTP verbs correctly
2. **Consistent Responses**: Standard response format
3. **Error Handling**: Meaningful error messages
4. **Validation**: Input validation and sanitization
5. **Documentation**: OpenAPI/Swagger documentation

### Response Format

```json
{
  "data": {}, // or []
  "message": "Success message",
  "errors": [],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "total_pages": 5
  }
}
```

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "reason": "Invalid email format"
    }
  },
  "request_id": "req_123456789"
}
```

### API Documentation

```python
# Using Flask-RESTX for automatic documentation
from flask_restx import Api, Resource, fields

api = Api(doc='/docs/')

anomaly_model = api.model('Anomaly', {
    'id': fields.String(description='Unique identifier'),
    'metric_name': fields.String(required=True, description='Metric name'),
    'value': fields.Float(required=True, description='Metric value'),
    'threshold': fields.Float(required=True, description='Alert threshold'),
    'severity': fields.String(enum=['low', 'medium', 'high', 'critical'])
})

@api.route('/anomalies')
class AnomalyList(Resource):
    @api.marshal_list_with(anomaly_model)
    def get(self):
        """Get list of anomalies"""
        return AnomalyService.get_anomalies()
    
    @api.expect(anomaly_model)
    @api.marshal_with(anomaly_model, code=201)
    def post(self):
        """Create new anomaly"""
        return AnomalyService.create_anomaly(api.payload)
```

## 🎨 Frontend Development

### Component Guidelines

#### Component Structure
```typescript
// Component template
import React from 'react';
import { ComponentProps } from './types';
import { useComponentLogic } from './hooks';
import styles from './Component.module.css';

interface Props extends ComponentProps {
  // Additional props
}

export const Component: React.FC<Props> = ({ prop1, prop2 }) => {
  const { state, actions } = useComponentLogic({ prop1, prop2 });

  return (
    <div className={styles.container}>
      {/* Component JSX */}
    </div>
  );
};

export default Component;
```

#### State Management with Zustand
```typescript
// stores/anomalyStore.ts
import { create } from 'zustand';
import { Anomaly } from '@/types';

interface AnomalyStore {
  anomalies: Anomaly[];
  loading: boolean;
  error: string | null;
  fetchAnomalies: () => Promise<void>;
  acknowledgeAnomaly: (id: string) => Promise<void>;
}

export const useAnomalyStore = create<AnomalyStore>((set, get) => ({
  anomalies: [],
  loading: false,
  error: null,

  fetchAnomalies: async () => {
    set({ loading: true, error: null });
    try {
      const anomalies = await anomalyApi.getAnomalies();
      set({ anomalies, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  acknowledgeAnomaly: async (id: string) => {
    try {
      await anomalyApi.acknowledge(id);
      const anomalies = get().anomalies.map(a => 
        a.id === id ? { ...a, status: 'acknowledged' } : a
      );
      set({ anomalies });
    } catch (error) {
      set({ error: error.message });
    }
  }
}));
```

#### Styling with Tailwind CSS
```typescript
// Using design system classes
const buttonClasses = {
  base: 'px-4 py-2 rounded-md font-medium transition-colors',
  variant: {
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300',
    danger: 'bg-red-600 text-white hover:bg-red-700'
  },
  size: {
    sm: 'px-2 py-1 text-sm',
    md: 'px-4 py-2',
    lg: 'px-6 py-3 text-lg'
  }
};
```

## 🤖 MLOps Development

### Model Development Workflow

```python
# scripts/mlops/train_model.py
from app.mlops.experiment_tracker import ExperimentTracker
from app.mlops.model_registry import ModelRegistry
from app.mlops.dataset_manager import DatasetManager

def train_anomaly_model():
    # Initialize MLOps components
    tracker = ExperimentTracker()
    registry = ModelRegistry()
    data_manager = DatasetManager()
    
    # Create experiment
    experiment = tracker.create_experiment(
        name="anomaly_detection_v2",
        description="Improved anomaly detection with ensemble methods",
        target_metric="f1_score",
        maximize_metric=True
    )
    
    # Start run
    run = tracker.start_run(
        experiment_id=experiment.experiment_id,
        run_name="isolation_forest_ensemble",
        parameters={
            'n_estimators': 100,
            'contamination': 0.1,
            'random_state': 42
        }
    )
    
    # Load dataset
    dataset = data_manager.load_dataset("training_data_v3")
    
    # Train model
    model = train_isolation_forest(dataset, run.parameters)
    
    # Log metrics
    tracker.log_metric('accuracy', 0.95)
    tracker.log_metric('precision', 0.92)
    tracker.log_metric('recall', 0.88)
    tracker.log_metric('f1_score', 0.90)
    
    # Register model
    model_metadata = registry.register_model(
        model=model,
        name="anomaly_detector_v2",
        description="Ensemble anomaly detection model",
        model_type="anomaly_detection",
        algorithm="isolation_forest_ensemble",
        framework="scikit-learn",
        input_features=dataset.feature_names,
        training_data_hash=dataset.checksum,
        hyperparameters=run.parameters,
        metrics={'f1_score': 0.90},
        created_by="ml_team"
    )
    
    # End run
    tracker.end_run()
    
    return model_metadata
```

### Model Deployment

```python
# app/services/ml_service.py
from app.mlops.model_registry import ModelRegistry
from app.mlops.model_monitor import ModelMonitor

class MLService:
    def __init__(self):
        self.registry = ModelRegistry()
        self.monitor = ModelMonitor()
        self.model = None
        self.model_version = None
    
    def load_production_model(self, model_name: str):
        """Load the current production model"""
        model_metadata = self.registry.get_production_model(model_name)
        if model_metadata:
            self.model = self.registry.load_model(
                model_metadata.model_id, 
                model_metadata.version
            )
            self.model_version = model_metadata.version
            
            # Start monitoring
            self.monitor.start_monitoring(
                model_metadata.model_id,
                model_metadata.version
            )
    
    def predict(self, features: dict) -> dict:
        """Make prediction with monitoring"""
        if not self.model:
            raise ValueError("No model loaded")
        
        start_time = time.time()
        
        try:
            # Make prediction
            prediction = self.model.predict([list(features.values())])[0]
            confidence = self.model.decision_function([list(features.values())])[0]
            
            prediction_time = (time.time() - start_time) * 1000
            
            # Log prediction for monitoring
            self.monitor.log_prediction(
                model_id=self.model_version.model_id,
                model_version=self.model_version.version,
                input_features=features,
                prediction={'anomaly': bool(prediction == -1), 'score': float(confidence)},
                confidence=abs(float(confidence)),
                prediction_time_ms=prediction_time
            )
            
            return {
                'anomaly': bool(prediction == -1),
                'confidence': abs(float(confidence)),
                'model_version': self.model_version
            }
            
        except Exception as e:
            # Log error for monitoring
            self.monitor.log_prediction(
                model_id=self.model_version.model_id,
                model_version=self.model_version.version,
                input_features=features,
                prediction=None,
                error_message=str(e)
            )
            raise
```

## 📝 Contributing Guidelines

### Code Review Checklist

#### General
- [ ] Code follows project style guidelines
- [ ] No hardcoded values or secrets
- [ ] Error handling is appropriate
- [ ] Logging is adequate for debugging
- [ ] Performance implications considered

#### Backend
- [ ] API endpoints follow RESTful conventions
- [ ] Input validation is implemented
- [ ] Database queries are optimized
- [ ] Tests cover new functionality
- [ ] Documentation is updated

#### Frontend
- [ ] Components are reusable and well-structured
- [ ] Accessibility guidelines followed
- [ ] Mobile responsiveness verified
- [ ] State management is appropriate
- [ ] Performance optimizations applied

#### Security
- [ ] No sensitive data in code
- [ ] Input sanitization implemented
- [ ] Authentication/authorization checked
- [ ] SQL injection prevention
- [ ] XSS protection measures

### Pull Request Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added for new features
- [ ] No breaking changes without migration path
```

### Release Process

```bash
# 1. Prepare release
git checkout main
git pull origin main

# 2. Update version
npm version patch # or minor/major
git push origin main --tags

# 3. Create release notes
gh release create v1.0.1 --title "Release v1.0.1" --notes-file CHANGELOG.md

# 4. Deploy to staging
helm upgrade smartcloudops-ai-staging ./deploy/helm/smartcloudops-ai \
  --set image.tag=v1.0.1 \
  --namespace smartcloudops-staging

# 5. Run staging tests
npm run test:staging

# 6. Deploy to production
helm upgrade smartcloudops-ai ./deploy/helm/smartcloudops-ai \
  --set image.tag=v1.0.1 \
  --namespace smartcloudops
```

---

## 📚 Related Documentation

- [Architecture Overview](./ARCHITECTURE.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [API Reference](./API_REFERENCE_COMPLETE.md)
- [Operations Runbook](./OPS_RUNBOOK.md)

---

*Happy coding! 🚀 If you have questions, reach out to the development team on Slack #dev-team*
