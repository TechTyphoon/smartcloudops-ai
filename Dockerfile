# =====================================================
# 🏗️ BUILDER STAGE - Install dependencies and build
# =====================================================
FROM python:3.10-slim as builder

# Set working directory
WORKDIR /app

# Set environment variables for Python optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        curl \
        gcc \
        g++ \
        ca-certificates \
        && rm -rf /var/lib/apt/lists/* \
        && apt-get clean

# Copy requirements file
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --verbose -r requirements.txt \
    && pip list \
    && pip install --no-cache-dir safety \
    && safety check --bare --output json > /tmp/security-report.json || true

# =====================================================
# 🚀 FINAL STAGE - Production runtime
# =====================================================
FROM python:3.10-slim

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser

# Set working directory
WORKDIR /app

# Install runtime system dependencies only
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        && rm -rf /var/lib/apt/lists/* \
        && apt-get clean

# Copy installed Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source code
COPY app/ ./app/
COPY scripts/ ./scripts/
COPY ml_models/ ./ml_models/
COPY templates/ ./templates/
COPY gunicorn.conf.py ./
COPY start.sh ./

# Create logs directory
RUN mkdir -p logs

# Set ownership to non-root user
RUN chown -R appuser:appuser /app \
    && chmod +x start.sh

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Health check with timeout
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Set production environment variables
ENV FLASK_ENV=production \
    FLASK_DEBUG=false \
    LOG_LEVEL=INFO \
    LOG_JSON=true \
    PYTHONPATH=/app

# Run the application with proper startup script
CMD ["./start.sh"]