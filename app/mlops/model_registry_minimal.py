"""
Model Registry Minimal - Database Models
Auto-generated minimal implementation.
"""

from datetime import datetime
from typing import Optional

class BaseModel:
    """Base model class."""
    
    def __init__(self):
        """Initialize."""
        self.id = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

class ModelRegistryMinimalModel(BaseModel):
    """Model for model_registry_minimal."""
    
    def __init__(self, name: str = "default"):
        """Initialize."""
        super().__init__()
        self.name = name
