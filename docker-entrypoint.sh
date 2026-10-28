#!/bin/sh
set -e

# Run migrations
python manage.py migrate --noinput

# Execute the CMD
exec "$@"
