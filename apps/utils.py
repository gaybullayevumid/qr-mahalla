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

        Returns:
            int: First available ID in the sequence
        """
        existing_ids = set(cls.objects.values_list("id", flat=True))

        expected_id = 1
        while expected_id in existing_ids:
            expected_id += 1

        return expected_id

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = self.__class__.get_next_available_id()
        super().save(*args, **kwargs)
