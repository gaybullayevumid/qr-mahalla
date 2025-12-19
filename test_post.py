import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.regions.models import Region, District
from apps.regions.serializers import DistrictCreateSerializer

# Get last region
region = Region.objects.last()
print(f"Region: {region.id} - {region.name}")

# Try to create district via serializer
data = {"name": "Test Tuman", "region": region.id}

serializer = DistrictCreateSerializer(data=data)
if serializer.is_valid():
    district = serializer.save()
    print(f"✅ District created: {district.id} - {district.name}")
else:
    print(f"❌ Validation errors: {serializer.errors}")
