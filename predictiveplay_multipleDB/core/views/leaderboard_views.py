import uuid

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
        user_id = token["user_id"]

        # ---------- Active events (master DB) ----------
        events = CricketEvent.objects.filter(
            status=CricketEvent.STATUS_ACTIVE,
            allow_predictions=True
        ).order_by("start_date")

        # ---------- Company DB ----------
        db_alias = get_company_db(company_display_id)

        if not db_alias:
            return Response(
                {"events": []},
                status=status.HTTP_200_OK
            )

        # ---------- Events where user joined leaderboard ----------
        leaderboard_ids = LeaderboardUser.objects.using(db_alias).filter(
            user_id=user_id,
            is_deleted=False
        ).values_list("leaderboard_id", flat=True)

        # ---------- Get event_id for those leaderboards ----------
        leaderboards = Leaderboard.objects.using(db_alias).filter(
            leaderboard_id__in=leaderboard_ids
        ).values("leaderboard_id", "event_id")

        # ---------- Build event → leaderboard mapping ----------
        event_leaderboard_map = {}

        for lb in leaderboards:
            event_id = str(lb["event_id"])
            lb_id = str(lb["leaderboard_id"])

            if event_id not in event_leaderboard_map:
                event_leaderboard_map[event_id] = []

            event_leaderboard_map[event_id].append(lb_id)

        response_events = []

        for event in events:
            event_id_str = str(event.event_id)
            leaderboards_for_event = event_leaderboard_map.get(event_id_str, [])

            response_events.append({
                "event_id": event.event_id,
                "event_display_id": event.display_event_id,
                "event_name": event.event_name,
                "short_name": event.short_name,
                "event_start_date": event.start_date,
                "event_end_date": event.end_date,
                "event_status": event.status,
                "location": event.location,
                "allow_predictions": event.allow_predictions,
                "has_leaderboard": len(leaderboards_for_event) > 0,
                "leaderboards_count": len(leaderboards_for_event),
                "leaderboard_ids": leaderboards_for_event
            })

        return Response(
            {
                "company_display_id": company_display_id,
                "events": response_events,
            },
            status=status.HTTP_200_OK
        )

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.authentication import CookieJWTAuthentication
from core.permissions import HasValidJWT
from core.utils.company import get_company_db

from core.models.leaderboard import Leaderboard
from core.models.leaderboard_user import LeaderboardUser

import uuid

class UserLeaderboardsByEventAPIViewV2(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [HasValidJWT]

    def get(self, request, event_id):
        token = request.auth

        user_id = token["user_id"]
        company_display_id = token["company_display_id"]

        db_alias = get_company_db(company_display_id)
        if not db_alias:
            return Response({"leaderboards": []})

        event_uuid = uuid.UUID(event_id)

        # ---------- Events where user joined leaderboard ----------
        leaderboard_ids = LeaderboardUser.objects.using(db_alias).filter(
            user_id=user_id,
            is_deleted=False
        ).values_list("leaderboard_id", flat=True)

        # ---------- Get event_id for those leaderboards ----------
        leaderboards = Leaderboard.objects.using(db_alias).filter(
            leaderboard_id__in=leaderboard_ids,
            event_id=event_uuid,
            company_display_id=company_display_id
        )

        data = [
            {
                "leaderboard_id": lb.leaderboard_id,
                "leaderboard_name": lb.leaderboard_name,
                "tag1": lb.tag1,
                "tag2": lb.tag2
            }
            for lb in leaderboards
        ]

        return Response({
            "event_id": event_id,
            "company_display_id": company_display_id,
            "leaderboards": data
        })

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.authentication import CookieJWTAuthentication
from core.permissions import HasValidJWT
from core.utils.company import get_company_db

from core.models.leaderboard import Leaderboard
from core.models.leaderboard_user import LeaderboardUser
from core.models.final_leaderboard_points import FinalLeaderboardPoints
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

        # ---------- Leaderboard users ----------
        leaderboard_users = LeaderboardUser.objects.using(db_alias).filter(
            leaderboard_id=leaderboard_id,
            is_deleted=False
        ).values("leaderboard_user_id", "user_id")

        current_user_id = uuid.UUID(token["user_id"])
        current_username = users.get(current_user_id, "Unknown")

        current_leaderboard_user_id = None
        current_user_rank = None

        for u in leaderboard_users:
            if u["user_id"] == current_user_id:
                current_leaderboard_user_id = u["leaderboard_user_id"]
                break

        user_count = len(leaderboard_users)

        if user_count == 0:
            return Response(
                {
                    "leaderboard_id": leaderboard_id,
                    "user_count": 0,
                    "rows": []
                },
                status=status.HTTP_200_OK,
            )

        leaderboard_user_ids = [u["leaderboard_user_id"] for u in leaderboard_users]

        leaderboard_user_to_user = {
            u["leaderboard_user_id"]: u["user_id"]
            for u in leaderboard_users
        }

        user_ids = list(leaderboard_user_to_user.values())

        # ---------- Fetch usernames ----------
        users = {
            u.user_id: u.username
            for u in CompanyUser.objects.using(db_alias)
            .filter(user_id__in=user_ids)
            .only("user_id", "username")
        }

        # ---------- Latest match ----------
        latest_match = (
            FinalLeaderboardPoints.objects.using(db_alias)
            .filter(leaderboard_user_id__in=leaderboard_user_ids)
            .order_by("-match_number")
            .values_list("match_number", flat=True)
            .first()
        )

        if not latest_match:
            return Response(
                {
                    "leaderboard_id": leaderboard.leaderboard_id,
                    "leaderboard_name": leaderboard.leaderboard_name,
                    "user_count": user_count,
                    "rows": []
                },
                status=status.HTTP_200_OK
            )

        # ---------- Fetch leaderboard ----------
        leaderboard_rows = (
            FinalLeaderboardPoints.objects.using(db_alias)
            .filter(
                leaderboard_user_id__in=leaderboard_user_ids,
                match_number=latest_match
            )
            .order_by("rank")
            .only(
                "leaderboard_user_id",
                "points1",
                "points2",
                "rank",
                "previous_rank"
            )
        )

        current_user_rank = FinalLeaderboardPoints.objects.using(db_alias).filter(
            leaderboard_user_id=current_leaderboard_user_id,
            match_number=latest_match
        ).values_list("rank", flat=True).first()

        rows = []

        for fp in leaderboard_rows:

            lb_user_id = fp.leaderboard_user_id
            user_id = leaderboard_user_to_user.get(lb_user_id)

            curr_rank = fp.rank
            prev_rank = fp.previous_rank
            total = fp.points1 + fp.points2

            # Compute delta
            if prev_rank:
                delta = prev_rank - curr_rank
                delta_position = 1 if delta > 0 else 2 if delta < 0 else 0
                delta_rank = abs(delta)
            else:
                delta_position = 0
                delta_rank = 0

            rows.append({
                "username": users.get(user_id, "Unknown"),
                "points1": fp.points1,
                "points2": fp.points2,
                "total_points": total,
                "rank": curr_rank,
                "delta_position": delta_position,
                "delta_rank": delta_rank,
            })

        return Response(
            {
                "leaderboard_id": leaderboard.leaderboard_id,
                "leaderboard_name": leaderboard.leaderboard_name,
                "event_id": leaderboard.event_id,
                "match_number": latest_match,
                "user_count": user_count,
                "current_user_rank": current_user_rank,
                "current_username": current_username,
                "rows": rows,
            },
            status=status.HTTP_200_OK,
        )
    

from math import ceil

class LeaderboardBoardPaginatedAPIViewV2(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [HasValidJWT]

    PAGE_SIZE = 10

    def get(self, request, leaderboard_id):

        token = request.auth
        company_display_id = token["company_display_id"]

        page = int(request.GET.get("page", 1))

        db_alias = get_company_db(company_display_id)
        if not db_alias:
            return Response({"rows": []}, status=status.HTTP_200_OK)

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

        leaderboard_users = LeaderboardUser.objects.using(db_alias).filter(
            leaderboard_id=leaderboard_id,
            is_deleted=False
        )

        user_count = leaderboard_users.count()

        if user_count == 0:
            return Response(
                {
                    "leaderboard_id": leaderboard_id,
                    "user_count": 0,
                    "rows": []
                },
                status=status.HTTP_200_OK
            )

        leaderboard_user_ids = list(
            leaderboard_users.values_list("leaderboard_user_id", flat=True)
        )

        leaderboard_user_to_user = {
            lu.leaderboard_user_id: lu.user_id
            for lu in leaderboard_users
        }

        user_ids = list(leaderboard_user_to_user.values())

        users = {
            u.user_id: u.username
            for u in CompanyUser.objects.using(db_alias).filter(
                user_id__in=user_ids
            )
        }

        latest_match = (
            FinalLeaderboardPoints.objects.using(db_alias)
            .filter(leaderboard_user_id__in=leaderboard_user_ids)
            .order_by("-match_number")
            .values_list("match_number", flat=True)
            .first()
        )

        previous_match = latest_match - 1 if latest_match and latest_match > 1 else None

        current_points = FinalLeaderboardPoints.objects.using(db_alias).filter(
            leaderboard_user_id__in=leaderboard_user_ids,
            match_number=latest_match
        )

        rows = []

        for fp in current_points:

            user_id = leaderboard_user_to_user.get(fp.leaderboard_user_id)

            total = fp.points1 + fp.points2

            rows.append({
                "leaderboard_user_id": fp.leaderboard_user_id,
                "username": users.get(user_id, "Unknown"),
                "points1": fp.points1,
                "points2": fp.points2,
                "total_points": total,
            })

        rows.sort(key=lambda x: x["total_points"], reverse=True)

        current_rank_map = {}

        for idx, row in enumerate(rows, start=1):
            row["rank"] = idx
            current_rank_map[row["leaderboard_user_id"]] = idx

        previous_rank_map = {}

        if previous_match:

            prev_points = FinalLeaderboardPoints.objects.using(db_alias).filter(
                leaderboard_user_id__in=leaderboard_user_ids,
                match_number=previous_match
            )

            prev_rows = []

            for fp in prev_points:
                total = fp.points1 + fp.points2
                prev_rows.append({
                    "leaderboard_user_id": fp.leaderboard_user_id,
                    "total_points": total
                })

            prev_rows.sort(key=lambda x: x["total_points"], reverse=True)

            for idx, row in enumerate(prev_rows, start=1):
                previous_rank_map[row["leaderboard_user_id"]] = idx

        for row in rows:

            user_lb_id = row["leaderboard_user_id"]

            prev_rank = previous_rank_map.get(user_lb_id)
            curr_rank = row["rank"]

            if prev_rank is None:
                row["delta_position"] = 0
                row["delta_rank"] = 0
            else:

                delta = prev_rank - curr_rank

                if delta > 0:
                    row["delta_position"] = 1   # moved up
                elif delta < 0:
                    row["delta_position"] = 2   # moved down
                else:
                    row["delta_position"] = 0   # unchanged

                row["delta_rank"] = abs(delta)

            del row["leaderboard_user_id"]

        # ---------- Pagination ----------
        total_pages = ceil(len(rows) / self.PAGE_SIZE)

        start = (page - 1) * self.PAGE_SIZE
        end = start + self.PAGE_SIZE

        paginated_rows = rows[start:end]

        return Response(
            {
                "leaderboard_id": leaderboard.leaderboard_id,
                "leaderboard_name": leaderboard.leaderboard_name,
                "event_id": leaderboard.event_id,
                "match_number": latest_match,
                "user_count": user_count,
                "page": page,
                "total_pages": total_pages,
                "rows": paginated_rows,
            },
            status=status.HTTP_200_OK,
        )

