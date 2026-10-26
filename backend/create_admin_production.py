"""
Create admin user for production deployment.
Run this script after migrations are applied.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'muq_system.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_admin():
    """Create admin user if it doesn't exist."""
    admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin@123!')
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@muq.com')

    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email=admin_email,
            password=admin_password
        )
        print("✅ Admin user created successfully")
        print(f"   Username: admin")
        print(f"   Email: {admin_email}")
        print(f"   Password: {'********' if admin_password else 'Not set'}")
    else:
        print("ℹ️  Admin user already exists")

if __name__ == '__main__':
    create_admin()
