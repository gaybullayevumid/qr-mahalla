import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.regions.models import Region, District, Mahalla

# Check data
print("=" * 50)
print("DATABASE CHECK")
print("=" * 50)

regions = Region.objects.all()[:5]
print(f"\n✅ Regions in DB: {Region.objects.count()}")
for r in regions:
    print(f"  - ID: {r.id}, Name: {r.name}")

districts = District.objects.all()[:5]
print(f"\n✅ Districts in DB: {District.objects.count()}")
for d in districts:
    print(f"  - ID: {d.id}, Name: {d.name}, Region: {d.region.name}")

mahallas = Mahalla.objects.all()[:5]
print(f"\n✅ Mahallas in DB: {Mahalla.objects.count()}")
for m in mahallas:
    print(f"  - ID: {m.id}, Name: {m.name}, District: {m.district.name}")

# Test serializers
print("\n" + "=" * 50)
print("SERIALIZER TEST")
print("=" * 50)

from apps.regions.serializers import (
    RegionSerializer,
    DistrictSerializer,
    MahallaSerializer,
)
from rest_framework.renderers import JSONRenderer

region = Region.objects.first()
serializer = RegionSerializer(region)
print(f"\n✅ Region Serializer Output:")
print(JSONRenderer().render(serializer.data).decode())

district = District.objects.first()
serializer = DistrictSerializer(district)
print(f"\n✅ District Serializer Output:")
print(JSONRenderer().render(serializer.data).decode())

mahalla = Mahalla.objects.first()
serializer = MahallaSerializer(mahalla)
print(f"\n✅ Mahalla Serializer Output:")
print(JSONRenderer().render(serializer.data).decode())

print("\n" + "=" * 50)
print("✅ All checks passed!")
print("=" * 50)
