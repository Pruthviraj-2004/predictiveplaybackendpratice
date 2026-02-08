from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.authentication import CookieJWTAuthentication
from core.permissions import HasValidJWT

from core.models.cricket_event import CricketEvent
from core.models.leaderboard import Leaderboard


class LeaderboardEventsAPIViewV2(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [HasValidJWT]

    def get(self, request):
        token = request.auth
        company_display_id = token["company_display_id"]

        # ---------- Active events (master DB) ----------
        events = CricketEvent.objects.filter(
            is_active=True,
            is_deleted=False
        ).order_by("start_date")

        # ---------- Existing leaderboards for company ----------
        leaderboard_event_ids = set(
            Leaderboard.objects.filter(
                company_display_id=company_display_id
            ).values_list("event_id", flat=True)
        )

        response_events = []

        for event in events:
            response_events.append({
                "event_id": event.event_id,
                "event_name": event.event_name,
                "short_name": event.short_name,
                "start_date": event.start_date,
                "end_date": event.end_date,
                "has_leaderboard": event.event_id in leaderboard_event_ids,
            })

        return Response(
            {
                "company_display_id": company_display_id,
                "events": response_events,
            },
            status=status.HTTP_200_OK,
        )


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.authentication import CookieJWTAuthentication
from core.permissions import HasValidJWT
from core.utils.company import get_company_db

from core.models.leaderboard import Leaderboard
from core.models.leaderboard_user import LeaderboardUser


class UserLeaderboardsByEventAPIViewV2(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [HasValidJWT]

    def get(self, request, event_id):
        token = request.auth

        user_id = token["user_id"]
        company_display_id = token["company_display_id"]

        db_alias = get_company_db(company_display_id)
        if not db_alias:
            return Response(
                {"leaderboards": []},
                status=status.HTTP_200_OK,
            )

        # ---------- Step 1: leaderboards where user EXISTS ----------
        user_leaderboard_ids = LeaderboardUser.objects.using(db_alias).filter(
            user_id=user_id,
            is_deleted=False
        ).values_list("leaderboard_id", flat=True)

        if not user_leaderboard_ids:
            return Response(
                {
                    "event_id": event_id,
                    "company_display_id": company_display_id,
                    "leaderboards": [],
                },
                status=status.HTTP_200_OK,
            )

        # ---------- Step 2: leaderboards for this event + company ----------
        leaderboards = Leaderboard.objects.using(db_alias).filter(
            leaderboard_id__in=user_leaderboard_ids,
            event_id=event_id,
            company_display_id=company_display_id
        ).order_by("leaderboard_name")

        data = [
            {
                "leaderboard_id": lb.leaderboard_id,
                "leaderboard_name": lb.leaderboard_name,
                "tag1": lb.tag1,
                "tag2": lb.tag2,
                "created_on": lb.created_on_1,
            }
            for lb in leaderboards
        ]

        return Response(
            {
                "event_id": event_id,
                "company_display_id": company_display_id,
                "leaderboards": data,
            },
            status=status.HTTP_200_OK,
        )

from collections import defaultdict

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.authentication import CookieJWTAuthentication
from core.permissions import HasValidJWT
from core.utils.company import get_company_db

from core.models.leaderboard import Leaderboard
from core.models.leaderboard_user import LeaderboardUser
from core.models.user_submission import UserSubmission
from core.models.company_user import CompanyUser


class LeaderboardBoardAPIViewV2(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [HasValidJWT]

    def get(self, request, leaderboard_id):
        token = request.auth
        company_display_id = token["company_display_id"]

        db_alias = get_company_db(company_display_id)
        if not db_alias:
            return Response({"rows": []}, status=status.HTTP_200_OK)

        # ---------- Leaderboard ----------
        try:
            leaderboard = Leaderboard.objects.using(db_alias).get(
                leaderboard_id=leaderboard_id,
                company_display_id=company_display_id
            )
        except Leaderboard.DoesNotExist:
            return Response(
                {"detail": "Leaderboard not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # ---------- Users in leaderboard ----------
        leaderboard_users = LeaderboardUser.objects.using(db_alias).filter(
            leaderboard_id=leaderboard_id,
            is_deleted=False
        ).values_list("user_id", flat=True)

        if not leaderboard_users:
            return Response(
                {
                    "leaderboard_id": leaderboard_id,
                    "rows": []
                },
                status=status.HTTP_200_OK,
            )

        # ---------- Fetch users ----------
        users = {
            u.user_id: u.username
            for u in CompanyUser.objects.using(db_alias).filter(
                user_id__in=leaderboard_users
            )
        }

        # ---------- Fetch submissions for this event ----------
        submissions = UserSubmission.objects.using(db_alias).filter(
            user_id__in=leaderboard_users,
            event_id=leaderboard.event_id
        )

        # ---------- Initialize scores for ALL leaderboard users ----------
        scores = {
            user_id: {
                "points1": 0,
                "points2": 0,
            }
            for user_id in leaderboard_users
        }

        # ---------- Add points from submissions ----------
        for sub in submissions:
            scores[sub.user_id]["points1"] += (
                leaderboard.leaderboard_points_winner_team +
                leaderboard.leaderboard_points_mom
            )
            scores[sub.user_id]["points2"] += (
                leaderboard.leaderboard_points_runs +
                leaderboard.leaderboard_points_wickets
            )

        # ---------- Build rows ----------
        rows = []
        for user_id, score in scores.items():
            total = score["points1"] + score["points2"]
            rows.append({
                "username": users.get(user_id, "Unknown"),
                "points1": score["points1"],
                "points2": score["points2"],
                "total_points": total,
            })


        # ---------- Sort & rank ----------
        rows.sort(key=lambda x: x["total_points"], reverse=True)

        for idx, row in enumerate(rows, start=1):
            row["rank"] = idx

        return Response(
            {
                "leaderboard_id": leaderboard.leaderboard_id,
                "leaderboard_name": leaderboard.leaderboard_name,
                "event_id": leaderboard.event_id,
                "rows": rows,
            },
            status=status.HTTP_200_OK,
        )
