from django.shortcuts import render
from rest_framework.views import APIView

from core.authentication import CookieJWTAuthentication
from core.permissions import HasValidJWT
from core.models.cricket_event import CricketEvent


class SelectEventViewV1(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [HasValidJWT]

    def get(self, request):
        token = request.auth  # decoded JWT (available if needed)

        events = CricketEvent.objects.filter(
            status=CricketEvent.STATUS_ACTIVE,
            allow_predictions=True
        ).order_by("start_date")

        return render(
            request,
            "fixtures/select_event.html",
            {
                "events": events,
                "company_display_id": token["company_display_id"],
            }
        )

from django.shortcuts import render, redirect
from rest_framework.views import APIView

from core.authentication import CookieJWTAuthentication
from core.permissions import HasValidJWT
from core.models.cricket_event import CricketEvent
from core.models.cricket_match_details import CricketMatchDetails


class FixturesViewV1(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [HasValidJWT]

    def get(self, request, event_id):
        token = request.auth  # JWT payload

        try:
            event = CricketEvent.objects.get(event_id=event_id)
        except CricketEvent.DoesNotExist:
            return redirect("select_event")

        upcoming_matches = CricketMatchDetails.objects.filter(
            event=event,
            status_id__in=[1, 2],
            is_active=True,
            is_deleted=False
        ).order_by("match_date", "match_time")

        past_matches = CricketMatchDetails.objects.filter(
            event=event,
            status_id__in=[3, 4],
            is_deleted=False
        ).order_by("-match_date", "-match_time")

        return render(
            request,
            "fixtures/fixtures.html",
            {
                "event": event,
                "upcoming_matches": upcoming_matches,
                "past_matches": past_matches,
                "company_display_id": token["company_display_id"],
            }
        )

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.authentication import CookieJWTAuthentication
from core.permissions import HasValidJWT
from core.models.cricket_event import CricketEvent


class SelectEventAPIViewV2(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [HasValidJWT]

    def get(self, request):
        token = request.auth

        events = CricketEvent.objects.filter(
            status=CricketEvent.STATUS_ACTIVE,
            allow_predictions=True
        ).order_by("start_date")

        data = {
            "company_display_id": token["company_display_id"],
            "events": [
                {
                    "event_id": event.event_id,
                    "display_event_id": event.display_event_id,
                    "event_name": event.event_name,
                    "short_name": event.short_name,
                    "location": event.location,
                    "allow_predictions": event.allow_predictions,
                    "is_public": event.is_public,
                    "is_featured": event.is_featured,
                    "start_date": event.start_date,
                    "end_date": event.end_date,
                    "status": event.get_status_display(),
                }
                for event in events
            ],
        }

        return Response(data, status=status.HTTP_200_OK)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.authentication import CookieJWTAuthentication
from core.permissions import HasValidJWT
from core.models.cricket_event import CricketEvent
from core.models.cricket_match_details import CricketMatchDetails


class FixturesAPIViewV2(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [HasValidJWT]

    def get(self, request, event_id):
        token = request.auth

        try:
            event = CricketEvent.objects.get(event_id=event_id)
        except CricketEvent.DoesNotExist:
            return Response(
                {"detail": "Event not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        upcoming_matches = CricketMatchDetails.objects.filter(
            event=event,
            status_id__in=[1, 2],
            is_active=True,
            is_deleted=False
        ).order_by("match_date", "match_time")

        past_matches = CricketMatchDetails.objects.filter(
            event=event,
            status_id__in=[3, 4],
            is_deleted=False
        ).order_by("-match_date", "-match_time")

        def serialize_match(match):
            return {
                "match" : {
                    "match_id": match.match_id,
                    "match_display_id": match.display_match_id,
                    "match_date": match.match_date,
                    "match_time": match.match_time,
                    "status_id": match.status_id,
                    "is_active": match.is_active,
                    "team1": {
                        "team_id": match.team1.team_id,
                        "team_name": match.team1.team_name,
                        "team_short_name": match.team1.short_name,
                        "team_display_id": match.team1.display_team_id,
                    },
                    "team2": {
                        "team_id": match.team2.team_id,
                        "team_name": match.team2.team_name,
                        "team_short_name": match.team2.short_name,
                        "team_display_id": match.team2.display_team_id,
                    },
}}

        data = {
            "company_display_id": token["company_display_id"],
            "event": {
                "event_id": event.event_id,
                "event_name": event.event_name,
                "event_short_name": event.short_name,
                "allow_predictions": event.allow_predictions,
                "is_public": event.is_public,
                "is_featured": event.is_featured,
                "start_date": event.start_date,
                "end_date": event.end_date,
            },
            "upcoming_matches": [serialize_match(m) for m in upcoming_matches],
            "past_matches": [serialize_match(m) for m in past_matches],
        }

        return Response(data, status=status.HTTP_200_OK)
