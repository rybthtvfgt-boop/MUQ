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

# Execute the CMD
exec "$@"
