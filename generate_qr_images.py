#!/usr/bin/env python
"""Generate QR code images for all existing QR codes."""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.qrcodes.models import QRCode

def main():
    qrs = QRCode.objects.all()
    print(f'Found {qrs.count()} QR codes')
    print('Generating images...\n')
    
    for i, qr in enumerate(qrs, 1):
        print(f'{i}. UUID: {qr.uuid}')
        
        if qr.image:
            print(f'   Image already exists: {qr.image.url}')
        else:
            qr.generate_qr_image()
            qr.save()
            if qr.image:
                print(f'   ✓ Generated: {qr.image.url}')
            else:
                print(f'   ✗ Failed to generate image')
        print()
    
    print(f'\nDone! Total QR codes with images: {QRCode.objects.filter(image__isnull=False).count()}')

if __name__ == '__main__':
    main()
