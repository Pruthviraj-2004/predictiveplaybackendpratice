from django.db import models
import uuid


class FinalLeaderboardPoints(models.Model):
    final_leaderboard_points_id = models.AutoField(
        primary_key=True
    )

    # Reference to LeaderboardUser (UUID only, no FK)
    leaderboard_user_id = models.UUIDField(
        help_text="LeaderboardUser UUID"
    )

    points1 = models.IntegerField(
        default=0
    )

    points2 = models.IntegerField(
        default=0
    )

    match_id = models.UUIDField(
        null=True,
        blank=True
    )

    match_number = models.IntegerField(
        null=True,
        blank=True
    )

    rank = models.IntegerField(
        null=True, 
        blank=True
    )

    previous_rank = models.IntegerField(
        null=True, 
        blank=True
    )

    updated_on = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "final_leaderboard_points"
        managed = True

        indexes = [
            models.Index(fields=["leaderboard_user_id"]),
            models.Index(fields=["match_number"]),
            models.Index(fields=["points1"]),
            models.Index(fields=["points2"]),
        ]

    def __str__(self):
        return f"{self.leaderboard_user_id} → {self.points1 + self.points2}"
