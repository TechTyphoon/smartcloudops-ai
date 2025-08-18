# Use Python 3.10 slim image for smaller size and better security
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies with security updates
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        curl \
        gcc \
        g++ \
        ca-certificates \
        && rm -rf /var/lib/apt/lists/* \
        && apt-get clean

# Copy requirements first for better Docker layer caching
COPY requirements.txt requirements-production.txt ./

# Install Python dependencies with security scanning
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir safety \
    && safety check --bare --output json > /tmp/security-report.json || true

# Copy application code
COPY app/ ./app/
COPY scripts/ ./scripts/
COPY ml_models/ ./ml_models/
COPY templates/ ./templates/
COPY gunicorn.conf.py ./
COPY start.sh ./

# Create logs directory
RUN mkdir -p logs

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app \
    && chmod +x start.sh
USER appuser

# Expose port
EXPOSE 5000

# Health check with timeout
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Set default environment variables
ENV FLASK_ENV=production \
    FLASK_DEBUG=false \
    LOG_LEVEL=INFO \
    LOG_JSON=true

# Run the application with proper startup script
CMD ["./start.sh"]