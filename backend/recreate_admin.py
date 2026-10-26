import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'muq_system.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Delete existing admin if exists
if User.objects.filter(username='admin').exists():
    User.objects.filter(username='admin').delete()
    print('Old admin deleted')

# Create new admin
admin = User.objects.create_superuser(
    username='admin',
    email='admin@muq.com',
    password='admin123',
    name='المشرف الأعلى',
    user_type='admin'
)
print('Admin user created successfully')
print('Username: admin')
print('Password: admin123')
