from django.core.management.base import BaseCommand
from apps.regions.models import Region, District, Mahalla
from apps.users.models import User


class Command(BaseCommand):
    help = "Load sample mahallas (neighborhoods) into database"

    def handle(self, *args, **options):
        # Create or get super admin user
        super_admin, created = User.objects.get_or_create(
            phone="+998930850955",
            defaults={
                "role": "super_admin",
                "first_name": "Super",
                "last_name": "Admin",
                "is_verified": True,
            },
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f"✓ Created super admin: {super_admin.phone}")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"- Super admin exists: {super_admin.phone}")
            )

        # Sample mahallas data for different regions
        mahallas_data = [
            # Toshkent shahri - Chilonzor
            {
                "region": "Toshkent shahri",
                "district": "Chilonzor",
                "mahallas": ["Qatortol", "Chilonzor", "Sebzor", "Algoritmchilar"],
            },
            # Toshkent shahri - Yunusobod
            {
                "region": "Toshkent shahri",
                "district": "Yunusobod",
                "mahallas": ["Yunusobod", "Minor", "Shayhantohur", "Beruniy"],
            },
            # Navoiy viloyati - Karmana
            {
                "region": "Navoiy viloyati",
                "district": "Karmana",
                "mahallas": ["Umid", "Navbahor", "Mustaqillik", "O'zbekiston"],
            },
            # Samarqand viloyati - Samarqand
            {
                "region": "Samarqand viloyati",
                "district": "Samarqand",
                "mahallas": ["Registon", "Siob", "Ishrat", "Afrosiyob"],
            },
            # Farg'ona viloyati - Farg'ona
            {
                "region": "Farg'ona viloyati",
                "district": "Farg'ona",
                "mahallas": ["Markaz", "Paxtazor", "Qo'qon yo'li", "Dehqonobod"],
            },
        ]

        created_mahallas = 0
        skipped_mahallas = 0

        for data in mahallas_data:
            try:
                region = Region.objects.get(name=data["region"])
                district = District.objects.get(region=region, name=data["district"])

                for mahalla_name in data["mahallas"]:
                    mahalla, created = Mahalla.objects.get_or_create(
                        district=district,
                        name=mahalla_name,
                        defaults={"admin": super_admin},
                    )

                    if created:
                        created_mahallas += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✓ Created: {region.name} → {district.name} → {mahalla_name}"
                            )
                        )
                    else:
                        skipped_mahallas += 1

            except Region.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"✗ Region not found: {data['region']}")
                )
            except District.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"✗ District not found: {data['district']} in {data['region']}"
                    )
                )

        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS(f"\n✓ Summary:"))
        self.stdout.write(f"  Mahallas created: {created_mahallas}")
        self.stdout.write(f"  Mahallas skipped: {skipped_mahallas}")
        self.stdout.write(f"  Total mahallas: {Mahalla.objects.count()}")
