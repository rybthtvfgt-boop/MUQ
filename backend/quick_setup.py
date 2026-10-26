import os
import sys
import django

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'muq_system.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("Checking for admin user...")
admin = User.objects.filter(username='admin').first()

if admin:
    print(f"Admin user exists: {admin.name}")
    print(f"User type: {admin.user_type}")
    print(f"Is superuser: {admin.is_superuser}")
    print(f"Is active: {admin.is_active}")
else:
    print("Creating admin user...")
    try:
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@muq.com',
            password='admin123',
            name='المدير العام',
            user_type='admin'
        )
        print("✅ Admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        print("Trying to create regular user...")
        try:
            admin = User.objects.create_user(
                username='admin',
                email='admin@muq.com',
                password='admin123',
                name='المدير العام',
                user_type='admin'
            )
            admin.is_superuser = True
            admin.is_staff = True
            admin.save()
            print("✅ Admin user created successfully!")
        except Exception as e2:
            print(f"❌ Error: {e2}")

print("\nAll users in database:")
for user in User.objects.all():
    print(f"  - {user.username} ({user.user_type})")
