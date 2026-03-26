import csv
import os
import django
from uuid import UUID

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "predictiveplay_multipleDB.settings")
django.setup()


from datetime import datetime

from core.models.cricket_event import CricketEvent
from core.models.cricket_team import CricketTeam
from core.models.cricket_match_details import CricketMatchDetails


CSV_FILE = "matches.csv"

EVENT_ID = UUID("916227b7-e825-4067-ae23-17385707ef32")


def load_matches():

    # ---------- FETCH EVENT ----------
    try:
        event = CricketEvent.objects.get(event_id=EVENT_ID)
    except CricketEvent.DoesNotExist:
        print("❌ Event not found")
        return

    # ---------- FETCH TEAMS ----------
    teams = CricketTeam.objects.filter(event=event, is_deleted=False)
    team_map = {team.team_name.lower(): team for team in teams}

    # ---------- READ CSV ----------
    with open(CSV_FILE, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        reader.fieldnames = [h.strip() for h in reader.fieldnames]

        for row in reader:

            try:
                display_id = int(row["DISPLAY EVENT ID"])

                # ---------- DATE ----------
                match_date = datetime.strptime(
                    row["MATCH DATE"].strip(), "%d/%m/%Y"
                ).date()

                # ---------- TIME ----------
                match_time = datetime.strptime(
                    row["MATCH TIME"].strip(), "%I:%M %p"
                ).time()

                # ---------- TEAM MAPPING ----------
                team1_name = row["TEAM1"].strip().lower()
                team2_name = row["TEAM2"].strip().lower()

                if team1_name not in team_map:
                    print(f"❌ Team1 not found: {team1_name}")
                    continue

                if team2_name not in team_map:
                    print(f"❌ Team2 not found: {team2_name}")
                    continue

                team1 = team_map[team1_name]
                team2 = team_map[team2_name]

                # ---------- OPTIONAL FIELDS ----------
                location = row.get("LOCATION", "").strip()
                stadium = row.get("STADIUM", "").strip()
                match_name1 = row.get("MATCH  NAME1", "").strip()
                match_name2 = row.get("MATCH NAME2", "").strip()

                # ---------- DUPLICATE CHECK ----------
                exists = CricketMatchDetails.objects.filter(
                    event=event,
                    display_match_id=display_id
                ).exists()

                if exists:
                    print(f"⚠️ Already exists: Match {display_id}")
                    continue

                # ---------- CREATE ----------
                CricketMatchDetails.objects.create(
                    display_match_id=display_id,
                    match_date=match_date,
                    match_time=match_time,
                    event=event,
                    team1=team1,
                    team2=team2,
                    location=location or None,
                    stadium=stadium or None,
                    match_name1=match_name1 or None,
                    match_name2=match_name2 or None,
                    status_id=CricketMatchDetails.STATUS_SCHEDULED
                )

                print(f"✅ Match {display_id}: {team1.team_name} vs {team2.team_name}")

            except Exception as e:
                print(f"❌ Error in row {row}: {str(e)}")

if __name__ == "__main__":
    load_matches()