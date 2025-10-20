#!/bin/bash
set -e

echo "Collecting static files..."
/app/.venv/bin/python manage.py collectstatic --noinput

# Execute the CMD (gunicorn)
exec "$@"