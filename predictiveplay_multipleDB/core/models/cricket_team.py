import uuid
from django.db import models
from .cricket_event import CricketEvent


class CricketTeam(models.Model):
    team_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    display_team_id = models.PositiveIntegerField(default=1)
    
    team_name = models.CharField(max_length=32)
    short_name = models.CharField(max_length=8)

    location = models.CharField(max_length=32, blank=True, null=True)
    home_stadium = models.CharField(max_length=40, blank=True, null=True)
    logo_url = models.URLField(blank=True, null=True)
    founded_year = models.PositiveIntegerField(null=True, blank=True)

    event = models.ForeignKey(
        CricketEvent,
        on_delete=models.CASCADE,
        related_name="teams"
    )

    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cricket_team"
        managed = True
        indexes = [
            models.Index(fields=["short_name"]),
            models.Index(fields=["team_name"]),
        ]
        unique_together = ("event", "display_team_id")

    def __str__(self):
        return f"{self.short_name} ({self.event.short_name})"
