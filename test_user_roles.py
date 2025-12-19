"""
Test permissions for regular user
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.users.models import User

print("=" * 50)
print("USER ROLES CHECK")
print("=" * 50)

users = User.objects.all()[:10]

for user in users:
    print(f"\nPhone: {user.phone}")
    print(f"Role: {user.role}")
    print(f"Is authenticated: {user.is_authenticated}")

# Find a regular user
regular_users = User.objects.filter(role="user")
print(f"\n{'=' * 50}")
print(f"Total regular users (role='user'): {regular_users.count()}")

if regular_users.exists():
    user = regular_users.first()
    print(f"\nSample regular user:")
    print(f"  Phone: {user.phone}")
    print(f"  Role: {user.role}")
    print(f"  Should be able to GET /api/regions/mahallas/")
else:
    print("\n⚠️  No regular users found with role='user'")
