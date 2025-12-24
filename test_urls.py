import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.urls import get_resolver
from pprint import pprint

# Get all URL patterns
resolver = get_resolver()

print("📍 All registered URL patterns:\n")
for pattern in resolver.url_patterns:
    print(f"Pattern: {pattern.pattern}")
    if hasattr(pattern, "url_patterns"):
        for sub_pattern in pattern.url_patterns:
            print(f"  - {sub_pattern}")

# Check regions specifically
from apps.regions.urls import router

print("\n📍 Regions router registered URLs:")
for url_pattern in router.urls:
    print(f"  {url_pattern.pattern} -> {url_pattern.name}")

# Check ViewSet
from apps.regions.views import RegionViewSet

print("\n📍 RegionViewSet configuration:")
viewset_instance = RegionViewSet()
print(f"  Queryset: {viewset_instance.queryset.model.__name__}")
print(f"  Basename: regions (from urls.py)")

# Check what methods ModelViewSet provides
from rest_framework.viewsets import ModelViewSet

print(f"\n📍 ModelViewSet default actions:")
print(f"  {ModelViewSet.get_extra_actions()}")
