import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.qrcodes.models import QRCode

print("🔄 Regenerating QR code images...\n")

qr_codes = QRCode.objects.all()
total = qr_codes.count()
print(f"Total QR codes to regenerate: {total}\n")

success = 0
errors = 0

for qr in qr_codes:
    try:
        # Delete old image if exists
        if qr.image:
            try:
                qr.image.delete(save=False)
            except:
                pass

        # Generate new image
        qr.generate_qr_image()
        qr.save()
        success += 1
        print(f"✅ {success}/{total} - UUID: {qr.uuid}")
    except Exception as e:
        errors += 1
        print(f"❌ Error for UUID {qr.uuid}: {str(e)}")

print(f"\n📊 Summary:")
print(f"  Success: {success}")
print(f"  Errors: {errors}")
print(f"  Total: {total}")
