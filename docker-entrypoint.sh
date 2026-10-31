#!/bin/sh
set -e

# Run migrations
python manage.py migrate --noinput

# Create or reset admin user
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
    print("Admin user 'muq' created! Password: 12345")
else:
    # Reset password if user exists
    user = User.objects.get(username='muq')
    user.set_password('12345')
    user.save()
    print("Admin user 'muq' password reset to: 12345")
EOF

# Create dataset directory structure
mkdir -p /app/dataset/training_data/smoking
mkdir -p /app/dataset/training_data/non_smoking
mkdir -p /app/dataset/validation_data/smoking
mkdir -p /app/dataset/validation_data/non_smoking
mkdir -p /app/dataset/testing_data/smoking
mkdir -p /app/dataset/testing_data/non_smoking
mkdir -p /app/dataset/trained_models



# Execute the CMD
exec "$@"
