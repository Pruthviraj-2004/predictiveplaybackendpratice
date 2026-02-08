import uuid
from django.db import models 
from django.contrib.auth.hashers import make_password

class CompanyUser(models.Model):
    """
    Core user identity model.
    Exists ONLY in company databases.
    Used for authentication, authorization, and all user-linked data.
    """

    # -------- Core Identity --------
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Company isolation (VERY IMPORTANT)
    company_display_id = models.CharField(
        max_length=8,
        db_index=True,
        help_text="Company display ID this user belongs to"
    )

    # -------- Login Fields --------
    email = models.EmailField(
        max_length=255,
        unique=True
    )

    username = models.CharField(
        max_length=150,
        unique=True
    )

    is_email_verified = models.BooleanField(
        default=False
    )

    password = models.CharField(
        max_length=128,
        default=make_password("1234")
    )
    # -------- Profile --------
    full_name = models.CharField(
        max_length=255,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    is_deleted = models.BooleanField(
        default=False
    )

    # -------- Auditing --------
    last_login_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "company_users"
        indexes = [
            models.Index(fields=["company_display_id", "email"]),
            models.Index(fields=["company_display_id", "username"]),
        ]

    def __str__(self):
        return f"{self.username} ({self.company_display_id})"

