import uuid
from django.db import models


class CricketEvent(models.Model):
    STATUS_DRAFT = "DRAFT"
    STATUS_ACTIVE = "ACTIVE"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_UPCOMING = "UPCOMING"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_UPCOMING, "Upcoming"),
    ]

    event_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    display_event_id = models.PositiveIntegerField(
        unique=True,
    )

    event_name = models.CharField(max_length=64)
    short_name = models.CharField(max_length=24, blank=True)

    start_date = models.DateField(default='2026-01-01')
    end_date = models.DateField(default='2026-01-01')

    location = models.CharField(max_length=64, blank=True, null=True)
    organizer = models.CharField(max_length=64, blank=True, null=True)
    logo_url = models.URLField(blank=True, null=True)

    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default=STATUS_UPCOMING
    )

    allow_predictions = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cricket_event"
        managed = True
        indexes = [
            models.Index(fields=["event_name"]),
            models.Index(fields=["start_date"]),
        ]

    def __str__(self):
        return f"{self.event_name}"
