#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'muq_system.settings')
django.setup()

from users.models import User

# Create admin user if it doesn't exist
if not User.objects.filter(username='muq').exists():
    print("Creating admin user 'muq' for production...")
    User.objects.create_superuser(
        username='muq',
        email='admin@muq.com',
        password='12345',
        user_type='admin',
        first_name='Admin',
        last_name='User'
    )
    print("Admin user created successfully!")
else:
    print("Admin user 'muq' already exists.")
