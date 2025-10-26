#!/usr/bin/env python
"""Reset admin password"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_dispatch.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Reset admin password
try:
    admin = User.objects.get(username='admin')
    admin.set_password('admin123')
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    print("✅ Admin password reset successfully")
    print(f"   Username: admin")
    print(f"   Password: admin123")
    print(f"   Login URL: http://localhost:8000/orders/login/")
except User.DoesNotExist:
    # Create new admin user
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )
    print("✅ Admin user created successfully")
    print(f"   Username: admin")
    print(f"   Password: admin123")
    print(f"   Login URL: http://localhost:8000/orders/login/")

# Also reset testuser password
try:
    testuser = User.objects.get(username='testuser')
    testuser.set_password('testpass123')
    testuser.is_staff = True
    testuser.is_superuser = True
    testuser.save()
    print("\n✅ Test user password reset")
    print(f"   Username: testuser")
    print(f"   Password: testpass123")
except User.DoesNotExist:
    testuser = User.objects.create_superuser(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    print("\n✅ Test user created")
    print(f"   Username: testuser")
    print(f"   Password: testpass123")
