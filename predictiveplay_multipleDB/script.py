import os
import django
import uuid

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "predictiveplay_multipleDB.settings")
django.setup()


#create 25 dummy users in company_kt5xg8b0 database

# from django.contrib.auth.hashers import make_password
# from core.models.company_user import CompanyUser

# db = "company_w5ddym3d"

# users = []

# for i in range(2, 26):
#     users.append(
#         CompanyUser(
#             user_id=uuid.uuid4(),
#             company_display_id="W5DDYM3D",
#             username=f"testuser{i}",
#             full_name=f"Test User {i}",
#             password=make_password("1234567890"),
#         )
#     )

# CompanyUser.objects.using(db).bulk_create(users)
# print("25 dummy users created successfully")


# add LeaderboardUser

# from core.models.company_user import CompanyUser
# from core.models.leaderboard import Leaderboard
# from core.models.leaderboard_user import LeaderboardUser

# db = "company_w5ddym3d"

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

# add random user submissions for a specific match

# from core.models.user_submission import UserSubmission
# from core.models.cricket_match_details import CricketMatchDetails
# from core.models.cricket_player import CricketPlayer
# from core.models.company_user import CompanyUser

# import uuid
# import random

# DB = "company_w5ddym3d"

# match_id = uuid.UUID("ef246e72-161a-4d5b-9266-7ae55f6a4937")

# # ✅ Fetch match
# match = CricketMatchDetails.objects.get(match_id=match_id)

# team_ids = [match.team1_id, match.team2_id]

# # ✅ Fetch players only from these teams
# players = list(
#     CricketPlayer.objects
#     .filter(team_id__in=team_ids)
#     .values_list("player_id", flat=True)
# )

# # Safety check
# if not players:
#     raise Exception("No players found for this match!")

# # ✅ Fetch users
# users = CompanyUser.objects.using(DB).all()

# created_count = 0
# skipped_count = 0

# for user in users:

#     # ✅ Skip if already submitted (unique_together protection)
#     if UserSubmission.objects.using(DB).filter(user=user, match_id=match_id).exists():
#         skipped_count += 1
#         continue

#     UserSubmission.objects.using(DB).create(
#         user=user,
#         event_id=match.event_id,
#         match_id=match_id,

#         predicted_winner_team_id=random.choice(team_ids),
#         predicted_player_of_match_id=random.choice(players),
#         predicted_most_runs_player_id=random.choice(players),
#         predicted_most_wickets_taker_id=random.choice(players),
#     )

#     created_count += 1

# print(f"✅ Created: {created_count}, Skipped: {skipped_count}")

# add user submissions for all matches

# from core.models.user_submission import UserSubmission
# from core.models.cricket_match_details import CricketMatchDetails
# from core.models.cricket_player import CricketPlayer
# from core.models.company_user import CompanyUser

# import uuid
# import random

# DB = "company_w5ddym3d"

# event_id = uuid.UUID("b68329a5-9e1b-4e1f-a239-488a3672b521")

# # ✅ Get all matches of event (MASTER DB)
# matches = CricketMatchDetails.objects.filter(event_id=event_id)

# # ✅ Get all users (COMPANY DB)
# users = list(CompanyUser.objects.using(DB).all())

# created_count = 0
# skipped_count = 0

# for match in matches:
#     match_id = match.match_id
#     team_ids = [match.team1_id, match.team2_id]

#     # ✅ Get players for this match (MASTER DB)
#     players = list(
#         CricketPlayer.objects
#         .filter(team_id__in=team_ids)
#         .values_list("player_id", flat=True)
#     )

#     if not players:
#         print(f"⚠️ No players found for match {match_id}, skipping...")
#         continue

#     for user in users:

#         # ✅ Skip if already exists
#         if UserSubmission.objects.using(DB).filter(user=user, match_id=match_id).exists():
#             skipped_count += 1
#             continue

#         UserSubmission.objects.using(DB).create(
#             user=user,
#             event_id=event_id,
#             match_id=match_id,

#             predicted_winner_team_id=random.choice(team_ids),
#             predicted_player_of_match_id=random.choice(players),
#             predicted_most_runs_player_id=random.choice(players),
#             predicted_most_wickets_taker_id=random.choice(players),
#         )

#         created_count += 1

# print(f"\n✅ Created: {created_count}")
# print(f"⏭️ Skipped (already exists): {skipped_count}")

# add match winner details for specific match

# from core.models.cricket_match_winner_details import CricketMatchWinnerDetails
# from core.models.cricket_match_details import CricketMatchDetails
# from core.models.cricket_player import CricketPlayer

# import uuid
# import random

# match_id = uuid.UUID("ef246e72-161a-4d5b-9266-7ae55f6a4937")

# # ✅ Get match (MASTER DB)
# match = CricketMatchDetails.objects.get(match_id=match_id)
# event = match.event

# team_ids = [match.team1_id, match.team2_id]

# # ✅ Skip if already exists
# if CricketMatchWinnerDetails.objects.filter(event=event, match=match).exists():
#     print("⚠️ Winner details already exist, skipping...")
# else:

#     # ✅ Fetch players of this match
#     players = CricketPlayer.objects.filter(
#         team_id__in=team_ids,
#         event=event,
#         is_active=True,
#         is_deleted=False
#     )

#     players = list(players)

#     if not players:
#         raise Exception("No players found for this match")

#     # ✅ Role-based filtering
#     batters = [p for p in players if p.role == CricketPlayer.ROLE_BATTER]
#     all_rounders = [p for p in players if p.role == CricketPlayer.ROLE_ALL_ROUNDER]
#     bowlers = [p for p in players if p.role == CricketPlayer.ROLE_BOWLER]

#     # 🔥 Pools based on rules
#     pom_pool = players  # all roles
#     runs_pool = batters + all_rounders
#     wickets_pool = bowlers + all_rounders

#     # Safety fallback
#     if not runs_pool:
#         runs_pool = players
#     if not wickets_pool:
#         wickets_pool = players

#     # ✅ Random selections
#     winner_team_id = random.choice(team_ids)
#     player_of_match = random.choice(pom_pool)
#     most_runs_player = random.choice(runs_pool)
#     most_wickets_player = random.choice(wickets_pool)

#     # ✅ Create winner record
#     winner = CricketMatchWinnerDetails.objects.create(
#         event=event,
#         match=match,
#         winner_team_id=winner_team_id
#     )

#     # ✅ Add M2M relations
#     winner.player_of_match_1.add(player_of_match)
#     winner.most_runs_player_1.add(most_runs_player)
#     winner.most_wickets_player_1.add(most_wickets_player)

#     print("✅ Winner details created successfully!")
#     print(f"Winner Team: {winner_team_id}")
#     print(f"POM: {player_of_match.player_name}")
#     print(f"Most Runs: {most_runs_player.player_name}")
#     print(f"Most Wickets: {most_wickets_player.player_name}")


# add match winner details for all matches of an event

# from core.models.cricket_match_winner_details import CricketMatchWinnerDetails
# from core.models.cricket_match_details import CricketMatchDetails
# from core.models.cricket_player import CricketPlayer

# import uuid
# import random

# event_id = uuid.UUID("b68329a5-9e1b-4e1f-a239-488a3672b521")

# # ✅ Fetch all matches of event
# matches = CricketMatchDetails.objects.filter(event_id=event_id)

# created_count = 0
# skipped_count = 0

# for match in matches:

#     # ✅ Skip if already exists
#     if CricketMatchWinnerDetails.objects.filter(event=match.event, match=match).exists():
#         skipped_count += 1
#         continue

#     team_ids = [match.team1_id, match.team2_id]

#     # ✅ Fetch players for this match
#     players = list(
#         CricketPlayer.objects.filter(
#             team_id__in=team_ids,
#             event=match.event,
#             is_active=True,
#             is_deleted=False
#         )
#     )

#     if not players:
#         print(f"⚠️ No players for match {match.match_id}, skipping...")
#         continue

#     # ✅ Role-based grouping
#     batters = [p for p in players if p.role == CricketPlayer.ROLE_BATTER]
#     all_rounders = [p for p in players if p.role == CricketPlayer.ROLE_ALL_ROUNDER]
#     bowlers = [p for p in players if p.role == CricketPlayer.ROLE_BOWLER]

#     # ✅ Pools
#     pom_pool = players
#     runs_pool = batters + all_rounders
#     wickets_pool = bowlers + all_rounders

#     # 🔁 Fallback safety
#     if not runs_pool:
#         runs_pool = players
#     if not wickets_pool:
#         wickets_pool = players

#     # ✅ Random selections
#     winner_team_id = random.choice(team_ids)
#     player_of_match = random.choice(pom_pool)
#     most_runs_player = random.choice(runs_pool)
#     most_wickets_player = random.choice(wickets_pool)

#     # ✅ Create record
#     winner = CricketMatchWinnerDetails.objects.create(
#         event=match.event,
#         match=match,
#         winner_team_id=winner_team_id
#     )

#     # ✅ Add M2M
#     winner.player_of_match_1.add(player_of_match)
#     winner.most_runs_player_1.add(most_runs_player)
#     winner.most_wickets_player_1.add(most_wickets_player)

#     created_count += 1

# print(f"\n✅ Created: {created_count}")
# print(f"⏭️ Skipped: {skipped_count}")



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

# update user submissions for a match with match winner details to calculate points

# from core.models.user_submission import UserSubmission
# from core.models.cricket_match_winner_details import CricketMatchWinnerDetails

# import uuid

# DB = "company_w5ddym3d"

# match_id = uuid.UUID("ef246e72-161a-4d5b-9266-7ae55f6a4937")

# # ✅ Fetch winner details (MASTER DB)
# winner = CricketMatchWinnerDetails.objects.select_related(
#     "winner_team", "match", "event"
# ).get(match__match_id=match_id)

# # ✅ Extract actual results
# actual_winner_team_id = winner.winner_team_id

# # M2M → take first player (since you added 1)
# actual_pom_id = winner.player_of_match_1.values_list("player_id", flat=True).first()
# actual_runs_id = winner.most_runs_player_1.values_list("player_id", flat=True).first()
# actual_wickets_id = winner.most_wickets_player_1.values_list("player_id", flat=True).first()

# # Safety check
# if not all([actual_pom_id, actual_runs_id, actual_wickets_id]):
#     raise Exception("Winner details incomplete!")

# # ✅ Fetch all submissions (COMPANY DB)
# submissions = UserSubmission.objects.using(DB).filter(match_id=match_id)

# updated_count = 0

# for sub in submissions:

#     points_winner = 0
#     points_mom = 0
#     points_runs = 0
#     points_wickets = 0

#     flag_winner = False
#     flag_mom = False
#     flag_mruns = False
#     flag_mwickets = False

#     # ✅ Winner team
#     if sub.predicted_winner_team_id == actual_winner_team_id:
#         points_winner = 3
#         flag_winner = True

#     # ✅ Player of match
#     if sub.predicted_player_of_match_id == actual_pom_id:
#         points_mom = 4
#         flag_mom = True

#     # ✅ Most runs
#     if sub.predicted_most_runs_player_id == actual_runs_id:
#         points_runs = 2
#         flag_mruns = True

#     # ✅ Most wickets
#     if sub.predicted_most_wickets_taker_id == actual_wickets_id:
#         points_wickets = 2
#         flag_mwickets = True

#     total_points = points_winner + points_mom + points_runs + points_wickets

#     # ✅ Update submission
#     sub.points_winner = points_winner
#     sub.points_mom = points_mom
#     sub.points_runs = points_runs
#     sub.points_wickets = points_wickets
#     sub.total_points = total_points

#     sub.flag_winner = flag_winner
#     sub.flag_mom = flag_mom
#     sub.flag_mruns = flag_mruns
#     sub.flag_mwickets = flag_mwickets

#     sub.save(using=DB)

#     updated_count += 1

# print(f"✅ Updated submissions: {updated_count}")

# update user submissions for all matches of an event with match winner details to calculate points

# from core.models.user_submission import UserSubmission
# from core.models.cricket_match_winner_details import CricketMatchWinnerDetails
# from core.models.cricket_match_details import CricketMatchDetails

# import uuid

# DB = "company_w5ddym3d"

# event_id = uuid.UUID("b68329a5-9e1b-4e1f-a239-488a3672b521")

# # ✅ Fetch all matches of event (MASTER DB)
# matches = CricketMatchDetails.objects.filter(event_id=event_id)

# total_updated = 0
# skipped_matches = 0

# for match in matches:

#     match_id = match.match_id

#     # ✅ Get winner details
#     winner = CricketMatchWinnerDetails.objects.filter(
#         event=match.event,
#         match=match
#     ).first()

#     if not winner:
#         print(f"⏭️ Skipping match {match_id} (no winner data)")
#         skipped_matches += 1
#         continue

#     # ✅ Extract actual results
#     actual_winner_team_id = winner.winner_team_id

#     actual_pom_id = winner.player_of_match_1.values_list("player_id", flat=True).first()
#     actual_runs_id = winner.most_runs_player_1.values_list("player_id", flat=True).first()
#     actual_wickets_id = winner.most_wickets_player_1.values_list("player_id", flat=True).first()

#     if not all([actual_pom_id, actual_runs_id, actual_wickets_id]):
#         print(f"⚠️ Incomplete winner data for match {match_id}, skipping...")
#         skipped_matches += 1
#         continue

#     # ✅ Fetch submissions (COMPANY DB)
#     submissions = UserSubmission.objects.using(DB).filter(match_id=match_id)

#     for sub in submissions:

#         points_winner = 0
#         points_mom = 0
#         points_runs = 0
#         points_wickets = 0

#         flag_winner = False
#         flag_mom = False
#         flag_mruns = False
#         flag_mwickets = False

#         # ✅ Compare predictions
#         if sub.predicted_winner_team_id == actual_winner_team_id:
#             points_winner = 3
#             flag_winner = True

#         if sub.predicted_player_of_match_id == actual_pom_id:
#             points_mom = 4
#             flag_mom = True

#         if sub.predicted_most_runs_player_id == actual_runs_id:
#             points_runs = 2
#             flag_mruns = True

#         if sub.predicted_most_wickets_taker_id == actual_wickets_id:
#             points_wickets = 2
#             flag_mwickets = True

#         total_points = points_winner + points_mom + points_runs + points_wickets

#         # ✅ Update submission
#         sub.points_winner = points_winner
#         sub.points_mom = points_mom
#         sub.points_runs = points_runs
#         sub.points_wickets = points_wickets
#         sub.total_points = total_points

#         sub.flag_winner = flag_winner
#         sub.flag_mom = flag_mom
#         sub.flag_mruns = flag_mruns
#         sub.flag_mwickets = flag_mwickets

#         sub.save(using=DB)

#         total_updated += 1

# print(f"\n✅ Total Updated Submissions: {total_updated}")
# print(f"⏭️ Skipped Matches: {skipped_matches}")

# add points for all users in the global leaderboard for a specific match

# from core.models.user_submission import UserSubmission
# from core.models.leaderboard_points import LeaderboardPoints
# from core.models.cricket_match_details import CricketMatchDetails
# from core.models.leaderboard_user import LeaderboardUser  # assumed model
# from core.models.leaderboard import Leaderboard

# import uuid

# DB = "company_w5ddym3d"

# match_id = uuid.UUID("c3ac6e98-c9e6-4477-b9a3-603ccc44e8a5")

# # ✅ Fetch match
# match = CricketMatchDetails.objects.get(match_id=match_id)
# match_number = match.display_match_id

# # ✅ Fetch leaderboards
# global_lb = Leaderboard.objects.using(DB).get(leaderboard_name="Global")
# weekly_lb = Leaderboard.objects.using(DB).get(leaderboard_name="Weekly")

# # ✅ Fetch submissions
# submissions = UserSubmission.objects.using(DB).filter(match_id=match_id)

# created = 0
# skipped = 0

# for sub in submissions:

#     user_id = sub.user_id
#     total_points = sub.total_points

#     # ✅ Get leaderboard users (one for each leaderboard)
#     lb_users = LeaderboardUser.objects.using(DB).filter(
#         user_id=user_id,
#         leaderboard_id__in=[global_lb.leaderboard_id, weekly_lb.leaderboard_id]
#     )

#     for lb_user in lb_users:

#         # ✅ Skip if already exists
#         if LeaderboardPoints.objects.using(DB).filter(
#             leaderboard_user_id=lb_user.leaderboard_user_id,
#             match_id=match_id
#         ).exists():
#             skipped += 1
#             continue

#         LeaderboardPoints.objects.using(DB).create(
#             leaderboard_user_id=lb_user.leaderboard_user_id,
#             match_id=match_id,
#             match_number=match_number,
#             points1=total_points,
#             points2=total_points
#         )

#         created += 1

# print(f"✅ Created: {created}")
# print(f"⏭️ Skipped: {skipped}")

# add points for all users in the leaderboard for all matches in event

# from core.models.user_submission import UserSubmission
# from core.models.leaderboard_points import LeaderboardPoints
# from core.models.cricket_match_details import CricketMatchDetails
# from core.models.leaderboard_user import LeaderboardUser
# from core.models.leaderboard import Leaderboard

# import uuid

# DB = "company_w5ddym3d"

# event_id = uuid.UUID("b68329a5-9e1b-4e1f-a239-488a3672b521")

# # ✅ Fetch all matches (MASTER DB)
# matches = CricketMatchDetails.objects.filter(event_id=event_id)

# # ✅ Fetch leaderboards
# global_lb = Leaderboard.objects.using(DB).get(leaderboard_name="Global")
# weekly_lb = Leaderboard.objects.using(DB).get(leaderboard_name="Weekly")

# created = 0
# skipped = 0

# for match in matches:

#     match_id = match.match_id
#     match_number = match.display_match_id

#     # ✅ Fetch submissions (COMPANY DB)
#     submissions = UserSubmission.objects.using(DB).filter(match_id=match_id)

#     for sub in submissions:

#         user_id = sub.user_id
#         total_points = sub.total_points

#         # ✅ Get leaderboard users (Global + Weekly)
#         lb_users = LeaderboardUser.objects.using(DB).filter(
#             user_id=user_id,
#             leaderboard_id__in=[global_lb.leaderboard_id, weekly_lb.leaderboard_id]
#         )

#         for lb_user in lb_users:

#             # ✅ Skip duplicates
#             if LeaderboardPoints.objects.using(DB).filter(
#                 leaderboard_user_id=lb_user.leaderboard_user_id,
#                 match_id=match_id
#             ).exists():
#                 skipped += 1
#                 continue

#             LeaderboardPoints.objects.using(DB).create(
#                 leaderboard_user_id=lb_user.leaderboard_user_id,
#                 match_id=match_id,
#                 match_number=match_number,
#                 points1=total_points,
#                 points2=total_points
#             )

#             created += 1

# print(f"\n✅ Created: {created}")
# print(f"⏭️ Skipped: {skipped}")

# add final cumulative points for all users in the leaderboard for all matches in event

from core.models.leaderboard_points import LeaderboardPoints
from core.models.final_leaderboard_points import FinalLeaderboardPoints

from collections import defaultdict
import uuid

DB = "company_w5ddym3d"

event_id = uuid.UUID("b68329a5-9e1b-4e1f-a239-488a3672b521")

# ✅ Step 1: Get all match-level points
points_qs = LeaderboardPoints.objects.using(DB).all()

# ✅ Step 2: Get sorted unique matches
matches = sorted(
    set((p.match_id, p.match_number) for p in points_qs),
    key=lambda x: x[1] or 0
)

# ✅ Step 3: Initialize trackers
cumulative_map = defaultdict(int)   # user -> cumulative points
previous_rank_map = {}              # user -> previous rank

created = 0

# ✅ Step 4: Process match by match
for match_id, match_number in matches:

    # 🔹 Get all records for this match
    match_records = [p for p in points_qs if p.match_id == match_id]

    # 🔹 Update cumulative scores
    for r in match_records:
        cumulative_map[r.leaderboard_user_id] += r.points1

    # 🔹 Prepare ranking list
    ranking_list = [
        (user_id, cumulative_map[user_id])
        for user_id in cumulative_map
    ]

    # 🔥 Sort by points DESC
    ranking_list.sort(key=lambda x: (-x[1], x[0]))

    # 🔹 Assign ranks
    current_rank_map = {}
    rank = 1

    for idx, (user_id, points) in enumerate(ranking_list):
        if idx > 0 and points < ranking_list[idx - 1][1]:
            rank = idx + 1
        current_rank_map[user_id] = rank

    # 🔹 Insert records
    for user_id, cumulative_points in ranking_list:

        current_rank = current_rank_map[user_id]
        previous_rank = previous_rank_map.get(user_id, 0)

        # ✅ Skip if already exists
        if FinalLeaderboardPoints.objects.using(DB).filter(
            leaderboard_user_id=user_id,
            match_id=match_id
        ).exists():
            continue

        FinalLeaderboardPoints.objects.using(DB).create(
            leaderboard_user_id=user_id,
            match_id=match_id,
            match_number=match_number,
            points1=cumulative_points,
            points2=cumulative_points,
            rank=current_rank,
            previous_rank=previous_rank
        )

        created += 1

    # 🔥 Update previous rank map for next match
    previous_rank_map = current_rank_map.copy()

print(f"✅ Final leaderboard records created: {created}")


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

# update ranks in FinalLeaderboardPoints table for all matches

# from core.models.final_leaderboard_points import FinalLeaderboardPoints
# from django.db import connections

# DB = "company_kt5xg8b0"

# # Get all match numbers
# match_numbers = (
#     FinalLeaderboardPoints.objects.using(DB)
#     .values_list("match_number", flat=True)
#     .distinct()
#     .order_by("match_number")
# )

# previous_rank_map = {}

# for match in match_numbers:

#     rows = list(
#         FinalLeaderboardPoints.objects.using(DB)
#         .filter(match_number=match)
#     )

#     # sort by total points
#     rows.sort(key=lambda x: (x.points1 + x.points2), reverse=True)

#     current_rank_map = {}

#     for idx, row in enumerate(rows, start=1):

#         row.rank = idx
#         row.previous_rank = previous_rank_map.get(row.leaderboard_user_id)

#         current_rank_map[row.leaderboard_user_id] = idx

#     FinalLeaderboardPoints.objects.using(DB).bulk_update(
#         rows,
#         ["rank", "previous_rank"]
#     )

#     previous_rank_map = current_rank_map

# print("Ranks and previous ranks updated successfully")

# command to create leaderboard
# from core.models.leaderboard import Leaderboard
# from django.utils import timezone
# import uuid

# leaderboard = Leaderboard.objects.using("company_w5ddym3d").create(
#     leaderboard_name="Weekly", 
#     event_id=uuid.UUID("916227b7-e825-4067-ae23-17385707ef32"),
#     company_display_id="W5DDYM3D",
#     created_on_1=timezone.now().date()
# )

# print(leaderboard.leaderboard_id)