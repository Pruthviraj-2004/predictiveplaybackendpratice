import uuid
from django.db import models
from .cricket_event import CricketEvent
from .cricket_team import CricketTeam


class CricketMatchDetails(models.Model):
    # ---------- STATUS CONSTANTS ----------
    STATUS_SCHEDULED = 1
    STATUS_LIVE = 2
    STATUS_COMPLETED = 3
    STATUS_CANCELLED = 4

    STATUS_CHOICES = [
        (STATUS_SCHEDULED, "Scheduled"),
        (STATUS_LIVE, "Live"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    match_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    display_match_id = models.PositiveSmallIntegerField()

    match_date = models.DateField(default="2026-01-01")
    match_time = models.TimeField(default="19:30:00")

    event = models.ForeignKey(
        CricketEvent,
        on_delete=models.CASCADE,
        related_name="matches"
    )

    team1 = models.ForeignKey(
        CricketTeam,
        on_delete=models.CASCADE,
        related_name="matches_as_team1"
    )

    team2 = models.ForeignKey(
        CricketTeam,
        on_delete=models.CASCADE,
        related_name="matches_as_team2"
    )

    match_type = models.CharField(
        max_length=16,
        blank=True,
        null=True
    )

    # ✅ DROPDOWN FIELD
    status_id = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES,
        default=STATUS_SCHEDULED
    )

    location = models.CharField(max_length=24, blank=True, null=True)
    stadium = models.CharField(max_length=40, blank=True, null=True)

    match_name1 = models.CharField(max_length=80, blank=True, null=True)
    match_name2 = models.CharField(max_length=24, blank=True, null=True)

    # ---------- FLAGS (UNCHANGED) ----------
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    allow_predictions = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cricket_match_details"
        managed = True  # set False if table already exists
        unique_together = ("event", "display_match_id")
        indexes = [
            models.Index(fields=["match_date"]),
            models.Index(fields=["event"]),
            models.Index(fields=["team1"]),
            models.Index(fields=["team2"]),
        ]

    def __str__(self):
        return self.match_name2 or f"Match {self.display_match_id}"
