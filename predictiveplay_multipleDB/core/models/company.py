import uuid
import random
import string

from django.db import models, transaction
from ..db_utils import create_company_database


def generate_company_display_id():
    """
    Generates an 8-character uppercase alphanumeric ID
    Example: A9X2P7QK
    """
    return "".join(
        random.choices(string.ascii_uppercase + string.digits, k=8)
    )


class Company(models.Model):
    db_alias = 'default'
    company_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    company_display_id = models.CharField(
        max_length=8,
        unique=True,
        editable=False,
        default=generate_company_display_id
    )

    company_name = models.CharField(
        max_length=255
    )

    company_domain = models.CharField(
        max_length=255,
        unique=True,
        help_text="Example: company.com (without @)"
    )

    db_alias = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text="Database alias used by Django router"
    )

    db_created_at = models.DateTimeField(
        auto_now_add=True
    )

    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        managed = True
        db_table = "companies"

    def __str__(self):
        return f"{self.company_name} ({self.company_display_id})"

    def save(self, *args, **kwargs):
        is_new = self._state.adding

        if not self.db_alias:
            self.db_alias = f"company_{self.company_display_id.lower()}"

        with transaction.atomic():
            super().save(*args, **kwargs)

            # Create DB only on first creation
            if is_new:
                create_company_database(self.db_alias)