import uuid
from django.db import models
from .cricket_team import CricketTeam
from .cricket_event import CricketEvent


class CricketPlayer(models.Model):
    # ---------- ROLE CONSTANTS ----------
    ROLE_BATTER = "BATTER"
    ROLE_ALL_ROUNDER = "ALL_ROUNDER"
    ROLE_BOWLER = "BOWLER"

    ROLE_CHOICES = [
        (ROLE_BATTER, "Batter"),
        (ROLE_ALL_ROUNDER, "All Rounder"),
        (ROLE_BOWLER, "Bowler"),
    ]

    player_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    display_player_id = models.PositiveIntegerField(
        help_text="Sequential player ID per event or team"
    )

    player_name = models.CharField(max_length=64, default="ABC")

    short_name = models.CharField(
        max_length=32,
        blank=True,
        null=True
    )

    team = models.ForeignKey(
        CricketTeam,
        on_delete=models.CASCADE,
        related_name="players"
    )

    event = models.ForeignKey(
        CricketEvent,
        on_delete=models.CASCADE,
        related_name="players"
    )

    # ✅ DROPDOWN FIELD
    role = models.CharField(
        max_length=16,
        choices=ROLE_CHOICES,
        default=ROLE_BATTER
    )

    batting_style = models.CharField(
        max_length=32,
        blank=True,
        null=True
    )

    bowling_style = models.CharField(
        max_length=32,
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cricket_player"
        managed = True
        unique_together = ("event", "display_player_id", "team")
        indexes = [
            models.Index(fields=["player_name"]),
            models.Index(fields=["team"]),
            models.Index(fields=["event"]),
            models.Index(fields=["role"]),
        ]

    def __str__(self):
        return f"{self.player_name} ({self.team.short_name})"
