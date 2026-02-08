import random
import uuid

from core.models.leaderboard import Leaderboard
from core.models.leaderboard_user import LeaderboardUser
from core.models.leaderboard_points import LeaderboardPoints

DB = "company_kt5xg8b0"
MATCH_ID = uuid.UUID("c3ac6e98-c9e6-4477-b9a3-603ccc44e8a5")

leaderboards = Leaderboard.objects.using(DB).filter(
    leaderboard_name__in=["Global", "Weekly"]
)

created = 0

for lb in leaderboards:
    lb_users = LeaderboardUser.objects.using(DB).filter(
        leaderboard_id=lb.leaderboard_id,
        is_deleted=False
    )

    for lb_user in lb_users:
        obj, is_created = LeaderboardPoints.objects.using(DB).get_or_create(
            leaderboard_user_id=lb_user.leaderboard_user_id,
            match_id=MATCH_ID,
            defaults={
                "points1": random.randint(0, 5),
                "points2": random.randint(0, 5),
            }
        )
        if is_created:
            created += 1

print(f"LeaderboardPoints rows created: {created}")
