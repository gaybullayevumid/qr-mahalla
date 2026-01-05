import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.houses.models import House

# Update all existing houses to be marked as created_by_agent
houses = House.objects.all()
count = houses.count()

print(f"Updating {count} houses to created_by_agent=True...")

houses.update(created_by_agent=True)

print(f"✓ Updated {count} houses")
print("\nThese houses will NOT have QR codes auto-generated.")
