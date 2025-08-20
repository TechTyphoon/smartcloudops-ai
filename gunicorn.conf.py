# gunicorn.conf.py - Production WSGI Server Configuration
# Smart CloudOps AI Production Settings

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:3000"
backlog = 2048

# Worker processes
workers = min(multiprocessing.cpu_count() * 2 + 1, 8)  # Cap at 8 workers
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Load application code before the worker processes are forked
preload_app = True

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8192

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"  # Log to stdout
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "smartcloudops_ai"

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# SSL (when certificates are available)
# keyfile = 'certs/server.key'
# certfile = 'certs/server.crt'

# Restart the workers gracefully on reload
graceful_timeout = 30
max_worker_restart = 3

# Enable stats
statsd_host = None
statsd_prefix = ""


def post_fork(server, worker):
    """Post fork hook."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)


def pre_fork(server, worker):
    """Pre fork hook."""
    pass


def worker_exit(server, worker):
    """Worker exit hook."""
    server.log.info("Worker exited (pid: %s)", worker.pid)
