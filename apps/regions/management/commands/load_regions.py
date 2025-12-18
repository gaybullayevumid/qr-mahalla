from django.core.management.base import BaseCommand
from apps.regions.models import Region, District


class Command(BaseCommand):
    help = "Load all Uzbekistan regions and districts into database"

    def handle(self, *args, **options):
        regions_data = {
            "Toshkent shahri": [
                "Bektemir",
                "Chilonzor",
                "Mirobod",
                "Mirzo Ulug'bek",
                "Olmazor",
                "Sergeli",
                "Shayxontohur",
                "Uchtepa",
                "Yakkasaroy",
                "Yunusobod",
                "Yashnaobod",
            ],
            "Toshkent viloyati": [
                "Angren",
                "Olmaliq",
                "Chirchiq",
                "Bekobod",
                "Nurafshon",
                "Ohangaron",
                "Yangiyo'l",
                "Bo'stonliq",
                "Bo'ka",
                "Chinoz",
                "Qibray",
                "Oqqo'rg'on",
                "Parkent",
                "Piskent",
                "Quyi Chirchiq",
                "O'rta Chirchiq",
                "Zangiota",
            ],
            "Andijon viloyati": [
                "Andijon",
                "Xonobod",
                "Asaka",
                "Marhamat",
                "Qo'rg'ontepa",
                "Baliqchi",
                "Bo'z",
                "Buloqboshi",
                "Izboskan",
                "Jalaquduq",
                "Oltinko'l",
                "Paxtaobod",
                "Shahrixon",
                "Ulug'nor",
                "Xo'jaobod",
            ],
            "Buxoro viloyati": [
                "Buxoro",
                "Kogon",
                "G'ijduvon",
                "Jondor",
                "Kogon",
                "Olot",
                "Peshku",
                "Qorako'l",
                "Qorovulbozor",
                "Romitan",
                "Shofirkon",
                "Vobkent",
            ],
            "Farg'ona viloyati": [
                "Farg'ona",
                "Marg'ilon",
                "Quvasoy",
                "Qo'qon",
                "Beshariq",
                "Bog'dod",
                "Buvayda",
                "Dang'ara",
                "Furqat",
                "Oltiariq",
                "Qo'shtepa",
                "Rishton",
                "So'x",
                "Toshloq",
                "Uchko'prik",
                "Yozyovon",
            ],
            "Jizzax viloyati": [
                "Jizzax",
                "Arnasoy",
                "Baxmal",
                "Do'stlik",
                "Forish",
                "G'allaorol",
                "Mirzacho'l",
                "Paxtakor",
                "Yangiobod",
                "Zafarobod",
                "Zarband",
                "Zomin",
            ],
            "Xorazm viloyati": [
                "Urganch",
                "Xiva",
                "Bog'ot",
                "Gurlan",
                "Qo'shko'pir",
                "Shovot",
                "Urganch tumani",
                "Xonqa",
                "Yangiariq",
                "Yangibozor",
                "Hazorasp",
            ],
            "Namangan viloyati": [
                "Namangan",
                "Chortoq",
                "Chust",
                "Kosonsoy",
                "Mingbuloq",
                "Namangan tumani",
                "Norin",
                "Pop",
                "To'raqo'rg'on",
                "Uchqo'rg'on",
                "Uychi",
                "Yangiqo'rg'on",
            ],
            "Navoiy viloyati": [
                "Navoiy",
                "Zarafshon",
                "Konimex",
                "Karmana",
                "Navbahor",
                "Nurota",
                "Qiziltepa",
                "Tomdi",
                "Uchquduq",
                "Xatirchi",
            ],
            "Qashqadaryo viloyati": [
                "Qarshi",
                "Shahrisabz",
                "Kitob",
                "Chiroqchi",
                "Dehqonobod",
                "G'uzor",
                "Kasbi",
                "Koson",
                "Mirishkor",
                "Muborak",
                "Nishon",
                "Qamashi",
                "Yakkabog'",
            ],
            "Samarqand viloyati": [
                "Samarqand",
                "Kattaqo'rg'on",
                "Bulung'ur",
                "Ishtixon",
                "Jomboy",
                "Narpay",
                "Nurobod",
                "Oqdaryo",
                "Past Darg'om",
                "Paxtachi",
                "Payariq",
                "Qo'shrabot",
                "Samarqand tumani",
                "Toyloq",
                "Urgut",
            ],
            "Sirdaryo viloyati": [
                "Guliston",
                "Yangiyer",
                "Shirin",
                "Boyovut",
                "Guliston tumani",
                "Xovos",
                "Mirzaobod",
                "Oqoltin",
                "Sardoba",
                "Sayxunobod",
            ],
            "Surxondaryo viloyati": [
                "Termiz",
                "Denov",
                "Sherobod",
                "Angor",
                "Bandixon",
                "Boysun",
                "Jarqo'rg'on",
                "Muzrabot",
                "Oltinsoy",
                "Qiziriq",
                "Qumqo'rg'on",
                "Sariosiyo",
                "Shurchi",
                "Uzun",
            ],
            "Qoraqalpog'iston": [
                "Nukus",
                "Mo'ynoq",
                "Amudaryo",
                "Beruniy",
                "Chimboy",
                "Ellikqal'a",
                "Kegeyli",
                "Qanliko'l",
                "Qo'ng'irot",
                "Shumanay",
                "Taxtako'pir",
                "To'rtko'l",
                "Xo'jayli",
            ],
        }

        created_regions = 0
        created_districts = 0
        skipped_regions = 0
        skipped_districts = 0

        for region_name, districts in regions_data.items():
            # Create or get region
            region, created = Region.objects.get_or_create(name=region_name)
            if created:
                created_regions += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Created region: {region_name}")
                )
            else:
                skipped_regions += 1
                self.stdout.write(
                    self.style.WARNING(f"- Skipped region (exists): {region_name}")
                )

            # Create districts
            for district_name in districts:
                district, created = District.objects.get_or_create(
                    region=region, name=district_name
                )
                if created:
                    created_districts += 1
                    self.stdout.write(f"  ✓ Created district: {district_name}")
                else:
                    skipped_districts += 1

        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS(f"\n✓ Summary:"))
        self.stdout.write(f"  Regions created: {created_regions}")
        self.stdout.write(f"  Regions skipped: {skipped_regions}")
        self.stdout.write(f"  Districts created: {created_districts}")
        self.stdout.write(f"  Districts skipped: {skipped_districts}")
        self.stdout.write(f"  Total regions: {Region.objects.count()}")
        self.stdout.write(f"  Total districts: {District.objects.count()}")
