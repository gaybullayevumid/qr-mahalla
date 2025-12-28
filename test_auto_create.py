import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.houses.models import House
from apps.users.models import User

print("=" * 50)
print("TESTING AUTO-CREATE ON CLAIM")
print("=" * 50)

# Get unclaimed count before
before = House.objects.filter(owner__isnull=True).count()
print(f"\n📊 Unclaimed houses BEFORE: {before}")

# Get an unclaimed house
unclaimed = House.objects.filter(owner__isnull=True).first()
print(f"\n🏠 Claiming house: {unclaimed.address} (ID: {unclaimed.id})")

# Get a user to assign as owner
user = User.objects.filter(role='client').first()
if not user:
    print("⚠️  No user with role 'client' found, using any user...")
    user = User.objects.first()

print(f"👤 Assigning to user: {user.phone}")

# Assign owner (this should trigger the signal)
unclaimed.owner = user
unclaimed.save()
print("✅ House saved with owner")

# Check unclaimed count after
after = House.objects.filter(owner__isnull=True).count()
print(f"\n📊 Unclaimed houses AFTER: {after}")

if after == 10:
    print("✅ SUCCESS! Signal worked - maintained 10 unclaimed houses")
else:
    print(f"⚠️  Expected 10, but got {after}")

print("\n" + "=" * 50)
