import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.regions.models import Region, District, Mahalla
from apps.houses.models import House
from apps.users.models import User

# Delete all houses
print("Deleting all houses...")
House.objects.all().delete()
print(f"Deleted all houses")

# Get or create regions
regions_data = ["Toshkent", "Samarqand", "Buxoro", "Farg'ona", "Andijon"]

print("\nCreating regions, districts, mahallas and houses...")

for region_name in regions_data:
    region, _ = Region.objects.get_or_create(name=region_name)
    print(f"\nRegion: {region.name} (ID: {region.id})")

    # Create 2 districts per region
    for district_num in range(1, 3):
        district_name = f"{region_name} {district_num}-tuman"
        district, _ = District.objects.get_or_create(name=district_name, region=region)
        print(f"  District: {district.name} (ID: {district.id})")

        # Create 2 mahallas per district
        for mahalla_num in range(1, 3):
            mahalla_name = f"{district_name} {mahalla_num}-mahalla"
            mahalla, _ = Mahalla.objects.get_or_create(
                name=mahalla_name, district=district
            )
            print(f"    Mahalla: {mahalla.name} (ID: {mahalla.id})")

            # Create 4 houses per mahalla
            for house_num in range(1, 5):
                phone = (
                    f"+998{90 + district_num}{1000000 + mahalla_num * 100 + house_num}"
                )
                first_name = f"Ism{house_num}"
                last_name = f"Familiya{house_num}"

                # Create or get user
                user, created = User.objects.get_or_create(
                    phone=phone,
                    defaults={
                        "first_name": first_name,
                        "last_name": last_name,
                        "role": "client",
                    },
                )

                # Create house
                house = House.objects.create(
                    owner=user,
                    mahalla=mahalla,
                    address=f"{mahalla_name}, {house_num}-ko'cha, {house_num}-uy",
                    house_number=str(house_num),
                )
                print(f"      House: {house.address} - Owner: {user.phone}")

print("\n" + "=" * 50)
print("Summary:")
print(f"Total regions: {Region.objects.count()}")
print(f"Total districts: {District.objects.count()}")
print(f"Total mahallas: {Mahalla.objects.count()}")
print(f"Total houses: {House.objects.count()}")
print(f"Total users: {User.objects.count()}")
print("=" * 50)
