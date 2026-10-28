#!/bin/sh
set -e

# Run migrations
python manage.py migrate --noinput

# Create admin user if needed
python manage.py shell << 'EOF'
from users.models import User
if not User.objects.filter(username='muq').exists():
    User.objects.create_superuser(
        username='muq',
        email='admin@muq.com',
        password='12345',
        user_type='admin',
        first_name='Admin',
        last_name='User'
    )
    print("Admin user 'muq' created!")
EOF

# Create dataset directory structure
mkdir -p /app/dataset/training_data/smoking
mkdir -p /app/dataset/training_data/non_smoking
mkdir -p /app/dataset/validation_data/smoking
mkdir -p /app/dataset/validation_data/non_smoking
mkdir -p /app/dataset/testing_data/smoking
mkdir -p /app/dataset/testing_data/non_smoking
mkdir -p /app/dataset/trained_models

echo "Dataset directory structure created"

# Execute the CMD
exec "$@"
