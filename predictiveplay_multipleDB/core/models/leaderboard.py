import uuid
from django.db import models
from django.utils import timezone


class Leaderboard(models.Model):
    leaderboard_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    leaderboard_name = models.CharField(
        max_length=40
    )

    event_id = models.UUIDField(null=True, blank=True)
    company_display_id = models.CharField(
        max_length=8,
        db_index=True,
        default="AAAAAAAA",
        help_text="Company display ID this user belongs to"
    )

    # ---------- POINT RULES ----------
    leaderboard_points_winner_team = models.IntegerField(default=4)
    leaderboard_points_mom = models.IntegerField(default=3)
    leaderboard_points_runs = models.IntegerField(default=3)
    leaderboard_points_wickets = models.IntegerField(default=3)

    # ---------- METADATA ----------
    created_by_user_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="CompanyUser UUID who created this leaderboard"
    )

    created_on_1 = models.DateField(default='2026-01-01')

    tag1 = models.CharField(
        max_length=16,
        blank=True,
        null=True
    )

    tag2 = models.CharField(
        max_length=16,
        blank=True,
        null=True
    )

    class Meta:
        db_table = "leaderboards"

        indexes = [
            models.Index(fields=["leaderboard_name"]),
            models.Index(fields=["event_id"]),
            models.Index(fields=["company_display_id"]),
        ]

    def __str__(self):
        return self.leaderboard_name
