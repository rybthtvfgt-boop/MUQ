import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'muq_system.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
admin = User.objects.filter(username='admin').first()
if admin:
    admin.set_password('admin123')
    admin.save()
    print('Admin password reset to admin123')
else:
    print('Admin user not found')
