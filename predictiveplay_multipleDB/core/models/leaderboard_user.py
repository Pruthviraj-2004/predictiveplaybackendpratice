import uuid
from django.db import models
from django.utils import timezone


class LeaderboardUser(models.Model):
    leaderboard_user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Reference to Leaderboard (UUID only, no FK)
    leaderboard_id = models.UUIDField(
        help_text="Leaderboard UUID"
    )

    # Reference to CompanyUser (UUID only, no FK)
    user_id = models.UUIDField(
        help_text="CompanyUser UUID"
    )

    created_on = models.DateTimeField(
        auto_now_add=True
    )

    is_deleted = models.BooleanField(
        default=False
    )

    class Meta:
        db_table = "leaderboard_users"

        # Prevent duplicate user entries in same leaderboard
        unique_together = ("leaderboard_id", "user_id")

        indexes = [
            models.Index(fields=["leaderboard_id"]),
            models.Index(fields=["user_id"]),
        ]

    def __str__(self):
        return f"{self.user_id} → {self.leaderboard_id}"
