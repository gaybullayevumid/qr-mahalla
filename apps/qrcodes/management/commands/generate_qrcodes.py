"""
Management command to generate initial QR codes.

Usage:
    python manage.py generate_qrcodes
    python manage.py generate_qrcodes --count 20
"""

from django.core.management.base import BaseCommand
from apps.qrcodes.models import QRCode


class Command(BaseCommand):
    help = "Generate unclaimed QR codes"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=10,
            help="Number of QR codes to generate (default: 10)",
        )

    def handle(self, *args, **options):
        count = options["count"]

        # Count existing unclaimed QR codes
        unclaimed_count = QRCode.objects.filter(house__isnull=True).count()

        self.stdout.write(
            self.style.WARNING(f"📊 Current unclaimed QR codes: {unclaimed_count}")
        )

        if unclaimed_count >= count:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Already have {unclaimed_count} unclaimed QR codes. No need to generate more."
                )
            )
            return

        # Calculate how many to create
        needed = count - unclaimed_count

        self.stdout.write(self.style.WARNING(f"🔄 Generating {needed} new QR codes..."))

        # Generate QR codes
        created_qrcodes = []
        for i in range(needed):
            qr = QRCode.objects.create()
            created_qrcodes.append(qr)

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Successfully generated {len(created_qrcodes)} QR codes!"
            )
        )

        # Show sample UUIDs
        self.stdout.write(self.style.WARNING("\n📝 Sample QR codes:"))
        for qr in created_qrcodes[:5]:
            self.stdout.write(f"   - {qr.uuid}")

        if len(created_qrcodes) > 5:
            self.stdout.write(f"   ... and {len(created_qrcodes) - 5} more")

        # Final count
        total_unclaimed = QRCode.objects.filter(house__isnull=True).count()
        self.stdout.write(
            self.style.SUCCESS(f"\n📊 Total unclaimed QR codes: {total_unclaimed}")
        )
