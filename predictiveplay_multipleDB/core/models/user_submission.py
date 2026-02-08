import uuid
from django.db import models
from .cricket_event import CricketEvent
from .cricket_match_details import CricketMatchDetails
from .cricket_team import CricketTeam
from .cricket_player import CricketPlayer
from .company_user import CompanyUser

class UserSubmission(models.Model):

    user_submission_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        CompanyUser,
        on_delete=models.CASCADE,
        related_name="submissions"
    )

    # ✅ MASTER DATA UUID REFERENCES (NULLABLE)
    event_id = models.UUIDField(null=True, blank=True)
    match_id = models.UUIDField(null=True, blank=True)

    predicted_winner_team_id = models.UUIDField(null=True, blank=True)
    predicted_player_of_match_id = models.UUIDField(null=True, blank=True)
    predicted_most_runs_player_id = models.UUIDField(null=True, blank=True)
    predicted_most_wickets_taker_id = models.UUIDField(null=True, blank=True)

    # points1 = models.IntegerField(default=0)
    # points2 = models.IntegerField(default=0)

    points_winner = models.IntegerField(default=0)
    points_mom = models.IntegerField(default=0)
    points_runs = models.IntegerField(default=0)
    points_wickets = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_submissions"
        unique_together = ("user", "match_id")
