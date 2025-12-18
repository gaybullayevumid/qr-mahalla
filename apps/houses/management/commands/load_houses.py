from django.core.management.base import BaseCommand
from apps.regions.models import Mahalla
from apps.users.models import User
from apps.houses.models import House


class Command(BaseCommand):
    help = "Load sample houses into database"

    def handle(self, *args, **options):
        # Get or create test users
        owner1, created = User.objects.get_or_create(
            phone="+998901234567",
            defaults={
                "role": "owner",
                "first_name": "Ahmadjon",
                "last_name": "Tursunov",
                "is_verified": True,
            },
        )

        owner2, created = User.objects.get_or_create(
            phone="+998912345678",
            defaults={
                "role": "owner",
                "first_name": "Dilshodjon",
                "last_name": "Karimov",
                "is_verified": True,
            },
        )

        owner3, created = User.objects.get_or_create(
            phone="+998923456789",
            defaults={
                "role": "owner",
                "first_name": "Murodjon",
                "last_name": "Salimov",
                "is_verified": True,
            },
        )

        self.stdout.write(self.style.SUCCESS(f"✓ Users ready"))

        # Sample houses data
        houses_data = [
            {
                "mahalla": "Qatortol",
                "district": "Chilonzor",
                "houses": [
                    {
                        "number": "12",
                        "address": "Qatortol ko'chasi, 12-uy",
                        "owner": owner1,
                    },
                    {
                        "number": "25",
                        "address": "Qatortol ko'chasi, 25-uy",
                        "owner": owner2,
                    },
                    {
                        "number": "37",
                        "address": "Qatortol ko'chasi, 37-uy",
                        "owner": owner3,
                    },
                ],
            },
            {
                "mahalla": "Umid",
                "district": "Karmana",
                "houses": [
                    {
                        "number": "5",
                        "address": "Navbahor ko'chasi, 5-uy",
                        "owner": owner1,
                    },
                    {
                        "number": "18",
                        "address": "Mustaqillik ko'chasi, 18-uy",
                        "owner": owner2,
                    },
                ],
            },
            {
                "mahalla": "Registon",
                "district": "Samarqand",
                "houses": [
                    {
                        "number": "3",
                        "address": "Registon ko'chasi, 3-uy",
                        "owner": owner3,
                    },
                    {
                        "number": "15",
                        "address": "Registon ko'chasi, 15-uy",
                        "owner": owner1,
                    },
                ],
            },
        ]

        created_houses = 0
        skipped_houses = 0

        for data in houses_data:
            try:
                mahalla = Mahalla.objects.get(
                    name=data["mahalla"], district__name=data["district"]
                )

                for house_data in data["houses"]:
                    house, created = House.objects.get_or_create(
                        mahalla=mahalla,
                        house_number=house_data["number"],
                        defaults={
                            "address": house_data["address"],
                            "owner": house_data["owner"],
                        },
                    )

                    if created:
                        created_houses += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✓ Created: {mahalla.name} → {house_data['number']} ({house_data['owner'].phone})"
                            )
                        )
                    else:
                        skipped_houses += 1

            except Mahalla.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"✗ Mahalla not found: {data['mahalla']} in {data['district']}"
                    )
                )

        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS(f"\n✓ Summary:"))
        self.stdout.write(f"  Houses created: {created_houses}")
        self.stdout.write(f"  Houses skipped: {skipped_houses}")
        self.stdout.write(f"  Total houses: {House.objects.count()}")
