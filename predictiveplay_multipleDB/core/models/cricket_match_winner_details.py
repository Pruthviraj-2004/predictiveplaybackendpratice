import uuid
from django.db import models
from .cricket_event import CricketEvent
from .cricket_match_details import CricketMatchDetails
from .cricket_team import CricketTeam
from .cricket_player import CricketPlayer


class CricketMatchWinnerDetails(models.Model):
    winner_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    event = models.ForeignKey(
        CricketEvent,
        on_delete=models.CASCADE,
        related_name="match_winners"
    )

    match = models.ForeignKey(
        CricketMatchDetails,
        on_delete=models.CASCADE,
        related_name="winner_details"
    )

    winner_team = models.ForeignKey(
        CricketTeam,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="won_matches"
    )

    player_of_match = models.ForeignKey(
        CricketPlayer,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="player_of_match_awards"
    )

    most_runs_player = models.ForeignKey(
        CricketPlayer,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="most_runs_awards"
    )

    most_wickets_taker = models.ForeignKey(
        CricketPlayer,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="most_wickets_awards"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cricket_match_winner_details"
        managed = True  # set False if table already exists
        unique_together = ("event", "match")
        indexes = [
            models.Index(fields=["event"]),
            models.Index(fields=["match"]),
        ]

    def __str__(self):
        return f"Winner details for Match {self.match.display_match_id}"
