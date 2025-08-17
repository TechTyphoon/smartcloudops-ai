#!/usr/bin/env python3
"""
Database Connection Test Script
"""

import os
import psycopg2
from urllib.parse import urlparse

def test_database_connection():
    """Test database connection with different configurations."""
    
    # Test configurations
    configs = [
        {
            "name": "Docker Compose URL",
            "url": "postgresql+psycopg://cloudops:cloudops@postgres:5432/cloudops"
        },
        {
            "name": "Direct PostgreSQL URL",
            "url": "postgresql://cloudops:cloudops@localhost:5434/cloudops"
        },
        {
            "name": "Environment Variable",
            "url": os.getenv("DATABASE_URL", "postgresql://cloudops:cloudops@localhost:5434/cloudops")
        }
    ]
    
    for config in configs:
        print(f"\n🔍 Testing: {config['name']}")
        print(f"URL: {config['url']}")
        
        try:
            # Parse the URL
            parsed = urlparse(config['url'].replace('postgresql+psycopg://', 'postgresql://'))
            
            # Connect using psycopg2
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                database=parsed.path[1:],  # Remove leading slash
                user=parsed.username,
                password=parsed.password
            )
            
            # Test query
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            
            print(f"✅ SUCCESS: {version[0]}")
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"❌ FAILED: {e}")

if __name__ == "__main__":
    print("🔍 Database Connection Test")
    print("=" * 50)
    test_database_connection()
