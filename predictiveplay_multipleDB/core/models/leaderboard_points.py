from django.db import models
import uuid


class LeaderboardPoints(models.Model):
    leaderboard_points_id = models.AutoField(
        primary_key=True
    )

    # Reference to LeaderboardUser (UUID only, no FK)
    leaderboard_user_id = models.UUIDField(
        help_text="LeaderboardUser UUID"
    )

    # Match reference (UUID only)
    match_id = models.UUIDField(
        null=True,
        blank=True
    )

    points1 = models.IntegerField(
        default=0
    )

    points2 = models.IntegerField(
        default=0
    )

    created_on = models.DateTimeField(
        auto_now_add=True
    )

    updated_on = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "leaderboard_points"
        managed = True

        indexes = [
            models.Index(fields=["leaderboard_user_id"]),
            models.Index(fields=["match_id"]),
        ]

    def __str__(self):
        return f"{self.leaderboard_user_id} | {self.match_id}"
