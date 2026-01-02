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
        logger.info(f"{cls.__name__}: Existing IDs count: {len(existing_ids)}")

        # Additional safety check for House model with QRCode relationship
        # to avoid OneToOne constraint violations
        if cls.__name__ == "House":
            # Import here to avoid circular imports
            from apps.qrcodes.models import QRCode

            # Get ALL house_ids currently referenced in QRCode table
            # This is critical because these IDs CANNOT be reused
            reserved_by_qrcodes = set(
                QRCode.objects.filter(house_id__isnull=False).values_list(
                    "house_id", flat=True
                )
            )

            logger.info(f"House: QRCode reserved IDs count: {len(reserved_by_qrcodes)}")

            # Combine both sets - we can't use IDs from either set
            all_used_ids = existing_ids | reserved_by_qrcodes

            logger.info(
                f"House: Total used IDs (houses + qrcodes): {len(all_used_ids)}"
            )

            # Find first available ID that's NOT in either set
            expected_id = 1
            while expected_id in all_used_ids:
                expected_id += 1

            logger.info(f"House: Found available ID: {expected_id}")
            return expected_id

        # For other models, just find gap in existing IDs
        expected_id = 1
        while expected_id in existing_ids:
            expected_id += 1

        logger.info(f"{cls.__name__}: Selected ID: {expected_id}")
        return expected_id

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = self.__class__.get_next_available_id()
        super().save(*args, **kwargs)
