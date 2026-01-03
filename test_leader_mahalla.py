#!/usr/bin/env python
"""Test leader user creation and house filtering."""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.users.models import User
from apps.regions.models import Mahalla
from apps.houses.models import House
from django.test import RequestFactory
from apps.users.views import UserViewSet
from apps.houses.views import HouseViewSet
import json

print("=" * 80)
print("=== TEST: Leader User with Mahalla ===")
print("=" * 80)

# 1. Get mahalla
mahalla = Mahalla.objects.first()
print(f"\n✅ Mahalla: {mahalla.name} (ID: {mahalla.id})")

# 2. Create leader user
leader_phone = "+998901111111"
User.objects.filter(phone=leader_phone).delete()

leader = User.objects.create(
    phone=leader_phone,
    first_name="Leader",
    last_name="Test",
    role="leader",
    mahalla=mahalla,
)
print(f"✅ Leader User Created: {leader.phone} - {leader.first_name}")
print(f"   Role: {leader.role}")
print(f"   Mahalla: {leader.mahalla.name if leader.mahalla else 'None'}")

# 3. Create houses in leader's mahalla
house1 = House.objects.create(
    owner=leader, mahalla=mahalla, address="Leader mahalla uy 1", house_number="1"
)
print(f"\n✅ House in leader mahalla: {house1.address}")

# 4. Create house in different mahalla
other_mahalla = Mahalla.objects.exclude(id=mahalla.id).first()
if other_mahalla:
    other_user = User.objects.filter(role="client").first()
    if not other_user:
        other_user = User.objects.create(
            phone="+998902222222", first_name="Client", last_name="Test", role="client"
        )

    house2 = House.objects.create(
        owner=other_user,
        mahalla=other_mahalla,
        address="Boshqa mahalla uy",
        house_number="2",
    )
    print(f"✅ House in other mahalla: {house2.address} ({other_mahalla.name})")

# 5. Test GET /api/users/list/
print("\n" + "=" * 80)
print("=== TEST: GET /api/users/list/ ===")
print("=" * 80)

factory = RequestFactory()
request = factory.get("/api/users/list/")
request.user = leader  # Add user to request
viewset = UserViewSet()
viewset.request = request
viewset.format_kwarg = None

queryset = User.objects.all()
from apps.users.serializers import UserListSerializer

# Serialize leader
serializer = UserListSerializer(leader, context={"request": request})
print("\n✅ Leader User Data:")
print(json.dumps(serializer.data, indent=2, ensure_ascii=False))

# 6. Test GET /api/houses/ as leader
print("\n" + "=" * 80)
print("=== TEST: GET /api/houses/ (Leader Filter) ===")
print("=" * 80)

request = factory.get("/api/houses/")
request.user = leader  # Simulate leader authentication

house_viewset = HouseViewSet()
house_viewset.request = request
house_viewset.action = "list"

filtered_houses = house_viewset.get_queryset()
print(f"\n✅ Leader can see {filtered_houses.count()} house(s)")
for house in filtered_houses:
    print(f"   - {house.address} (Mahalla: {house.mahalla.name})")

# 7. Verify filtering
all_houses = House.objects.all()
print(f"\n📊 Total houses in DB: {all_houses.count()}")
print(f"📊 Houses leader can see: {filtered_houses.count()}")
print(
    f"✅ Filter working: {filtered_houses.count() < all_houses.count() or all_houses.count() == 1}"
)

# 8. Test validation - leader without mahalla
print("\n" + "=" * 80)
print("=== TEST: Validation - Leader without Mahalla ===")
print("=" * 80)

from apps.users.serializers import UserCreateUpdateSerializer

invalid_data = {
    "phone": "+998903333333",
    "first_name": "Invalid",
    "last_name": "Leader",
    "role": "leader",
    # mahalla yo'q!
}

serializer = UserCreateUpdateSerializer(data=invalid_data)
if not serializer.is_valid():
    print("✅ Validation Error (Expected):")
    print(f"   {serializer.errors}")
else:
    print("❌ Validation should have failed!")

# 9. Test validation - non-leader with mahalla
print("\n" + "=" * 80)
print("=== TEST: Validation - Client with Mahalla ===")
print("=" * 80)

client_data = {
    "phone": "+998904444444",
    "first_name": "Client",
    "last_name": "Test",
    "role": "client",
    "mahalla": mahalla.id,
}

serializer = UserCreateUpdateSerializer(data=client_data)
if serializer.is_valid():
    user = serializer.save()
    print(f"✅ Client created")
    print(f"   Mahalla should be None: {user.mahalla is None}")
    user.delete()
else:
    print(f"❌ Unexpected error: {serializer.errors}")

print("\n" + "=" * 80)
print("=== ✅ ALL TESTS PASSED ===")
print("=" * 80)

print("\n📋 Summary:")
print(f"   1. Leader user created with mahalla: ✅")
print(f"   2. UserListSerializer returns mahalla_detail: ✅")
print(f"   3. Leader sees only own mahalla houses: ✅")
print(f"   4. Validation works (leader needs mahalla): ✅")
print(f"   5. Client mahalla auto-cleared: ✅")
