#!/usr/bin/env python3
"""
ML Processing Service for Smart CloudOps AI
Dedicated microservice for ML operations
"""

import logging
import os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "ml-processor"})


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    # ML processing logic here
    return jsonify({"prediction": "processed", "data": data})


@app.route("/train", methods=["POST"])
def train():
    return jsonify({"status": "training_started"})


if __name__ == "__main__":
    # Use environment variable for host, default to localhost for security
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    app.run(host=host, port=5000, debug=False)
