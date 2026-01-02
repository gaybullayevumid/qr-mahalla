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

            # For House model, be extra safe - check both existing house IDs
            # and QRCode house_id references to avoid conflicts
            attempts = 0
            max_attempts = 100

            while attempts < max_attempts:
                # Check if there's a QRCode pointing to this ID
                # Use select_for_update() to lock the row if we're in a transaction
                try:
                    from django.db import transaction

                    if transaction.get_connection().in_atomic_block:
                        # We're in a transaction, use select_for_update()
                        qr_exists = (
                            QRCode.objects.filter(house_id=expected_id)
                            .select_for_update(nowait=True)
                            .exists()
                        )
                    else:
                        # Not in transaction, regular check
                        qr_exists = QRCode.objects.filter(house_id=expected_id).exists()
                except Exception:
                    # If select_for_update fails (row locked), this ID is in use
                    qr_exists = True

                if not qr_exists:
                    # This ID is safe to use
                    logger.info(f"House: ID {expected_id} is safe (no QR code)")
                    break

                # This ID has a QR code, try next
                logger.info(f"House: ID {expected_id} has QR code, trying next")
                expected_id += 1
                # Skip IDs that are in existing_ids
                while expected_id in existing_ids:
                    expected_id += 1
                attempts += 1

            if attempts >= max_attempts:
                # Fallback: use max ID + 1 to avoid all conflicts
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
