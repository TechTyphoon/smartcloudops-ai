#!/usr/bin/env python3
"""
Simple Database Connection Test
"""

import os
import psycopg2

def test_simple_connection():
    """Test simple database connection"""
    
    # Set environment variables
    os.environ['POSTGRES_USER'] = 'cloudops'
    os.environ['POSTGRES_PASSWORD'] = 'cloudops'
    os.environ['POSTGRES_HOST'] = 'localhost'
    os.environ['POSTGRES_PORT'] = '5434'
    os.environ['POSTGRES_DB'] = 'cloudops'
    
    print("🔍 Testing simple database connection...")
    print(f"Host: {os.environ['POSTGRES_HOST']}")
    print(f"Port: {os.environ['POSTGRES_PORT']}")
    print(f"Database: {os.environ['POSTGRES_DB']}")
    print(f"User: {os.environ['POSTGRES_USER']}")
    
    try:
        conn = psycopg2.connect(
            host=os.environ['POSTGRES_HOST'],
            port=os.environ['POSTGRES_PORT'],
            database=os.environ['POSTGRES_DB'],
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD']
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print(f"✅ SUCCESS: {version[0]}")
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

if __name__ == "__main__":
    test_simple_connection()
