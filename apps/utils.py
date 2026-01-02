from django.db import models


class GapFillingIDMixin(models.Model):
    """
    Mixin that automatically fills gaps in ID sequence when creating new records.
    Instead of always incrementing, finds first available ID.
    """

    id = models.IntegerField(primary_key=True, verbose_name="ID")

    class Meta:
        abstract = True

    @classmethod
    def get_next_available_id(cls):
        """
        Find the first available ID (fills gaps from deleted records).

        For models with OneToOne relationships (like House with QRCode),
        also checks if the ID is safe to use (no existing related records).

        Returns:
            int: First available ID in the sequence
        """
        import logging

        logger = logging.getLogger(__name__)

        existing_ids = set(cls.objects.values_list("id", flat=True))
        logger.info(
            f"{cls.__name__}: Existing IDs: {sorted(existing_ids) if len(existing_ids) < 20 else f'{len(existing_ids)} IDs'}"
        )

        expected_id = 1
        while expected_id in existing_ids:
            expected_id += 1

        # Additional safety check for House model with QRCode relationship
        # to avoid OneToOne constraint violations
        if cls.__name__ == "House":
            # Import here to avoid circular imports
            from apps.qrcodes.models import QRCode

            # Check if there's a QRCode pointing to a House with this ID
            # (even if the House was deleted, the QRCode might still exist)
            qr_exists = QRCode.objects.filter(house_id=expected_id).exists()
            logger.info(f"House: Checking ID {expected_id}, QR exists: {qr_exists}")

            attempts = 0
            max_attempts = 100
            while qr_exists and attempts < max_attempts:
                expected_id += 1
                # Also check if this new ID is in existing_ids
                while expected_id in existing_ids:
                    expected_id += 1
                qr_exists = QRCode.objects.filter(house_id=expected_id).exists()
                attempts += 1
                logger.info(
                    f"House: Attempt {attempts}, trying ID {expected_id}, QR exists: {qr_exists}"
                )

            if attempts >= max_attempts:
                # Fallback: use max ID + 1
                max_id = max(existing_ids) if existing_ids else 0
                expected_id = max_id + 1
                logger.warning(
                    f"House: Max attempts reached, using fallback ID {expected_id}"
                )

        logger.info(f"{cls.__name__}: Selected ID: {expected_id}")
        return expected_id

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = self.__class__.get_next_available_id()
        super().save(*args, **kwargs)
