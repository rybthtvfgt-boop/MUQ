"""
Check admin user details
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'muq_system.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

admin = User.objects.filter(username='admin').first()
if admin:
    print("Admin user found:")
    print(f"  Username: {admin.username}")
    print(f"  Name: {admin.name}")
    print(f"  User Type: {admin.user_type}")
    print(f"  Is Superuser: {admin.is_superuser}")
    print(f"  Is Active: {admin.is_active}")
    print(f"  Email: {admin.email}")
else:
    print("Admin user not found")
