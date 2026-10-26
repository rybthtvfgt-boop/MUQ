"""
Initialize MUQ Database
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'muq_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import call_command

User = get_user_model()

print("Initializing MUQ Database...")
print("=" * 50)

# Run migrations
print("Running migrations...")
call_command('migrate', verbosity=0)
print("Migrations completed")

# Create admin user
print("Creating admin user...")
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@muq.com',
        password='admin123',
        name='Admin User',
        user_type='admin'
    )
    print("Admin user created successfully")
    print("Username: admin")
    print("Password: admin123")
else:
    print("Admin user already exists")
    admin = User.objects.get(username='admin')
    admin.set_password('admin123')
    admin.save()
    print("Admin password reset to admin123")

print("=" * 50)
print("Database initialization completed!")
print("=" * 50)
