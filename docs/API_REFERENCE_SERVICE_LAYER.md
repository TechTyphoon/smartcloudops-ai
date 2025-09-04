# 🔧 SmartCloudOps AI - Service Layer API Reference

**Complete API reference for Phase 1 service layer architecture**

## 📋 Overview

This document provides comprehensive API reference for the service layer implementation completed in Phase 1. The service layer provides clean separation of business logic from API endpoints, enabling better testability, maintainability, and security.

---

## 🏗️ Service Layer Architecture

### **Design Principles**
- **Separation of Concerns**: Business logic isolated from HTTP concerns
- **Input Validation**: Comprehensive validation at service boundary  
- **Error Handling**: Consistent exception handling patterns
- **Testability**: Services are easily unit testable
- **Security**: Input sanitization and validation built-in

### **Service Pattern**
```python
# Standard service pattern used across all services
class ServiceName:
    def __init__(self):
        """Initialize service with dependencies."""
        
    def operation_name(self, data: Dict) -> Dict:
        """Perform operation with validation.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Result dictionary
            
        Raises:
            ValueError: When validation fails
        """
        # 1. Validate inputs
        self._validate_input(data)
        
        # 2. Process business logic
        result = self._process_business_logic(data)
        
        # 3. Return structured result
        return result
```

---

## 🔍 AnomalyService API

**File**: `app/services/anomaly_service.py`  
**Tests**: `tests/unit/test_anomaly_service.py` (29 tests)  
**Coverage**: Business logic, validation, edge cases, error handling

### **Methods**

#### `get_anomalies(page, per_page, status, severity, source)`
```python
def get_anomalies(
    self, 
    page: int = 1, 
    per_page: int = 20,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    source: Optional[str] = None
) -> Tuple[List[Dict], Dict]:
```

**Description**: Retrieve anomalies with pagination and filtering

**Parameters**:
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 20, max: 100)
- `status` (str, optional): Filter by status ("open", "acknowledged", "resolved")
- `severity` (str, optional): Filter by severity ("low", "medium", "high", "critical")
- `source` (str, optional): Filter by source ("ml_model", "manual", "system")

**Returns**: Tuple of (anomalies_list, pagination_info)
```python
# Example return value
(
    [
        {
            "id": 1,
            "title": "High CPU Usage Detected",
            "description": "CPU usage exceeded 90% threshold",
            "severity": "high",
            "status": "open",
            "anomaly_score": 0.95,
            "confidence": 0.87,
            "source": "ml_model",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }
    ],
    {
        "page": 1,
        "per_page": 20,
        "total": 1,
        "pages": 1
    }
)
```

**Example Usage**:
```python
# Get all anomalies
anomalies, pagination = service.get_anomalies()

# Get high severity anomalies  
high_anomalies, pagination = service.get_anomalies(severity="high")

# Get paginated results
page2_anomalies, pagination = service.get_anomalies(page=2, per_page=10)
```

#### `get_anomaly_by_id(anomaly_id)`
```python
def get_anomaly_by_id(self, anomaly_id: int) -> Optional[Dict]:
```

**Description**: Get a specific anomaly by ID

**Parameters**:
- `anomaly_id` (int): Unique anomaly identifier

**Returns**: Anomaly dictionary or None if not found

**Example Usage**:
```python
anomaly = service.get_anomaly_by_id(1)
if anomaly:
    print(f"Found anomaly: {anomaly['title']}")
else:
    print("Anomaly not found")
```

#### `create_anomaly(anomaly_data)`
```python
def create_anomaly(self, anomaly_data: Dict) -> Dict:
```

**Description**: Create a new anomaly with comprehensive validation

**Parameters**:
- `anomaly_data` (Dict): Anomaly data dictionary

**Required Fields**:
- `title` (str): Anomaly title
- `description` (str): Detailed description
- `severity` (str): One of ["low", "medium", "high", "critical"]
- `anomaly_score` (float): Score between 0.0 and 1.0
- `confidence` (float): Confidence between 0.0 and 1.0

**Optional Fields**:
- `status` (str): Status (default: "open")
- `source` (str): Source (default: "manual")

**Returns**: Created anomaly dictionary with assigned ID and timestamps

**Raises**:
- `ValueError`: When required fields are missing or invalid

**Example Usage**:
```python
# Create new anomaly
anomaly_data = {
    "title": "Database Connection Timeout",
    "description": "Database queries are timing out after 30 seconds",
    "severity": "high",
    "anomaly_score": 0.85,
    "confidence": 0.92,
    "source": "monitoring_system"
}

try:
    new_anomaly = service.create_anomaly(anomaly_data)
    print(f"Created anomaly with ID: {new_anomaly['id']}")
except ValueError as e:
    print(f"Validation error: {e}")
```

#### `update_anomaly(anomaly_id, update_data)`
```python
def update_anomaly(self, anomaly_id: int, update_data: Dict) -> Optional[Dict]:
```

**Description**: Update an existing anomaly

**Parameters**:
- `anomaly_id` (int): Anomaly ID to update
- `update_data` (Dict): Fields to update

**Updatable Fields**:
- `title`, `description`, `severity`, `status`, `explanation`

**Returns**: Updated anomaly dictionary or None if not found

**Example Usage**:
```python
# Update anomaly status
updated = service.update_anomaly(1, {"status": "acknowledged"})

# Update multiple fields
updated = service.update_anomaly(1, {
    "title": "Updated Title",
    "severity": "critical"
})
```

#### `acknowledge_anomaly(anomaly_id)` / `resolve_anomaly(anomaly_id)`
```python
def acknowledge_anomaly(self, anomaly_id: int) -> Optional[Dict]:
def resolve_anomaly(self, anomaly_id: int) -> Optional[Dict]:
```

**Description**: Change anomaly status with timestamp tracking

**Parameters**:
- `anomaly_id` (int): Anomaly ID

**Returns**: Updated anomaly or None if not found

**Example Usage**:
```python
# Acknowledge an anomaly
acknowledged = service.acknowledge_anomaly(1)

# Resolve an anomaly  
resolved = service.resolve_anomaly(1)
```

#### `delete_anomaly(anomaly_id)`
```python
def delete_anomaly(self, anomaly_id: int) -> Optional[Dict]:
```

**Description**: Delete an anomaly

**Parameters**:
- `anomaly_id` (int): Anomaly ID to delete

**Returns**: Deleted anomaly dictionary or None if not found

#### `get_anomaly_statistics()`
```python
def get_anomaly_statistics(self) -> Dict:
```

**Description**: Get comprehensive anomaly statistics

**Returns**: Statistics dictionary
```python
{
    "total_anomalies": 42,
    "by_severity": {"high": 15, "medium": 20, "low": 7},
    "by_status": {"open": 25, "acknowledged": 10, "resolved": 7},
    "by_source": {"ml_model": 30, "manual": 8, "system": 4}
}
```

---

## 🔧 RemediationService API

**File**: `app/services/remediation_service.py`  
**Tests**: `tests/unit/test_remediation_service.py` (35 tests)

### **Key Methods**

#### `get_remediation_actions(filters...)`
Get remediation actions with filtering and pagination

#### `create_remediation_action(action_data)`
Create new remediation action with validation:
- Required: `anomaly_id`, `action_type`, `action_name`, `description`
- Valid action types: `scale_up`, `scale_down`, `restart_service`, `custom`
- Valid priorities: `low`, `medium`, `high`, `critical`

#### `execute_remediation_action(action_id)`
Execute a pending or approved remediation action

#### `approve_remediation_action(action_id)` / `cancel_remediation_action(action_id)`
Change action status with workflow validation

#### `get_remediation_statistics()`
Get success rates and execution statistics

---

## 💬 FeedbackService API

**File**: `app/services/feedback_service.py`  
**Tests**: `tests/unit/test_feedback_service.py` (32 tests)

### **Key Methods**

#### `get_feedback(filters...)`
Get user feedback with filtering and pagination

#### `create_feedback(feedback_data)`
Create new feedback with validation:
- Required: `feedback_type`, `title`, `description`
- Valid types: `bug_report`, `feature_request`, `general`, `performance`
- Optional: `rating` (1-5), `priority`, `user_id`, `tags`

#### `get_feedback_statistics()`
Get feedback statistics including rating distributions

#### `get_feedback_types()`
Get available feedback types with descriptions

---

## 🤖 AIService API

**File**: `app/services/ai_service.py`  
**Purpose**: AI analysis and ChatOps integration

### **Key Methods**

#### `analyze_query(query_data)`
Process AI analysis requests

#### `get_analysis_history(filters...)`
Get historical analysis data

#### `chat_completion(messages)`
Handle ChatOps conversations

---

## 🧠 MLService API

**File**: `app/services/ml_service.py`  
**Purpose**: Machine learning operations and model management

### **Key Methods**

#### `predict_anomaly(data)`
Run anomaly prediction on input data

#### `get_model_info()`
Get current model information and performance metrics

#### `retrain_model(training_data)`
Trigger model retraining

---

## 🔗 API Integration Patterns

### **Flask Blueprint Integration**
```python
# app/api/anomalies.py
from flask import Blueprint, jsonify, request
from app.services.anomaly_service import AnomalyService

anomalies_bp = Blueprint("anomalies", __name__, url_prefix="/api/anomalies")
anomaly_service = AnomalyService()

@anomalies_bp.route("/", methods=["GET"])
def get_anomalies():
    try:
        # Extract parameters
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        status = request.args.get("status")
        
        # Call service layer
        anomalies, pagination = anomaly_service.get_anomalies(
            page=page, per_page=per_page, status=status
        )
        
        # Return standardized response
        return jsonify({
            "status": "success",
            "data": {
                "anomalies": anomalies,
                "pagination": pagination
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to retrieve anomalies: {str(e)}"
        }), 500
```

### **Error Handling Pattern**
```python
@anomalies_bp.route("/", methods=["POST"])
def create_anomaly():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No data provided"
            }), 400

        # Service layer handles validation
        new_anomaly = anomaly_service.create_anomaly(data)

        return jsonify({
            "status": "success",
            "message": "Anomaly created successfully",
            "data": {"anomaly": new_anomaly}
        }), 201

    except ValueError as ve:
        # Validation errors (400)
        return jsonify({
            "status": "error",
            "message": str(ve)
        }), 400
    except Exception as e:
        # Internal errors (500)
        return jsonify({
            "status": "error",
            "message": f"Failed to create anomaly: {str(e)}"
        }), 500
```

### **Response Format Standards**
All API responses follow this format:
```python
{
    "status": "success" | "error",
    "message": "Human readable message",
    "data": {
        # Response payload
    }
}
```

Success responses (2xx):
```python
{
    "status": "success",
    "data": {
        "anomaly": {...},
        "pagination": {...}
    }
}
```

Error responses (4xx/5xx):
```python
{
    "status": "error",
    "message": "Validation failed: Missing required field 'title'"
}
```

---

## 🧪 Testing Service Layer

### **Unit Test Structure**
```python
# tests/unit/test_anomaly_service.py
class TestAnomalyService:
    def setup_method(self):
        self.service = AnomalyService()
    
    def test_get_anomalies_default_pagination(self):
        """Test getting anomalies with default pagination."""
        anomalies, pagination = self.service.get_anomalies()
        
        assert isinstance(anomalies, list)
        assert isinstance(pagination, dict)
        assert pagination["page"] == 1
        assert pagination["per_page"] == 20
    
    def test_create_anomaly_valid_data(self):
        """Test creating an anomaly with valid data."""
        anomaly_data = {
            "title": "Test Anomaly",
            "description": "Test description",
            "severity": "medium",
            "anomaly_score": 0.75,
            "confidence": 0.85
        }
        
        new_anomaly = self.service.create_anomaly(anomaly_data)
        
        assert new_anomaly["title"] == "Test Anomaly"
        assert new_anomaly["severity"] == "medium"
        assert new_anomaly["status"] == "open"
    
    def test_create_anomaly_invalid_severity(self):
        """Test validation error handling."""
        anomaly_data = {
            "title": "Test",
            "description": "Test",
            "severity": "invalid",
            "anomaly_score": 0.75,
            "confidence": 0.85
        }
        
        with pytest.raises(ValueError, match="Invalid severity"):
            self.service.create_anomaly(anomaly_data)
```

### **Running Service Tests**
```bash
# Run all service tests
pytest tests/unit/test_*service*.py -v

# Run specific service tests
pytest tests/unit/test_anomaly_service.py -v

# Run with coverage
pytest tests/unit/test_*service*.py --cov=app.services --cov-report=html
```

---

## 🛡️ Security Considerations

### **Input Validation**
All services implement comprehensive input validation:
- Required field validation
- Type checking
- Range validation for numeric fields
- Enum validation for categorical fields
- String length limits

### **Error Handling**
Services use consistent error handling:
- `ValueError` for validation errors
- `Exception` for unexpected errors  
- No sensitive data in error messages
- Proper logging for debugging

### **Security Testing**
Security validation tests cover:
- SQL injection prevention
- XSS prevention
- Command injection prevention
- Path traversal prevention
- Data leakage prevention

---

## 📊 Performance Considerations

### **Pagination**
All list operations support pagination:
- Default page size: 20
- Maximum page size: 100
- Efficient offset-based pagination

### **Filtering**
Services support filtering to reduce data transfer:
- Status-based filtering
- Severity-based filtering
- Source-based filtering
- Date range filtering (where applicable)

### **Caching**
Consider implementing caching for:
- Statistics calculations
- Frequently accessed anomalies
- Model predictions

---

## 🔮 Future Enhancements

### **Database Integration**
Replace mock data with SQLAlchemy models:
```python
# Future: Real database implementation
def get_anomalies(self, filters...):
    with get_db_session() as session:
        query = session.query(Anomaly)
        
        if filters.get('status'):
            query = query.filter(Anomaly.status == filters['status'])
            
        return query.offset(offset).limit(per_page).all()
```

### **Async Support**
Add async operations for improved performance:
```python
async def create_anomaly_async(self, data: Dict) -> Dict:
    # Async validation and processing
    pass
```

### **Event Sourcing**
Add event tracking for audit and replay:
```python
def create_anomaly(self, data: Dict) -> Dict:
    # Create anomaly
    anomaly = self._create_anomaly_record(data)
    
    # Record event
    self._record_event("anomaly_created", anomaly.id, data)
    
    return anomaly
```

---

*Last Updated: September 2025*  
*Version: Phase 1 Service Layer Complete*
