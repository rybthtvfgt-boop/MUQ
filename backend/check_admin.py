import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'muq_system.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Check if admin exists
admin = User.objects.filter(username='admin').first()
if admin:
    print(f"Admin user exists: {admin.name}")
    print(f"User type: {admin.user_type}")
    print(f"Is superuser: {admin.is_superuser}")
    print(f"Is active: {admin.is_active}")
else:
    print("Admin user does not exist")
    print("Creating admin user...")
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@muq.com',
        password='admin123',
        name='المدير العام',
        user_type='admin'
    )
    print("Admin user created successfully")
