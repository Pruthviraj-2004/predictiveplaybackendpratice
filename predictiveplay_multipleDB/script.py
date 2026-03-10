import os
import django
import uuid

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "predictiveplay_multipleDB.settings")
django.setup()


# import random

# from core.models.leaderboard import Leaderboard
# from core.models.leaderboard_user import LeaderboardUser
# from core.models.leaderboard_points import LeaderboardPoints

# DB = "company_kt5xg8b0"
# MATCH_ID = uuid.UUID("c3ac6e98-c9e6-4477-b9a3-603ccc44e8a5")

# leaderboards = Leaderboard.objects.using(DB).filter(
#     leaderboard_name__in=["Global"]
# )

# created = 0

# for lb in leaderboards:
#     lb_users = LeaderboardUser.objects.using(DB).filter(
#         leaderboard_id=lb.leaderboard_id,
#         is_deleted=False
#     )

#     for lb_user in lb_users:
#         obj, is_created = LeaderboardPoints.objects.using(DB).get_or_create(
#             leaderboard_user_id=lb_user.leaderboard_user_id,
#             match_id=MATCH_ID,
#             defaults={
#                 "points1": random.randint(0, 5),
#                 "points2": random.randint(0, 5),
#             }
#         )
#         if is_created:
#             created += 1

# print(f"LeaderboardPoints rows created: {created}")

#create 25 dummy users in company_kt5xg8b0 database

# import os
# import django
# import uuid

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "predictiveplay_multipleDB.settings")
# django.setup()

# from django.contrib.auth.hashers import make_password
# from core.models.company_user import CompanyUser

# db = "company_kt5xg8b0"

# users = []

# for i in range(1, 26):
#     users.append(
#         CompanyUser(
#             user_id=uuid.uuid4(),
#             company_display_id="KT5XG8B0",
#             username=f"testuser{i}",
#             email=f"testuser{i}@gmail.com",
#             full_name=f"Test User {i}",
#             is_email_verified=True,
#             password=make_password("1234567890"),
#         )
#     )

# CompanyUser.objects.using(db).bulk_create(users)

# print("25 dummy users created successfully")


# add LeaderboardUser

# from core.models.company_user import CompanyUser
# from core.models.leaderboard import Leaderboard
# from core.models.leaderboard_user import LeaderboardUser

# db = "company_kt5xg8b0"

# # get global leaderboard
# leaderboard = Leaderboard.objects.using(db).get(leaderboard_name="Weekly")

# # get all users
# users = CompanyUser.objects.using(db).values_list("user_id", flat=True)

# created = 0

# for user_id in users:
#     obj, is_created = LeaderboardUser.objects.using(db).get_or_create(
#         leaderboard_id=leaderboard.leaderboard_id,
#         user_id=user_id
#     )
#     if is_created:
#         created += 1

# print("Users added:", created)

# add points for all users in the weekly leaderboard for a specific match

# import uuid
# import random

# from core.models.leaderboard_user import LeaderboardUser
# from core.models.leaderboard_points import LeaderboardPoints
# from core.models.cricket_match_details import CricketMatchDetails

# DB = "company_kt5xg8b0"

# # get all leaderboard users (Global leaderboard users)
# lb_users = LeaderboardUser.objects.using(DB).filter(is_deleted=False)

# # matches are stored in main DB
# matches = CricketMatchDetails.objects.using("default").values_list("match_id", flat=True)

# created = 0

# for lb_user in lb_users:
#     for match_id in matches:

#         obj, is_created = LeaderboardPoints.objects.using(DB).get_or_create(
#             leaderboard_user_id=lb_user.leaderboard_user_id,
#             match_id=match_id,
#             defaults={
#                 "points1": random.randint(0, 5),
#                 "points2": random.randint(0, 5)
#             }
#         )

#         if is_created:
#             created += 1

# print("Rows created:", created)

# create cumulative points in FinalLeaderboardPoints table for all users and matches

# from core.models.leaderboard_points import LeaderboardPoints
# from core.models.final_leaderboard_points import FinalLeaderboardPoints
# from core.models.cricket_match_details import CricketMatchDetails

# DB = "company_kt5xg8b0"

# # clear old cumulative table
# FinalLeaderboardPoints.objects.using(DB).all().delete()

# users = (
#     LeaderboardPoints.objects.using(DB)
#     .values_list("leaderboard_user_id", flat=True)
#     .distinct()
# )

# created = 0

# for user_id in users:

#     submissions = (
#         LeaderboardPoints.objects.using(DB)
#         .filter(leaderboard_user_id=user_id)
#         .order_by("match_id")   # temporary order
#     )

#     cumulative_p1 = 0
#     cumulative_p2 = 0

#     for sub in submissions:

#         # get match number from match table
#         match = CricketMatchDetails.objects.get(match_id=sub.match_id)

#         cumulative_p1 += sub.points1
#         cumulative_p2 += sub.points2

#         FinalLeaderboardPoints.objects.using(DB).create(
#             leaderboard_user_id=user_id,
#             match_id=sub.match_id,
#             match_number=match.display_match_id,
#             points1=cumulative_p1,
#             points2=cumulative_p2
#         )

#         created += 1

# print("Rows created:", created)