#!/usr/bin/env python3
"""
API Gateway Service for Smart CloudOps AI
Central entry point for all API requests
"""

from flask import Flask, jsonify, request
import requests
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "api-gateway"})

@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def gateway(path):
    # Route requests to appropriate services
    if path.startswith('ml/'):
        target = 'http://ml-processor:5000'
        path = path[3:]  # Remove 'ml/' prefix
    else:
        target = 'http://smartcloudops-app:5000'
    
    try:
        resp = requests.request(
            method=request.method,
            url=f"{target}/{path}",
            headers=dict(request.headers),
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False
        )
        return resp.content, resp.status_code, resp.headers.items()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
