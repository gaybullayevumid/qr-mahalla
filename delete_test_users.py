import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.users.models import User

# Delete only test users created by setup_test_data.py
# Test users have phone numbers like +998911000101, +998921000201, etc.

print("Deleting test users...")

# Pattern: +99891XXXXXXX or +99892XXXXXXX
test_users = User.objects.filter(phone__regex=r"^\+99891[0-9]{7}$|^\+99892[0-9]{7}$")

count = test_users.count()
print(f"Found {count} test users to delete")

if count > 0:
    for user in test_users:
        print(f"  Deleting: {user.phone} - {user.first_name} {user.last_name}")

    test_users.delete()
    print(f"\n✓ Deleted {count} test users")
else:
    print("No test users found")

print("\nRemaining users:")
remaining = User.objects.all()
for user in remaining:
    print(f"  {user.phone} - {user.first_name} {user.last_name} - {user.role}")

print(f"\nTotal remaining users: {remaining.count()}")
