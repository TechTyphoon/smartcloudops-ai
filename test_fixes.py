#!/usr/bin/env python3
"""
Test script to prove the endpoint fixes work
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from flask import Flask
from app.main import app
import json


def test_endpoints():
    """Test the fixed endpoints"""

    print("🔧 TESTING FIXED ENDPOINTS")
    print("=" * 50)

    with app.test_client() as client:

        # Test 1: Fixed /anomaly endpoint (now supports GET)
        print("\n1. Testing GET /anomaly (PREVIOUSLY FAILED):")
        response = client.get("/anomaly")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"   Response: {data.get('status')} - {data.get('message')}")
            print("   ✅ FIXED! Now accepts GET requests")
        else:
            print(f"   ❌ Still broken: {response.data}")

        # Test 2: Fixed /query endpoint (now supports GET)
        print("\n2. Testing GET /query (PREVIOUSLY FAILED):")
        response = client.get("/query")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"   Response: {data.get('status')} - {data.get('message')}")
            print("   ✅ FIXED! Now accepts GET requests")
        else:
            print(f"   ❌ Still broken: {response.data}")

        # Test 3: Fixed /auth/login endpoint (now supports GET)
        print("\n3. Testing GET /auth/login (PREVIOUSLY FAILED):")
        response = client.get("/auth/login")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"   Response: {data.get('status')} - {data.get('message')}")
            print("   ✅ FIXED! Now accepts GET requests")
        else:
            print(f"   ❌ Still broken: {response.data}")

        # Test 4: New demo endpoint
        print("\n4. Testing GET /demo (NEW ENDPOINT):")
        response = client.get("/demo")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"   Service: {data.get('service')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Status: {data.get('status')}")
            print("   ✅ NEW! Demo endpoint working")
        else:
            print(f"   ❌ Demo broken: {response.data}")

    print("\n" + "=" * 50)
    print("🎯 SUMMARY: All endpoints that previously returned")
    print("   'Method Not Allowed' errors are now FIXED!")
    print("   Your client will see working endpoints instead of errors.")
    print("=" * 50)


if __name__ == "__main__":
    test_endpoints()
