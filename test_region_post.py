import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from rest_framework.test import APIClient
from apps.users.models import User

# Create test superuser
try:
    user = User.objects.get(phone="+998901234567")
    # Make sure role is super_admin
    if user.role != "super_admin":
        user.role = "super_admin"
        user.save()
except User.DoesNotExist:
    user = User.objects.create_superuser(
        phone="+998901234567",
        password="testpass123",
        first_name="Admin",
        last_name="User",
    )
    user.role = "super_admin"  # Set role explicitly
    user.save()
    print(f"✅ Created superuser: {user.phone}")

# Test API
client = APIClient()
client.force_authenticate(user=user)

# Print auth header
print(f"\n🔐 Authentication:")
print(f"  User: {user.phone} (role: {user.role})")
print(f"  Is authenticated: {user.is_authenticated}")

# Test POST to regions
print("\n📍 Testing POST /api/regions/")
data = {"name": "Test Region"}

response = client.post("/api/regions/", data, format="json")
print(f"Status: {response.status_code}")
print(f"Response: {response.data}")

# Try with DRF test request factory directly
from rest_framework.test import APIRequestFactory
from apps.regions.views import RegionViewSet

factory = APIRequestFactory()
request = factory.post("/api/regions/", data, format="json")
request.user = user

print(f"\n📍 Testing with ViewSet directly:")
view = RegionViewSet.as_view({"post": "create"})
response = view(request)
print(f"Status: {response.status_code}")
print(f"Response: {response.data}")

# Check ViewSet configuration
from apps.regions.views import RegionViewSet

viewset = RegionViewSet()

print(f"\n🔍 ViewSet Details:")
print(f"Base classes: {RegionViewSet.__bases__}")
print(f"Has create method: {hasattr(viewset, 'create')}")
print(f"Has list method: {hasattr(viewset, 'list')}")
print(f"HTTP methods allowed: {viewset.http_method_names}")

# Check permissions for create
viewset.action = "create"
viewset.request = None
perms = viewset.get_permissions()
print(f"\nPermissions for 'create' action: {[p.__class__.__name__ for p in perms]}")

# Check what user has
print(f"\nUser details:")
print(f"  - Is superuser: {user.is_superuser}")
print(f"  - Is staff: {user.is_staff}")
print(f"  - Role: {user.role}")
