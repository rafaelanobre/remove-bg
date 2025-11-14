#!/bin/bash
set -e

echo "Running database migrations..."
/app/.venv/bin/python manage.py migrate --noinput

echo "Collecting static files..."
/app/.venv/bin/python manage.py collectstatic --noinput

# Execute the CMD (gunicorn)
exec "$@"