from django.shortcuts import render, redirect
from django.utils import timezone
from rest_framework.views import APIView

from core.authentication import CookieJWTAuthentication
from core.permissions import HasValidJWT
from core.utils.company import get_company_db

from core.models.cricket_match_details import CricketMatchDetails
from core.models.cricket_player import CricketPlayer
from core.models.user_submission import UserSubmission


class MatchPredictionViewV1(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [HasValidJWT]

    def get(self, request, match_id):
        token = request.auth

        user_id = token["user_id"]
        company_display_id = token["company_display_id"]
        db_alias = get_company_db(company_display_id)

        # ---------- FETCH MATCH (default DB) ----------
        try:
            match = CricketMatchDetails.objects.select_related(
                "team1", "team2", "event"
            ).get(match_id=match_id, is_deleted=False)
        except CricketMatchDetails.DoesNotExist:
            return redirect("select_event")

        teams = [match.team1, match.team2]

        # ---------- PLAYERS FROM MATCH TEAMS ----------
        base_players = CricketPlayer.objects.filter(
            team__in=teams,
            is_active=True,
            is_deleted=False
        ).select_related("team")

        mom_players = base_players

        run_scorers = base_players.filter(
            role__in=[
                CricketPlayer.ROLE_BATTER,
                CricketPlayer.ROLE_ALL_ROUNDER,
            ]
        )

        wicket_takers = base_players.filter(
            role__in=[
                CricketPlayer.ROLE_ALL_ROUNDER,
                CricketPlayer.ROLE_BOWLER,
            ]
        )

        # ---------- EXISTING SUBMISSION (company DB) ----------
        submission = UserSubmission.objects.using(db_alias).filter(
            user_id=user_id,
            match_id=match.match_id
        ).first()

        return render(
            request,
            "matches/match_prediction.html",
            {
                "match": match,
                "teams": teams,
                "mom_players": mom_players,
                "run_scorers": run_scorers,
                "wicket_takers": wicket_takers,
                "submission": submission,
                "company_display_id": company_display_id,
            }
        )

    def post(self, request, match_id):
        token = request.auth

        user_id = token["user_id"]
        company_display_id = token["company_display_id"]
        db_alias = get_company_db(company_display_id)

        # ---------- FETCH MATCH (default DB) ----------
        try:
            match = CricketMatchDetails.objects.get(
                match_id=match_id,
                is_deleted=False
            )
        except CricketMatchDetails.DoesNotExist:
            return redirect("select_event")

        winning_team_id = request.POST.get("winning_team")
        pom_id = request.POST.get("player_of_match")
        runs_id = request.POST.get("most_runs")
        wickets_id = request.POST.get("most_wickets")

        # ---------- BASIC VALIDATION ----------
        if not all([winning_team_id, pom_id, runs_id, wickets_id]):
            return redirect("match_prediction", match_id=match_id)

        # ---------- SAVE / UPDATE (company DB) ----------
        UserSubmission.objects.using(db_alias).update_or_create(
            user_id=user_id,
            match_id=match.match_id,
            defaults={
                "event_id": match.event.event_id,
                "predicted_winner_team_id": winning_team_id,
                "predicted_player_of_match_id": pom_id,
                "predicted_most_runs_player_id": runs_id,
                "predicted_most_wickets_taker_id": wickets_id,
                "updated_at": timezone.now(),
            }
        )

        # ---------- REDIRECT ----------
        return redirect("fixtures", event_id=match.event.event_id)

from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.authentication import CookieJWTAuthentication
from core.permissions import HasValidJWT
from core.utils.company import get_company_db

from core.models.cricket_match_details import CricketMatchDetails
from core.models.cricket_player import CricketPlayer
from core.models.user_submission import UserSubmission


class MatchPredictionAPIViewV2(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [HasValidJWT]

    def get(self, request, match_id):
        token = request.auth

        user_id = token["user_id"]
        company_display_id = token["company_display_id"]
        db_alias = get_company_db(company_display_id)

        # ---------- FETCH MATCH (default DB) ----------
        try:
            match = CricketMatchDetails.objects.select_related(
                "team1", "team2", "event"
            ).get(match_id=match_id, is_deleted=False)
        except CricketMatchDetails.DoesNotExist:
            return Response(
                {"detail": "Match not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        teams = [match.team1, match.team2]

        # ---------- PLAYERS ----------
        base_players = CricketPlayer.objects.filter(
            team__in=teams,
            is_active=True,
            is_deleted=False
        ).select_related("team")

        def serialize_player(p):
            return {
                "player_id": p.player_id,
                "player_name": p.player_name,
                "team_id": p.team.team_id,
                "team_name": p.team.team_name,
                "role": p.role,
            }

        mom_players = [serialize_player(p) for p in base_players]

        run_scorers = [
            serialize_player(p)
            for p in base_players.filter(
                role__in=[
                    CricketPlayer.ROLE_BATTER,
                    CricketPlayer.ROLE_ALL_ROUNDER,
                ]
            )
        ]

        wicket_takers = [
            serialize_player(p)
            for p in base_players.filter(
                role__in=[
                    CricketPlayer.ROLE_ALL_ROUNDER,
                    CricketPlayer.ROLE_BOWLER,
                ]
            )
        ]

        # ---------- EXISTING SUBMISSION (company DB) ----------
        submission = UserSubmission.objects.using(db_alias).filter(
            user_id=user_id,
            match_id=match.match_id
        ).first()

        submission_data = None
        if submission:
            submission_data = {
                "predicted_winner_team_id": submission.predicted_winner_team_id,
                "predicted_player_of_match_id": submission.predicted_player_of_match_id,
                "predicted_most_runs_player_id": submission.predicted_most_runs_player_id,
                "predicted_most_wickets_taker_id": submission.predicted_most_wickets_taker_id,
            }

        return Response(
            {
                "company_display_id": company_display_id,
                "match": {
                    "match_id": match.match_id,
                    "match_date": match.match_date,
                    "match_time": match.match_time,
                    "event_id": match.event.event_id,
                    "event_name": match.event.event_name,
                    "team1": {
                        "team_id": match.team1.team_id,
                        "team_name": match.team1.team_name,
                    },
                    "team2": {
                        "team_id": match.team2.team_id,
                        "team_name": match.team2.team_name,
                    },
                },
                "teams": [
                    {
                        "team_id": t.team_id,
                        "team_name": t.team_name,
                    }
                    for t in teams
                ],
                "mom_players": mom_players,
                "run_scorers": run_scorers,
                "wicket_takers": wicket_takers,
                "submission": submission_data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request, match_id):
        token = request.auth

        user_id = token["user_id"]
        company_display_id = token["company_display_id"]
        db_alias = get_company_db(company_display_id)

        # ---------- FETCH MATCH ----------
        try:
            match = CricketMatchDetails.objects.get(
                match_id=match_id,
                is_deleted=False
            )
        except CricketMatchDetails.DoesNotExist:
            return Response(
                {"detail": "Match not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        winning_team_id = request.data.get("winning_team_id")
        pom_id = request.data.get("player_of_match_id")
        runs_id = request.data.get("most_runs_player_id")
        wickets_id = request.data.get("most_wickets_player_id")

        # ---------- VALIDATION ----------
        if not all([winning_team_id, pom_id, runs_id, wickets_id]):
            return Response(
                {"detail": "All prediction fields are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ---------- SAVE / UPDATE (company DB) ----------
        UserSubmission.objects.using(db_alias).update_or_create(
            user_id=user_id,
            match_id=match.match_id,
            defaults={
                "event_id": match.event.event_id,
                "predicted_winner_team_id": winning_team_id,
                "predicted_player_of_match_id": pom_id,
                "predicted_most_runs_player_id": runs_id,
                "predicted_most_wickets_taker_id": wickets_id,
                "updated_at": timezone.now(),
            }
        )

        return Response(
            {
                "message": "Prediction saved successfully",
                "match_id": match.match_id,
                "event_id": match.event.event_id,
            },
            status=status.HTTP_200_OK,
        )

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.models.cricket_match_details import CricketMatchDetails


class ActiveMatchesAPIViewV2(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [HasValidJWT]

    def get(self, request):
        token = request.auth

        matches = (
            CricketMatchDetails.objects
            .select_related("event", "team1", "team2")
            .filter(
                is_active=True,
                is_deleted=False,
                status_id__in=[
                    CricketMatchDetails.STATUS_SCHEDULED,
                    CricketMatchDetails.STATUS_LIVE,
                ],
            )
            .order_by("match_date", "match_time")
        )

        data = []

        for match in matches:
            data.append({
                "match_id": match.match_id,
                "display_match_id": match.display_match_id,
                "match_date": match.match_date,
                "match_time": match.match_time,
                "status_id": match.status_id,
                "status_label": match.get_status_id_display(),
                "allow_predictions": match.allow_predictions,
                "event": {
                    "event_id": match.event.event_id,
                    "event_name": match.event.event_name,
                },
                "team1": {
                    "team_id": match.team1.team_id,
                    "team_display_id": match.team1.display_team_id,
                    "team_name": match.team1.team_name,
                    "short_name": match.team1.short_name,
                },
                "team2": {
                    "team_id": match.team2.team_id,
                    "team_display_id": match.team2.display_team_id,
                    "team_name": match.team2.team_name,
                    "short_name": match.team2.short_name,
                },
            })

        return Response(
            {"matches": data},
            status=status.HTTP_200_OK,
        )
