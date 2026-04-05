from django.shortcuts import render
from rest_framework.views import APIView

from core.authentication import CookieJWTAuthentication
from core.permissions import HasValidJWT
from core.utils.company import get_company_db

from core.models.user_submission import UserSubmission
from core.models.cricket_match_details import CricketMatchDetails
from core.models.cricket_team import CricketTeam
from core.models.cricket_player import CricketPlayer
from core.models.cricket_match_winner_details import CricketMatchWinnerDetails


class MySubmissionsViewV1(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [HasValidJWT]

    def get(self, request):
        token = request.auth

        user_id = token["user_id"]
        company_display_id = token["company_display_id"]

        db_alias = get_company_db(company_display_id)
        if not db_alias:
            # Extremely rare, but safe fallback
            return render(request, "submissions/my_submissions.html", {
                "submissions": []
            })

        # ---------- Fetch submissions (company DB) ----------
        submissions = (
            UserSubmission.objects.using(db_alias)
            .filter(user_id=user_id)
            .order_by("-updated_at")
        )

        submission_rows = []

        for sub in submissions:
            # ---------- Master data (default DB) ----------
            match = CricketMatchDetails.objects.select_related(
                "event", "team1", "team2"
            ).get(match_id=sub.match_id)

            submission_rows.append({
                "event_name": match.event.event_name,
                "match_name": match.match_name2,
                "winner_team": CricketTeam.objects.get(
                    team_id=sub.predicted_winner_team_id
                ).team_name,
                "mom": CricketPlayer.objects.get(
                    player_id=sub.predicted_player_of_match_id
                ).player_name,
                "most_runs": CricketPlayer.objects.get(
                    player_id=sub.predicted_most_runs_player_id
                ).player_name,
                "most_wickets": CricketPlayer.objects.get(
                    player_id=sub.predicted_most_wickets_taker_id
                ).player_name,
                "updated_at": sub.updated_at,
                "match_id": match.match_id,
            })

        return render(
            request,
            "submissions/my_submissions.html",
            {
                "submissions": submission_rows,
                "company_display_id": company_display_id,
                "user_id": user_id,
            }
        )

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.authentication import CookieJWTAuthentication
from core.permissions import HasValidJWT
from core.utils.company import get_company_db

from core.models.user_submission import UserSubmission
from core.models.cricket_match_details import CricketMatchDetails
from core.models.cricket_team import CricketTeam
from core.models.cricket_player import CricketPlayer


class MySubmissionsAPIViewV2(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [HasValidJWT]

    def get(self, request):
        token = request.auth

        user_id = token["user_id"]
        company_display_id = token["company_display_id"]

        db_alias = get_company_db(company_display_id)
        if not db_alias:
            return Response(
                {"submissions": []},
                status=status.HTTP_200_OK,
            )

        # ---------- Fetch submissions (company DB) ----------
        submissions = (
            UserSubmission.objects.using(db_alias)
            .filter(user_id=user_id)
            .order_by("-updated_at")
        )

        if not submissions:
            return Response(
                {
                    "company_display_id": company_display_id,
                    "user_id": user_id,
                    "submissions": [],
                },
                status=status.HTTP_200_OK,
            )

        # ---------- Collect IDs ----------
        match_ids = {s.match_id for s in submissions}
        team_ids = set()
        player_ids = set()

        for s in submissions:
            team_ids.add(s.predicted_winner_team_id)
            player_ids.update([
                s.predicted_player_of_match_id,
                s.predicted_most_runs_player_id,
                s.predicted_most_wickets_taker_id,
            ])

        # ---------- Bulk fetch master data (default DB) ----------
        matches = {
            m.match_id: m
            for m in CricketMatchDetails.objects.select_related(
                "event", "team1", "team2"
            ).filter(match_id__in=match_ids)
        }

        teams = {
            t.team_id: t.team_name
            for t in CricketTeam.objects.filter(team_id__in=team_ids)
        }

        players = {
            p.player_id: p.player_name
            for p in CricketPlayer.objects.filter(player_id__in=player_ids)
        }

        # ---------- Build response ----------
        submission_rows = []

        for sub in submissions:
            match = matches.get(sub.match_id)
            if not match:
                continue

            submission_rows.append({
                "match_id": match.match_id,
                "event_id": match.event.event_id,
                "event_name": match.event.event_name,
                "match_name": match.match_name2,
                "team1": match.team1.team_name,
                "team2": match.team2.team_name,
                "predicted_winner_team": teams.get(sub.predicted_winner_team_id),
                "predicted_player_of_match": players.get(sub.predicted_player_of_match_id),
                "predicted_most_runs": players.get(sub.predicted_most_runs_player_id),
                "predicted_most_wickets": players.get(sub.predicted_most_wickets_taker_id),
                "points_winner": sub.points_winner,
                "points_mom": sub.points_mom,
                "points_runs": sub.points_runs,
                "points_wickets": sub.points_wickets,
                "total_points": sub.total_points,
                "flag_winner": sub.flag_winner,
                "flag_mom": sub.flag_mom,
                "flag_mruns": sub.flag_mruns,
                "flag_mwickets": sub.flag_mwickets,
                "updated_at": sub.updated_at,
            })

        return Response(
            {
                "company_display_id": company_display_id,
                "user_id": user_id,
                "submissions": submission_rows,
            },
            status=status.HTTP_200_OK,
        )

class MySubmissionsByEventAPIViewV2(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [HasValidJWT]

    def get(self, request, event_id):
        token = request.auth

        user_id = token["user_id"]
        company_display_id = token["company_display_id"]

        db_alias = get_company_db(company_display_id)
        if not db_alias:
            return Response(
                {"submissions": []},
                status=status.HTTP_200_OK,
            )

        # ✅ Filter submissions by event_id
        submissions = (
            UserSubmission.objects.using(db_alias)
            .filter(user_id=user_id, event_id=event_id)
            .order_by("-updated_at")
        )

        if not submissions.exists():
            return Response(
                {
                    "company_display_id": company_display_id,
                    "user_id": user_id,
                    "event_id": event_id,
                    "submissions": [],
                },
                status=status.HTTP_200_OK,
            )

        # ---------- Collect IDs ----------
        match_ids = {s.match_id for s in submissions}
        team_ids = set()
        player_ids = set()

        for s in submissions:
            team_ids.add(s.predicted_winner_team_id)
            player_ids.update([
                s.predicted_player_of_match_id,
                s.predicted_most_runs_player_id,
                s.predicted_most_wickets_taker_id,
            ])

        # ---------- Bulk fetch master data (default DB) ----------
        matches = {
            m.match_id: m
            for m in CricketMatchDetails.objects.select_related(
                "event", "team1", "team2"
            ).filter(match_id__in=match_ids)
        }

        teams = {
            t.team_id: t.team_name
            for t in CricketTeam.objects.filter(team_id__in=team_ids)
        }

        players = {
            p.player_id: p.player_name
            for p in CricketPlayer.objects.filter(player_id__in=player_ids)
        }

        winner_details_qs = CricketMatchWinnerDetails.objects.select_related(
        "winner_team"
        ).prefetch_related(
            "player_of_match_1",
            "most_runs_player_1",
            "most_wickets_player_1"
        ).filter(match__match_id__in=match_ids)

        winner_details = {
            w.match.match_id: w for w in winner_details_qs
        }

        # ---------- Build response ----------
        submission_rows = []
        completed_predictions = []

        for sub in submissions:
            match = matches.get(sub.match_id)
            winner = winner_details.get(sub.match_id)
            if not match:
                continue

            row = {
                "match_id": match.match_id,
                "match_display_id": match.display_match_id,
                "event_id": match.event.event_id,
                "event_name": match.event.event_name,
                "event_short_name": match.event.short_name,
                "match_date": match.match_date,
                "match_time": match.match_time,
                "match_name": match.match_name2,
                "match_status": match.get_status_id_display(),
                "location": match.location,
                "stadium": match.stadium,

                "team1": match.team1.team_name,
                "team2": match.team2.team_name,

                # ---------- Actual Results ----------

                "actual_winner_team": (
                    winner.winner_team.team_name
                    if winner and winner.winner_team else None
                ),

                "actual_player_of_match": (
                    [p.player_name for p in winner.player_of_match_1.all()]
                    if winner else []
                ),
                "actual_most_runs_player": (
                    [p.player_name for p in winner.most_runs_player_1.all()]
                    if winner else []
                ),
                "actual_most_wickets_taker": (
                    [p.player_name for p in winner.most_wickets_player_1.all()]
                    if winner else []
                ),

                # ---------- User Predictions ----------
                "predicted_winner_team": teams.get(sub.predicted_winner_team_id),
                "predicted_player_of_match": players.get(sub.predicted_player_of_match_id),
                "predicted_most_runs": players.get(sub.predicted_most_runs_player_id),
                "predicted_most_wickets": players.get(sub.predicted_most_wickets_taker_id),

                # ---------- Points ----------
                "points_winner": sub.points_winner,
                "points_mom": sub.points_mom,
                "points_runs": sub.points_runs,
                "points_wickets": sub.points_wickets,
                "total_points": sub.total_points,
                "max_points": 11,  # Placeholder, can be dynamic based on scoring rules

                # ---------- Flags ----------
                "flag_winner": sub.flag_winner,
                "flag_mom": sub.flag_mom,
                "flag_mruns": sub.flag_mruns,
                "flag_mwickets": sub.flag_mwickets,

                "updated_at": sub.updated_at,
            }

            submission_rows.append(row)
            if match.status_id in [3, 4]:
                completed_predictions.append(row)

        total_matches = CricketMatchDetails.objects.filter(
            event_id=event_id
        ).count()

        predicted_matches = (
            UserSubmission.objects.using(db_alias)
            .filter(user_id=user_id, event_id=event_id)
            .values("match_id")
            .distinct()
            .count()
        )

        upcoming_matches = CricketMatchDetails.objects.filter(
            event_id=event_id,
            status_id__in=[1, 2],
            is_active=True,
            is_deleted=False
        ).order_by("match_date", "match_time")[:9]

        upcoming_matches_data = []

        for match in upcoming_matches:
            upcoming_matches_data.append({
                "match_id": match.match_id,
                "match_display_id": match.display_match_id,
                "match_date": match.match_date,
                "match_time": match.match_time,
                "status_id": match.get_status_id_display(),

                "location": match.location,
                "stadium": match.stadium,

                "event_name": match.event.event_name,
                "event_short_name": match.event.short_name,

                "team1": {
                    "team_id": match.team1.team_id,
                    "team_name": match.team1.team_name,
                    "team_short_name": match.team1.short_name,
                },
                "team2": {
                    "team_id": match.team2.team_id,
                    "team_name": match.team2.team_name,
                    "team_short_name": match.team2.short_name,
                },
            })

        submission_rows = sorted(
            submission_rows,
            key=lambda x: x["match_display_id"],
            reverse=True
        )

        completed_predictions = sorted(
            completed_predictions,
            key=lambda x: x["match_display_id"],
            reverse=True
        )

        upcoming_matches_data = sorted(
            upcoming_matches_data,
            key=lambda x: x["match_display_id"]
        )

        return Response(
            {
                "company_display_id": company_display_id,
                "user_id": user_id,
                "event_id": event_id,
                "kpis": {
                    "total_matches": total_matches,
                    "matches_predicted": predicted_matches,
                    "streak": 0,  # Placeholder for future implementation
                },
                "submissions": submission_rows,
                "completed_predictions": completed_predictions,
                "upcoming_matches_display_card": upcoming_matches_data,
            },
            status=status.HTTP_200_OK,
        )
