from django.core.management.base import BaseCommand
from apps.regions.models import Region, District, Mahalla


class Command(BaseCommand):
    help = "Load default regions, districts, and mahallas data"

    def handle(self, *args, **kwargs):
        # O'zbekiston viloyatlari va tumanlari
        regions_data = {
            "Toshkent shahri": [
                "Bektemir tumani",
                "Chilonzor tumani",
                "Mirobod tumani",
                "Mirzo Ulug'bek tumani",
                "Olmazor tumani",
                "Sergeli tumani",
                "Shayxontohur tumani",
                "Uchtepa tumani",
                "Yakkasaroy tumani",
                "Yashnobod tumani",
                "Yunusobod tumani",
            ],
            "Toshkent viloyati": [
                "Bekobod tumani",
                "Bo'ka tumani",
                "Bo'stonliq tumani",
                "Chinoz tumani",
                "Ohangaron tumani",
                "Oqqo'rg'on tumani",
                "Parkent tumani",
                "Piskent tumani",
                "Qibray tumani",
                "Quyichirchiq tumani",
                "O'rtachirchiq tumani",
                "Yangiyo'l tumani",
                "Yuqorichirchiq tumani",
                "Zangiota tumani",
                "Angren shahri",
                "Bekobod shahri",
                "Nurafshon shahri",
                "Ohangaron shahri",
                "Olmaliq shahri",
                "Chirchiq shahri",
            ],
            "Andijon viloyati": [
                "Andijon tumani",
                "Asaka tumani",
                "Baliqchi tumani",
                "Bo'ston tumani",
                "Buloqboshi tumani",
                "Izboskan tumani",
                "Jalaquduq tumani",
                "Marhamat tumani",
                "Oltinko'l tumani",
                "Paxtaobod tumani",
                "Qo'rg'ontepa tumani",
                "Shahrixon tumani",
                "Ulug'nor tumani",
                "Xo'jaobod tumani",
                "Andijon shahri",
                "Xonobod shahri",
            ],
            "Buxoro viloyati": [
                "Buxoro tumani",
                "G'ijduvon tumani",
                "Jondor tumani",
                "Kogon tumani",
                "Olot tumani",
                "Peshku tumani",
                "Qorako'l tumani",
                "Qorovulbozor tumani",
                "Romitan tumani",
                "Shofirkon tumani",
                "Vobkent tumani",
                "Buxoro shahri",
                "Kogon shahri",
            ],
            "Farg'ona viloyati": [
                "Bog'dod tumani",
                "Beshariq tumani",
                "Buvayda tumani",
                "Dang'ara tumani",
                "Farg'ona tumani",
                "Furqat tumani",
                "O'zbekiston tumani",
                "Qo'qon tumani",
                "Qo'shtepa tumani",
                "Quva tumani",
                "Rishton tumani",
                "So'x tumani",
                "Toshloq tumani",
                "Uchko'prik tumani",
                "Yozyovon tumani",
                "Farg'ona shahri",
                "Marg'ilon shahri",
                "Qo'qon shahri",
            ],
            "Jizzax viloyati": [
                "Arnasoy tumani",
                "Baxmal tumani",
                "Do'stlik tumani",
                "Forish tumani",
                "G'allaorol tumani",
                "Mirzacho'l tumani",
                "Paxtakor tumani",
                "Sharof Rashidov tumani",
                "Yangiobod tumani",
                "Zafarobod tumani",
                "Zarbdor tumani",
                "Zomin tumani",
                "Jizzax shahri",
            ],
            "Qashqadaryo viloyati": [
                "Chiroqchi tumani",
                "Dehqonobod tumani",
                "G'uzor tumani",
                "Qamashi tumani",
                "Qarshi tumani",
                "Kasbi tumani",
                "Kitob tumani",
                "Koson tumani",
                "Mirishkor tumani",
                "Muborak tumani",
                "Nishon tumani",
                "Shahrisabz tumani",
                "Yakkabog' tumani",
                "Qarshi shahri",
                "Shahrisabz shahri",
            ],
            "Navoiy viloyati": [
                "Karmana tumani",
                "Konimex tumani",
                "Navbahor tumani",
                "Nurota tumani",
                "Qiziltepa tumani",
                "Tomdi tumani",
                "Uchquduq tumani",
                "Xatirchi tumani",
                "Zarafshon tumani",
                "Navoiy shahri",
                "Zarafshon shahri",
            ],
            "Namangan viloyati": [
                "Chortoq tumani",
                "Chust tumani",
                "Kosonsoy tumani",
                "Mingbuloq tumani",
                "Namangan tumani",
                "Norin tumani",
                "Pop tumani",
                "To'raqo'rg'on tumani",
                "Uchqo'rg'on tumani",
                "Uychi tumani",
                "Yangiqo'rg'on tumani",
                "Namangan shahri",
            ],
            "Samarqand viloyati": [
                "Bulungur tumani",
                "Ishtixon tumani",
                "Jomboy tumani",
                "Kattaqo'rg'on tumani",
                "Narpay tumani",
                "Nurobod tumani",
                "Oqdaryo tumani",
                "Paxtachi tumani",
                "Payariq tumani",
                "Pastdarg'om tumani",
                "Qo'shrabot tumani",
                "Samarqand tumani",
                "Toyloq tumani",
                "Urgut tumani",
                "Samarqand shahri",
                "Kattaqo'rg'on shahri",
            ],
            "Sirdaryo viloyati": [
                "Boyovut tumani",
                "Guliston tumani",
                "Mirzaobod tumani",
                "Oqoltin tumani",
                "Sardoba tumani",
                "Sayxunobod tumani",
                "Sirdaryo tumani",
                "Xavos tumani",
                "Guliston shahri",
                "Shirin shahri",
            ],
            "Surxondaryo viloyati": [
                "Angor tumani",
                "Boysun tumani",
                "Denov tumani",
                "Jarqo'rg'on tumani",
                "Qiziriq tumani",
                "Qo'mqo'rg'on tumani",
                "Muzrabot tumani",
                "Oltinsoy tumani",
                "Sariosiyo tumani",
                "Sherobod tumani",
                "Sho'rchi tumani",
                "Termiz tumani",
                "Uzun tumani",
                "Termiz shahri",
            ],
            "Xorazm viloyati": [
                "Bog'ot tumani",
                "Gurlan tumani",
                "Xonqa tumani",
                "Hazorasp tumani",
                "Qo'shko'pir tumani",
                "Shovot tumani",
                "Urganch tumani",
                "Tuproqqal'a tumani",
                "Xiva tumani",
                "Yangiariq tumani",
                "Yangibozor tumani",
                "Urganch shahri",
                "Xiva shahri",
            ],
            "Qoraqalpog'iston Respublikasi": [
                "Amudaryo tumani",
                "Beruniy tumani",
                "Chimboy tumani",
                "Ellikqal'a tumani",
                "Kegeyli tumani",
                "Mo'ynoq tumani",
                "Nukus tumani",
                "Qanliko'l tumani",
                "Qorao'zak tumani",
                "Qo'ng'irot tumani",
                "Shumanay tumani",
                "Taxtako'pir tumani",
                "To'rtko'l tumani",
                "Xo'jayli tumani",
                "Nukus shahri",
            ],
        }

        # Har bir viloyat uchun tumanlar va mahallalar qo'shish
        for region_name, districts in regions_data.items():
            region, created = Region.objects.get_or_create(name=region_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created region: {region_name}"))

            for district_name in districts:
                district, created = District.objects.get_or_create(
                    name=district_name, region=region
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"  Created district: {district_name}")
                    )

                # Har bir tuman uchun 5 ta mahalla qo'shamiz (agar mavjud bo'lmasa)
                existing_mahallas = Mahalla.objects.filter(district=district).count()
                if existing_mahallas < 5:
                    for i in range(1, 6):
                        mahalla_name = f"{district_name} {i}-mahalla"
                        mahalla, created = Mahalla.objects.get_or_create(
                            name=mahalla_name, district=district
                        )
                        if created:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"    Created mahalla: {mahalla_name}"
                                )
                            )

        # Statistika
        total_regions = Region.objects.count()
        total_districts = District.objects.count()
        total_mahallas = Mahalla.objects.count()

        self.stdout.write(self.style.SUCCESS("\n=== Database Statistics ==="))
        self.stdout.write(self.style.SUCCESS(f"Total Regions: {total_regions}"))
        self.stdout.write(self.style.SUCCESS(f"Total Districts: {total_districts}"))
        self.stdout.write(self.style.SUCCESS(f"Total Mahallas: {total_mahallas}"))
