import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'muq_system.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser(
        username='admin',
        email='admin@muq.com',
        password='admin123',
        name='المدير العام',
        user_type='admin'
    )
    print('Admin user created successfully')
else:
    print('Admin user already exists')
