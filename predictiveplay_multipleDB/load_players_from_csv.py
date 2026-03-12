import csv
import os
import django
from uuid import UUID

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "predictiveplay_multipleDB.settings")
django.setup()

# from core.models.cricket_event import CricketEvent
# from core.models.cricket_team import CricketTeam
# from core.models.cricket_player import CricketPlayer


# CSV_FILE = "playersinfo1.csv"
# EVENT_ID = UUID("b68329a5-9e1b-4e1f-a239-488a3672b521")


# ROLE_MAP = {
#     "batter": "BATTER",
#     "bowler": "BOWLER",
#     "all rounder": "ALL_ROUNDER",
# }


# def load_players():

#     event = CricketEvent.objects.get(event_id=EVENT_ID)

#     # Fetch all teams for this event
#     teams = CricketTeam.objects.filter(event=event, is_deleted=False)

#     team_map = {team.team_name.lower(): team for team in teams}

#     team_player_counter = {}

#     with open(CSV_FILE, newline="", encoding="utf-8") as file:
#         reader = csv.DictReader(file)

#         for row in reader:
#             player_name = row["playerName"].strip()
#             team_name = row["playerTeamNo"].strip().lower()
#             role_raw = row["playerRole"].strip().lower()

#             role = ROLE_MAP.get(role_raw)

#             if role is None:
#                 print(f"❌ Invalid role for {player_name}: {role_raw}")
#                 continue

#             if team_name not in team_map:
#                 print(f"❌ Team not found: {team_name}")
#                 continue

#             team = team_map[team_name]

#             # initialize counter
#             if team.team_id not in team_player_counter:

#                 existing_count = CricketPlayer.objects.filter(
#                     event=event,
#                     team=team,
#                     is_deleted=False
#                 ).count()

#                 team_player_counter[team.team_id] = existing_count + 1
#             else:
#                 team_player_counter[team.team_id] += 1

#             display_player_id = team_player_counter[team.team_id]

#             CricketPlayer.objects.create(
#                 display_player_id=display_player_id,
#                 player_name=player_name,
#                 team=team,
#                 event=event,
#                 role=role
#             )

#             print(f"✅ {player_name} -> {team.team_name} ({display_player_id})")


# if __name__ == "__main__":
#     load_players()


from core.models.cricket_event import CricketEvent
from core.models.cricket_team import CricketTeam
from core.models.cricket_player import CricketPlayer

CSV_FILE = "playersinfo2.csv"
EVENT_ID = UUID("916227b7-e825-4067-ae23-17385707ef32")


ROLE_MAP = {
    "batter": "BATTER",
    "bowler": "BOWLER",
    "all rounder": "ALL_ROUNDER",
}


def load_players():

    event = CricketEvent.objects.get(event_id=EVENT_ID)

    teams = CricketTeam.objects.filter(event=event, is_deleted=False)

    team_map = {team.team_name.lower(): team for team in teams}

    with open(CSV_FILE, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        reader.fieldnames = [h.strip() for h in reader.fieldnames]

        for row in reader:

            display_no = int(row["DisplayNo"])
            player_name = row["Player"].strip()
            team_name = row["Team"].strip().lower()
            role_raw = row["Role"].strip().lower()

            role = ROLE_MAP.get(role_raw)

            if role is None:
                print(f"❌ Invalid role for {player_name}: {role_raw}")
                continue

            if team_name not in team_map:
                print(f"❌ Team not found: {team_name}")
                continue

            team = team_map[team_name]

            CricketPlayer.objects.create(
                display_player_id=display_no,
                player_name=player_name,
                team=team,
                event=event,
                role=role
            )

            print(f"✅ {display_no} - {player_name} -> {team.team_name}")


if __name__ == "__main__":
    load_players()