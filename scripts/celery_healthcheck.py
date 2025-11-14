#!/usr/bin/env python
# Celery worker wrapper with HTTP health check for Cloud Run.

import os
import signal
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# Add parent directory to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class HealthCheckHandler(BaseHTTPRequestHandler):
    """Minimal HTTP handler that responds 200 OK to Cloud Run health checks."""

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')

    def log_message(self, format, *args):
        # Suppress HTTP logs to avoid cluttering Celery output
        pass


def run_health_server():
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f'Health check server listening on port {port}', flush=True)
    server.serve_forever()


def run_celery_worker():
    import django

    # Set Django settings module before calling setup()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'remove_bg.settings')
    django.setup()  # Ensure Django is fully initialized

    from remove_bg.celery import app

    print('Celery worker starting...', flush=True)
    worker = app.Worker(
        loglevel='INFO',
        concurrency=2,
        pool='prefork',
        logfile=None,  # Log to stdout
    )
    print('Starting Celery worker.start()...', flush=True)
    worker.start()


def shutdown_handler(sig, frame):
    """Handle SIGTERM/SIGINT for graceful shutdown within Cloud Run grace period."""
    print('\nShutdown signal received, exiting...', flush=True)
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)

    print('Starting Celery worker with health check endpoint', flush=True)

    # Health check server runs in daemon thread
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()

    try:
        run_celery_worker()
    except Exception as e:
        print(f'Celery worker error: {e}', flush=True)
        sys.exit(1)
